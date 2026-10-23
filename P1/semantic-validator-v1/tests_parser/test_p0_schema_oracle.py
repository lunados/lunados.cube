"""Optional independent oracle based on the published P0 JSON Schema 2020-12.
Requires `pip install jsonschema`. Skips cleanly if dependency is absent.
"""
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from cube_parser import parse_acg_bytes

try:
    import jsonschema
except ImportError:
    jsonschema=None

@unittest.skipUnless(jsonschema is not None, 'Install jsonschema for independent P0 AST oracle')
class P0SchemaOracle(unittest.TestCase):
    def test_golden_and_p11_valid_syntax_ast_schema(self):
        schema=json.loads((ROOT/'baseline/P0_reference/ast.schema.json').read_text())
        oracle=jsonschema.Draft202012Validator(schema)
        fixture=json.loads((ROOT/'baseline/P1_1_Contract_Freeze/fixtures/conformance_cases.json').read_text())
        sources=[(ROOT/'fixtures/migration.acg').read_bytes(), (ROOT/'fixtures/metaphysics.acg').read_bytes()]
        sources += [item['input_text'].encode() for item in fixture['cases'] if item.get('input_text') and item['id'] not in ('F18','F19')]
        self.assertEqual(len(sources),23)
        for i,raw in enumerate(sources):
            with self.subTest(i=i):
                self.assertEqual(list(oracle.iter_errors(parse_acg_bytes(raw))),[])

if __name__=='__main__':
    unittest.main()
