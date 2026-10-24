#!/usr/bin/env python3
"""Full VP-03 local conformance gate; Python standard library, optional jsonschema."""
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from vplenses import LensPrinter, PROFILES
from vplenses.printer import NS, source_digest

def run():
    # Old P0/P1 reference copies and all 85 earlier tests are still independently verified.
    r=subprocess.run([sys.executable,str(ROOT/'scripts/verify_vp02.py')],cwd=ROOT)
    if r.returncode:raise SystemExit(r.returncode)
    suite=unittest.defaultTestLoader.discover(str(ROOT/'lens_tests'),pattern='test_*.py')
    tests=unittest.TextTestRunner(verbosity=1).run(suite)
    if not tests.wasSuccessful():raise SystemExit(1)
    printer=LensPrinter();tally=0;source_names=set()
    for f in sorted((ROOT/'lens_bundles').glob('*.json')):
        bundle=json.loads(f.read_text('utf8'))
        plan=bundle['view_plan']
        source_names.add(plan['view'])
        assert source_digest(plan)==bundle['source_view_sha256'],f
        # Golden sources are not newly authored and were not altered after VP-02.
        baseline=[x for x in (ROOT/'view_fixtures').glob('*.json') if json.loads(x.read_text('utf8'))==plan]
        assert len(baseline)==1,(f,'not a byte-equivalent fixture model')
        for lens in PROFILES:
            name=lens.rsplit('.',1)[-1];stem=f.stem+'__'+name
            svg=printer.render(bundle,lens)
            stored=(ROOT/'lens_outputs'/(stem+'.svg')).read_bytes()
            assert svg==stored,stem
            tree=ET.fromstring(svg)
            assert tree.tag==f'{{{NS}}}svg' and tree.get('data-vp03-lens')==lens
            assert tree.get('data-vp03-source-sha256')==bundle['source_view_sha256']
            assert tree.find(f'{{{NS}}}metadata') is not None
            assert not any(el.tag.rsplit('}',1)[-1].lower() in ('script','foreignobject','image','use','animate') for el in tree.iter()),stem
            assert not any(key in ('href','xlink:href') or key.lower().startswith('on') for el in tree.iter() for key in el.attrib),stem
            report=printer.report(bundle,lens,svg)
            saved=json.loads((ROOT/'lens_outputs'/(stem+'.report.json')).read_text('utf8'))
            assert report==saved,stem
            assert report['svg_sha256']==hashlib.sha256(svg).hexdigest()
            assert report['source_view_sha256']==source_digest(plan)
            for k in ('semantic_conformance','epistemic_warrant','current_authority','canonical_admission'):
                assert report[k]=='NOT_EVALUATED',k
            tally+=1
    assert source_names=={'cube.flow','cube.diagramm','cube.tree'}
    assert tally==15

    # Integrity ledger excludes itself and manifest to avoid recursive SHA derivation.
    checksums=(ROOT/'VP03_SHA256SUMS.txt').read_text('utf8').splitlines()
    checked=set()
    for row in checksums:
        digest,relpath=row.split('  ',1)
        assert relpath not in checked and '..' not in Path(relpath).parts
        checked.add(relpath)
        assert hashlib.sha256((ROOT/relpath).read_bytes()).hexdigest()==digest,relpath
    actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name not in ('VP03_SHA256SUMS.txt','VP03_RELEASE_MANIFEST.json') and p.suffix!='.pyc'}
    assert actual==checked,('inventory mismatch',sorted(actual-checked),sorted(checked-actual))
    manifest=json.loads((ROOT/'VP03_RELEASE_MANIFEST.json').read_text('utf8'))
    assert manifest['profile']=='P2-VP-LENSES/0.3.0'
    assert manifest['resource_count']==len(checked)
    assert manifest['snapshot_count']==15
    assert manifest['fixture_count']==3
    assert manifest['checksum_ledger_sha256']==hashlib.sha256((ROOT/'VP03_SHA256SUMS.txt').read_bytes()).hexdigest()

    schema_status='NOT_EVALUATED (jsonschema unavailable)'
    try:
        import jsonschema
        for key,pat in [('LENS_BUNDLE.schema.json','lens_bundles/*.json'),('LENS_PRINT_REPORT.schema.json','lens_outputs/*.report.json')]:
            schema=json.loads((ROOT/key).read_text('utf8'))
            jsonschema.Draft202012Validator.check_schema(schema)
            validate=jsonschema.Draft202012Validator(schema)
            for file in sorted(ROOT.glob(pat)):
                validate.validate(json.loads(file.read_text('utf8')))
        schema_status='3/3 bundles + 15/15 reports PASS (Draft 2020-12)'
    except ImportError:pass
    print(f'PASS VP-03: previous 85 tests + {tests.testsRun} new tests; 3 source view fixtures × 5 lenses = {tally} SVGs/reports; {len(checked)} checksum files; {schema_status}')
    print('NOT EVALUATED: macOS/Safari/Claude/Grok visual fidelity; actual P1 semantic/authority/evidence verification; lens auto-classification; granularity VP-04; 3D')

if __name__=='__main__':run()
