"""P1.6 Charge 1 schema-preflight. Does NOT test a P1.6 runtime validator."""
import copy
import json
import pathlib
import unittest
from jsonschema import Draft202012Validator

BASE = pathlib.Path(__file__).resolve().parents[1]
def load(name):
    return json.loads((BASE / name).read_text(encoding='utf-8'))

class ContractSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = load('context-v2.schema.json')
        cls.profile = load('INSTANTIATION_PROFILES.schema.json')
        cls.vocab = load('instantiation_reference_v1.json')
        cls.example = load('fixtures/valid_conclusion_context_v2.json')
        cls.validator = Draft202012Validator(cls.context)

    def test_schemas_are_valid(self):
        Draft202012Validator.check_schema(self.context)
        Draft202012Validator.check_schema(self.profile)

    def test_complete_fixture_is_schema_valid(self):
        self.assertEqual([], list(self.validator.iter_errors(self.example)))

    def test_old_context_format_rejected_by_v2(self):
        wrong = copy.deepcopy(self.example)
        wrong['format'] = 'aiaeao.cube.binding-context/1'
        self.assertFalse(self.validator.is_valid(wrong))

    def test_root_unknown_key_rejected(self):
        wrong = copy.deepcopy(self.example)
        wrong['surprise'] = 1
        self.assertFalse(self.validator.is_valid(wrong))

    def test_referent_unknown_key_rejected(self):
        wrong = copy.deepcopy(self.example)
        wrong['referents'][-1]['unknown_key'] = 1
        self.assertFalse(self.validator.is_valid(wrong))

    def test_invalid_slot_scalar_shape_rejected(self):
        wrong = copy.deepcopy(self.example)
        wrong['referents'][-1]['slots']['basis_refs'] = 3
        self.assertFalse(self.validator.is_valid(wrong))

    def test_unknown_descriptor_key_rejected(self):
        wrong = copy.deepcopy(self.example)
        wrong['instantiation_profiles'][0]['slots'][0]['permit_anything'] = True
        self.assertFalse(self.validator.is_valid(wrong))

    def test_profile_empty_enum_rejected(self):
        wrong = copy.deepcopy(self.example)
        sl = next(s for s in wrong['instantiation_profiles'][0]['slots'] if s['kind'] == 'enum')
        sl['values'] = []
        self.assertFalse(self.validator.is_valid(wrong))

    def test_ten_endpoints_and_five_specific_scopes(self):
        endpoints = self.vocab['endpoints']
        self.assertEqual(10, len(endpoints))
        self.assertEqual(5, len({e['pair_scope_concept_id'] for e in endpoints}))
        self.assertEqual(10, len({e['concept_id'] for e in endpoints}))
        for e in endpoints:
            sl = e['slots'][0]
            self.assertEqual('pair_scope_ref', sl['name'])
            self.assertTrue(sl['required'])
            self.assertEqual([e['pair_scope_concept_id']], sl['concept_ids'])

    def test_reference_types_include_string_literals(self):
        s = {e['concept_id']:e for e in self.vocab['endpoints']}
        aut = s['X:endpoint:authority']
        self.assertEqual('string',next(x['kind'] for x in aut['slots'] if x['name']=='action_kind'))

    def test_nonpromotion_marker_remains_in_spec(self):
        body = (BASE/'P1_6_ACCEPTANCE_SPEC.md').read_text(encoding='utf-8')
        self.assertIn('P1.6-10',body)
        self.assertIn('NOT_EVALUATED',body)
        self.assertIn('G5 Remote',body)

if __name__ == '__main__':
    unittest.main()
