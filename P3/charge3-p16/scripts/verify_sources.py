#!/usr/bin/env python3
"""Pin the Charge 3 P3 overlay separately from historic G5 source freeze."""
from __future__ import annotations
import hashlib
from pathlib import Path
REPO=Path(__file__).resolve().parents[3]
manifest=REPO/'P3/charge3-p16/CHARGE3_SOURCE_SHA256SUMS.txt'
if not manifest.is_file():raise SystemExit('FAIL: missing Charge 3 checksum manifest')
lines=manifest.read_text('utf-8').splitlines()
if len(lines)<14:raise SystemExit('FAIL: incomplete Charge 3 source checksum manifest')
for entry in lines:
    digest,rel=entry.split('  ',1)
    path=REPO/rel
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
        raise SystemExit('FAIL: Charge 3 source drift in '+rel)
print(f'PASS CHARGE 3 source SHA-256: {len(lines)} P3 overlay files')
