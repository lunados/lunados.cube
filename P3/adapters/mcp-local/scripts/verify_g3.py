"""G3 offline release gate:  P0/P1/P2 separation and frozen prior regressions."""
from __future__ import annotations
import os
import subprocess
import sys
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parents[2]

def execute(command, cwd):
    env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
    proc=subprocess.run(command, cwd=cwd, env=env, text=True,
                        stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180)
    if proc.returncode:
        print(proc.stdout, file=sys.stderr)
        raise SystemExit(proc.returncode)
    return proc.stdout

def main():
    result=execute([sys.executable,'-m','unittest','discover','-v','-s','tests',
                    '-p','g3_cross_domain_cases.py'],BASE)
    count=int(result.split('Ran ')[-1].split(' tests')[0])
    print(f'PASS G3 local cross-domain: {count} independent tests')
    p3=execute([sys.executable,'scripts/verify_g2.py'],BASE)
    assert 'PASS G2 OFFLINE: 137 P3 tests' in p3, p3[-1000:]
    print('PASS G2 frozen regression: 137 P3 tests + P1.5 gate')
    # Optional independent JSON Schema validation of all three concrete traces.
    import json
    evidence=json.loads((BASE/'evidence/G3_OFFLINE_TRACE.json').read_text(encoding='utf-8'))
    schema=json.loads((BASE/'spec/G3_CROSS_DOMAIN_EVIDENCE.schema.json').read_text(encoding='utf-8'))
    assert set(evidence['scenarios']) == {'declared_fixture','p1_fail_p2_valid','p1_unresolved_p2_valid'}
    try:
        import jsonschema
    except ImportError:
        print('INFO independent JSON Schema test skipped (install jsonschema>=4)')
    else:
        jsonschema.Draft202012Validator.check_schema(schema)
        for trace in evidence['scenarios'].values():
            jsonschema.Draft202012Validator(schema).validate(trace)
        print('PASS G3 JSON Schema: 3 evidence scenarios')
    print('PASS G3 OFFLINE: CP-001 G3 independent evidence; official MCP SDK and Claude host separately required')
    return 0

if __name__=='__main__':raise SystemExit(main())
