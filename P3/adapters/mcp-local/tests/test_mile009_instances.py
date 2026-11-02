"""MILE-009 TASK-056: VP-11 instance view through G6 (cube_plan_source, cube_plan_views, cube_plan_check), byte-identical to the CLI."""
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
INST = REPO/'P2/visual-printer-instances-v1'
VEC = {c['id']: c for c in json.loads((INST/'fixtures/i01_i34_materialized.json').read_text())['cases']}
ORACLE = {c['id']: c for c in json.loads((INST/'oracles/independent_i01_i34.json').read_text())['cases']}
from vpinstances.view import render_instances  # noqa: E402  (on the path through plan_views)
from vpinstances.trace import from_trace  # noqa: E402


def src(cid):
    c = copy.deepcopy(VEC[cid])
    return pv.plan_source(c['context'], None, 'vpinstances', statements=c['trace'], records=c['records'])


def code(fn, *a, **k):
    try:
        fn(*a, **k)
    except PlanFailure as e:
        return e.diagnostic['code'], e.diagnostic.get('printer'), e.diagnostic.get('input_profile')
    return None


class InstancesG6(unittest.TestCase):
    def test_all_vectors_equal_cli_render(self):
        """G6 = CLI: every vector through G6 gives the bytes of the printer; errors pass through with printer and profile."""
        for cid, c in VEC.items():
            with self.subTest(id=cid):
                e = ORACLE[cid]
                if e['status'] == 'error':
                    self.assertEqual(code(src, cid), (e['code'], 'vpinstances', 'P2-VP-INSTANCES/0.12.0'))
                    continue
                s = src(cid)
                self.assertEqual((s['printer'], s['profile']), ('vpinstances', 'P2-VP-INSTANCES/0.12.0'))
                loc = None if c['locale'] == 'en' else c['locale']
                res = pv.plan_views(json.loads(json.dumps(s['source'])), 'cube.instances', 'standard', locale=loc)
                cc = copy.deepcopy(c)
                _, svg = render_instances(from_trace(cc['context'], cc['trace'], cc['records']), loc)
                self.assertEqual(res['panels'][0]['svg'].encode('utf-8'), svg)
                chk = pv.plan_check(json.loads(json.dumps(res)))
                self.assertEqual((chk['status'], chk['printer'], chk['violation_marks']), ('PASS', 'vpinstances', e['violation_marks']))

    def test_byte_identical_to_cli_files(self):
        c = VEC['I-22']
        res = pv.plan_views(src('I-22')['source'], 'cube.instances', 'standard', locale='de')
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            (t/'ctx.json').write_text(json.dumps(c['context'])); (t/'trace.json').write_text(json.dumps(c['trace']))
            recs = []
            for n, r in enumerate(c['records']):
                (t/f'r{n}.json').write_text(json.dumps(r)); recs += ['--record', str(t/f'r{n}.json')]
            for args in (['from-trace', '--context', str(t/'ctx.json'), '--trace', str(t/'trace.json'), *recs, '--out', str(t/'in.json')],
                         ['print-instances', '--input', str(t/'in.json'), '--out', str(t/'o'), '--locale', 'de']):
                r = subprocess.run([sys.executable, '-m', 'vpinstances', *args], capture_output=True, cwd=INST)
                self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual((t/'o/render.svg').read_text('utf-8'), res['panels'][0]['svg'])
            self.assertEqual(json.loads((t/'in.json').read_text()), src('I-22')['source'])

    def test_arguments(self):
        c = VEC['I-01']
        self.assertEqual(code(pv.plan_source, c['context'], 'mp-x', 'vpinstances', statements=c['trace'])[0], 'P3_PLAN_ARGUMENT_INVALID')
        self.assertEqual(code(pv.plan_source, c['context'], None, 'vpinstances')[0], 'P3_PLAN_ARGUMENT_INVALID')
        self.assertEqual(code(pv.plan_source, c['context'], None, 'vpinstances', statements=c['trace'], predicate='x')[0], 'P3_PLAN_ARGUMENT_INVALID')
        self.assertEqual(code(pv.plan_source, c['context'], None, 'vpcells', statements=c['trace'], records=[])[0], 'P3_PLAN_ARGUMENT_INVALID')
        s = src('I-01')['source']
        self.assertEqual(code(pv.plan_views, s, 'cube.cells', 'standard')[0], 'P3_PLAN_ARGUMENT_INVALID')
        self.assertEqual(code(pv.plan_views, s, 'cube.instances', 'standard', rows='Y:referent')[0], 'P3_PLAN_ARGUMENT_INVALID')
        self.assertEqual(code(pv.plan_views, s, 'cube.instances', 'standard', locale='fr')[0], 'VP11_LOCALE_INVALID')

    def test_tool_signature_and_discovery(self):
        params = inspect.signature(server.cube_plan_source).parameters
        self.assertIsNone(params['records'].default)
        self.assertIn('vpinstances', str(params['printer'].annotation))
        self.assertIn('cube.instances', str(inspect.signature(server.cube_plan_views).parameters['view'].annotation))
        p2 = surface.discover_surface_local()['domains']['P2']['plan_views']
        self.assertEqual(p2['views']['cube.instances'], 'vpinstances')
        self.assertEqual(p2['printers']['vpinstances']['profiles'], ['P2-VP-INSTANCES/0.12.0'])
        self.assertFalse(p2['remote_available'])


if __name__ == '__main__':
    unittest.main()
