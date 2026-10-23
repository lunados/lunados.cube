#!/usr/bin/env python3
"""Verify pinned source copies, suite and released file hashes. Read-only."""
import hashlib,json,subprocess,sys
from pathlib import Path
p=Path(__file__).resolve().parents[1]
m=json.loads((p/'RELEASE_MANIFEST.json').read_text())
for item in m['files']:
    raw=(p/item['path']).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==item['sha256'],item['path']
    assert len(raw)==item['bytes']
for suite in ('tests_parser','tests'):
    r=subprocess.run([sys.executable,'-m','unittest','discover','-s',suite,'-v'],cwd=p)
    if r.returncode:raise SystemExit(r.returncode)
print('PASS release integrity:',len(m['files']),'files')
