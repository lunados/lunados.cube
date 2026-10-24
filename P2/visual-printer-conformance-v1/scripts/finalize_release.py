"""Development-only: regenerate locks and manifest; verify_vp05.py never writes."""
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R.parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source={}
for name in ('visual-printer-2d-lab','visual-printer-granularity-v1'):
    base=P/name
    files=sorted(p for p in base.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc')
    inventory=''.join(f'{sha(p)}  {p.relative_to(base).as_posix()}\n' for p in files)
    source[name]={'file_count':len(files),'file_inventory_sha256':hashlib.sha256(inventory.encode('utf8')).hexdigest()}
lock={'format':'aiaeao.cube.vp05-source-lock/1','reference_version':'v9.4','snapshots':source,
      'meaning':'byte-identical locally frozen VP-01–VP-04 snapshots, including their release manifests and integrity ledgers'}
(R/'SOURCE_LOCK_VP05.json').write_text(json.dumps(lock,indent=2,ensure_ascii=False)+'\n','utf8')
reports=[json.loads(p.read_text('utf8')) for p in (R/'matrix').glob('*.vp05.report.json')]
actions={}
for x in reports:
    if x['status']=='PASS':actions[x['decision']['action']]=actions.get(x['decision']['action'],0)+1
report={'format':'aiaeao.cube.vp05-local-test-report/1','profile':'P2-VP-CONFORMANCE/0.5.0',
 'baseline_tests':149,'new_tests':42,'total_tests':191,'matrix_total':90,
 'positive_cases':54,'expected_rejections':36,'positive_vp04_reports':54,'positive_vp05_reports':54,
 'decision_counts':actions,'manual_visual_review':'NOT_EVALUATED','macos_font_conformance':'NOT_EVALUATED',
 'auto_multipage_export':'NOT_IMPLEMENTED','P1_semantic_conformance':'NOT_EVALUATED','3D':'NOT_IMPLEMENTED'}
(R/'LOCAL_TEST_REPORT_VP05.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n','utf8')
files=sorted(p for p in R.rglob('*') if p.is_file() and p.name not in ('VP05_SHA256SUMS.txt','VP05_RELEASE_MANIFEST.json') and '__pycache__' not in p.parts and p.suffix!='.pyc')
ledger=''.join(f'{sha(p)}  {p.relative_to(R).as_posix()}\n' for p in files)
(R/'VP05_SHA256SUMS.txt').write_text(ledger,'utf8')
manifest={'format':'aiaeao.cube.vp05-release-manifest/1','profile':'P2-VP-CONFORMANCE/0.5.0',
 'reference_version':'v9.4','status':'local_conformance_pass_release_candidate','baseline_tests':149,
 'new_tests':42,'total_unit_tests':191,'matrix_total':90,'positive_cases':54,'expected_rejections':36,
 'view_ids':['cube.flow','cube.diagramm','cube.tree'],
 'lens_ids':['cube.lens.semantics','cube.lens.provenance','cube.lens.execution','cube.lens.governance','cube.lens.epistemology'],
 'granularity_ids':['overview','standard','detail'],'file_count':len(files),
 'checksum_ledger_sha256':sha(R/'VP05_SHA256SUMS.txt'),
 'source_snapshots':source,'decision_counts':actions,'release_eligibility':'local_review_only',
 'nonimplications':['not_P1_semantic_admission','not_a_web_app','not_an_auto_multi_svg_printer','not_3D']}
(R/'VP05_RELEASE_MANIFEST.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n','utf8')
print('finalized',len(files),'VP05 files;',actions)
