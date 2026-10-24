import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R))
from vpconformance import ConformanceAuditor,ConformanceError,VIEWS,LENSES,LEVELS
from vpconformance.conformance import sha
from vpgranularity.printer import CAPS
from vplenses.printer import source_digest

oracle=json.loads((R/'fixtures'/'INDEPENDENT_ORACLE.json').read_text('utf8'))

def request(name,lens='semantics',level='overview'):
    return json.loads((R/'matrix'/f'{name}__{lens}__{level}.json').read_text('utf8'))

def audit(q):return ConformanceAuditor().audit(q)

def rehash(q):
    q['source_bundle']['source_view_sha256']=source_digest(q['source_bundle']['view_plan'])
    q['source_bundle_sha256']=sha(q['source_bundle'])

class TestVP05(unittest.TestCase):
    def test_01_oracle_not_derived_from_golden(self):
        self.assertNotIn('svg_sha256',(R/'fixtures'/'INDEPENDENT_ORACLE.json').read_text('utf8'))
        self.assertEqual(set(oracle['lenses']),{'semantics','provenance','execution','governance','epistemology'})
        self.assertEqual(len(oracle['sources']),6)

    def test_02_all_90_combinations_with_independent_expected_counts(self):
        accept=reject=0
        for source,spec in oracle['sources'].items():
            for lens in oracle['lenses']:
                for level in LEVELS:
                    with self.subTest(source=source,lens=lens,level=level):
                        case=f'{source}__{lens}__{level}';q=request(source,lens,level)
                        gold=json.loads((R/'matrix'/(case+'.vp05.report.json')).read_text('utf8'))
                        declared=('cube.lens.'+lens) in {b['lens'] for b in q['source_bundle']['facet_bindings']}
                        if not declared:
                            self.assertEqual(gold['status'],'EXPECTED_REJECTION')
                            with self.assertRaisesRegex(ConformanceError,'selected lens has no explicit facet bindings'):audit(q)
                            self.assertFalse((R/'matrix'/(case+'.svg')).exists())
                            reject+=1;continue
                        data=spec['levels'][level]
                        expected={'source_items':spec['source_items'],'shown_items':data[0],
                                  'shown_edges':data[1],'completeness':data[2]}
                        a,svg,pr=ConformanceAuditor().audit(q,expected,include_svg=True)
                        self.assertEqual(a,gold)
                        self.assertEqual(svg,(R/'matrix'/(case+'.svg')).read_bytes())
                        self.assertEqual(pr,json.loads((R/'matrix'/(case+'.vp04.report.json')).read_text('utf8')))
                        self.assertEqual(a['decision']['status'] in ('proposal_not_printed','descriptive_display_only'),True)
                        accept+=1
        self.assertEqual((accept,reject),(54,36))

    def test_03_source_bundles_identical_between_lenses(self):
        for source in oracle['sources']:
            shas=set()
            for lens in oracle['lenses']:
                for level in LEVELS:
                    q=request(source,lens,level)
                    shas.add(q['source_bundle_sha256'])
            self.assertEqual(len(shas),1,source)

    def test_04_source_order_never_mutated(self):
        q=request('tree_modules');original=copy.deepcopy(q)
        _=audit(q)
        self.assertEqual(q,original)

    def test_05_no_authority_promotion(self):
        a=audit(request('flow_migration','governance'))
        self.assertEqual([a[x] for x in ('epistemic_warrant','current_authority','canonical_admission')],['NOT_EVALUATED']*3)

    def test_06_missing_lens_rejection_not_fallback(self):
        with self.assertRaisesRegex(ConformanceError,'no explicit facet bindings'):audit(request('chart_line','governance'))

    def test_07_unknown_planner_view(self):
        q=request('flow_migration');q['projection']['view']='flow'
        with self.assertRaisesRegex(ConformanceError,'VP04 rejected'):audit(q)

    def test_08_lens_typo(self):
        q=request('flow_migration');q['projection']['lens']='cube.lens.origin'
        with self.assertRaisesRegex(ConformanceError,'VP04 rejected'):audit(q)

    def test_09_unknown_granularity(self):
        q=request('flow_migration');q['projection']['granularity']='microscopic'
        with self.assertRaisesRegex(ConformanceError,'VP04 rejected'):audit(q)

    def test_10_original_source_hash_tamper(self):
        q=request('flow_migration');q['source_bundle']['view_plan']['title']='changed'
        with self.assertRaisesRegex(ConformanceError,'checksum'):audit(q)

    def test_11_nested_source_hash_tamper(self):
        q=request('flow_migration');q['source_bundle']['view_plan']['title']='changed';q['source_bundle_sha256']=sha(q['source_bundle'])
        with self.assertRaisesRegex(ConformanceError,'source view checksum'):audit(q)

    def test_12_lens_retarget_tamper(self):
        q=request('flow_migration');q['source_bundle']['facet_bindings'][0]['target_id']='not_exist';rehash(q)
        with self.assertRaises(ConformanceError):audit(q)

    def test_13_effective_scope_strict_input(self):
        q=request('chart_inventory');q['projection']['extra']='invalid'
        with self.assertRaises(ConformanceError):audit(q)

    def test_14_invalid_budget_boolean(self):
        q=request('tree_modules');q['projection']['budget']['max_items']=True
        with self.assertRaises(ConformanceError):audit(q)

    def test_15_detail_cannot_hide(self):
        q=request('tree_resources','semantics','detail');q['projection']['budget']['max_items']=3
        with self.assertRaisesRegex(ConformanceError,'detail cannot omit'):audit(q)

    def test_16_strict_reject(self):
        q=request('tree_modules');q['projection']['overflow']='reject'
        with self.assertRaisesRegex(ConformanceError,'overflow=reject'):audit(q)

    def test_17_focus_edge_present(self):
        q=request('flow_research');q['projection']['focus']={'kind':'edge','id':'e2'}
        a=audit(q);self.assertIn('e2',a['displayed_source_edge_ids'])

    def test_18_tree_focus_preserves_ancestors(self):
        q=request('tree_resources');q['projection']['focus']={'kind':'node','id':'resource'}
        try:a=audit(q)
        except ConformanceError as e:self.assertIn('focus ancestry',str(e))
        else:self.assertIn('resource',a['displayed_item_ids'])

    def test_19_focus_budget_conflict(self):
        q=request('flow_migration');q['projection']['focus']={'kind':'node','id':'nonexistent'}
        with self.assertRaises(ConformanceError):audit(q)

    def test_20_bar_maximum(self):
        q=request('chart_inventory');a=audit(q)
        plan=q['source_bundle']['view_plan'];peak=max(s['value'] for s in plan['samples'])
        self.assertTrue(any(s['id'] in a['displayed_item_ids'] and s['value']==peak for s in plan['samples']))

    def test_21_line_has_no_new_segment(self):
        q=request('chart_line');a=audit(q)
        order=[s['id'] for s in q['source_bundle']['view_plan']['samples']]
        idx=[order.index(i) for i in a['displayed_item_ids']]
        self.assertEqual(idx,list(range(min(idx),max(idx)+1)))

    def test_22_decision_for_complete(self):
        self.assertEqual(audit(request('flow_migration'))['decision']['action'],'SINGLE_COMPLETE')

    def test_23_split_recommendation_materializes_no_panels(self):
        a=audit(request('chart_line'))
        self.assertEqual(a['decision']['action'],'SPLIT_RECOMMENDED')
        s=a['split_feasibility'];self.assertEqual(s['status'],'FEASIBLE')
        self.assertFalse(s['panels_materialized'])
        self.assertGreaterEqual(s['estimated_panel_count'],2)
        self.assertEqual(s['uncovered_item_ids'],[])

    def test_24_overview_partial_not_auto_split(self):
        a=audit(request('tree_modules'))
        self.assertEqual(a['decision']['action'],'SINGLE_DISCLOSED')
        self.assertEqual(a['completeness'],'PARTIAL_EXPLICIT')

    def test_25_recommendation_does_not_insert_virtual_nodes(self):
        a=audit(request('chart_line'))
        source={x['id'] for x in request('chart_line')['source_bundle']['view_plan']['samples']}
        for page in a['split_feasibility']['panels']:
            self.assertTrue(set(page['shown_item_ids'])<=source)

    def test_26_split_panel_overlap_explicit(self):
        a=audit(request('chart_inventory'))
        s=a['split_feasibility']
        self.assertIn(s['status'],('FEASIBLE','NOT_REQUIRED'))
        if s['status']=='FEASIBLE':self.assertIn('repeated_item_ids',s)

    def test_27_scope_no_separate_application(self):
        a=audit(request('tree_modules'))
        self.assertNotIn('saved_state',a)
        self.assertNotIn('svg_scene',a)

    def test_28_request_reject_method_not_change_semantic(self):
        q=request('tree_modules');q['source_bundle']['basis']='verified';rehash(q)
        with self.assertRaisesRegex(ConformanceError,'declared_unverified'):audit(q)

    def test_29_svg_contains_declared_ledger(self):
        q=request('flow_research');a,svg,_=ConformanceAuditor().audit(q,include_svg=True)
        root=ET.fromstring(svg)
        meta=[el for el in root.iter() if el.get('id')=='vp04-source-and-reduction-ledger']
        self.assertEqual(len(meta),1)
        self.assertEqual(json.loads(meta[0].text)['omitted_item_ids'],a['omitted_item_ids'])

    def test_30_svg_no_script_or_remote_import(self):
        _,svg,_=ConformanceAuditor().audit(request('tree_modules'),include_svg=True)
        self.assertNotIn(b'<script',svg);self.assertNotIn(b'<image',svg);self.assertNotIn(b'https://',svg)

    def test_31_same_inputs_byteidentical(self):
        q=request('chart_inventory','provenance','standard')
        a,s1,_=ConformanceAuditor().audit(q,include_svg=True)
        b,s2,_=ConformanceAuditor().audit(q,include_svg=True)
        self.assertEqual(s1,s2);self.assertEqual(a,b)

    def test_32_lens_can_affect_selection_only_declared(self):
        for lens in oracle['lenses']:
            q=request('tree_modules',lens)
            result=audit(q)
            originals={n['id'] for n in q['source_bundle']['view_plan']['nodes']}
            self.assertTrue(set(result['displayed_item_ids'])<=originals)

    def test_33_measurement_not_invented(self):
        q=request('chart_inventory');a=audit(q)
        self.assertEqual(a['source_status'],'declared_unverified')
        self.assertEqual(a['epistemic_warrant'],'NOT_EVALUATED')

    def test_34_all_registered_dimensions_only(self):
        self.assertEqual(len(VIEWS)*len(LENSES)*len(LEVELS),45)

    def test_35_overview_complete_small_case(self):
        a=audit(request('flow_migration','epistemology'))
        self.assertEqual(a['omitted_item_ids'],[])
        self.assertEqual(a['completeness'],'COMPLETE_INPUT_VIEW')

    def test_36_invalid_source_characters_fail(self):
        q=request('flow_migration');q['source_bundle']['view_plan']['nodes'][0]['label']='bad\x00';rehash(q)
        with self.assertRaises(ConformanceError):audit(q)

    def test_39_complete_feasible_split_coverage(self):
        for path in sorted((R/'matrix').glob('*.vp05.report.json')):
            a=json.loads(path.read_text('utf8'))
            if a['status']!='PASS':continue
            split=a['split_feasibility'];q=json.loads((R/'matrix'/path.name.replace('.vp05.report.json','.json')).read_text('utf8'))
            original=q['source_bundle']['view_plan']
            ids={x['id'] for x in original.get('samples',original.get('nodes',[]))}
            edges={'e'+str(i+1) for i in range(len(original.get('edges',[])))}
            if split['status']=='FEASIBLE':
                covered=set().union(*(set(p['shown_item_ids']) for p in split['panels']))
                covered_edges=set().union(*(set(p['shown_edge_ids']) for p in split['panels']))
                self.assertEqual(covered,ids)
                self.assertEqual(covered_edges,edges)
                counts={i:sum(i in p['shown_item_ids'] for p in split['panels']) for i in ids}
                self.assertEqual(split['repeated_item_ids'],sorted(i for i,c in counts.items() if c>1))

    def test_40_infeasible_deep_tree_disclosed(self):
        q=request('tree_modules');p=q['source_bundle']['view_plan'];ids=p['order']
        p['order']=[ids[0],ids[1],ids[4],ids[2],ids[3]]
        p['nodes']=sorted(p['nodes'],key=lambda x:p['order'].index(x['id']))
        for i,e in enumerate(p['edges']):
            e['from'],e['to']=[(ids[0],ids[1]),(ids[0],ids[4]),(ids[1],ids[2]),(ids[2],ids[3])][i]
        rehash(q)
        a=audit(q)
        self.assertEqual(a['split_feasibility']['status'],'NOT_FEASIBLE')
        self.assertIn(ids[3],a['split_feasibility']['uncovered_item_ids'])
        self.assertFalse(a['split_feasibility']['panels_materialized'])

    def test_41_split_never_claims_global_optimum(self):
        for name in ('chart_line','tree_resources','flow_research'):
            a=audit(request(name))
            self.assertFalse(a['split_feasibility']['is_minimum_proven'])

    def test_42_cli_duplicate_json_keys_rejected(self):
        from vpconformance.__main__ import load
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            f=Path(td)/'bad.json';f.write_text('{"x":1,"x":2}',encoding='utf8')
            with self.assertRaises(Exception):load(f)

    def test_37_schema_dimensions_and_reports(self):
        try:import jsonschema
        except ImportError:self.skipTest('optional jsonschema')
        d=json.loads((R/'VP05_AUDIT_REPORT.schema.json').read_text('utf8'))
        v=jsonschema.Draft202012Validator(d);v.check_schema(d)
        for fname in sorted((R/'matrix').glob('*.vp05.report.json')):
            x=json.loads(fname.read_text('utf8'))
            if x['status']=='PASS':v.validate(x)

    def test_38_expected_rejections_not_confused_with_semantic_fail(self):
        x=json.loads((R/'matrix'/'flow_research__governance__overview.vp05.report.json').read_text('utf8'))
        self.assertEqual(x['diagnostic'],'LENS_DECLARATION_MISSING')
        self.assertEqual(x['semantic_conformance'],'NOT_EVALUATED')

if __name__=='__main__':unittest.main()
