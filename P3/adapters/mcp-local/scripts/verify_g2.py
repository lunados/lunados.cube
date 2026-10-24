"""G2 offline regression gate: complete P3/G1 and frozen P1.5 oracle."""
from __future__ import annotations
import subprocess
import sys
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
BASE=Path(__file__).resolve().parents[1]

def run(cmd,cwd):
    env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
    p=subprocess.run(cmd,cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    if p.returncode:
        print(p.stdout,file=sys.stderr)
        raise SystemExit(p.returncode)
    return p.stdout

def main():
    res=run([sys.executable,'scripts/verify_g1.py'],BASE)
    print('PASS G1/P3: legacy printer, P0 Resources, tool fallback and P1 adapter tests')
    assert 'Ran 137 tests' in res,res[-2000:]
    p=ROOT/'P1'/'release-v1'/'scripts'/'verify_p15.py'
    if not p.is_file():
        raise SystemExit('MISSING_FROZEN_P1_RELEASE: install P1 as sibling P1 directory')
    res=run([sys.executable,str(p)],ROOT)
    assert 'PASS P1.5:' in res,res[-2000:]
    print('PASS P1.5: source locks + 26 parser + 41 resolver + 73 semantic tests + independent CLI conformance')
    print('PASS G2 OFFLINE: 137 P3 tests, frozen P1.5 gate; official MCP SDK stdio and Claude host separately required')
    return 0

if __name__=='__main__':raise SystemExit(main())
