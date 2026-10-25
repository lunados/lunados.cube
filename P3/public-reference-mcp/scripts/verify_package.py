#!/usr/bin/env python3
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parent.parent
manifest = root / 'SHA256SUMS.txt'
assert manifest.is_file(), 'SHA256SUMS.txt missing'
count=0
for row in manifest.read_text().splitlines():
    if not row.strip():continue
    digest,relative = row.split('  ',1)
    path=(root/relative).resolve()
    assert path.is_relative_to(root.resolve()), 'path escape in SHA manifest'
    assert path.is_file(), relative
    got=hashlib.sha256(path.read_bytes()).hexdigest()
    assert got==digest, f'SHA-256 mismatch: {relative}'
    count += 1
print(f'PASS Public Reference MCP archive integrity: {count} files')
