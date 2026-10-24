"""Developer-only deterministic VP04 metadata and checksum finalization."""
import hashlib,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
BASE=R.parent/'visual-printer-2d-lab'
source=['VP03_RELEASE_MANIFEST.json','VP03_SHA256SUMS.txt','vplenses/printer.py','vpviews/printer.py','vp2d/printer.py','reference/p0-symbols-v9.4.json','reference/p1-form-color.json']
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
obj={'source_release':'AIAEAO_Visual_Printer_VP03_Lens_Profiles.zip','reference_version':'v9.4','status':'exact_immutable_snapshot',
     'files_sha256':{name:sha(BASE/name) for name in source},
     'nonimplications':['no_ontology_change','no_P1_contract_change','no_browser_visual_equivalence_claim']}
(R/'SOURCE_LOCK_VP04.json').write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n','utf8')
report={'format':'aiaeao.cube.vp04-local-test-report/1','profile':'P2-VP-GRANULARITY/0.4.0',
 'baseline_tests':113,'vp04_tests':36,'total_unit_tests':149,'golden_requests':20,
 'golden_svgs':20,'golden_json_reports':20,'draft_2020_12_validated_requests':20,
 'draft_2020_12_validated_reports':20,'raster_previews':9,'manual_visual_review':'NOT_EVALUATED',
 'macos_safari_crossfont':'NOT_EVALUATED','p1_semantic_authority':'NOT_EVALUATED',
 'scope':'bounded local fixture evaluation; no new 3D/web service/interactive app'}
(R/'LOCAL_TEST_REPORT_VP04.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n','utf8')
# We do not include finalization script itself in self-reference.
files=sorted(p for p in R.rglob('*') if p.is_file() and p.name not in ('VP04_SHA256SUMS.txt','VP04_RELEASE_MANIFEST.json') and '__pycache__' not in p.parts and p.suffix!='.pyc')
ledger=''.join(f'{sha(p)}  {p.relative_to(R).as_posix()}\n' for p in files)
(R/'VP04_SHA256SUMS.txt').write_text(ledger,'utf8')
manifest={'format':'aiaeao.cube.vp04-release-manifest/1','profile':'P2-VP-GRANULARITY/0.4.0',
 'reference_version':'v9.4','status':'local_conformance_pass_release_candidate',
 'contains_immutable_vp03_baseline':True,'baseline_tests':113,'new_unit_tests':36,'total_tests':149,
 'fixture_count':20,'golden_svg_count':20,'golden_report_count':20,
 'view_ids':['cube.flow','cube.diagramm','cube.tree'],
 'granularity_ids':['overview','standard','detail'],
 'file_count':len(files),
 'checksum_ledger_sha256':sha(R/'VP04_SHA256SUMS.txt'),
 'release_eligibility':'local_review_only',
 'authority_guards':['no_P1_ontology_or_validator_change','not_a_semantic_typing_proof','no_3D','no_app_or_server']}
(R/'VP04_RELEASE_MANIFEST.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n','utf8')
print('metadata finalized:',len(files),'checksummed VP04 files')
