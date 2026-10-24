#!/usr/bin/env python3
"""Verify 2D lab without network; requires only Python stdlib."""
from pathlib import Path
import sys,hashlib,json,subprocess,unittest
from xml.etree import ElementTree as ET
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from vp2d import Printer

suite=unittest.defaultTestLoader.discover(str(root/'tests'))
result=unittest.TextTestRunner(verbosity=1).run(suite)
if not result.wasSuccessful():raise SystemExit(1)
manifest=json.loads((root/'SOURCE_LOCK.json').read_text('utf8'))
for name,entry in manifest['sources'].items():
 data=(root/'reference'/name).read_bytes()
 assert hashlib.sha256(data).hexdigest()==entry['sha256'],name
p=Printer(); files=[]
for x in sorted((root/'fixtures').glob('*.json')):
 data=json.loads(x.read_text('utf8')); expected=p.render(data)
 y=root/'outputs'/(x.stem+'.svg'); actual=y.read_bytes()
 assert actual==expected, f'non-reproducible snapshot: {y}'
 r=ET.fromstring(actual)
 assert r.tag.endswith('svg')
 assert b'<script' not in actual and b'<!DOCTYPE' not in actual
 files.append(y.name)
print(f'PASS 2D lab: {result.testsRun} tests; {len(manifest["sources"])} locked references; {len(files)} deterministic, valid SVGs')
print('NOT EVALUATED: macOS/Safari font compatibility, cross-agent semantics, human usability gate')
