#!/usr/bin/env python3
"""Reproducible VP04 gate. Historical VP03 frozen gate runs in its own untouched root."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT.parent/'visual-printer-2d-lab'
sys.path.insert(0,str(ROOT))
from vpgranularity import GranularityPrinter
from vpgranularity.printer import sha, NS

def check_subprocess(args,cwd=None):
    proc=subprocess.run(args,cwd=cwd,encoding='utf8',capture_output=True,timeout=70)
    if proc.returncode:raise RuntimeError(f'command failed {args}:\n{proc.stdout}\n{proc.stderr}')
    return proc

def run():
    print('G01: independent frozen VP03 baseline (original VP01/VP02/VP03 gates)')
    old=check_subprocess([sys.executable,str(BASE/'scripts'/'verify_vp03.py')],cwd=BASE)
    print(old.stdout.strip().splitlines()[-2]);print('G02: VP04 unit and adversarial tests')
    suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_*.py')
    result=unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful():raise SystemExit(1)
    print('G03: deterministic snapshots, XML safety, report and input source locks')
    pr=GranularityPrinter();files=sorted((ROOT/'fixtures').glob('*.json'))
    assert len(files)==20
    kinds=set();cases=0
    for f in files:
        req=json.loads(f.read_text('utf8'));kinds.add((req['projection']['view'],req['projection']['granularity']))
        assert req['source_bundle_sha256']==sha(req['source_bundle'])
        svg=pr.render(req);report=pr.report(req,svg)
        assert svg==(ROOT/'outputs'/(f.stem+'.svg')).read_bytes(),('SVG',f.stem)
        assert report==json.loads((ROOT/'outputs'/(f.stem+'.report.json')).read_text('utf8')),('report',f.stem)
        root=ET.fromstring(svg);assert root.tag==f'{{{NS}}}svg'
        assert root.get('data-vp04-granularity')==req['projection']['granularity']
        assert not any(el.tag.rsplit('}',1)[-1].lower() in ('script','foreignobject','image','use','animate','set') for el in root.iter())
        assert not any(key in ('href','xlink:href') or key.lower().startswith('on') for el in root.iter() for key in el.attrib)
        assert report['completeness']=='COMPLETE_INPUT_VIEW' or 'vp04-source-and-reduction-ledger' in svg.decode('utf8')
        assert report['semantic_conformance']=='NOT_EVALUATED' and report['canonical_admission']=='NOT_EVALUATED'
        cases+=1
    assert kinds=={(v,l) for v in ('cube.flow','cube.diagramm','cube.tree') for l in ('overview','standard','detail')}
    print('G04: independent JSON Schema Draft 2020-12 checks')
    schema_note='NOT_EVALUATED (optional jsonschema missing)'
    try:
        import jsonschema
        rq=json.loads((ROOT/'PROJECTION_REQUEST.schema.json').read_text('utf8'))
        rp=json.loads((ROOT/'PRINT_REPORT_VP04.schema.json').read_text('utf8'))
        jsonschema.Draft202012Validator.check_schema(rq)
        jsonschema.Draft202012Validator.check_schema(rp)
        qv=jsonschema.Draft202012Validator(rq);rv=jsonschema.Draft202012Validator(rp)
        for f in files:
            qv.validate(json.loads(f.read_text('utf8')))
            rv.validate(json.loads((ROOT/'outputs'/(f.stem+'.report.json')).read_text('utf8')))
        schema_note='20/20 requests + 20/20 reports PASS'
    except ImportError:pass
    print(schema_note)
    print('G05: subprocess CLI output and adversarial rejection')
    with tempfile.TemporaryDirectory(prefix='aiaeao_vp04_') as temp:
        out=Path(temp)/'test.svg';report=Path(temp)/'test.report.json'
        check_subprocess([sys.executable,'-m','vpgranularity','--input',str(files[0]),'--output',str(out),'--report',str(report)],cwd=ROOT)
        assert out.read_bytes()==(ROOT/'outputs'/(files[0].stem+'.svg')).read_bytes()
        assert json.loads(report.read_text('utf8'))==json.loads((ROOT/'outputs'/(files[0].stem+'.report.json')).read_text('utf8'))
        bad=json.loads(files[0].read_text('utf8'));bad['projection']['view']='planner.flow'
        badpath=Path(temp)/'bad.json';badpath.write_text(json.dumps(bad),'utf8')
        x=subprocess.run([sys.executable,'-m','vpgranularity','--input',str(badpath),'--output',str(Path(temp)/'invalid.svg')],cwd=ROOT,capture_output=True,encoding='utf8')
        assert x.returncode==2 and not (Path(temp)/'invalid.svg').exists()
    print('G06: immutable source lock')
    source_lock=json.loads((ROOT/'SOURCE_LOCK_VP04.json').read_text('utf8'))
    assert source_lock['source_release']=='AIAEAO_Visual_Printer_VP03_Lens_Profiles.zip'
    for relative,digest in source_lock['files_sha256'].items():
        assert hashlib.sha256((BASE/relative).read_bytes()).hexdigest()==digest,relative
    print('G07: checksum inventory and release manifest')
    ledger=(ROOT/'VP04_SHA256SUMS.txt').read_bytes();entries={}
    for line in ledger.decode('utf8').splitlines():
        digest,relative=line.split('  ',1)
        assert relative not in entries and '..' not in Path(relative).parts
        entries[relative]=digest
        assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==digest,relative
    actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc' and p.name not in ('VP04_SHA256SUMS.txt','VP04_RELEASE_MANIFEST.json')}
    assert set(entries)==actual,(sorted(actual-set(entries)),sorted(set(entries)-actual))
    manifest=json.loads((ROOT/'VP04_RELEASE_MANIFEST.json').read_text('utf8'))
    assert manifest['profile']=='P2-VP-GRANULARITY/0.4.0'
    assert manifest['file_count']==len(entries)
    assert manifest['golden_svg_count']==cases
    assert manifest['new_unit_tests']==result.testsRun
    assert manifest['checksum_ledger_sha256']==hashlib.sha256(ledger).hexdigest()
    print('PASS VP-04: baseline VP01+VP02+VP03=113; new=',result.testsRun,'; golden cases=',cases,
          '; checked files=',len(entries),'; schemas:',schema_note)
    print('NOT EVALUATED: independent macOS/Safari/Claude/Grok typography QA; empirical accuracy; actual P1 conformance; 3D; production deployment')

if __name__=='__main__':run()
