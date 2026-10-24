#!/usr/bin/env python3
"""Offline G5 Cloudflare non-Python frozen-asset coverage gate.

Executed after verify_g5.py, which assembles .g5-runtime. No remote claim.
"""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
RT=HERE/'.g5-runtime'
MANIFEST=RT/'G5_SOURCE_MANIFEST.json'
if not MANIFEST.is_file():sys.exit('FAIL: first run python3 P3/remote-mcp-g5/scripts/verify_g5.py')
config=json.loads((RT/'wrangler.jsonc').read_text('utf-8'))
source_config=json.loads((HERE/'python-core/wrangler.jsonc').read_text('utf-8'))
if config!=source_config:sys.exit('FAIL: staged wrangler config differs from source')
if not config.get('find_additional_modules'):sys.exit('FAIL: auto module discovery disabled')
if config.get('workers_dev') is not False or config.get('preview_urls') is not False:
    sys.exit('FAIL: private Python Core cannot have public target')
rules=config.get('rules',[])
if not rules or any(x.get('type')!='Text' for x in rules):
    sys.exit('FAIL: asset module rules must be Text only')
patterns=[s for rule in rules for s in rule.get('globs',[])]
manifest=json.loads(MANIFEST.read_text('utf-8'))
assets={x['path']:x['sha256'] for x in manifest['files'] if Path(x['path']).suffix != '.py'}
if len(assets)!=40:
    sys.exit(f'FAIL: expected 40 frozen non-Python assets, found {len(assets)}')
matched={p.relative_to(RT).as_posix() for pattern in patterns for p in RT.glob(pattern) if p.is_file()}
missing=sorted(set(assets)-matched)
if missing:sys.exit('FAIL: missing Wrangler Text coverage: '+', '.join(missing))
for path,digest in assets.items():
    full=RT/path
    if not full.is_file():sys.exit('FAIL: frozen source file absent: '+path)
    if hashlib.sha256(full.read_bytes()).hexdigest()!=digest:
        sys.exit('FAIL: frozen source digest mismatch: '+path)
from collections import Counter
counts=Counter('P0' if x.startswith('P3/adapters/mcp-local/p0_snapshot/') else
               'P1' if x.startswith('P1/semantic-validator-v1/baseline/') else
               'P2' if x.startswith('P2/visual-printer-2d-lab/reference/') else 'OTHER'
               for x in assets)
if counts!={'P0':14,'P1':20,'P2':6}:
    sys.exit(f'FAIL: unexpected asset family counts {dict(counts)}')
# Explicitly check the exact resources loaded by P1 Resolver and VP-06 Printer.
critical=[
'P1/semantic-validator-v1/baseline/P1_1_Contract_Freeze/contract/source_lock.json',
'P1/semantic-validator-v1/baseline/P1_1_Contract_Freeze/contract/concept_keys.json',
'P1/semantic-validator-v1/baseline/P0_reference/grammar/concepts.json',
'P2/visual-printer-2d-lab/reference/p0-symbols-v9.4.json',
'P2/visual-printer-2d-lab/reference/p0-core-v9.4.json',
'P2/visual-printer-2d-lab/reference/p0-concepts-v9.4.json',
'P2/visual-printer-2d-lab/reference/p1-anchors.json',
'P2/visual-printer-2d-lab/reference/p1-form-color.json',
]
if any(f not in assets or f not in matched for f in critical):
    sys.exit('FAIL: critical frozen P1/P2 resource is not included in Wrangler Text rules')
print('PASS G5 offline packaging coverage: 40 frozen assets (P0=14, P1=20, P2=6); SHA-256 verified')
print('PASS G5 private Worker and module rules match the assembled runtime config')
print('NOT PROVEN: Cloudflare Pyodide read/validation/render until re-deployment and remote smoke')
