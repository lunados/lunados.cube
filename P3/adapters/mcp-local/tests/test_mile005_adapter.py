"""MILE-005 TASK-036: P1.12 (/8) through the local cube_validate adapter (G4) and VP-10 through G6 plan views."""
from __future__ import annotations
import copy
import json
import unittest
from pathlib import Path
from aiaeao_mcp_local import p1_adapter as p1, plan_views as pv, validation_discovery as vd, surface

REPO = Path(__file__).resolve().parents[4]
VEC = json.loads((REPO/'P1/coverage-instance-profile-v1/fixtures/k01_k21_materialized.json').read_text())['cases']
GOLD = json.loads((REPO/'P2/visual-printer-cells-v1/fixtures/golden_cells.json').read_text())['cases']


def codes(env):
    return sorted(d['code'] for d in env['report']['diagnostics'])


class P112Adapter(unittest.TestCase):
    def test_k_vectors_through_adapter(self):
        """P1.12-08: every K vector gives the oracle status through the MCP adapter."""
        for c in VEC:
            with self.subTest(id=c['id']):
                env = p1.validate(c['input_text'], c['input_format'], copy.deepcopy(c['context']))
                self.assertEqual(env['report']['overall_status'], c['expected_overall'])
                for x in c['required_codes']:
                    self.assertIn(x, codes(env))
                for x in c['forbidden_codes']:
                    self.assertNotIn(x, codes(env))

    def test_envelope_profiles(self):
        env = p1.validate(VEC[16]['input_text'], 'acg_text', copy.deepcopy(VEC[16]['context']))
        self.assertEqual(env['coverage_profile'], 'P1.12/coverage-instance-profile-v1')
        self.assertIs(env['population_evaluation_by_cube'], False)
        self.assertEqual(env['migration_profile'], 'P1.11/migration-methods-v1')
        for k in ('binding_context_profile', 'simulation_profile', 'comparison_profile'):
            self.assertIn(k, env)

    def test_p112_fields_in_v7_are_config_error(self):
        c = copy.deepcopy(VEC[7]['context']); c['format'] = 'aiaeao.cube.binding-context/7'
        with self.assertRaises(p1.P1AdapterFailure) as e:
            p1.validate(VEC[7]['input_text'], 'acg_text', c)
        self.assertEqual(e.exception.diagnostic['code'], 'P1_MCP_CONFIG_INVALID')

    def test_v7_envelope_unchanged(self):
        c = copy.deepcopy(VEC[20]['context']); c['format'] = 'aiaeao.cube.binding-context/7'
        for r in c['referents']:
            r.pop('instance_ref', None)
        for p in c['predicate_contracts']:
            p.pop('requires_same_instance', None)
        env = p1.validate(VEC[20]['input_text'], 'acg_text', c)
        self.assertNotIn('coverage_profile', env)

    def test_discovery_lists_v8(self):
        """Q-6: local discovery names binding-context/8 with entry profile P1.12."""
        row = vd.describe_validation_contexts()['contexts'][-1]
        self.assertEqual((row['context_format'], row['entry_profile']), ('aiaeao.cube.binding-context/8', 'P1.12/coverage-instance-profile-v1'))
        self.assertTrue(row['required_sources_present'])
        self.assertEqual(surface.discover_surface_local()['domains']['P1']['validation_contexts']['contexts'][-1], row)


class VP10PlanViews(unittest.TestCase):
    def setUp(self):
        self.g = GOLD[1]

    def test_source_views_check(self):
        src = pv.plan_source(copy.deepcopy(self.g['context']), self.g['plan_id'], 'vpcells', predicate='references')
        self.assertEqual((src['printer'], src['profile']), ('vpcells', 'P2-VP-CELLS/0.10.0'))
        res = pv.plan_views(src['source'], 'cube.cells', 'standard', hide_empty='cols', locale='de')
        self.assertEqual(res['report']['state_counts'], self.g['expected_state_counts'])
        self.assertEqual(res['report']['hidden_cols'], ['m:printer'])
        chk = pv.plan_check(json.loads(json.dumps(res)))
        self.assertEqual((chk['status'], chk['printer']), ('PASS', 'vpcells'))

    def test_predicate_required(self):
        with self.assertRaises(pv.PlanFailure) as e:
            pv.plan_source(copy.deepcopy(self.g['context']), self.g['plan_id'], 'vpcells')
        self.assertEqual(e.exception.diagnostic['code'], 'VP10_PREDICATE_INVALID')

    def test_wrong_source_and_options(self):
        axes = pv.plan_source(self._v6(), 'mp-dsm', 'vpaxes', profile='P2-VP-AXES/0.9.2')
        with self.assertRaises(pv.PlanFailure) as e:
            pv.plan_views(axes['source'], 'cube.cells', 'standard')
        self.assertEqual(e.exception.diagnostic['code'], 'P3_PLAN_ARGUMENT_INVALID')
        src = pv.plan_source(copy.deepcopy(self.g['context']), self.g['plan_id'], 'vpcells', predicate='references')
        with self.assertRaises(pv.PlanFailure) as e:
            pv.plan_views(src['source'], 'cube.cells', 'standard', partition='x')
        self.assertEqual(e.exception.diagnostic['code'], 'P3_PLAN_ARGUMENT_INVALID')
        with self.assertRaises(pv.PlanFailure) as e:
            pv.plan_views(src['source'], 'cube.cells', 'standard', rows='T', cols='Y:referent')
        self.assertEqual(e.exception.diagnostic['code'], 'VP10_PAIR_INVALID')

    def _v6(self):
        c = copy.deepcopy(self.g['context']); c['format'] = 'aiaeao.cube.binding-context/5'; c.pop('coverage_declarations')
        return c

    def test_capabilities(self):
        cap = pv.capabilities()
        self.assertEqual(cap['views']['cube.cells'], 'vpcells')
        self.assertEqual(cap['printers']['vpcells']['profiles'], ['P2-VP-CELLS/0.10.0'])


if __name__ == '__main__':
    unittest.main()
