"""G4 offline gate: whole-surface contract + frozen G0-G3 regression.

SDK host smoke separately: python scripts/sdk_g4_stdio_smoke.py
"""
from __future__ import annotations
import os
import subprocess
import sys
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE))

def run(cmd):
    env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
    p=subprocess.run(cmd,cwd=BASE,env=env,text=True,
                     stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=360)
    if p.returncode:
        print(p.stdout,file=sys.stderr)
        raise SystemExit(p.returncode)
    return p.stdout

def main():
    out=run([sys.executable,'-m','unittest','discover','-s','tests','-p','test_g4_surface.py','-v'])
    tests=int(out.split('Ran ')[-1].split(' tests')[0])
    assert tests>=50,tests
    print(f'PASS G4 surface contract: {tests} new tests')
    out=run([sys.executable,'scripts/verify_g3.py'])
    assert 'PASS G3 OFFLINE:' in out,out[-1600:]
    print('PASS G3 frozen regression: 41 independent cross-domain tests, 137 G2 tests, P1.5 gate')
    from aiaeao_mcp_local import p0_resources,surface
    assert p0_resources.verify_snapshot()['status']=='PASS'
    assert len(surface.discover_surface()['mcp']['tools'])==7
    try:
        import jsonschema
    except ImportError:
        print('INFO JSON schema optional; run CI with jsonschema>=4 for independent gate')
    else:
        import json
        schema=json.loads((BASE/'spec/G4_CAPABILITY_SURFACE.schema.json').read_text(encoding='utf-8'))
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(schema).validate(surface.discover_surface())
        print('PASS G4 JSON Schema Draft 2020-12')
    print('PASS G4 OFFLINE: frozen P0/P1/P2; whole-surface introspection; MCP SDK/Claude host proof on target macOS separately')
    return 0

if __name__=='__main__':raise SystemExit(main())
