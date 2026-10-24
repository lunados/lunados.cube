import copy
import hashlib
import json
import re
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
from vp2d import Printer,PrintError
ROOT=Path(__file__).resolve().parents[1]
NS={'svg':'http://www.w3.org/2000/svg'}

class PrinterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=Printer()
        cls.fixtures=[json.loads(p.read_text('utf8')) for p in sorted((ROOT/'fixtures').glob('*.json'))]

    def test_symbol_lock(self):
        self.assertEqual(len(self.p.anchors),129)
        self.assertEqual(len(self.p.symbols['anchors']),129)
        self.assertEqual(len(set(a['unicode'] for a in self.p.anchors)),129)
    def test_fixtures(self):
        self.assertEqual(len(self.fixtures),4)
        for p in self.fixtures:
            with self.subTest(view=p['view_id']):
                self.assertTrue(self.p.validate(p))
                raw=self.p.render(p)
                root=ET.fromstring(raw)
                self.assertEqual(root.tag,'{http://www.w3.org/2000/svg}svg')
                self.assertEqual(root.attrib['role'],'img')
                self.assertIsNotNone(root.find('svg:title',NS))
                self.assertIsNotNone(root.find('svg:desc',NS))
                self.assertNotIn(b'<script',raw)
                self.assertNotIn(b'<image',raw)
                self.assertNotIn(b'<foreignObject',raw)
                self.assertNotIn(b'http://www.w3.org/1999/xlink',raw)
                self.assertNotIn(b'<!DOCTYPE',raw)
                self.assertEqual(raw,self.p.render(p))
                self.assertEqual(hashlib.sha256(raw).digest(),hashlib.sha256(self.p.render(p)).digest())
    def test_pairs_canonical_order(self):
        root=ET.fromstring(self.p.render(self.fixtures[0]))
        ids=[e.attrib.get('data-anchor-id') for e in root.findall('.//svg:g',NS) if e.attrib.get('data-anchor-id')]
        expected=[]
        for x in self.p.pairs:
            for k in ('dimension','opening','complement'):
                expected.append(self.p.concept_by_id[x[k]]['visual_semantic_id'])
        self.assertEqual(ids,expected)
    def test_relation_arrow_unicode(self):
        root=ET.fromstring(self.p.render(self.fixtures[1]))
        texts=''.join(n.text or '' for n in root.findall('.//svg:text',NS))
        self.assertIn(self.p.by_id['relation-arrows.reference']['unicode'],texts)
        self.assertIn('declared',texts)
    def test_no_hidden_status_proof(self):
        base=copy.deepcopy(self.fixtures[2]);a=base['items'][1]
        a['color_token']='status.pending'
        with self.assertRaises(PrintError):self.p.render(base)
        a['qualified_state_witness_ref']='fixture:witness-1'
        self.assertTrue(self.p.validate(base))
    def test_status_wrong_anchor(self):
        base=copy.deepcopy(self.fixtures[1]);a=base['items'][0]
        a['color_token']='status.success';a['qualified_state_witness_ref']='fixture:witness-1'
        with self.assertRaises(PrintError):self.p.render(base)
    def test_bad_operator_accent(self):
        base=copy.deepcopy(self.fixtures[1]);a=base['items'][0]
        a['anchor_id']='relation-arrows.reference';a['form_id']='form.relation-edge';a['color_token']='domain.epistemology'
        with self.assertRaises(PrintError):self.p.render(base)
    def test_bad_forms(self):
        base=copy.deepcopy(self.fixtures[1]);base['items'][0]['form_id']='form.lens-marker'
        with self.assertRaises(PrintError):self.p.render(base)
    def test_invalid_anchor(self):
        base=copy.deepcopy(self.fixtures[1]);base['items'][0]['anchor_id']='some.unsupported'
        with self.assertRaises(PrintError):self.p.render(base)
    def test_invalid_relation(self):
        base=copy.deepcopy(self.fixtures[1]);base['links'][0]['to']='not_found'
        with self.assertRaises(PrintError):self.p.render(base)
    def test_relation_requires_declaration(self):
        base=copy.deepcopy(self.fixtures[1]);del base['links'][0]['declaration_ref']
        with self.assertRaises(PrintError):self.p.render(base)
    def test_no_free_layout_or_3d(self):
        base=copy.deepcopy(self.fixtures[1]);base['template']='3d'
        with self.assertRaises(PrintError):self.p.render(base)
    def test_markup_escaped(self):
        base=copy.deepcopy(self.fixtures[1]);base['items'][0]['label']='<script>alert(1)</script> & quoted'
        raw=self.p.render(base)
        self.assertNotIn(b'<script',raw)
        self.assertIn(b'&lt;script&gt;',raw)
        ET.fromstring(raw)
    def test_duplicate_id(self):
        base=copy.deepcopy(self.fixtures[1]);base['items'][1]['id']=base['items'][0]['id']
        with self.assertRaises(PrintError):self.p.render(base)
    def test_no_silent_auto_pair_change(self):
        base=copy.deepcopy(self.fixtures[0]);base['items'].append(copy.deepcopy(self.fixtures[1]['items'][0]))
        with self.assertRaises(PrintError):self.p.render(base)
    def test_wrong_version(self):
        base=copy.deepcopy(self.fixtures[2]);base['reference_version']='v9.3'
        with self.assertRaises(PrintError):self.p.render(base)
    def test_extra_attribute(self):
        base=copy.deepcopy(self.fixtures[1]);base['items'][0]['href']='https://evil.example'
        with self.assertRaises(PrintError):self.p.render(base)
    def test_missing_sequence_basis(self):
        base=copy.deepcopy(self.fixtures[2]);del base['sequence_basis']
        with self.assertRaises(PrintError):self.p.render(base)
    def test_sequence_order_mismatch(self):
        base=copy.deepcopy(self.fixtures[2]);base['order']=list(reversed(base['order']))
        with self.assertRaises(PrintError):self.p.render(base)
    def test_label_overflow_rejected(self):
        base=copy.deepcopy(self.fixtures[1]);base['items'][0]['label']='a'*90
        with self.assertRaises(PrintError):self.p.render(base)
    def test_no_unauthorized_scope_inference(self):
        raw=self.p.render(self.fixtures[3]); self.assertIn(b'not governance Admission',raw)
        self.assertNotIn(b'authorized="true"',raw)
    def test_fonts_are_external_assets_never_required(self):
        raw=self.p.render(self.fixtures[0]);self.assertIn(b'font-family',raw)
        self.assertNotIn(b'@font-face',raw)
    def test_static_geometry(self):
        for x in self.fixtures:
            raw=self.p.render(x)
            self.assertIn(b'viewBox',raw)
            self.assertNotIn(b'<animate',raw)
            self.assertNotIn(b'javascript:',raw)

if __name__=='__main__':unittest.main()
