"""Focused VP-02 view grammar tests; stdlib only."""
import copy
import hashlib
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
from vpviews import ViewPrinter,ViewError,PROFILE
from vpviews.__main__ import strict_load

ROOT=Path(__file__).resolve().parents[1]
FILES=sorted((ROOT/'view_fixtures').glob('*.json'))
NS={'s':'http://www.w3.org/2000/svg'}

class ViewContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=ViewPrinter()
        cls.plans={p.stem:json.loads(p.read_text('utf8')) for p in FILES}
    def p0(self,idx):return copy.deepcopy(list(self.plans.values())[idx])
    def invalid(self,plan):
        with self.assertRaises(ViewError):self.p.render(plan)
    def test_exact_names(self):
        self.assertEqual([self.p0(i)['view'] for i in range(6)],['cube.flow']*2+['cube.diagramm']*2+['cube.tree']*2)
    def test_6_view_golden(self):
        for name,plan in self.plans.items():
            with self.subTest(name=name):
                raw=self.p.render(plan)
                self.assertEqual(raw,(ROOT/'view_outputs'/(name+'.svg')).read_bytes())
                self.assertEqual(raw,self.p.render(plan))
                svg=ET.fromstring(raw)
                self.assertEqual(svg.attrib.get('data-cube-view'),plan['view'])
                self.assertEqual(svg.attrib.get('data-printer-profile'),PROFILE)
                self.assertEqual(svg.attrib.get('role'),'img')
                self.assertTrue(svg.find('s:title',NS).text)
                self.assertTrue(svg.find('s:desc',NS).text)
    def test_reports_are_display_only(self):
        for plan in self.plans.values():
            rep=self.p.report(plan,self.p.render(plan))
            for k in ('semantic_conformance','epistemic_warrant','current_authority','canonical_admission'):
                self.assertEqual(rep[k],'NOT_EVALUATED')
            self.assertEqual(rep['content_status'],'declared_unverified')
    def test_no_active_svg(self):
        for plan in self.plans.values():
            v=self.p.render(plan)
            for prohibited in (b'<script',b'<foreignObject',b'<image',b'javascript:',b'<!DOCTYPE',b'@font-face',b'<animate'):
                self.assertNotIn(prohibited,v)
    def test_no_planner_name(self):
        for name in ('flow','chart','tree','cube.chart','planner.flow','cube.diagram','cube.Diagramm'):
            p=self.p0(0);p['view']=name;self.invalid(p)
    def test_wrong_lens(self):
        p=self.p0(0);p['lens']='provenance';self.invalid(p)
    def test_wrong_granularity(self):
        p=self.p0(0);p['granularity']='overview';self.invalid(p)
    def test_wrong_profile(self):
        p=self.p0(0);p['printer_profile']='P2-VP-2D/0.1.0';self.invalid(p)
    def test_wrong_morphology(self):
        p=self.p0(0);p['reference_version']='v9.3';self.invalid(p)
    def test_injection_escaping(self):
        p=self.p0(0);p['nodes'][0]['label']='<script>alert(1)</script> & text'
        raw=self.p.render(p)
        self.assertIn(b'&lt;script&gt;',raw)
        self.assertNotIn(b'<script',raw)
        ET.fromstring(raw)
    def test_external_properties_rejected(self):
        p=self.p0(0);p['onclick']='javascript:alert(1)';self.invalid(p)
        p=self.p0(0);p['nodes'][0]['href']='https://evil.example';self.invalid(p)
    def test_unknown_glyph(self):
        p=self.p0(0);p['nodes'][0]['anchor_id']='madeup.glyph';self.invalid(p)
    def test_node_form_contract(self):
        p=self.p0(0);p['nodes'][0]['form_id']='form.lens-marker';self.invalid(p)
    def test_status_accent_witness(self):
        p=self.p0(0);p['nodes'][0]['color_token']='status.success';self.invalid(p)
    def test_duplicate_nodes(self):
        p=self.p0(0);p['nodes'][1]['id']=p['nodes'][0]['id'];self.invalid(p)
    def test_missing_order(self):
        p=self.p0(0);del p['order'];self.invalid(p)
    def test_arbitrary_order_not_inferred(self):
        p=self.p0(0);p['order']=['resource','artifact'];self.assertTrue(self.p.validate(p))
    def test_flow_missing_declaration(self):
        p=self.p0(0);del p['edges'][0]['declaration_ref'];self.invalid(p)
    def test_flow_unknown_target(self):
        p=self.p0(0);p['edges'][0]['to']='missing';self.invalid(p)
    def test_flow_bad_arrow(self):
        p=self.p0(0);p['edges'][0]['arrow_anchor_id']='relation-arrows.causation';self.invalid(p)
    def test_flow_wrong_direction(self):
        p=self.p0(0);p['direction']='bidirectional';self.invalid(p)
    def test_flow_no_semantic_promotion(self):
        p=self.p0(0);p['declaration_status']='verified';self.invalid(p)
    def test_flow_duplicate_edge(self):
        p=self.p0(0);p['edges'].append(p['edges'][0]);self.invalid(p)
    def test_flow_two_modes(self):
        for i in (0,1):
            self.assertTrue(self.p.render(self.p0(i)))
    def test_flow_budget(self):
        p=self.p0(0);p['nodes']+= [copy.deepcopy(p['nodes'][0])]*4;self.invalid(p)
    def test_tree_multiparent(self):
        p=self.p0(5);p['edges'][-1]['to']='revision';self.invalid(p)
    def test_tree_cycle(self):
        p=self.p0(4);p['edges'][0]['from']='runtime';self.invalid(p)
    def test_tree_wrong_root(self):
        p=self.p0(4);p['root_id']='runtime';self.invalid(p)
    def test_tree_disconnected(self):
        p=self.p0(4);p['edges'][1]['to']='runtime';self.invalid(p)
    def test_tree_too_many_links(self):
        p=self.p0(4);p['edges'].append(copy.deepcopy(p['edges'][0]));self.invalid(p)
    def test_tree_order_must_be_breadth_first(self):
        p=self.p0(5);p['order']=['resource','artifact','revision','source','cache','evidence'];self.invalid(p)
    def test_tree_two_valid_hierarchies(self):
        for i in (4,5):
            self.assertTrue(self.p.validate(self.p0(i)))
    def test_chart_both_plot_types(self):
        self.assertEqual({self.p0(i)['plot'] for i in (2,3)},{'bar','line'})
    def test_chart_no_string_values(self):
        p=self.p0(2);p['samples'][0]['value']='12';self.invalid(p)
    def test_chart_nan(self):
        p=self.p0(2);p['samples'][0]['value']=float('nan');self.invalid(p)
    def test_chart_infinity(self):
        p=self.p0(2);p['samples'][0]['value']=float('inf');self.invalid(p)
    def test_chart_negative(self):
        p=self.p0(3);p['samples'][0]['value']=-2;self.invalid(p)
    def test_chart_boolean(self):
        p=self.p0(2);p['samples'][0]['value']=True;self.invalid(p)
    def test_chart_precision(self):
        p=self.p0(3);p['samples'][0]['value']=1.2346;self.invalid(p)
    def test_chart_wrong_unit_context(self):
        p=self.p0(2);p['samples'][0]['unit']='ms';self.invalid(p)
    def test_chart_missing_unit(self):
        p=self.p0(2);del p['metric']['unit'];self.invalid(p)
    def test_chart_missing_measurement_provenance(self):
        p=self.p0(2);del p['metric']['declaration_ref'];self.invalid(p)
    def test_chart_no_verified_data_because_unsupported(self):
        p=self.p0(2);p['metric']['evidence_status']='verified';self.invalid(p)
    def test_chart_line_is_not_time(self):
        p=self.p0(3);p['samples'][0]['timestamp']='2026-10-24T06:00:00Z';self.invalid(p)
    def test_chart_budget(self):
        p=self.p0(2);p['samples']*=3;self.invalid(p)
    def test_chart_scale(self):
        p=self.p0(2);p['metric']['scale']='logarithmic';self.invalid(p)
    def test_chart_all_zero(self):
        p=self.p0(2)
        for item in p['samples']:item['value']=0
        self.assertIn(b'<svg',self.p.render(p))
    def test_chart_max_limit(self):
        p=self.p0(2);p['samples'][0]['value']=1000000001;self.invalid(p)
    def test_chart_markup_escape(self):
        p=self.p0(3);p['samples'][0]['label']='<a>&"';raw=self.p.render(p)
        self.assertIn(b'&lt;a&gt;',raw)
        ET.fromstring(raw)
    def test_report_contains_declaration_pointers(self):
        for i in (0,4):
            p=self.p0(i);r=self.p.report(p,self.p.render(p))
            self.assertEqual(len(r['displayed_edges']),len(p['edges']))
            self.assertEqual(r['displayed_item_ids'],p['order'])
    def test_chart_report_unit(self):
        p=self.p0(3);r=self.p.report(p,self.p.render(p));self.assertEqual(r['unit'],'ms')
    def test_cli_success(self):
        with tempfile.TemporaryDirectory() as d:
            svg=Path(d)/'test.svg';rep=Path(d)/'report.json'
            q=subprocess.run([sys.executable,'-m','vpviews','--input',str(FILES[0]),'--output',str(svg),'--report',str(rep)],cwd=str(ROOT),capture_output=True,text=True)
            self.assertEqual(q.returncode,0,q.stderr)
            self.assertEqual(svg.read_bytes(),self.p.render(self.p0(0)))
            self.assertEqual(json.loads(rep.read_text('utf8'))['svg_sha256'],hashlib.sha256(svg.read_bytes()).hexdigest())
    def test_cli_bad_planner_view(self):
        with tempfile.TemporaryDirectory() as d:
            p=self.p0(0);p['view']='flow';f=Path(d)/'bad.json';f.write_text(json.dumps(p))
            q=subprocess.run([sys.executable,'-m','vpviews','--input',str(f),'--output',str(Path(d)/'bad.svg')],cwd=str(ROOT),capture_output=True,text=True)
            self.assertEqual(q.returncode,2)
            self.assertIn('cube.flow',q.stderr)
            self.assertFalse((Path(d)/'bad.svg').exists())
    def test_duplicate_json_keys_cli(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'dup.json';f.write_text('{"view":"cube.flow","view":"cube.tree"}')
            with self.assertRaises(ViewError):strict_load(f)
    def test_reference_identity_is_stable(self):
        for p in (self.p0(0),self.p0(4)):
            svg=ET.fromstring(self.p.render(p))
            items=[g for g in svg.findall('.//s:g',NS) if 'data-item-id' in g.attrib]
            self.assertEqual({g.attrib['data-item-id'] for g in items},{n['id'] for n in p['nodes']})
            self.assertTrue(all('data-anchor-id' in g.attrib for g in items))
    def test_no_layer_inference(self):
        for plan in self.plans.values():
            self.assertNotIn(b'data-authorized',self.p.render(plan))

if __name__=='__main__':unittest.main()
