#!/usr/bin/env python3
"""Reproduce P1.4 tests and SHA256 checks; no server or network required."""
import hashlib,json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
m=json.loads((root/'RELEASE_MANIFEST.json').read_text())
for f in m['files']:
    b=(root/f['path']).read_bytes()
    assert len(b)==f['bytes'] and hashlib.sha256(b).hexdigest()==f['sha256'],f['path']
for suite in ('tests_parser','tests','tests_semantic'):
    r=subprocess.run([sys.executable,'-m','unittest','discover','-s',suite,'-q'],cwd=root)
    if r.returncode:raise SystemExit(r.returncode)
print('PASS P1.4 release integrity:',len(m['files']),'files; 26 parser + 41 resolver + 73 semantic tests')
