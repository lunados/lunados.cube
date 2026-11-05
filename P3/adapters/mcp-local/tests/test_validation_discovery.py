import ast
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from aiaeao_mcp_local import surface, validation_discovery as vd, p1_adapter

BASE = Path(__file__).resolve().parents[1]

class ValidationDiscoveryTests(unittest.TestCase):
    def test_advertised_contexts_match_dispatch_literals(self):
        tree = ast.parse((BASE / 'aiaeao_mcp_local/p1_adapter.py').read_text())
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == '_validator_for')
        explicit = {n.value for n in ast.walk(fn) if isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value.startswith('aiaeao.cube.binding-context/')}
        rows = vd.describe_validation_contexts()['contexts']
        self.assertEqual({r['context_format'] for r in rows}, explicit | {'aiaeao.cube.binding-context/1'})
        self.assertTrue(all(r['required_sources_present'] for r in rows))
        self.assertTrue(all(not r['runtime_load_verified'] for r in rows))

    def test_missing_modules_are_not_advertised_as_present(self):
        with tempfile.TemporaryDirectory() as d, patch.object(vd, 'ROOT', Path(d)):
            rows = vd.describe_validation_contexts()['contexts']
            self.assertTrue(all(not r['required_sources_present'] for r in rows))
            self.assertTrue(all(not r['runtime_load_verified'] for r in rows))

    def test_inventory_never_runs_validator(self):
        with patch.object(p1_adapter, '_validator_for', side_effect=AssertionError('not discovery')):
            self.assertEqual(len(vd.describe_validation_contexts()['contexts']), 11)

    def test_local_only_extension_does_not_mutate_g4(self):
        before = surface.discover_surface()
        card = surface.discover_surface_local()
        self.assertIn('validation_contexts', card['domains']['P1'])
        self.assertNotIn('validation_contexts', surface.discover_surface()['domains']['P1'])
        self.assertEqual(before, surface.discover_surface())
        card['domains']['P1']['validation_contexts']['contexts'].clear()
        self.assertEqual(len(surface.discover_surface_local()['domains']['P1']['validation_contexts']['contexts']), 11)

    def test_extension_schema(self):
        import jsonschema
        schema = json.loads((BASE / 'spec/LOCAL_VALIDATION_DISCOVERY.schema.json').read_text())
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.validate(vd.describe_validation_contexts(), schema)
        bad = vd.describe_validation_contexts()
        bad['contexts'][0]['runtime_load_verified'] = True
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(bad, schema)

if __name__ == '__main__':
    unittest.main()
