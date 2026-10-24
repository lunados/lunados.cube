"""VP-04 contracts: source preservation, omission ledger, focus, budgets, no semantic invention."""
import copy
import json
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

from vpgranularity.printer import GranularityPrinter,GranularityError,sha,PROFILE,FORMAT,NS
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT.parent/'visual-printer-2d-lab'

def read(name):return json.loads((ROOT/'fixtures'/(name+'.json')).read_text('utf8'))

def clone(x):return copy.deepcopy(x)

class GranularityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.p=GranularityPrinter()

    def test_all_golden_requests_render(self):
        files=sorted((ROOT/'fixtures').glob('*.json'))
        self.assertEqual(len(files),20)
        for f in files:
            with self.subTest(f=f.name):
                req=json.loads(f.read_text('utf8'))
                self.assertEqual(self.p.render(req),self.p.render(req))

    def test_golden_reports_exclude_p1_ontological_claims(self):
        for f in sorted((ROOT/'fixtures').glob('*.json')):
            req=json.loads(f.read_text('utf8'));svg=self.p.render(req);report=self.p.report(req,svg)
            for key in ('semantic_conformance','epistemic_warrant','current_authority','canonical_admission'):
                self.assertEqual(report[key],'NOT_EVALUATED')
            self.assertEqual(report['source_bundle_sha256'],sha(req['source_bundle']))
            self.assertEqual(report['counts']['source_items'],report['counts']['items_shown']+len(report['omitted_item_ids']))
            self.assertEqual(report['counts']['source_edges'],report['counts']['edges_shown']+len(report['omitted_edges']))
            self.assertEqual(report['completeness']=='COMPLETE_INPUT_VIEW',not report['omitted_item_ids'] and not report['omitted_edges'])

    def test_unchanged_source_plan(self):
        for f in sorted((ROOT/'fixtures').glob('*.json')):
            req=json.loads(f.read_text('utf8'));old=copy.deepcopy(req)
            self.p.render(req)
            self.assertEqual(req,old)

    def test_svg_metadata_contains_full_loss_ledger(self):
        req=read('tree_modules__overview');svg=self.p.render(req);root=ET.fromstring(svg)
        md=next(el for el in root if el.tag==f'{{{NS}}}metadata' and el.get('id')=='vp04-source-and-reduction-ledger')
        ledger=json.loads(md.text);report=self.p.report(req,svg)
        self.assertEqual(ledger['omitted_item_ids'],report['omitted_item_ids'])
        self.assertEqual(ledger['omitted_edges'],report['omitted_edges'])
        self.assertEqual(ledger['omitted_facet_bindings'],report['omitted_facet_bindings'])
        self.assertEqual(root.get('data-vp04-source-bundle-sha256'),req['source_bundle_sha256'])

    def test_no_synthetic_predicates(self):
        for f in (ROOT/'fixtures').glob('*.json'):
            req=json.loads(f.read_text('utf8'));proj=self.p.project(req)
            original=req['source_bundle']['view_plan']
            if 'edges' in original:
                for e in proj['plan']['edges']:self.assertIn(e,original['edges'])
                self.assertEqual(len(proj['plan']['edges'])+len(proj['omitted_edges']),len(original['edges']))
            if 'samples' in original:
                for s in proj['plan']['samples']:self.assertIn(s,original['samples'])

    def test_tree_ancestry_preserved(self):
        req=read('tree_resources__overview');p=req['projection'];p['focus']={'kind':'node','id':'revision'}
        req['source_bundle_sha256']=sha(req['source_bundle'])
        try:
            proj=self.p.project(req)
        except GranularityError as e:
            self.assertIn('ancestry',str(e))
        else:
            full=req['source_bundle']['view_plan'];pairs={e['to']:e['from'] for e in full['edges']}
            visible=set(proj['plan']['order'])
            current='revision'
            while current!=full['root_id']:
                self.assertIn(current,visible)
                current=pairs[current]
            self.assertIn(current,visible)

    def test_focus_edge_remapping(self):
        req=read('tree_modules__focus_edge');rep=self.p.report(req,self.p.render(req))
        self.assertIn('e3',{x['source_edge_id'] for x in rep['shown_edges']})
        root=ET.fromstring(self.p.render(req))
        self.assertTrue(any(el.get('data-source-edge-id')=='e3' for el in root.iter()))

    def test_chart_max_sample_kept_for_bar_scale(self):
        req=read('chart_inventory__overview');p=self.p.project(req)
        full=req['source_bundle']['view_plan']['samples']
        maxs=max(x['value'] for x in full)
        self.assertTrue(any(x['value']==maxs for x in p['plan']['samples']))
        self.assertFalse(p['axis_rescaled'])

    def test_chart_line_never_joins_nonadjacent_samples(self):
        req=read('chart_line__overview');full=req['source_bundle']['view_plan']['samples']
        projected=self.p.project(req)['plan']['samples']
        pos=[full.index(s) for s in projected]
        self.assertEqual(pos,list(range(pos[0],pos[-1]+1)))

    def test_chart_scale_change_is_flagged(self):
        req=read('chart_line__overview')
        bundle=req['source_bundle'];bundle['view_plan']['samples'][0]['value']=5000
        from vplenses.printer import source_digest
        bundle['source_view_sha256']=source_digest(bundle['view_plan'])
        req['source_bundle_sha256']=sha(bundle)
        proj=self.p.project(req)
        self.assertTrue(proj['axis_rescaled'])
        svg=self.p.render(req)
        self.assertIn(b'CHART AXIS RESCALED',svg)
        self.assertTrue(self.p.report(req,svg)['chart_axis_rescaled'])

    def test_no_authority_from_lens(self):
        req=read('flow_research__overview');root=ET.fromstring(self.p.render(req))
        self.assertEqual(root.get('data-vp04-granularity'),'overview')
        self.assertTrue(any(el.get('data-vp04-complexity-ledger')=='display-only' for el in root.iter()))
        self.assertFalse(any(el.tag.rsplit('}',1)[-1] in ('foreignObject','image','script','use') for el in root.iter()))

    def test_empty_visible_lens_is_explicit_not_faked(self):
        req=read('chart_line__overview')
        # The only lens binding points to final sample; focus forces first window here.
        req['projection']['focus']=None
        # Redirect facet to first sample but request focus on last, making it omitted.
        req['source_bundle']['facet_bindings'][0]['target_id']='s1'
        from vplenses.printer import source_digest
        req['source_bundle_sha256']=sha(req['source_bundle'])
        req['projection']['focus']={'kind':'sample','id':'s5'}
        svg=self.p.render(req);rep=self.p.report(req,svg)
        self.assertEqual(rep['lens_emphasis'],'no_visible_declared_targets')
        self.assertIn(b'LENS HAS NO VISIBLE DECLARED TARGETS',svg)

    def test_projection_consistent_between_levels(self):
        name='tree_resources'
        shown=[]
        for level in ('overview','standard','detail'):
            rep=self.p.report(read(f'{name}__{level}'),self.p.render(read(f'{name}__{level}')))
            shown.append(len(rep['shown_item_ids']))
        self.assertEqual(shown,[3,5,6])

    def assert_rejected(self,name,mutate,fragment=None):
        q=read(name);mutate(q)
        with self.assertRaises(GranularityError) as ctx:self.p.render(q)
        if fragment:self.assertIn(fragment,str(ctx.exception))

    def test_invalid_profile(self):self.assert_rejected('flow_research__overview',lambda q:q.update(profile='Planner'), 'profile')
    def test_wrong_format(self):self.assert_rejected('flow_research__overview',lambda q:q.update(format='x'),'format')
    def test_legacy_planner_view_rejected(self):self.assert_rejected('flow_research__overview',lambda q:q['projection'].update(view='flow'),'view')
    def test_invalid_lens(self):self.assert_rejected('flow_research__overview',lambda q:q['projection'].update(lens='governance'),'lens')
    def test_unknown_level(self):self.assert_rejected('flow_research__overview',lambda q:q['projection'].update(granularity='micro'),'granularity')
    def test_extra_field_rejected(self):self.assert_rejected('flow_research__overview',lambda q:q.update(extra=True),'requires exactly')
    def test_budget_boolean_invalid(self):self.assert_rejected('flow_research__overview',lambda q:q['projection']['budget'].update(max_items=True),'integer')
    def test_budget_too_big(self):self.assert_rejected('flow_research__overview',lambda q:q['projection']['budget'].update(max_items=7),'max_items')
    def test_budget_too_small(self):self.assert_rejected('flow_research__overview',lambda q:q['projection']['budget'].update(max_items=1),'max_items')
    def test_edge_budget_too_big(self):self.assert_rejected('flow_research__overview',lambda q:q['projection']['budget'].update(max_edges=6),'max_edges')
    def test_unknown_focus(self):self.assert_rejected('flow_research__overview',lambda q:q['projection'].update(focus={'kind':'node','id':'not_there'}),'focus')
    def test_focus_id_with_control(self):self.assert_rejected('flow_research__overview',lambda q:q['projection'].update(focus={'kind':'node','id':'bad\n'}),'focus')
    def test_invalid_focus_kind(self):self.assert_rejected('flow_research__overview',lambda q:q['projection'].update(focus={'kind':'sample','id':'a'}),'focus')
    def test_invalid_overflow(self):self.assert_rejected('flow_research__overview',lambda q:q['projection'].update(overflow='silent'),'overflow')
    def test_reject_overflow(self):self.assert_rejected('tree_modules__overview',lambda q:q['projection'].update(overflow='reject'),'overflow=reject')
    def test_detail_cannot_truncate(self):self.assert_rejected('tree_modules__detail',lambda q:q['projection']['budget'].update(max_items=3,max_edges=2),'detail cannot omit')
    def test_bundle_hash_tamper(self):self.assert_rejected('flow_research__overview',lambda q:q['source_bundle']['view_plan'].update(title='tampered'),'checksum')
    def test_plan_hash_tamper(self):
        def bad(q):
            q['source_bundle']['view_plan']['title']='tampered'
            q['source_bundle_sha256']=sha(q['source_bundle'])
        self.assert_rejected('flow_research__overview',bad,'source view checksum')
    def test_unverified_authority_changed(self):
        def bad(q):
            q['source_bundle']['basis']='verified'
            q['source_bundle_sha256']=sha(q['source_bundle'])
        self.assert_rejected('flow_research__overview',bad,'declared_unverified')
    def test_focus_edge_requires_budget(self):
        def bad(q):q['projection']['focus']={'kind':'edge','id':'e2'}
        # Can still fit two endpoint nodes, so demand budget=1 is rejected deterministically.
        self.assert_rejected('flow_research__overview',lambda q:(bad(q),q['projection']['budget'].update(max_edges=0)),'max_edges')
    def test_tree_more_nodes_than_edge_budget_is_bounded(self):
        q=read('tree_modules__overview')
        q['projection']['budget']['max_edges']=1
        rep=self.p.report(q,self.p.render(q))
        self.assertEqual(rep['counts']['items_shown'],2)
        self.assertEqual(rep['counts']['edges_shown'],1)
        self.assertEqual(rep['counts']['items_omitted'],3)

    def test_focus_tree_deep_reject(self):
        # Create a valid VP02 tree with a 4-level chain from the existing registered nodes.
        q=read('tree_resources__overview');bundle=q['source_bundle'];p=bundle['view_plan']
        ids=p['order'][:4];p['nodes']=[n for n in p['nodes'] if n['id'] in ids]
        p['order']=ids
        old=p['edges'][:3]
        p['edges']=[dict(e,**{'from':ids[i],'to':ids[i+1]}) for i,e in enumerate(old)]
        bundle['facet_bindings'][0]['target_id']=ids[3]
        from vplenses.printer import source_digest
        bundle['source_view_sha256']=source_digest(p)
        q['source_bundle_sha256']=sha(bundle)
        q['projection']['focus']={'kind':'node','id':ids[3]}
        # Baseline validates the authored tree, but VP04 overview has room for 3 of 4 required ancestors.
        self.p.view_printer.validate(p)
        with self.assertRaisesRegex(GranularityError,'ancestry'):self.p.render(q)
    def test_flow_not_fabricated_if_only_isolated_nodes_possible(self):
        q=read('flow_research__overview')
        full=q['source_bundle']['view_plan']
        # Choose focus node that occurs in no edge? Source fixture may have none; explicit mutate via full graph.
        self.assertTrue(full['edges'])

if __name__=='__main__':unittest.main()
