"""Self-contained P1.2 parser conformance suite; no external deps required."""
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from decimal import Decimal

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from cube_parser import (parse_result, parse_acg_bytes, load_ast_bytes,
                         validate_ast, canonical_acg, json_dump, ParseError)

R=lambda s: parse_result(s.encode('utf-8'))

class ParserPositive(unittest.TestCase):
    def test_p0_golden_examples(self):
        for key in ('migration','metaphysics'):
            with self.subTest(key=key):
                acg=(ROOT/'fixtures'/(key+'.acg')).read_bytes()
                expected=json.loads((ROOT/'fixtures'/(key+'.ast.json')).read_text())
                result=parse_result(acg)
                self.assertEqual(result['syntax_status'],'PASS')
                self.assertEqual(result['structure_status'],'PASS')
                self.assertEqual(result['ast'],expected)
                self.assertEqual(parse_acg_bytes((canonical_acg(result['ast'])+'\n').encode()),expected)

    def test_all_p11_case_texts_syntax(self):
        data=json.loads((ROOT/'baseline/P1_1_Contract_Freeze/fixtures/conformance_cases.json').read_text())
        self.assertEqual(len(data['cases']),25)
        for case in data['cases']:
            if not case.get('input_text'): continue
            with self.subTest(case=case['id']):
                r=R(case['input_text'])
                if case['id']=='F18':
                    self.assertEqual(r['diagnostics'][0]['code'],'P1_SYNTAX')
                elif case['id']=='F19':
                    self.assertEqual(r['diagnostics'][0]['code'],'P1_DUPLICATE_PARAMETER')
                else:
                    self.assertEqual(r['syntax_status'],'PASS')
                    self.assertEqual(r['structure_status'],'PASS')
                    self.assertEqual(r['semantic_validation'],'NOT_EVALUATED')

    def test_unknown_concept_not_lexical_error(self):
        for s in ['Y:α:Wizard["x"]','X:α:Σ["q"]','Y:α:Event["x"]']:
            self.assertEqual(R(s)['syntax_status'],'PASS')

    def test_nested_parentheses_and_qualifier_order(self):
        s='((Y:α:Actor["x"]@T(role="occurrence"))@O(observer="b"))@T(role="recording")'
        ast=parse_acg_bytes(s.encode())
        self.assertEqual(ast['kind'],'qualified')
        self.assertEqual(ast['qualifiers'][0]['coordinate'],'T')
        self.assertEqual(ast['expression']['qualifiers'][0]['coordinate'],'O')
        self.assertEqual(ast['expression']['expression']['qualifiers'][0]['coordinate'],'T')
        self.assertEqual(parse_acg_bytes(canonical_acg(ast).encode()),ast)

    def test_nested_methods_relations_params(self):
        s='rel("α\\n\\ud83d\\ude00",audio.duck/v1(Y:α:Actor["x"];num=-1.23e+80,on=true),Y:β:Resource["r"];flag=null,s="ok")'
        ast=parse_acg_bytes(s.encode())
        self.assertEqual(ast['predicate_id'],'α\n😀')
        self.assertEqual(ast['subject']['parameters']['num'], Decimal('-1.23E+80'))
        self.assertIsNone(ast['parameters']['flag'])
        self.assertEqual(parse_acg_bytes(canonical_acg(ast).encode()),ast)

    def test_simplest_variants(self):
        for s in ['Y:α:Artifact["a"]','rel("related",Y:α:Actor["a"],Y:α:Actor["b"])',
                  'audio.duck/v1()','audio.duck/v1(;flag=false)',
                  'Y:α:Actor["x"]@T()','Y:α:Actor["x"]@T()@T()',
                  '(Y:α:Actor["x"])','\t Y : α : Actor ["x"] \r\n']:
            with self.subTest(source=s):
                a=parse_acg_bytes(s.encode())
                self.assertEqual(parse_acg_bytes(canonical_acg(a).encode()),a)

    def test_decimal_exact_and_canonical_value_semantics(self):
        for n in ['0','-0','0.000001','1.2300000000000000000000','1e400000', '-8.9e-400000',
                  '987654321098765432109876543210987654321098765432109876543210']:
            with self.subTest(n=n):
                a=parse_acg_bytes(('audio.duck/v1(;n='+n+')').encode())
                b=parse_acg_bytes(canonical_acg(a).encode())
                self.assertEqual(a,b)
                self.assertEqual(load_ast_bytes(json_dump(a,indent=None).encode()),a)
        self.assertEqual(canonical_acg(parse_acg_bytes(b'audio.duck/v1(;n=1.00)')),
                         'audio.duck/v1(;n=1)')

    def test_unicode_exact_not_normalized(self):
        a=parse_acg_bytes('Y:α:Café["é"]'.encode())
        b=parse_acg_bytes('Y:α:Cafe\u0301["e\u0301"]'.encode())
        self.assertNotEqual(a,b)
        self.assertEqual(parse_acg_bytes(canonical_acg(a).encode()),a)
        self.assertEqual(parse_acg_bytes(canonical_acg(b).encode()),b)

    def test_whitespace_and_json_strings(self):
        a=parse_acg_bytes('Y:\tα\n:Actor [ "a\\n\\tb" ]\r\n'.encode())
        self.assertEqual(a['referent_ref'],'a\n\tb')
        a=parse_acg_bytes('rel("\\u03b1",Y:α:Actor["x"],Y:α:Actor["y"])'.encode())
        self.assertEqual(a['predicate_id'],'α')

    def test_ast_json_input_is_structural_not_provenance(self):
        ast={'kind':'reference','address':{'home':'Y','layer':'α','concept_key':'Actor'},'referent_ref':'a'}
        raw=json_dump(ast).encode()
        result=parse_result(raw,input_format='json_ast')
        self.assertEqual(result['syntax_status'],'NOT_EVALUATED')
        self.assertEqual(result['structure_status'],'PASS')
        self.assertEqual(result['ast'],ast)


class ParserNegative(unittest.TestCase):
    def assert_invalid(self, source: str | bytes, expected_code='P1_SYNTAX'):
        raw=source if isinstance(source,bytes) else source.encode('utf-8')
        report=parse_result(raw)
        self.assertNotIn('ast',report)
        self.assertTrue(report['diagnostics'],source)
        self.assertEqual(report['diagnostics'][0]['code'],expected_code,source)
        return report

    def test_bad_forms(self):
        for s in ['', ' ', 'Y:α:Actor["x"] Y:α:Actor["y"]', 'Y:α:Actor["x"] # comment',
                  'Y:α:Actor[x]', 'Y:α:Actor["x"', 'Y:α:Actor"x"',
                  'Y:δ:Actor["x"]','A:α:Actor["x"]','Y:α:Actor["x"]@G()',
                  'Y:α:Actor["x"]@T(foo)', 'Y:α:Actor["x"]@T(foö=1)',
                  'Y:α:Actor["x"]@T(a=+1)','Y:α:Actor["x"]@T(a=01)',
                  'Y:α:Actor["x"]@T(a=NaN)','Y:α:Actor["x"]@T(a=Infinity)',
                  'Y:α:Actor["x"]@T(a=1.)','Y:α:Actor["x"]@T(a=.2)',
                  'Y:α:Actor["x"]@T(a=0x1)',
                  'Y:α:Actor["x"]@T(a="\\ud800")', 'Y:α:Actor["\\udc00"]',
                  'rel("",Y:α:Actor["x"],Y:α:Actor["y"])',
                  'rel("related",Y:α:Actor["x"]Y:α:Actor["y"])',
                  'rel("related",Y:α:Actor["x"],Y:α:Actor["y"];)',
                  'audio.duck/v01()','audio.duck/v0()', 'audio.duck(Y:α:Actor["x"])',
                  'audio.duck/v1(Y:α:Actor["x"],)',
                  'Y:α:Actor["x"] -> Y:α:Actor["y"]',
                  '```Y:α:Actor["x"]```',
                  'Y:α:Actor["x"]\u00a0@T()',
                  'Y:α:Actor["x"]@T(a=1,b=2,a=3)']:
            with self.subTest(s=s):
                self.assert_invalid(s, 'P1_DUPLICATE_PARAMETER' if 'a=1,b=2,a=3' in s else 'P1_SYNTAX')

    def test_utf8_and_bom(self):
        for x in [b'\xff',b'\xed\xa0\x80', b'\xef\xbb\xbfY:\xce\xb1:Actor["x"]']:
            self.assert_invalid(x,'P1_INVALID_UTF8')

    def test_max_bytes(self):
        r=self.assert_invalid(b' '+b'x'*1_048_576, 'P1_INPUT_LIMIT')
        self.assertEqual(r['diagnostics'][0]['byte_start'],0)

    def test_depth_limit(self):
        self.assert_invalid('('*65+'Y:α:Actor["x"]'+')'*65, 'P1_INPUT_LIMIT')

    def test_qualifier_limit(self):
        self.assert_invalid('Y:α:Actor["x"]' + '@T()'*65,'P1_INPUT_LIMIT')

    def test_parameter_limit(self):
        self.assert_invalid('Y:α:Actor["x"]@T(' + ','.join(f'p{i}=1' for i in range(65))+')','P1_INPUT_LIMIT')

    def test_byte_column_is_unicode_scalar(self):
        raw='Y:α:Actor["x"]\nY:α:Actor["y"]'.encode()
        r=self.assert_invalid(raw)
        d=r['diagnostics'][0]
        self.assertEqual(d['line'],2)
        self.assertEqual(d['column'],1)
        self.assertEqual(d['byte_start'],len('Y:α:Actor["x"]\n'.encode()))

    def test_json_shape_errors(self):
        base={'kind':'reference','address':{'home':'Y','layer':'α','concept_key':'Actor'},'referent_ref':'a'}
        bad=[{},[],{'kind':'bogus'},
             dict(base, unexpected=42),dict(base,referent_ref=''),
             dict(base,address={'home':'Y','layer':'wrong','concept_key':'Actor'}),
             {'kind':'qualified','expression':base,'qualifiers':[]},
             {'kind':'application','method_id':'notversioned','arguments':[],'parameters':{}},
             {'kind':'relation','predicate_id':'x','subject':base,'object':base,'parameters':{'wrong key':1}}]
        for ast in bad:
            with self.subTest(ast=ast):
                r=parse_result(json_dump(ast).encode(),input_format='json_ast')
                self.assertEqual(r['structure_status'],'FAIL')
                self.assertEqual(r['diagnostics'][0]['code'],'P1_STRUCTURAL_AST')

    def test_json_duplicate_keys(self):
        for raw in [b'{"kind":"reference","kind":"reference"}',
                    b'{"kind":"reference","address":{},"referent_ref":"r","address":{}}']:
            r=parse_result(raw,input_format='json_ast')
            self.assertEqual(r['structure_status'],'FAIL')

    def test_json_nan_and_lone_surrogate(self):
        for raw in [b'{"kind":"x","params":NaN}',
                    b'{"kind":"reference","address":{"home":"Y","layer":"\\u03b1","concept_key":"Actor"},"referent_ref":"\\ud800"}']:
            r=parse_result(raw,input_format='json_ast')
            self.assertEqual(r['structure_status'],'FAIL')

    def test_print_annotated_ast_refuses_loss(self):
        ast={'kind':'reference','address':{'home':'Y','layer':'α','concept_key':'Actor','concept_id':'c'},'referent_ref':'a'}
        validate_ast(ast)
        with self.assertRaisesRegex(ValueError,'concept_id'):
            canonical_acg(ast)
        q={'kind':'qualified','expression':{k:v for k,v in ast.items() if k!='address'}|{'address':{'home':'Y','layer':'α','concept_key':'Actor'}},
           'qualifiers':[{'coordinate':'O','parameters':{},'profile_ref':'ctx'}]}
        validate_ast(q)
        with self.assertRaisesRegex(ValueError,'profile_ref'):
            canonical_acg(q)


class Cli(unittest.TestCase):
    def test_cli_parse_examples(self):
        for name in ['migration','metaphysics']:
            p=subprocess.run([sys.executable,'-m','cube_parser','--input',str(ROOT/'fixtures'/(name+'.acg')),'--emit','acg'],
                             capture_output=True,text=True,cwd=ROOT)
            self.assertEqual(p.returncode,0,p.stderr)
            self.assertEqual(parse_acg_bytes(p.stdout.encode()),parse_acg_bytes((ROOT/'fixtures'/(name+'.acg')).read_bytes()))

    def test_cli_error_exit(self):
        p=subprocess.run([sys.executable,'-m','cube_parser','--input','-'],input='Y:α:Actor[',
                         capture_output=True,text=True,cwd=ROOT)
        self.assertEqual(p.returncode,2)
        self.assertEqual(json.loads(p.stdout)['diagnostics'][0]['code'],'P1_SYNTAX')

    def test_cli_ast_json_mode(self):
        p=subprocess.run([sys.executable,'-m','cube_parser','--input-format','json_ast','--input',str(ROOT/'fixtures/migration.ast.json'),'--emit','acg'],
                         capture_output=True,text=True,cwd=ROOT)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(parse_acg_bytes(p.stdout.encode()),parse_acg_bytes((ROOT/'fixtures/migration.acg').read_bytes()))


if __name__=='__main__':
    unittest.main()
