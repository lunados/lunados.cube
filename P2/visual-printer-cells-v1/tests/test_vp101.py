"""VP-10.1 (declared axis order, feedback mark) local tests. Fixed oracle expectations; no network, no G5."""
import copy, json, subprocess, sys, tempfile, unittest
from pathlib import Path
from xml.etree import ElementTree as ET
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE/'scripts')); sys.dont_write_bytecode = True
import run_vectors_o as RO  # noqa: E402
from vpcells import api  # noqa: E402
from vpcells.cells import render_cells, _ordered  # noqa: E402
from vpcells.common import VP09Error, NS, PROFILE, PROFILE_101, LOCALE_PINNED, LOCALE_PINNED_0101, sha_bytes  # noqa: E402

VEC = {c['id']: c for c in RO.VEC}
PINS = json.loads((HERE/'fixtures/regression_0100_digests.json').read_text())['cases']
PY = sys.executable
O1 = ['m:parser', 'm:resolver', 'm:validator', 'm:printer']


def code(fn):
    try:
        fn()
    except VP09Error as e:
        return e.code
    return None


def doc(c=None):
    c = c or VEC['O-01']
    return RO.from_plan(copy.deepcopy(c['context']), c['plan_id'], c['predicate'])[0]


class Vectors(unittest.TestCase):
    def test_o01_o10_match_oracle(self):
        by_id = {c['id']: c for c in RO.VEC}
        for c in RO.VEC:
            with self.subTest(id=c['id']):
                ok, why = RO.check(c, by_id)
                self.assertTrue(ok, why)


class ByteIdentity(unittest.TestCase):
    def test_no_axis_order_is_0100(self):
        """Q-2: without axis_order the output is 0.10.0, byte for byte (J-02 pin)."""
        rep, svg = render_cells(doc())
        self.assertEqual(sha_bytes(svg), PINS['J-02']['svg_sha256'])
        self.assertEqual(rep['profile'], PROFILE)
        for k in ('axis_order', 'feedback_cells', 'unordered_values', 'order_locale'):
            self.assertNotIn(k, rep)

    def test_pin_script_16_of_16(self):
        r = subprocess.run([PY, str(HERE/'scripts/pin_0100_digests.py')], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout+r.stderr)
        self.assertIn('16/16', r.stdout)

    def test_0100_locale_untouched(self):
        self.assertEqual(LOCALE_PINNED['de'], '73447ba2a023f9b1d1016d2ae017519ed2e46d84f5c782eb55650dd29fa3b831')
        self.assertEqual(sha_bytes((HERE/'vpcells/locales/de.json').read_bytes()), LOCALE_PINNED['de'])
        self.assertEqual(sha_bytes((HERE/'vpcells/locales/de-0101.json').read_bytes()), LOCALE_PINNED_0101['de'])


class Order(unittest.TestCase):
    def test_profile_switch(self):
        rep, svg = render_cells(doc(), axis_order=O1)
        self.assertEqual(rep['profile'], PROFILE_101)
        self.assertEqual(ET.fromstring(svg).get('data-printer-profile'), PROFILE_101)
        self.assertEqual(rep['base_profile'], 'P2-VP-AXES/0.9.2')

    def test_order_within_kind_group(self):
        """Q-5: values keep their kind group; order applies inside it; unlisted follow (Q-3)."""
        vals = [('a', None, 'X'), ('b', None, 'X'), ('c', None, 'Z'), ('d', None, 'Z')]
        self.assertEqual([v[0] for v in _ordered(vals, ['d', 'b'])], ['b', 'a', 'd', 'c'])

    def test_invalid_orders(self):
        for bad in ([], ['m:parser', 'm:parser'], ['m:parser', 3], 'm:parser', [''], {'m:parser': 1}):
            with self.subTest(bad=bad):
                self.assertEqual(code(lambda: render_cells(doc(), axis_order=bad)), 'VP10_ORDER_INVALID')

    def test_feedback_is_text_not_colour(self):
        """AO-2/AO-3: the mark is an italic text line; the cell rect keeps its colours."""
        _, plain = render_cells(doc())                       # 0.10.0: no order, no mark (R-1 has a cycle, so every order marks one)
        _, fb = render_cells(doc(), axis_order=O1)
        q = lambda t: f'{{{NS}}}{t}'  # noqa: E731
        g = next(g for g in ET.fromstring(fb).iter(q('g')) if g.get('data-vp10-feedback'))
        rects = [(r.get('fill'), r.get('stroke')) for r in g.iter(q('rect'))]
        g0 = next(g for g in ET.fromstring(plain).iter(q('g')) if g.get('data-vp09-cell') == 'm:parser|m:validator')
        self.assertEqual(rects, [(x.get('fill'), x.get('stroke')) for x in g0.iter(q('rect'))])
        self.assertEqual([t.get('font-style') for t in g.iter(q('text'))][-1], 'italic')
        self.assertFalse(any(g.get('data-vp10-feedback') for g in ET.fromstring(plain).iter(q('g'))))

    def test_first_appearance_order_declared(self):
        """Declaring the 0.10.0 order keeps rows and columns but adds the mark: d-rp lies above the diagonal there."""
        order = ['m:resolver', 'm:validator', 'm:printer', 'm:parser']
        rep0, _ = render_cells(doc())
        rep, _ = render_cells(doc(), axis_order=order)
        self.assertEqual(rep['row_values'], rep0['row_values'])
        self.assertEqual(rep['feedback_cells'], ['m:resolver|m:parser'])

    def test_hidden_cells_never_feedback(self):
        rep, _ = render_cells(doc(), axis_order=list(reversed(O1)), hide_empty='cols')
        self.assertFalse(set(rep['feedback_cells']) & set(rep['hidden_cells']))

    def test_ledger_and_nonimplication(self):
        rep, svg = render_cells(doc(), axis_order=O1)
        q = lambda t: f'{{{NS}}}{t}'  # noqa: E731
        led = json.loads(next(m for m in ET.fromstring(svg).iter(q('metadata')) if m.get('id') == 'vp10-cells-ledger').text)
        self.assertEqual(led['axis_order'], O1)
        self.assertEqual(led['feedback_cells'], ['m:parser|m:validator'])
        self.assertIn('feedback as a finding (it follows from the declared order only)', led['nonimplications'])
        self.assertIsNone(rep['order_locale'])
        rep_de, _ = render_cells(doc(), axis_order=O1, locale='de')
        self.assertEqual(rep_de['order_locale'], {'code': 'de', 'sha256': LOCALE_PINNED_0101['de']})
        self.assertEqual(rep_de['locale'], {'code': 'de', 'sha256': LOCALE_PINNED['de']})

    def test_deterministic(self):
        a = render_cells(doc(), axis_order=O1, locale='de')[1]
        self.assertEqual(a, render_cells(doc(), axis_order=O1, locale='de')[1])


class G6AndCli(unittest.TestCase):
    def test_views_check_roundtrip(self):
        src = api.source(copy.deepcopy(VEC['O-01']['context']), VEC['O-01']['plan_id'], 'references')
        res = api.views(src['source'], axis_order=O1)
        self.assertEqual(res['profile'], PROFILE_101)
        self.assertEqual(res['panels'][0]['input']['axis_order'], O1)
        self.assertEqual(api.check(json.loads(json.dumps(res)))['status'], 'PASS')
        plain = api.views(src['source'])
        self.assertNotIn('axis_order', plain['panels'][0]['input'])
        self.assertEqual(plain['profile'], PROFILE)

    def test_cli_axis_order(self):
        with tempfile.TemporaryDirectory() as t:
            inp = Path(t)/'in.json'
            inp.write_text(json.dumps(doc()))
            r = subprocess.run([PY, '-m', 'vpcells', 'print-cells', '--input', str(inp), '--out', str(Path(t)/'o'),
                                '--axis-order', ','.join(O1)], capture_output=True, cwd=HERE)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual((Path(t)/'o/render.svg').read_bytes(), render_cells(doc(), axis_order=O1)[1])
            r = subprocess.run([PY, '-m', 'vpcells', 'check-cells', '--input', str(inp), '--axis-order', 'm:parser,m:parser'],
                               capture_output=True, cwd=HERE)
            self.assertEqual(r.returncode, 2)
            self.assertEqual(json.loads(r.stderr)['code'], 'VP10_ORDER_INVALID')


if __name__ == '__main__':
    unittest.main()
