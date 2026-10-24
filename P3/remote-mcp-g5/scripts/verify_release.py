#!/usr/bin/env python3
"""Verify source freeze checksums, package pins, G5 discovery MIME and optional npm lock."""
import argparse,hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--require-npm-lock',action='store_true');opt=p.parse_args()
manifest=HERE/'SHA256SUMS.txt'
if not manifest.is_file():raise SystemExit('FAIL no G5 source SHA256SUMS')
lines=manifest.read_text('utf-8').splitlines()
for line in lines:
    digest,rel=line.split('  ',1)
    full=HERE/rel
    if not full.is_file() or hashlib.sha256(full.read_bytes()).hexdigest()!=digest:
        raise SystemExit('FAIL G5 source hash: '+rel)
for rel in (HERE/'gateway').rglob('*'):
    if rel.is_file() and rel.name in ('package-lock.json','npm-shrinkwrap.json'):
        pass # npm lock is local post-freeze evidence, not part of immutable P3 overlay
pkg=json.loads((HERE/'gateway/package.json').read_text('utf-8'))
assert pkg['dependencies']=={'@modelcontextprotocol/server':'2.4.0','zod':'4.6.7'}
assert pkg['devDependencies']['wrangler']=='4.152.0'
config=json.loads((HERE/'python-core/wrangler.jsonc').read_text('utf-8'))
assert config['workers_dev'] is False and config['find_additional_modules'] is True
if not (HERE/'.g5-runtime/G5_SOURCE_MANIFEST.json').is_file():
    raise SystemExit('FAIL assemble runtime first: python3 P3/remote-mcp-g5/scripts/verify_g5.py')
registry=json.loads((HERE/'gateway/src/p0-registry.json').read_text('utf-8'))['resources']
lock=json.loads((HERE.parents[1]/'P3/adapters/mcp-local/p0_snapshot/lock.json').read_text('utf-8'))
expected={e['uri']:e['mime_type'] for e in lock['resources']}
expected['aiaeao://p0/resources/v1']='application/json'
assert {e['uri']:e['mime_type'] for e in registry}==expected
npm_lock=HERE/'gateway/package-lock.json'
if npm_lock.exists():
    lockdata=json.loads(npm_lock.read_text('utf-8'))
    base=lockdata['packages']['']
    assert base['dependencies']==pkg['dependencies'], 'package-lock direct dependencies mismatch'
    assert base['devDependencies']['wrangler']==pkg['devDependencies']['wrangler']
    for name,version in pkg['dependencies'].items():
        assert lockdata['packages']['node_modules/'+name]['version']==version
    print('PASS npm full transitive lock locally present; run npm ci and npm audit on target Mac')
elif opt.require_npm_lock:
    raise SystemExit('FAIL npm package-lock.json absent; run npm install --package-lock-only --ignore-scripts in gateway')
else:
    print('PENDING npm transitive lock (not generated offline; required for final Git freeze)')
print('PASS G5 source SHA-256:',len(lines),'files; registry MIME exact to pinned lock')
