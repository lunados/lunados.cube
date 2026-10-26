#!/usr/bin/env python3
"""P1.10.1-08 offline parity: G4 local adapter vs. staged G5 core dispatch for G-01..G-10.

Requires a fresh assembly: python3 P3/remote-mcp-g5/scripts/assemble_core.py
Compares the exact P1 report (or the MCP error code). Live G5 parity is part of host acceptance.
"""
import json, subprocess, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[3]
VEC = REPO/'P1/migration-profile-v2/fixtures/g01_g10_materialized.json'
LOCAL = '''
import sys,json;sys.dont_write_bytecode=True;sys.path.insert(0,sys.argv[1])
from aiaeao_mcp_local import p1_adapter
res={}
for c in json.load(open(sys.argv[2]))["cases"]:
    try: res[c["id"]]=p1_adapter.validate(c["input_text"],c["input_format"],c["context"],c.get("qualification_profiles"))["report"]
    except p1_adapter.P1AdapterFailure as e: res[c["id"]]={"err":e.diagnostic["code"]}
print(json.dumps(res))'''

def main():
    sys.dont_write_bytecode = True
    local = json.loads(subprocess.run([sys.executable, '-c', LOCAL, str(REPO/'P3/adapters/mcp-local'), str(VEC)],
                                      capture_output=True, text=True, check=True).stdout)
    sys.path.insert(0, str(REPO/'P3/remote-mcp-g5/.g5-runtime'))
    from core_runtime import dispatch
    cases = json.loads(VEC.read_text('utf-8'))['cases']; same = 0
    for c in cases:
        r = dispatch('cube_validate', {'input_text': c['input_text'], 'context': c['context'],
                                       'qualification_profiles': c.get('qualification_profiles')})
        remote = r['result']['report'] if r['ok'] else {'err': r['diagnostic']['code']}
        ok = remote == local[c['id']]; same += ok
        print('PASS' if ok else 'DIFF', c['id'])
    print(f'{same}/{len(cases)} identical'); sys.exit(0 if same == len(cases) else 1)

if __name__ == '__main__': main()
