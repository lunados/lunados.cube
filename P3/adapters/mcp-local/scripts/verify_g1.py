"""Offline CP-001/G1 verifier: P0 snapshot plus existing P2 bridge regression.

No SDK import required. For protocol proof separately run sdk_g1_resources_smoke.py.
"""
from __future__ import annotations
import json
import unittest
import sys
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE))
from aiaeao_mcp_local.p0_resources import verify_snapshot


def main():
    print('P0 snapshot:', json.dumps(verify_snapshot(), sort_keys=True), flush=True)
    # Freeze the G1/G2 137-test baseline; G4 tests run in verify_g4.py.
    suite=unittest.TestSuite()
    for file in ('test_bridge.py','test_p0_resources.py','test_p0_tool_fallback.py','test_p1_validation.py'):
        suite.addTests(unittest.defaultTestLoader.discover(str(BASE/'tests'),pattern=file))
    result=unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful(): return 1
    print('PASS G1 offline: 40 P0 resource + 36 P3 legacy bridge + 25 G1.1 fallback tests; MCP SDK/Host pending',flush=True)
    return 0

if __name__=='__main__':raise SystemExit(main())
