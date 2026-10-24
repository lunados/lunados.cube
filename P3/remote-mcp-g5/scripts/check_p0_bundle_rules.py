#!/usr/bin/env python3
"""Offline check that P0 snapshot resources are covered by explicit Wrangler Text rules.

Does not prove Cloudflare runtime file availability; the real remote MCP test does.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parents[3]
CONFIG = json.loads((HERE.parents[1]/'python-core'/'wrangler.jsonc').read_text('utf-8'))
SNAP = REPO / 'P3/adapters/mcp-local/p0_snapshot'

if not CONFIG.get('find_additional_modules'):
    sys.exit('FAIL: find_additional_modules disabled')
text_patterns = [g for rule in CONFIG.get('rules', []) if rule.get('type') == 'Text'
                 for g in rule.get('globs', [])]
if not SNAP.is_dir():
    sys.exit('FAIL: G4 P0 snapshot unavailable at '+str(SNAP))
all_files = {p.relative_to(REPO).as_posix() for p in SNAP.rglob('*') if p.is_file()}
matched = {p.relative_to(REPO).as_posix() for glob in text_patterns
           for p in REPO.glob(glob) if p.is_file()}
missing = sorted(all_files - matched)
if missing:
    sys.exit('FAIL: P0 files not included by Text rules: '+', '.join(missing))
if len(all_files)!=14:
    sys.exit(f'FAIL: expected 14 frozen P0 snapshot files, found {len(all_files)}')
if CONFIG.get('workers_dev') is not False or CONFIG.get('preview_urls') is not False:
    sys.exit('FAIL: private Core Worker must not have public targets')
# Independently verify actual lock bytes (not mere existence).
import hashlib
from importlib.util import module_from_spec, spec_from_file_location
modfile=REPO/'P3/adapters/mcp-local/aiaeao_mcp_local/p0_resources.py'
spec=spec_from_file_location('g5_p0_resource_check',modfile)
mod=module_from_spec(spec)
spec.loader.exec_module(mod)
actual=hashlib.sha256((SNAP/'lock.json').read_bytes()).hexdigest()
if actual!=mod.PINNED_LOCK_SHA256:
    sys.exit('FAIL: pinned lock SHA-256 mismatch')
print(f'PASS G5 P0 bundle rules: {len(all_files)} snapshot files explicitly matched, lock SHA-256 {actual}')
print('PENDING: verify actual Cloudflare bundling and remote P0 access after deployment')
