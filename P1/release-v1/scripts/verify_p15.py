#!/usr/bin/env python3
"""One-command P1.5 release gate, no network/effects, with independent oracle."""
from __future__ import annotations
from pathlib import Path
import json,subprocess,sys,hashlib,os
REPO=Path(__file__).resolve().parents[3]
R=REPO/'P1'/'release-v1';V=REPO/'P1'/'semantic-validator-v1';P0=REPO/'AIAEAO_Pure_Cube_P0_v9.4'

def run(cmd,cwd=REPO):
    e=os.environ.copy();e['PYTHONDONTWRITEBYTECODE']='1'
    x=subprocess.run(cmd,cwd=cwd,env=e,check=False)
    if x.returncode: raise SystemExit(x.returncode)

def main():
    run([sys.executable,'scripts/test_release.py'],P0)
    run([sys.executable,'scripts/verify_semantic_release.py'],V)
    run([sys.executable,'-m','unittest','discover','-s','scripts','-p','conformance_cli.py','-v'],R)
    m=json.loads((P0/'manifest.json').read_text(encoding='utf8'))
    for name in ('core','time','observer'):
        assert m['entrypoints'][name].endswith('/v9.4/'+name+'.json')
    entry='https://cube.lunados.net/validation/v1/manifest.json'
    assert m['validation_profiles']['P1-VC/1.0.0']==entry
    publication=json.loads((P0/'validation'/'v1'/'manifest.json').read_text())
    assert publication['reference_version']=='v9.4'
    assert publication['function_invocation_available'] is False
    for key,info in publication['assets'].items():
        path=REPO/'AIAEAO_Pure_Cube_P0_v9.4'/info['href'].removeprefix('https://cube.lunados.net/')
        raw=path.read_bytes()
        assert hashlib.sha256(raw).hexdigest()==info['sha256'],(key,'sha256')
        assert len(raw)==info['bytes'],(key,'bytes')
    for line in (P0/'SHA256SUMS.txt').read_text().splitlines():
        sha,path=line.split('  ',1)
        assert hashlib.sha256((P0/path).read_bytes()).hexdigest()==sha,path
    print('PASS P1.5: P0 source locks, P1.1-P1.4 regression, independent black-box oracle, publication hashes')

if __name__=='__main__':main()
