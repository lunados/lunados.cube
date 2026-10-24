#!/usr/bin/env python3
"""VP-02 independent local regression/snapshot/reference gate; stdlib only."""
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from vpviews import ViewPrinter

# Preserve untouched baseline (including its 27/29 tests) as a separate gate.
base=subprocess.run([sys.executable,str(ROOT/'scripts/verify_lab.py')],cwd=ROOT)
if base.returncode:raise SystemExit(base.returncode)

suite=unittest.defaultTestLoader.discover(str(ROOT/'view_tests'),pattern='test_*.py')
r=unittest.TextTestRunner(verbosity=1).run(suite)
if not r.wasSuccessful():raise SystemExit(1)

pr=ViewPrinter()
files=sorted((ROOT/'view_fixtures').glob('*.json'))
assert len(files)==6
counts={}
for file in files:
    p=json.loads(file.read_text('utf8'))
    counts[p['view']]=counts.get(p['view'],0)+1
    svg=pr.render(p)
    assert svg==(ROOT/'view_outputs'/(file.stem+'.svg')).read_bytes(),file.stem
    rep=json.loads((ROOT/'view_outputs'/(file.stem+'.report.json')).read_text('utf8'))
    assert rep==pr.report(p,svg),file.stem
    assert ET.fromstring(svg).tag=='{http://www.w3.org/2000/svg}svg'
assert counts=={'cube.flow':2,'cube.diagramm':2,'cube.tree':2}

sums=(ROOT/'VP02_SHA256SUMS.txt').read_text('utf8').splitlines()
for line in sums:
    digest,name=line.split('  ',1)
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name

# Optional independent Draft 2020-12 jsonschema check when installed.
schema_results='NOT_EVALUATED (jsonschema not installed)'
try:
    import jsonschema
    j=json.loads((ROOT/'VIEW_PLAN.schema.json').read_text('utf8'))
    jsonschema.Draft202012Validator.check_schema(j)
    validator=jsonschema.Draft202012Validator(j)
    for file in files:
        validator.validate(json.loads(file.read_text('utf8')))
    report_schema=json.loads((ROOT/'PRINT_REPORT.schema.json').read_text('utf8'))
    jsonschema.Draft202012Validator.check_schema(report_schema)
    rep_validator=jsonschema.Draft202012Validator(report_schema)
    for file in files:
        rep_validator.validate(json.loads((ROOT/'view_outputs'/(file.stem+'.report.json')).read_text('utf8')))
    schema_results='6/6 plans + 6/6 reports PASS (jsonschema Draft 2020-12)'
except ImportError:pass
print(f'PASS VP-02: {r.testsRun} view-unit tests; 6/6 golden SVGs; 6/6 reports; {len(sums)} release SHA256 hashes; schema: {schema_results}')
print('NOT EVALUATED: browser-specific Unicode fallback, macOS/Safari QA, 3D, lenses, dynamic granularity, actual P1 semantic validation')
