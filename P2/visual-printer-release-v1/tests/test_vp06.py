"""Independent VP-06 acceptance: focused facade, fail-closed diagnostics, release safety."""
from __future__ import annotations
import copy,hashlib,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
from vpprint import make_job,render_job,capabilities,PrintError,load_json
from vpprint.core import encode,persist_job,persist_print,MAX_INPUT_BYTES
BASE=HERE/'examples'
P2=HERE.parent

def gold(name):return load_json(BASE/(name+'.job.json'))
def bundle(name):return load_json(BASE/(name+'.vp03.bundle.json'))

def cli(*args):
    return subprocess.run([sys.executable,'-m','vpprint',*map(str,args)],cwd=HERE,text=True,capture_output=True,timeout=30)

class Conformance(unittest.TestCase):
    def test_01_capabilities_identifiers(self):
        c=capabilities();self.assertEqual(c['views'],['cube.flow','cube.diagramm','cube.tree']);self.assertEqual(len(c['lenses']),5);self.assertEqual(len(c['granularities']),3)
    def test_02_capabilities_no_online_api(self):self.assertFalse(capabilities()['network_api'])
    def test_03_capabilities_no_3d(self):self.assertFalse(capabilities()['3d'])
    def test_04_capabilities_no_multisvg_claim(self):self.assertFalse(capabilities()['auto_multisvg'])
    def test_05_capabilities_cli(self):
        p=cli('capabilities');self.assertEqual(p.returncode,0);self.assertEqual(json.loads(p.stdout),capabilities())
    def test_06_prepare_flow_matches_frozen_job(self):
        q=make_job(bundle('flow_provenance_standard'),'cube.lens.provenance','standard');self.assertEqual(q,gold('flow_provenance_standard'))
    def test_07_prepare_diagramm_matches_frozen_job(self):
        q=make_job(bundle('diagramm_semantics_standard'),'cube.lens.semantics','standard');self.assertEqual(q,gold('diagramm_semantics_standard'))
    def test_08_prepare_tree_matches_frozen_job(self):
        q=make_job(bundle('tree_governance_overview'),'cube.lens.governance','overview');self.assertEqual(q,gold('tree_governance_overview'))
    def test_09_prepare_detail_matches_frozen_job(self):
        q=make_job(bundle('tree_semantics_detail'),'cube.lens.semantics','detail');self.assertEqual(q,gold('tree_semantics_detail'))
    def test_10_prepare_unknown_view(self):
        b=bundle('flow_provenance_standard');b['view_plan']['view']='flow'
        with self.assertRaisesRegex(PrintError,'unknown cube view'):make_job(b,'cube.lens.provenance','standard')
    def test_11_prepare_unknown_lens(self):
        with self.assertRaisesRegex(PrintError,'unsupported lens'):make_job(bundle('flow_provenance_standard'),'governance','standard')
    def test_12_prepare_unknown_granularity(self):
        with self.assertRaises(PrintError):make_job(bundle('flow_provenance_standard'),'cube.lens.provenance','ultra')
    def test_13_prepare_unknown_overflow(self):
        with self.assertRaises(PrintError):make_job(bundle('flow_provenance_standard'),'cube.lens.provenance','standard',overflow='truncate')
    def test_14_prepare_exceeded_budget(self):
        with self.assertRaises(PrintError):make_job(bundle('flow_provenance_standard'),'cube.lens.provenance','overview',max_items=5)
    def test_15_prepare_focus_on_missing_id(self):
        with self.assertRaises(PrintError):make_job(bundle('flow_provenance_standard'),'cube.lens.provenance','standard',focus={'kind':'node','id':'undefined'})
    def test_16_prepare_reject_overflow(self):
        with self.assertRaises(PrintError):make_job(bundle('tree_governance_overview'),'cube.lens.governance','overview',overflow='reject')
    def test_17_render_hash_flow(self):
        r,s=render_job(gold('flow_provenance_standard'));self.assertEqual(s,(BASE/'flow_provenance_standard.svg').read_bytes());self.assertEqual(hashlib.sha256(s).hexdigest(),r['svg_sha256'])
    def test_18_render_hash_chart(self):
        r,s=render_job(gold('diagramm_semantics_standard'));self.assertEqual(s,(BASE/'diagramm_semantics_standard.svg').read_bytes())
    def test_19_render_hash_tree(self):
        r,s=render_job(gold('tree_governance_overview'));self.assertEqual(s,(BASE/'tree_governance_overview.svg').read_bytes())
    def test_20_render_hash_detail(self):
        r,s=render_job(gold('tree_semantics_detail'));self.assertEqual(s,(BASE/'tree_semantics_detail.svg').read_bytes())
    def test_21_report_golden_exact(self):
        for name in ('flow_provenance_standard','diagramm_semantics_standard','tree_governance_overview','tree_semantics_detail'):
            with self.subTest(name=name):self.assertEqual(render_job(gold(name))[0],load_json(BASE/(name+'.report.json')))
    def test_22_report_unverified_guard(self):
        r,_=render_job(gold('tree_semantics_detail'))
        for x in ('epistemic_warrant','canonical_admission','current_authority'):self.assertEqual(r[x],'NOT_EVALUATED')
    def test_23_loss_ledger_exhaustive(self):
        r,_=render_job(gold('tree_governance_overview'));self.assertEqual(r['loss_ledger']['omitted_item_ids'],['connector','toolbox']);self.assertEqual(r['loss_ledger']['omitted_source_edge_ids'],['e3','e4'])
    def test_24_split_proposal_not_materialized(self):
        r,_=render_job(gold('tree_governance_overview'));self.assertFalse(r['split_feasibility']['panels_materialized'])
    def test_25_source_tampering_fails(self):
        q=gold('flow_provenance_standard');q['source_bundle']['view_plan']['title']='tampered'
        with self.assertRaises(PrintError) as e:render_job(q)
        self.assertEqual(e.exception.code,'VP06_SOURCE_DIGEST_MISMATCH')
    def test_26_no_lens_inference(self):
        q=gold('flow_provenance_standard');q['source_bundle']['facet_bindings']=[b for b in q['source_bundle']['facet_bindings'] if b['lens']!='cube.lens.provenance']
        from vpconformance.conformance import json_sha
        from vpgranularity.printer import sha
        q['source_bundle_sha256']=sha(q['source_bundle'])
        with self.assertRaises(PrintError) as e:render_job(q)
        self.assertEqual(e.exception.code,'VP06_LENS_NOT_DECLARED')
    def test_27_unknown_planner_view(self):
        q=gold('flow_provenance_standard');q['projection']['view']='flow'
        with self.assertRaises(PrintError):render_job(q)
    def test_28_bad_json_duplicate_keys(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.json';p.write_text('{"a":1,"a":2}')
            with self.assertRaises(PrintError) as e:load_json(p)
            self.assertEqual(e.exception.code,'VP06_DUPLICATE_KEY')
    def test_29_bad_json_nonfinite(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.json';p.write_text('{"v":NaN}')
            with self.assertRaises(PrintError) as e:load_json(p)
            self.assertEqual(e.exception.code,'VP06_INVALID_JSON')
    def test_30_bad_json_utf8(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.json';p.write_bytes(b'\xff')
            with self.assertRaises(PrintError):load_json(p)
    def test_31_input_size_cap(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'large.json';p.write_bytes(b' '* (MAX_INPUT_BYTES+1))
            with self.assertRaises(PrintError) as e:load_json(p)
            self.assertEqual(e.exception.code,'VP06_INPUT_TOO_LARGE')
    def test_32_output_dir_atomic_presence(self):
        r,s=render_job(gold('flow_provenance_standard'))
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'printed';persist_print(r,s,p)
            self.assertEqual((p/'render.svg').read_bytes(),s)
            self.assertEqual(load_json(p/'report.json'),r)
            self.assertEqual(sorted(x.name for x in p.iterdir()),['render.svg','report.json'])
    def test_33_output_existing_refused(self):
        r,s=render_job(gold('flow_provenance_standard'))
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'existing';p.mkdir()
            with self.assertRaises(PrintError) as e:persist_print(r,s,p)
            self.assertEqual(e.exception.code,'VP06_OUTPUT_EXISTS');self.assertEqual(list(p.iterdir()),[])
    def test_34_job_existing_refused(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'job.json';persist_job(gold('flow_provenance_standard'),p)
            with self.assertRaises(PrintError):persist_job(gold('flow_provenance_standard'),p)
    def test_35_cli_check_is_read_only(self):
        p=cli('check','--input',BASE/'flow_provenance_standard.job.json')
        self.assertEqual(p.returncode,0,p.stderr);self.assertEqual(json.loads(p.stdout)['status'],'PASS')
    def test_36_cli_print_emits_two_files(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'out';p=cli('print','--input',BASE/'flow_provenance_standard.job.json','--out',out)
            self.assertEqual(p.returncode,0,p.stderr);self.assertTrue((out/'render.svg').exists());self.assertEqual(json.loads(p.stdout)['status'],'PASS')
    def test_37_cli_prepare_then_print(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'job.json';out=Path(d)/'out'
            p=cli('prepare','--bundle',BASE/'tree_governance_overview.vp03.bundle.json','--lens','cube.lens.governance','--granularity','overview','--out',f)
            self.assertEqual(p.returncode,0,p.stderr)
            p=cli('print','--input',f,'--out',out);self.assertEqual(p.returncode,0,p.stderr)
            self.assertEqual((out/'render.svg').read_bytes(),(BASE/'tree_governance_overview.svg').read_bytes())
    def test_38_cli_bad_lens_no_dir_created(self):
        with tempfile.TemporaryDirectory() as d:
            q=gold('flow_provenance_standard');q['projection']['lens']='cube.lens.invalid'
            f=Path(d)/'bad.json';f.write_bytes(encode(q));out=Path(d)/'out'
            p=cli('print','--input',f,'--out',out)
            self.assertEqual(p.returncode,2);self.assertFalse(out.exists());self.assertTrue(json.loads(p.stderr)['code'].startswith('VP06_'))
    def test_39_cli_invalid_json_diagnostic(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.json';p.write_text('{oops')
            q=cli('check','--input',p)
            self.assertEqual(q.returncode,2);self.assertEqual(json.loads(q.stderr)['code'],'VP06_INVALID_JSON')
    def test_40_cli_no_hidden_net_service(self):self.assertEqual(capabilities()['transport'],'local_cli_only')
    def test_41_sha_lock_from_prepare(self):
        from vpgranularity.printer import sha
        b=bundle('flow_provenance_standard');q=make_job(b,'cube.lens.provenance','standard')
        self.assertEqual(q['source_bundle_sha256'],sha(b))
    def test_42_cli_unknown_focus_diagnostic(self):
        p=cli('prepare','--bundle',BASE/'flow_provenance_standard.vp03.bundle.json','--lens','cube.lens.provenance','--granularity','standard','--focus','bogus','--out','/tmp/does-not-matter-vp06')
        self.assertEqual(p.returncode,2);self.assertEqual(json.loads(p.stderr)['code'],'VP06_FOCUS_INVALID')
    def test_43_print_output_does_not_contain_script(self):
        r,svg=render_job(gold('flow_provenance_standard'));self.assertNotIn(b'<script',svg.lower())
    def test_44_prepare_no_source_mutation(self):
        b=bundle('flow_provenance_standard');before=copy.deepcopy(b);make_job(b,'cube.lens.provenance','standard');self.assertEqual(b,before)
    def test_45_report_identity(self):
        r,svg=render_job(gold('flow_provenance_standard'))
        self.assertEqual(r['conformance']['svg_sha256'],r['svg_sha256'])
        self.assertEqual(r['conformance']['source_bundle_sha256'],r['source_bundle_sha256'])
    def test_46_utf8_reproducible(self):
        q=gold('flow_provenance_standard');r1,s1=render_job(q);r2,s2=render_job(q)
        self.assertEqual(encode(r1),encode(r2));self.assertEqual(s1,s2)

if __name__=='__main__':unittest.main()
