#!/usr/bin/env python3
"""Complete local VP06 release gate. No web access, no external effects."""
from __future__ import annotations
import hashlib,json,subprocess,sys,unittest
from pathlib import Path

R=Path(__file__).resolve().parents[1]
P2=R.parent
ROOT=P2.parent
WEB=ROOT/'AIAEAO_Pure_Cube_P0_v9.4'/'validation'/'v1'/'visual'/'printer'/'v1'
WORKFLOW=ROOT/'.github'/'workflows'/'cube-vp06-conformance.yml'

sys.path.insert(0,str(R))
from vpprint import render_job,load_json,capabilities

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dumps(obj):return (json.dumps(obj,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode('utf-8')
def files_of(d):return sorted(p for p in d.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc' and p.name!='.DS_Store')
def snapshot(d):
    files=files_of(d)
    ledger=''.join(f'{digest(p)}  {p.relative_to(d).as_posix()}\n' for p in files)
    return {'file_count':len(files),'sha256_inventory':hashlib.sha256(ledger.encode()).hexdigest()}

def verify():
    print('G01: VP-01…VP-05 regression and 90-case independent oracle',flush=True)
    baseline=P2/'visual-printer-conformance-v1'
    process=subprocess.run([sys.executable,str(baseline/'scripts'/'verify_vp05.py')],cwd=baseline,
                           capture_output=True,text=True,timeout=200)
    if process.returncode!=0:raise AssertionError('Baseline regression failed\n'+process.stdout[-4000:]+'\n'+process.stderr[-4000:])
    assert 'PASS VP-05:' in process.stdout,process.stdout[-700:]
    print(process.stdout.strip().splitlines()[-2],flush=True)
    print('G02: 46 focused VP-06 interface and safety tests',flush=True)
    suite=unittest.defaultTestLoader.discover(str(R/'tests'),pattern='test_*.py')
    result=unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful():raise AssertionError('VP06 suite failed')
    assert result.testsRun==46,result.testsRun
    print('G03: Four byte-identical, golden local print jobs',flush=True)
    for key in ('flow_provenance_standard','diagramm_semantics_standard','tree_governance_overview','tree_semantics_detail'):
        req=load_json(R/'examples'/(key+'.job.json'))
        report,svg=render_job(req)
        assert svg==(R/'examples'/(key+'.svg')).read_bytes(),key
        assert dumps(report)==(R/'examples'/(key+'.report.json')).read_bytes(),key
    print('G04: JSON Schemas against 4 reports and failure diagnostics',flush=True)
    schema_status='SKIPPED (jsonschema missing; independent schema gate not evaluated)'
    try:
        import jsonschema
    except ImportError:pass
    else:
        paths={'report':R/'spec'/'VP06_PRINT_RESULT.schema.json',
               'diagnostic':R/'spec'/'VP06_DIAGNOSTIC.schema.json',
               'request':WEB/'VP04_PROJECTION_REQUEST.schema.json',
               'bundle':WEB/'VP03_LENS_BUNDLE.schema.json'}
        validators={}
        for name,path in paths.items():
            schema=load_json(path)
            jsonschema.Draft202012Validator.check_schema(schema)
            validators[name]=jsonschema.Draft202012Validator(schema)
        for p in sorted((R/'examples').glob('*.job.json')):
            validators['request'].validate(load_json(p))
            validators['bundle'].validate(load_json(p.with_name(p.name.replace('.job.json','.vp03.bundle.json'))))
        for p in sorted((R/'examples').glob('*.report.json')):validators['report'].validate(load_json(p))
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            invalid=Path(tmp)/'malformed.json';invalid.write_text('{x')
            cli=subprocess.run([sys.executable,'-m','vpprint','check','--input',str(invalid)],cwd=R,text=True,capture_output=True)
            assert cli.returncode==2
            validators['diagnostic'].validate(json.loads(cli.stderr))
        schema_status='PASS (4 print results, 4 jobs, 4 source bundles, 1 diagnostic, 4 schema definitions)'
    print(schema_status,flush=True)
    print('G05: Public metadata/manifest is static, truthful, and add-only',flush=True)
    public=load_json(WEB/'manifest.json')
    assert public['callable_api'] is False and public['http_post_supported'] is False
    assert public['static_guide_only'] is True and public['no_svg_assets_in_public_overlay'] is True
    assert public['status']=='local_release_candidate_unpublished'
    assert load_json(WEB/'capabilities.json')==capabilities()
    assert {p.name for p in WEB.iterdir()}=={'manifest.json','capabilities.json','AGENT_QUICKSTART.md',
        'VP06_PRINT_RESULT.schema.json','VP06_DIAGNOSTIC.schema.json','VP04_PROJECTION_REQUEST.schema.json','VP03_LENS_BUNDLE.schema.json'}
    for item in public['assets'].values():
        assert item.startswith('https://cube.lunados.net/validation/v1/visual/printer/v1/')
        assert (WEB/item.rsplit('/',1)[-1]).is_file(),item
    assert WORKFLOW.exists()
    assert (R/'quick_preview.html').is_file()
    print('G06: unchanged baseline source inventory hashes',flush=True)
    lock=load_json(R/'VP06_SOURCE_LOCK.json')
    for name,expected in lock['baseline_snapshots'].items():
        assert snapshot(P2/name)==expected,name
    print('G07: release checksum ledger and complete file inventory',flush=True)
    ledger=(R/'VP06_SHA256SUMS.txt').read_bytes();records={}
    for row in ledger.decode('utf-8').splitlines():
        h,rel=row.split('  ',1)
        assert rel not in records and '..' not in Path(rel).parts,rel
        records[rel]=h;assert digest(R/rel)==h,rel
    complete={p.relative_to(R).as_posix() for p in files_of(R) if p.name not in ('VP06_SHA256SUMS.txt','VP06_RELEASE_MANIFEST.json')}
    assert set(records)==complete,(len(records),len(complete),sorted(complete-set(records))[:7])
    m=load_json(R/'VP06_RELEASE_MANIFEST.json')
    assert m['file_count']==len(records)
    assert m['sha256_ledger_sha256']==hashlib.sha256(ledger).hexdigest()
    assert m['baseline_tests']==191 and m['vp06_tests']==result.testsRun and m['matrix_cases']==90
    assert m['golden_svgs']==4 and m['publication_status']=='local_release_candidate_unpublished'
    print('PASS VP-06:',191,'frozen unit tests +',result.testsRun,'new tests;',90,
          'matrix cases; 4 golden SVGs;',len(records),'release-directory files',flush=True)
    print('NOT EVALUATED: cross-agent live usage, macOS glyph parity, P1 semantic truth, deployed Cloudflare URLs, auto-multisvg or 3D',flush=True)
    return {'status':'PASS','frozen_unit_tests':191,'new_vp06_unit_tests':result.testsRun,'matrix_cases':90,
            'matrix_positive':54,'matrix_expected_rejections':36,'golden_svgs':4,'schema_status':schema_status,
            'web_publication':'NOT_EVALUATED','external_agents':'NOT_EVALUATED','glyph_parity':'NOT_EVALUATED'}
if __name__=='__main__':verify()
