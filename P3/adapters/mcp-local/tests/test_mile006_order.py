"""MILE-006 TASK-040: VP-10.1 axis_order through G6 cube_plan_views / cube_plan_check (in memory, byte-identical to the CLI)."""
from __future__ import annotations
import copy
import inspect
import json
import unittest
from pathlib import Path
from aiaeao_mcp_local import plan_views as pv, server
from aiaeao_mcp_local.plan_views import PlanFailure
from vpcells.source import project  # noqa: E402  (on the path through plan_views)

REPO = Path(__file__).resolve().parents[4]
VEC = {c['id']: c for c in json.loads((REPO/'P2/visual-printer-cells-v1/fixtures/o01_o10_materialized.json').read_text())['cases']}
O1 = ['m:parser', 'm:resolver', 'm:validator', 'm:printer']


def src(cid='O-01'):
    c = VEC[cid]
    return pv.plan_source(copy.deepcopy(c['context']), c['plan_id'], 'vpcells', predicate='references')['source']


class AxisOrderG6(unittest.TestCase):
    def test_o10_views_and_check(self):
        res = pv.plan_views(src(), 'cube.cells', 'standard', axis_order=O1)
        self.assertEqual(res['profile'], 'P2-VP-CELLS/0.10.1')
        self.assertEqual(res['report']['feedback_cells'], ['m:parser|m:validator'])
        self.assertEqual(pv.plan_check(json.loads(json.dumps(res)))['status'], 'PASS')

    def test_without_order_unchanged(self):
        res = pv.plan_views(src(), 'cube.cells', 'standard')
        self.assertEqual(res['profile'], 'P2-VP-CELLS/0.10.0')
        self.assertNotIn('axis_order', res['panels'][0]['input'])

    def test_error_passes_through(self):
        with self.assertRaises(PlanFailure) as e:
            pv.plan_views(src(), 'cube.cells', 'standard', axis_order=['m:parser', 'm:parser'])
        self.assertEqual(e.exception.diagnostic['code'], 'VP10_ORDER_INVALID')
        self.assertEqual(e.exception.diagnostic['printer'], 'vpcells')

    def test_axis_order_only_for_cells(self):
        c = VEC['O-01']
        axes = pv.plan_source(project(c['context']), c['plan_id'], 'vpaxes', profile='P2-VP-AXES/0.9.2')['source']
        pv.plan_views(axes, 'cube.axes', 'standard', rows='Y:referent', cols='Y:referent')          # the source itself is fine
        with self.assertRaises(PlanFailure) as e:
            pv.plan_views(axes, 'cube.axes', 'standard', rows='Y:referent', cols='Y:referent', axis_order=O1)
        self.assertEqual(e.exception.diagnostic['code'], 'P3_PLAN_ARGUMENT_INVALID')
        self.assertIn('unexpected: axis_order', e.exception.diagnostic['message'])

    def test_tool_signature(self):
        p = inspect.signature(server.cube_plan_views).parameters['axis_order']
        self.assertIsNone(p.default)


if __name__ == '__main__':
    unittest.main()
