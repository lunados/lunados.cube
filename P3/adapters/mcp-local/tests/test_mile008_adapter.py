"""MILE-008 TASK-052: P1.13 (binding-context/9) through the local cube_validate adapter (G4) and local discovery."""
from __future__ import annotations
import copy
import json
import unittest
from pathlib import Path
from aiaeao_mcp_local import p1_adapter as p1, validation_discovery as vd, surface

REPO = Path(__file__).resolve().parents[4]
VEC = json.loads((REPO/'P1/control-flow-profile-v1/fixtures/kf01_kf09_materialized.json').read_text())['cases']
ORACLE = {c['id']: c for c in json.loads((REPO/'P1/control-flow-profile-v1/oracles/independent_kf01_kf09.json').read_text())['cases']}


def codes(env):
    return [d['code'] for d in env['report']['diagnostics']]


class P113Adapter(unittest.TestCase):
    def test_kf_vectors_through_adapter(self):
        """P1.13-08: every KF vector gives the oracle status through the MCP adapter."""
        for c in VEC:
            with self.subTest(id=c['id']):
                o = ORACLE[c['id']]
                env = p1.validate(c['input_text'], c.get('input_format', 'acg_text'), copy.deepcopy(c['context']))
                self.assertEqual(env['report']['overall_status'], o['expected_overall'])
                for x in o['required_codes']:
                    self.assertIn(x, codes(env))
                for x in o['forbidden_codes']:
                    self.assertNotIn(x, codes(env))

    def test_envelope_profiles(self):
        c = VEC[0]
        env = p1.validate(c['input_text'], 'acg_text', copy.deepcopy(c['context']))
        self.assertEqual(env['control_flow_profile'], 'P1.13/control-flow-profile-v1')
        self.assertIs(env['trace_evaluation_by_cube'], False)
        self.assertIs(env['condition_evaluation_by_cube'], False)
        self.assertEqual(env['coverage_profile'], 'P1.12/coverage-instance-profile-v1')
        for k in ('binding_context_profile', 'simulation_profile', 'comparison_profile', 'migration_profile'):
            self.assertIn(k, env)

    def test_v8_envelope_unchanged(self):
        c = next(x for x in VEC if x['id'] == 'KF-08')
        env = p1.validate(c['input_text'], 'acg_text', copy.deepcopy(c['context']))
        self.assertNotIn('control_flow_profile', env)
        self.assertEqual(env['coverage_profile'], 'P1.12/coverage-instance-profile-v1')

    def test_p113_fields_in_v8_are_config_error(self):
        c = copy.deepcopy(VEC[0]['context']); c['format'] = 'aiaeao.cube.binding-context/8'
        with self.assertRaises(p1.P1AdapterFailure) as e:
            p1.validate(VEC[0]['input_text'], 'acg_text', c)
        self.assertEqual(e.exception.diagnostic['code'], 'P1_MCP_CONFIG_INVALID')

    def test_malformed_v9_is_config_error(self):
        c = copy.deepcopy(VEC[0]['context']); c['control_flow']['gateways'][0]['outgoing'][0]['order'] = 0
        with self.assertRaises(p1.P1AdapterFailure) as e:
            p1.validate(VEC[0]['input_text'], 'acg_text', c)
        self.assertEqual(e.exception.diagnostic['code'], 'P1_MCP_CONFIG_INVALID')

    def test_discovery_lists_v9(self):
        row = vd.describe_validation_contexts()['contexts'][-1]
        self.assertEqual((row['context_format'], row['entry_profile']), ('aiaeao.cube.binding-context/9', 'P1.13/control-flow-profile-v1'))
        self.assertTrue(row['required_sources_present'])
        self.assertIs(row['runtime_load_verified'], False)
        self.assertEqual(surface.discover_surface_local()['domains']['P1']['validation_contexts']['contexts'][-1], row)


if __name__ == '__main__':
    unittest.main()
