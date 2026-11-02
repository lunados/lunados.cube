"""TASK-065: binding-context/10 through local G4 and discovery."""
import copy
import json
import unittest
from pathlib import Path

from aiaeao_mcp_local import p1_adapter as p1, validation_discovery as discovery

REPO = Path(__file__).resolve().parents[4]
HERE = REPO / 'P1/relation-origin-profile-v1'
VEC = json.loads((HERE / 'fixtures/ho01_ho12_materialized.json').read_text())['cases']
ORACLE = {c['id']: c for c in json.loads((HERE / 'oracles/independent_ho01_ho12.json').read_text())['cases']}


class P114Adapter(unittest.TestCase):
    def test_all_vectors(self):
        for case in VEC:
            with self.subTest(id=case['id']):
                env = p1.validate(case['input_text'], case['input_format'], copy.deepcopy(case['context']))
                o = ORACLE[case['id']]
                report = env['report']
                self.assertEqual(report['overall_status'], o['expected_overall'])
                codes = [d['code'] for d in report['diagnostics']]
                self.assertTrue(set(o['required_codes']) <= set(codes))
                self.assertFalse(set(o['forbidden_codes']) & set(codes))
                if case['context']['format'].endswith('/10'):
                    self.assertEqual(env['relation_origin_profile'], 'P1.14/relation-origin-profile-v1')
                    self.assertIs(env['origin_verification_by_cube'], False)
                    self.assertEqual(env['control_flow_profile'], 'P1.13/control-flow-profile-v1')
                else:
                    self.assertNotIn('relation_origin_profile', env)

    def test_config_errors(self):
        c = copy.deepcopy(VEC[1])
        c['context']['origin_bases'][0]['statement_ids'].append('s-1')
        with self.assertRaises(p1.P1AdapterFailure) as error:
            p1.validate(c['input_text'], c['input_format'], c['context'])
        self.assertEqual(error.exception.diagnostic['code'], 'P1_MCP_CONFIG_INVALID')

    def test_discovery(self):
        rows = discovery.describe_validation_contexts()['contexts']
        self.assertEqual(len(rows), 10)
        row = rows[-1]
        self.assertEqual((row['context_format'], row['entry_profile']),
                         ('aiaeao.cube.binding-context/10', 'P1.14/relation-origin-profile-v1'))
        self.assertEqual(set(row['diagnostic_codes']),
                         {'P1_ORIGIN_UNDECLARED', 'P1_ORIGIN_BASIS_MISSING', 'P1_ORIGIN_INVALID'})
        self.assertTrue(row['required_sources_present'])


if __name__ == '__main__':
    unittest.main()
