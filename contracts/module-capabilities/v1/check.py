#!/usr/bin/env python3
"""Check explicitly supplied local capability descriptors and their exact bytes.

This is a documentary, read-only check. It does not load modules, contact hosts,
infer capability implementation, or grant admission/authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator
except ImportError:
    print(json.dumps({"status": "UNAVAILABLE", "diagnostics": ["jsonschema dependency missing; install requirements.txt"]}))
    raise SystemExit(2)


HERE = Path(__file__).resolve().parent
DESCRIPTOR_FORMAT = "aiaeao.module-capabilities/1"
NEIGHBORS_FORMAT = "aiaeao.module-capabilities.neighbors/1"


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _strict_json(data: bytes) -> Any:
    return json.loads(
        data.decode("utf-8"),
        object_pairs_hook=_strict_object,
        parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f"invalid JSON constant: {value}")),
    )


def _schema(name: str) -> Draft202012Validator:
    schema = _strict_json((HERE / name).read_bytes())
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def _errors(validator: Draft202012Validator, document: Any, label: str) -> list[str]:
    return [
        f"{label}: {'.'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}"
        for error in sorted(validator.iter_errors(document), key=lambda error: (list(map(str, error.absolute_path)), error.message))
    ]


def _path(base: Path, raw: str) -> Path:
    # Paths come only from the caller-supplied local manifest. No URL or glob lookup.
    if "://" in raw or raw.startswith("urn:"):
        raise ValueError("manifest path must be a local filesystem path")
    path = Path(raw)
    return path if path.is_absolute() else base / path


def _bytes(path: Path) -> bytes | None:
    try:
        return path.read_bytes()
    except OSError:
        return None


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _unique(values: list[str], label: str, failures: list[str]) -> None:
    if len(values) != len(set(values)):
        failures.append(f"{label}: duplicate ID")


def _v2_ref_valid(data: bytes, capability: dict[str, Any]) -> bool:
    try:
        manifest = _strict_json(data)
    except (UnicodeError, ValueError):
        return False
    if not isinstance(manifest, dict) or manifest.get("contract") != {"identity": "aiaeao-module-contract", "version": "v2"}:
        return False
    descriptors = manifest.get("descriptors")
    if not isinstance(descriptors, list) or len(descriptors) != 2:
        return False
    expected = {
        "structured-inspection": (
            "schemas/payloads.schema.json#/$defs/structured-parameters",
            "schemas/payloads.schema.json#/$defs/structured-result",
        ),
        "artifact-observation": (
            "schemas/payloads.schema.json#/$defs/artifact-observation-parameters",
            "schemas/payloads.schema.json#/$defs/artifact-observation-result",
        ),
    }
    found: dict[str, tuple[str, str]] = {}
    for item in descriptors:
        if not isinstance(item, dict) or item.get("capability_version") != "v1":
            return False
        capability_id = item.get("capability_id")
        if capability_id not in expected or capability_id in found:
            return False
        found[capability_id] = (item.get("parameters_schema_ref"), item.get("result_schema_ref"))
    if found != expected:
        return False
    ref = capability["v2_ref"]
    return ref["capability_id"] in found and ref["capability_version"] == "v1"


def canonical_neighbors(items: list[dict[str, str]]) -> bytes:
    """Serialize only the new neighbors block, independent of G4/G5 envelopes."""
    ordered = sorted(items, key=lambda item: item["module_id"])
    block = {"format": NEIGHBORS_FORMAT, "items": ordered}
    errors = _errors(_schema("neighbors.schema.json"), block, "neighbors")
    if errors or len({item["module_id"] for item in ordered}) != len(ordered):
        raise ValueError("invalid or duplicate neighbors: " + "; ".join(errors))
    return json.dumps(block, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def check(manifest_path: Path) -> tuple[str, list[str], bytes | None]:
    failures: list[str] = []
    unavailable: list[str] = []
    raw = _bytes(manifest_path)
    if raw is None:
        return "UNAVAILABLE", ["pin manifest: local bytes missing"], None
    try:
        manifest = _strict_json(raw)
    except (UnicodeError, ValueError) as exc:
        return "FAIL", [f"pin manifest: invalid JSON: {exc}"], None
    errors = _errors(_schema("pin-manifest.schema.json"), manifest, "pin manifest")
    if errors:
        return "FAIL", errors, None

    descriptor_validator = _schema("descriptor.schema.json")
    base = manifest_path.parent
    module_ids: list[str] = []
    refs: list[str] = []
    neighbor_items: list[dict[str, str]] = []
    for index, pin in enumerate(manifest["descriptors"]):
        label = f"descriptor[{index}]"
        refs.append(pin["ref"])
        _unique([source["id"] for source in pin["sources"]], f"{label} manifest sources", failures)
        try:
            descriptor_path = _path(base, pin["path"])
        except ValueError as exc:
            failures.append(f"{label}: {exc}")
            continue
        data = _bytes(descriptor_path)
        if data is None:
            unavailable.append(f"{label}: local descriptor bytes missing")
            continue
        if _hash(data) != pin["sha256"]:
            failures.append(f"{label}: descriptor SHA-256 mismatch")
            continue
        try:
            descriptor = _strict_json(data)
        except (UnicodeError, ValueError) as exc:
            failures.append(f"{label}: invalid JSON: {exc}")
            continue
        errors = _errors(descriptor_validator, descriptor, label)
        if errors:
            failures.extend(errors)
            continue

        module_ids.append(descriptor["module"]["id"])
        source_ids = [source["id"] for source in descriptor["sources"]]
        _unique(source_ids, f"{label} declared sources", failures)
        _unique([cap["id"] for cap in descriptor["capabilities"]], f"{label} capabilities", failures)
        declared = {source["id"]: source for source in descriptor["sources"]}
        supplied = {source["id"]: source["path"] for source in pin["sources"]}
        if set(declared) != set(supplied):
            failures.append(f"{label}: manifest source IDs must exactly match descriptor sources")
            continue
        source_bytes: dict[str, bytes] = {}
        for source_id, source in declared.items():
            try:
                source_path = _path(base, supplied[source_id])
            except ValueError as exc:
                failures.append(f"{label} source {source_id}: {exc}")
                continue
            content = _bytes(source_path)
            if content is None:
                unavailable.append(f"{label} source {source_id}: local bytes missing")
            elif _hash(content) != source["sha256"]:
                failures.append(f"{label} source {source_id}: SHA-256 mismatch")
            else:
                source_bytes[source_id] = content

        for capability in descriptor["capabilities"]:
            cap_label = f"{label} capability {capability['id']}"
            for field in ("source_ids", "implementation_evidence"):
                if not set(capability.get(field, [])).issubset(declared):
                    failures.append(f"{cap_label}: {field} refers to undeclared source")
            ref = capability.get("v2_ref")
            if ref is not None:
                source_id = ref["source_id"]
                if source_id not in capability["source_ids"] or source_id not in declared:
                    failures.append(f"{cap_label}: v2_ref source must be declared and cited")
                elif declared[source_id]["version"] != "v2":
                    failures.append(f"{cap_label}: v2_ref source version is not v2")
                elif source_id in source_bytes and not _v2_ref_valid(source_bytes[source_id], capability):
                    failures.append(f"{cap_label}: v2_ref is not in the pinned v2 manifest")

        neighbor_items.append({
            "module_id": descriptor["module"]["id"],
            "module_version": descriptor["module"]["version"],
            "descriptor_format": DESCRIPTOR_FORMAT,
            "descriptor_ref": pin["ref"],
            "descriptor_sha256": pin["sha256"],
        })

    _unique(refs, "pin manifest descriptor refs", failures)
    _unique(module_ids, "pin manifest module IDs", failures)
    if failures:
        return "FAIL", failures + unavailable, None
    if unavailable:
        return "UNAVAILABLE", unavailable, None
    try:
        neighbors = canonical_neighbors(neighbor_items)
    except ValueError as exc:
        return "FAIL", [str(exc)], None
    return "PASS", [], neighbors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path, help="explicit local pin manifest")
    parser.add_argument("--neighbors-only", action="store_true", help="print canonical neighbors bytes only on PASS")
    args = parser.parse_args()
    status, diagnostics, neighbors = check(args.manifest)
    if status == "PASS" and args.neighbors_only:
        print(neighbors.decode("utf-8"))
    else:
        print(json.dumps({"status": status, "diagnostics": diagnostics}, ensure_ascii=False, sort_keys=True))
    return {"PASS": 0, "FAIL": 1, "UNAVAILABLE": 2}[status]


if __name__ == "__main__":
    raise SystemExit(main())
