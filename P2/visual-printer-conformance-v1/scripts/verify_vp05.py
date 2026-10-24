#!/usr/bin/env python3
"""Offline P2 VP05 release gate; includes independent VP04 snapshot regression."""
import hashlib,json,subprocess,sys,tempfile,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R.parent
sys.path.insert(0,str(R))
from vpconformance import ConformanceAuditor,ConformanceError

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def run():
    print('G01: Frozen VP01–VP04 baseline regression')
    x=subprocess.run([sys.executable,str(P/'visual-printer-granularity-v1'/'scripts'/'verify_vp04.py')],cwd=P/'visual-printer-granularity-v1',capture_output=True,text=True,timeout=110)
    assert x.returncode==0,(x.stdout[-2500:],x.stderr[-2500:])
    print(x.stdout.splitlines()[-2]);print('G02: VP05 42 independent unit tests')
    suite=unittest.defaultTestLoader.discover(str(R/'tests'),pattern='test_*.py')
    result=unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful():raise SystemExit(1)
    oracle=json.loads((R/'fixtures'/'INDEPENDENT_ORACLE.json').read_text('utf8'))
    print('G03: fixture matrix and expected outcomes')
    cases=sorted((R/'matrix').glob('*.json'))
    requests=sorted(p for p in cases if not p.name.endswith(('.vp04.report.json','.vp05.report.json')))
    assert len(requests)==90
    assert len(list((R/'matrix').glob('*.svg')))==54
    assert len(list((R/'matrix').glob('*.vp04.report.json')))==54
    assert len(list((R/'matrix').glob('*.vp05.report.json')))==90
    successes=failures=0
    for src,spec in oracle['sources'].items():
        for lens in oracle['lenses']:
            for level in ('overview','standard','detail'):
                stem=f'{src}__{lens}__{level}'
                q=json.loads((R/'matrix'/(stem+'.json')).read_text('utf8'))
                report=json.loads((R/'matrix'/(stem+'.vp05.report.json')).read_text('utf8'))
                has_lens=('cube.lens.'+lens) in {b['lens'] for b in q['source_bundle']['facet_bindings']}
                if not has_lens:
                    assert report['status']=='EXPECTED_REJECTION'
                    try:ConformanceAuditor().audit(q)
                    except ConformanceError as e:assert 'selected lens has no explicit facet bindings' in str(e)
                    else:raise AssertionError('undisclosed lens accepted '+stem)
                    failures+=1;continue
                exp={'source_items':spec['source_items'],'shown_items':spec['levels'][level][0],
                    'shown_edges':spec['levels'][level][1],'completeness':spec['levels'][level][2]}
                a,svg,r=ConformanceAuditor().audit(q,exp,include_svg=True)
                assert a==report and svg==(R/'matrix'/(stem+'.svg')).read_bytes()
                assert r==json.loads((R/'matrix'/(stem+'.vp04.report.json')).read_text('utf8'))
                successes+=1
    assert successes==54 and failures==36
    print('G04: JSON Schema validation (optional independent oracle)')
    schema_status='NOT_EVALUATED (optional jsonschema unavailable)'
    try:
        import jsonschema
        sv={n:json.loads((R/n).read_text('utf8')) for n in ('VP05_AUDIT_REPORT.schema.json','VP05_REJECTION.schema.json')}
        vs={n:jsonschema.Draft202012Validator(s) for n,s in sv.items()}
        for schema in sv.values():jsonschema.Draft202012Validator.check_schema(schema)
        vp04r=jsonschema.Draft202012Validator(json.loads((P/'visual-printer-granularity-v1'/'PRINT_REPORT_VP04.schema.json').read_text('utf8')))
        vp04q=jsonschema.Draft202012Validator(json.loads((P/'visual-printer-granularity-v1'/'PROJECTION_REQUEST.schema.json').read_text('utf8')))
        for p in requests:
            s=p.stem;vp04q.validate(json.loads(p.read_text('utf8')))
            a=json.loads((R/'matrix'/(s+'.vp05.report.json')).read_text('utf8'))
            if a['status']=='PASS':
                vs['VP05_AUDIT_REPORT.schema.json'].validate(a)
                vp04r.validate(json.loads((R/'matrix'/(s+'.vp04.report.json')).read_text('utf8')))
            else:vs['VP05_REJECTION.schema.json'].validate(a)
        schema_status='90 requests + 54 VP04 reports + 54 VP05 audits + 36 rejection records PASS'
    except ImportError:pass
    print(schema_status)
    print('G05: CLI smoke (success and rejection)')
    with tempfile.TemporaryDirectory() as d:
        output=Path(d)/'audit.json';svg=Path(d)/'file.svg'
        good=R/'matrix'/'tree_modules__governance__overview.json'
        p=subprocess.run([sys.executable,'-m','vpconformance','--input',str(good),'--output',str(output),'--svg',str(svg)],cwd=R,text=True,capture_output=True,timeout=30)
        assert p.returncode==0,p.stderr
        observed=json.loads(output.read_text('utf8'))
        gold=json.loads((R/'matrix'/'tree_modules__governance__overview.vp05.report.json').read_text('utf8'))
        assert observed['status']=='PASS' and observed['svg_sha256']==gold['svg_sha256']
        assert observed['decision']==gold['decision'] and observed['split_feasibility']==gold['split_feasibility']
        assert set(gold['invariants_passed'])-set(observed['invariants_passed'])=={'INDEPENDENT_ORACLE_SOURCE_ITEMS','INDEPENDENT_ORACLE_SHOWN_ITEMS','INDEPENDENT_ORACLE_SHOWN_EDGES','INDEPENDENT_ORACLE_COMPLETENESS'}
        assert svg.read_bytes()==(R/'matrix'/'tree_modules__governance__overview.svg').read_bytes()
        output.unlink();svg.unlink()
        bad=R/'matrix'/'flow_research__governance__overview.json'
        p=subprocess.run([sys.executable,'-m','vpconformance','--input',str(bad),'--output',str(output),'--svg',str(svg)],cwd=R,text=True,capture_output=True,timeout=30)
        assert p.returncode==2 and not output.exists() and not svg.exists()
    print('G06: source freeze lock')
    lock=json.loads((R/'SOURCE_LOCK_VP05.json').read_text('utf8'))
    for name,d in lock['snapshots'].items():
        base=P/name
        files=sorted(p for p in base.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc')
        inventory=''.join(f'{sha(p)}  {p.relative_to(base).as_posix()}\n' for p in files)
        assert len(files)==d['file_count']
        assert hashlib.sha256(inventory.encode('utf8')).hexdigest()==d['file_inventory_sha256'],name
    print('G07: checksums and manifest')
    ledger=(R/'VP05_SHA256SUMS.txt').read_bytes();seen={}
    for line in ledger.decode('utf8').splitlines():
        checksum,path=line.split('  ',1)
        assert path not in seen and '..' not in Path(path).parts
        seen[path]=checksum;assert sha(R/path)==checksum,path
    actual={p.relative_to(R).as_posix() for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc' and p.name not in ('VP05_SHA256SUMS.txt','VP05_RELEASE_MANIFEST.json')}
    assert set(seen)==actual,(len(set(seen)),len(actual),sorted(actual-set(seen))[:5],sorted(set(seen)-actual)[:5])
    m=json.loads((R/'VP05_RELEASE_MANIFEST.json').read_text('utf8'))
    assert m['file_count']==len(seen)
    assert m['checksum_ledger_sha256']==hashlib.sha256(ledger).hexdigest()
    assert m['new_tests']==result.testsRun and m['matrix_total']==90
    assert m['positive_cases']==54 and m['expected_rejections']==36
    assert (R/'matrix_preview.html').is_file() and (R/'previews'/'contact_sheet.png').is_file()
    print('PASS VP-05: 149 frozen baseline +',result.testsRun,'new tests;',successes,'golden projections;',failures,'expected lens rejections;',len(seen),'VP05 files')
    print('NOT EVALUATED: macOS/Safari/other agent typography; P1 semantic correctness; production publishing; automatic multi-SVG export; 3D')
if __name__=='__main__':run()
