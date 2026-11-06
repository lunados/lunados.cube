"""Contract cases for the documentary, offline module-capabilities checker."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import check  # noqa: E402


def encoded(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


class CheckerCases(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source.txt"
        self.source.write_bytes(b"bounded source revision\n")
        self.descriptor = {
            "format": "aiaeao.module-capabilities/1",
            "module": {"id": "example.module", "version": "v1", "owner": "example-owner"},
            "sources": [{
                "id": "s1", "artifact": "example:source.txt", "version": "r1",
                "owner": "example-owner", "sha256": hashlib.sha256(self.source.read_bytes()).hexdigest(),
            }],
            "capabilities": [{
                "id": "inspect", "version": "v1", "status": "candidate", "source_ids": ["s1"],
                "inputs": [{"role": "request", "description": "declared input"}],
                "outputs": [{"role": "report", "description": "declared result"}],
                "exclusions": ["no execution claim"],
            }],
            "exclusions": ["no admission"],
        }
        self.manifest = {
            "format": "aiaeao.module-capabilities.pin-manifest/1",
            "descriptors": [{
                "path": "descriptor.json", "ref": "example:descriptor/v1", "sha256": "",
                "sources": [{"id": "s1", "path": "source.txt"}],
            }],
        }
        self.manifest_path = self.root / "pins.json"

    def run_case(self, descriptor: dict | None = None, manifest: dict | None = None) -> tuple[str, list[str], bytes | None]:
        doc = self.descriptor if descriptor is None else descriptor
        pins = copy.deepcopy(self.manifest if manifest is None else manifest)
        data = encoded(doc)
        (self.root / "descriptor.json").write_bytes(data)
        pins["descriptors"][0]["sha256"] = hashlib.sha256(data).hexdigest()
        self.manifest_path.write_bytes(encoded(pins))
        return check.check(self.manifest_path)

    def test_valid_and_canonical_neighbors(self) -> None:
        status, diagnostics, neighbors = self.run_case()
        self.assertEqual((status, diagnostics), ("PASS", []))
        self.assertEqual(neighbors, encoded({
            "format": "aiaeao.module-capabilities.neighbors/1",
            "items": [{
                "module_id": "example.module", "module_version": "v1",
                "descriptor_format": "aiaeao.module-capabilities/1",
                "descriptor_ref": "example:descriptor/v1",
                "descriptor_sha256": hashlib.sha256((self.root / "descriptor.json").read_bytes()).hexdigest(),
            }],
        }))

    def test_wrong_format_type_and_status(self) -> None:
        for mutate in (
            lambda d: d.update(format="aiaeao.module-capabilities/2"),
            lambda d: d["capabilities"][0].update(inputs="not-an-array"),
            lambda d: d["capabilities"][0].update(status="active"),
        ):
            with self.subTest(mutate=mutate):
                doc = copy.deepcopy(self.descriptor)
                mutate(doc)
                self.assertEqual(self.run_case(doc)[0], "FAIL")

    def test_implemented_needs_pinned_evidence(self) -> None:
        doc = copy.deepcopy(self.descriptor)
        doc["capabilities"][0]["status"] = "implemented"
        self.assertEqual(self.run_case(doc)[0], "FAIL")
        doc["capabilities"][0]["implementation_evidence"] = ["s1"]
        self.assertEqual(self.run_case(doc)[0], "PASS")

    def test_duplicate_ids_and_undeclared_references(self) -> None:
        doc = copy.deepcopy(self.descriptor)
        doc["capabilities"].append(copy.deepcopy(doc["capabilities"][0]))
        self.assertIn("duplicate ID", " ".join(self.run_case(doc)[1]))
        doc = copy.deepcopy(self.descriptor)
        doc["capabilities"][0]["source_ids"] = ["missing"]
        self.assertEqual(self.run_case(doc)[0], "FAIL")

    def test_missing_source_mapping_is_invalid(self) -> None:
        pins = copy.deepcopy(self.manifest)
        pins["descriptors"][0]["sources"] = [{"id": "other", "path": "source.txt"}]
        self.assertIn("exactly match", " ".join(self.run_case(manifest=pins)[1]))

    def test_changed_bytes_fail_and_missing_bytes_are_unavailable(self) -> None:
        self.source.write_bytes(b"changed")
        self.assertEqual(self.run_case()[0], "FAIL")
        self.source.unlink()
        self.assertEqual(self.run_case()[0], "UNAVAILABLE")

    def test_missing_descriptor_is_unavailable(self) -> None:
        self.run_case()
        (self.root / "descriptor.json").unlink()
        self.assertEqual(check.check(self.manifest_path)[0], "UNAVAILABLE")

    def test_changed_descriptor_bytes_fail_and_cli_codes_match(self) -> None:
        self.run_case()
        script = Path(check.__file__).resolve()
        (self.root / "descriptor.json").write_bytes(b"changed")
        failed = subprocess.run([sys.executable, str(script), "--manifest", str(self.manifest_path)],
                                capture_output=True, text=True, check=False)
        self.assertEqual(failed.returncode, 1)
        self.assertEqual(json.loads(failed.stdout)["status"], "FAIL")
        (self.root / "descriptor.json").unlink()
        unavailable = subprocess.run([sys.executable, str(script), "--manifest", str(self.manifest_path)],
                                     capture_output=True, text=True, check=False)
        self.assertEqual(unavailable.returncode, 2)
        self.assertEqual(json.loads(unavailable.stdout)["status"], "UNAVAILABLE")

    def test_duplicate_json_key_refused(self) -> None:
        self.run_case()
        bad = b'{"format":"x","format":"y"}'
        (self.root / "descriptor.json").write_bytes(bad)
        pins = json.loads(self.manifest_path.read_text())
        pins["descriptors"][0]["sha256"] = hashlib.sha256(bad).hexdigest()
        self.manifest_path.write_bytes(encoded(pins))
        self.assertIn("duplicate JSON key", " ".join(check.check(self.manifest_path)[1]))

    def test_generic_mcp_tool_cannot_claim_unmodified_v2(self) -> None:
        doc = copy.deepcopy(self.descriptor)
        doc["capabilities"][0]["v2_ref"] = {
            "contract": "aiaeao-module-contract/v2", "source_id": "s1",
            "capability_id": "generic-mcp-tool", "capability_version": "v1",
        }
        self.assertEqual(self.run_case(doc)[0], "FAIL")

    def test_exact_v2_manifest_reference(self) -> None:
        v2 = {"contract": {"identity": "aiaeao-module-contract", "version": "v2"},
              "descriptors": [
                  {"capability_id": "structured-inspection", "capability_version": "v1",
                   "parameters_schema_ref": "schemas/payloads.schema.json#/$defs/structured-parameters",
                   "result_schema_ref": "schemas/payloads.schema.json#/$defs/structured-result"},
                  {"capability_id": "artifact-observation", "capability_version": "v1",
                   "parameters_schema_ref": "schemas/payloads.schema.json#/$defs/artifact-observation-parameters",
                   "result_schema_ref": "schemas/payloads.schema.json#/$defs/artifact-observation-result"},
              ]}
        v2_path = self.root / "v2-manifest.json"
        v2_path.write_bytes(encoded(v2))
        doc = copy.deepcopy(self.descriptor)
        doc["sources"].append({"id": "v2", "artifact": "aiaeao-module-contract:v2/manifest.json",
                               "version": "v2", "owner": "contract-maintainers",
                               "sha256": hashlib.sha256(v2_path.read_bytes()).hexdigest()})
        doc["capabilities"][0]["source_ids"].append("v2")
        doc["capabilities"][0]["v2_ref"] = {
            "contract": "aiaeao-module-contract/v2", "source_id": "v2",
            "capability_id": "structured-inspection", "capability_version": "v1",
        }
        pins = copy.deepcopy(self.manifest)
        pins["descriptors"][0]["sources"].append({"id": "v2", "path": "v2-manifest.json"})
        self.assertEqual(self.run_case(doc, pins)[0], "PASS")
        v2["descriptors"][0]["result_schema_ref"] = "wrong"
        v2_path.write_bytes(encoded(v2))
        doc["sources"][1]["sha256"] = hashlib.sha256(v2_path.read_bytes()).hexdigest()
        self.assertEqual(self.run_case(doc, pins)[0], "FAIL")
        v2["descriptors"][0]["result_schema_ref"] = "schemas/payloads.schema.json#/$defs/structured-result"
        v2["contract"]["version"] = "v1"
        v2_path.write_bytes(encoded(v2))
        doc["sources"][1]["sha256"] = hashlib.sha256(v2_path.read_bytes()).hexdigest()
        self.assertEqual(self.run_case(doc, pins)[0], "FAIL")

    def test_neighbors_order_is_stable(self) -> None:
        items = [
            {"module_id": name, "module_version": "v1", "descriptor_format": "aiaeao.module-capabilities/1",
             "descriptor_ref": name, "descriptor_sha256": "0" * 64}
            for name in ("zeta", "alpha")
        ]
        actual = json.loads(check.canonical_neighbors(items))
        self.assertEqual([x["module_id"] for x in actual["items"]], ["alpha", "zeta"])
        with self.assertRaises(ValueError):
            check.canonical_neighbors(items + [items[0]])


if __name__ == "__main__":
    unittest.main()
