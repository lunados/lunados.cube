"""MILE-007 TASK-046: VP-10 0.11.0 statement sets through G6 (cube_plan_source, cube_plan_views, cube_plan_check), byte-identical to the CLI."""
from __future__ import annotations
import copy
import inspect
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from aiaeao_mcp_local import plan_views as pv, server, surface
from aiaeao_mcp_local.plan_views import PlanFailure

REPO = Path(__file__).resolve().parents[4]
CELLS = REPO/'P2/visual-printer-cells-v1'
VEC = {c['id']: c for c in json.loads((CELLS/'fixtures/s01_s16_materialized.json').read_text())['cases']}


def src(cid='S-04'):
    c = copy.deepcopy(VEC[cid])
    return pv.plan_source(c['context'], None, 'vpcells', predicate=c['predicate'], statements=c['statements'], projection=c['projection'])['source']


class StatementSetsG6(unittest.TestCase):
    def test_views_and_check(self):
        res = pv.plan_views(src(), 'cube.cells', 'standard')
        self.assertEqual(res['profile'], 'P2-VP-CELLS/0.11.0')
        self.assertEqual(res['report']['aggregation']['loss']['merged'], 2)
        self.assertEqual(pv.plan_check(json.loads(json.dumps(res)))['status'], 'PASS')

    def test_plain_set_with_order(self):
        res = pv.plan_views(src('S-03'), 'cube.cells', 'standard', axis_order=VEC['S-03']['axis_order'])
        self.assertEqual(res['report']['feedback_cells'], ['m:parser|m:validator'])

    def test_byte_identical_to_cli(self):
        c = VEC['S-04']
        res = pv.plan_views(src(), 'cube.cells', 'standard')
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            for n in ('context', 'statements', 'projection'):
                (t/f'{n}.json').write_text(json.dumps(c[n]))
            for args in (['from-statements', '--context', str(t/'context.json'), '--statements', str(t/'statements.json'),
                          '--projection', str(t/'projection.json'), '--out', str(t/'in.json')],
                         ['print-cells', '--input', str(t/'in.json'), '--out', str(t/'o')]):
                r = subprocess.run([sys.executable, '-m', 'vpcells', *args], capture_output=True, cwd=CELLS)
                self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual((t/'o/render.svg').read_text('utf-8'), res['panels'][0]['svg'])
            self.assertEqual(json.loads((t/'in.json').read_text()), src())

    def test_errors_pass_through(self):
        c = VEC['S-12']
        with self.assertRaises(PlanFailure) as e:
            pv.plan_source(c['context'], None, 'vpcells', statements=c['statements'], projection=c['projection'])
        self.assertEqual((e.exception.diagnostic['code'], e.exception.diagnostic['input_profile']), ('VP10_PROJECTION_INVALID', 'P2-VP-CELLS/0.11.0'))
        with self.assertRaises(PlanFailure) as e:
            pv.plan_source(c['context'], 'mp-x', 'vpcells', statements=c['statements'])
        self.assertEqual(e.exception.diagnostic['code'], 'VP10_ADAPTER_INPUT')

    def test_matrix_input_only_for_cells(self):
        with self.assertRaises(PlanFailure) as e:
            pv.plan_views(src(), 'cube.axes', 'standard', rows='Y:referent', cols='Y:referent')
        self.assertEqual(e.exception.diagnostic['code'], 'P3_PLAN_ARGUMENT_INVALID')

    def test_tool_signature_and_discovery(self):
        params = inspect.signature(server.cube_plan_source).parameters
        self.assertIsNone(params['statements'].default)
        self.assertIsNone(params['projection'].default)
        cells = surface.discover_surface_local()['domains']['P2']['plan_views']['printers']['vpcells']
        self.assertEqual(cells['profiles'], ['P2-VP-CELLS/0.10.0'])          # MILE-005 entry unchanged
        self.assertEqual(cells['opt_in_profiles']['P2-VP-CELLS/0.11.0'], 'statements instead of plan_id')


if __name__ == '__main__':
    unittest.main()
