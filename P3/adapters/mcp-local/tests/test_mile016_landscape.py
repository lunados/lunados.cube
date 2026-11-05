"""TASK-080 (MILE-016, R10): VP-12 cube.landscape through the G6 plan tools, byte-identical to the VP-12 API."""
import json
import unittest
from pathlib import Path

from aiaeao_mcp_local import plan_views as pv

REPO = Path(__file__).resolve().parents[4]
LAND = REPO/'P2/visual-printer-landscape-v1'
CASES = {c['id']: c for c in json.loads((LAND/'fixtures/l01_l14_materialized.json').read_text('utf-8'))['cases']}
from vplandscape import api as vp12  # noqa: E402  (on the path through plan_views)


def code(fn, *a, **k):
    try:
        fn(*a, **k)
    except pv.PlanFailure as e:
        return e.diagnostic['code'], e.diagnostic.get('printer')
    return None


class Landscape(unittest.TestCase):
    def setUp(self):
        self.c = CASES['L-01']

    def test_source_views_check_parity(self):
        src = pv.plan_source(self.c['context'], 'pm-ls', 'vplandscape', layers=self.c['layers'], steps='current,mvp,beta')
        self.assertEqual((src['printer'], src['profile']), ('vplandscape', 'P2-VP-LANDSCAPE/0.12.0'))
        local = vp12.source(self.c['context'], 'pm-ls', self.c['layers'], None, ['current', 'mvp', 'beta'])
        self.assertEqual(pv.canonical(src), pv.canonical(local))
        res = pv.plan_views(src['source'], 'cube.landscape', 'detail', locale='de')
        self.assertEqual(pv.canonical(res), pv.canonical(vp12.views(local['source'], 'detail', 'de')))
        self.assertEqual((res['printer'], res['view'], len(res['panels'])), ('vplandscape', 'cube.landscape', 1))
        self.assertIn('Y × Z über T · abgeleitet · Morphologie 01.3', res['panels'][0]['svg'])
        chk = pv.plan_check(res)
        self.assertEqual((chk['status'], chk['printer']), ('PASS', 'vplandscape'))

    def test_errors(self):
        self.assertEqual(code(pv.plan_source, self.c['context'], 'pm-ls', 'vplandscape', steps='current,gamma'),
                         ('VP12_STEP_UNKNOWN', 'vplandscape'))
        seven = dict(self.c['layers'], layer_order=self.c['layers']['layer_order']+['edge', 'cloud', 'vendor'])
        wide = pv.plan_source(self.c['context'], 'pm-ls', 'vplandscape', layers=seven)['source']   # the budget is a display limit
        self.assertEqual(code(pv.plan_views, wide, 'cube.landscape', 'detail'), ('VP12_BUDGET_EXCEEDED', 'vplandscape'))
        self.assertEqual(code(pv.plan_source, self.c['context'], 'pm-ls', 'vplandscape', steps=['current'])[0], 'P3_PLAN_ARGUMENT_INVALID')
        self.assertEqual(code(pv.plan_source, self.c['context'], 'pm-ls', 'vplandscape', predicate='x')[0], 'P3_PLAN_ARGUMENT_INVALID')
        self.assertEqual(code(pv.plan_source, self.c['context'], 'pm-nope', 'vplandscape'), ('VP07_ADAPTER_INPUT', 'vplandscape'))
        src = pv.plan_source(self.c['context'], 'pm-ls', 'vplandscape')['source']
        self.assertEqual(code(pv.plan_views, src, 'cube.landscape', 'detail', rows='X')[0], 'P3_PLAN_ARGUMENT_INVALID')
        self.assertEqual(code(pv.plan_views, src, 'cube.flow', 'detail', partition='subject')[0], 'P3_PLAN_ARGUMENT_INVALID')
        mig = pv.plan_source(self.c['context'], 'pm-ls', 'vpmigration', profile='P2-VP-MIGRATION/0.7.8')['source']
        self.assertEqual(code(pv.plan_views, mig, 'cube.landscape', 'detail')[0], 'P3_PLAN_ARGUMENT_INVALID')

    def test_capabilities(self):
        cap = pv.capabilities()
        self.assertEqual(cap['views']['cube.landscape'], 'vplandscape')
        self.assertEqual(cap['printers']['vplandscape']['profiles'], ['P2-VP-LANDSCAPE/0.12.0', 'P2-VP-LANDSCAPE/0.12.1'])
        self.assertEqual(cap['printers']['vplandscape']['budget']['max_columns'], 6)

    def test_profile_0121(self):
        src = pv.plan_source(self.c['context'], 'pm-ls', 'vplandscape', layers=self.c['layers'], profile='P2-VP-LANDSCAPE/0.12.1')
        res = pv.plan_views(src['source'], 'cube.landscape', 'detail')
        self.assertIn('data-anchor-id="skeleton-shell.section"', res['panels'][0]['svg'])
        self.assertEqual(pv.plan_check(res)['status'], 'PASS')


if __name__ == '__main__':
    unittest.main()
