#!/usr/bin/env python3
"""Build the seven documentary discovery references from verified owner pins."""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "contracts/module-capabilities/v1/check.py"
OUTPUT = ROOT / "P3/adapters/mcp-local/aiaeao_mcp_local/neighbors.json"
EXPECTED = {
    "aiaeao.core-server", "aiaeao.server-gui", "aiaeao.web-app",
    "lunados.connector", "lunados.cube", "lunados.lib", "lunados.toolbox",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--relay", type=Path, required=True,
                        help="TASK-090 Relay worktree containing module-capabilities/v1/pins.json")
    parser.add_argument("--write", action="store_true", help="write the canonical block into the Cube package")
    args = parser.parse_args()

    spec = importlib.util.spec_from_file_location("module_capabilities_check", CHECKER)
    assert spec and spec.loader
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)

    manifests = (
        ROOT / "module-capabilities/v1/pins.json",
        ROOT.parent / "lunados.lib/module-capabilities/v1/pins.json",
        ROOT.parent / "lunados.toolbox/module-capabilities/v1/pins.json",
        ROOT.parent / "lunados.connector/module-capabilities/v1/pins.json",
        args.relay / "module-capabilities/v1/pins.json",
    )
    items = []
    for manifest in manifests:
        status, diagnostics, raw = checker.check(manifest)
        if status != "PASS" or raw is None:
            print(f"{status} {manifest}: {'; '.join(diagnostics)}", file=sys.stderr)
            return 1
        items.extend(checker.json.loads(raw)["items"])
    ids = [item["module_id"] for item in items]
    if len(ids) != 7 or set(ids) != EXPECTED:
        print(f"FAIL unexpected module IDs: {ids}", file=sys.stderr)
        return 1
    raw = checker.canonical_neighbors(items)
    if args.write:
        OUTPUT.write_bytes(raw)
    elif not OUTPUT.is_file() or OUTPUT.read_bytes() != raw:
        print("FAIL neighbors.json differs from verified owner pins", file=sys.stderr)
        return 1
    print(f"PASS seven pinned neighbors ({len(raw)} canonical bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
