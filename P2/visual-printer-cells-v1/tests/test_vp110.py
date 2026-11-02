"""VP-10 0.11.0 (statement sets without a plan, aggregation records) local tests. Fixed oracle expectations; no network, no G5."""
import copy, json, subprocess, sys, tempfile, unittest
from pathlib import Path
from xml.etree import ElementTree as ET
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE/'scripts')); sys.dont_write_bytecode = True
import run_vectors_s as RS  # noqa: E402
from vpcells import api  # noqa: E402
from vpcells.statements import from_statements  # noqa: E402
from vpcells.cells import render_cells  # noqa: E402
from vpcells.common import (VP09Error, NS, PROFILE_110, LOCALE_PINNED, LOCALE_PINNED_0101, LOCALE_PINNED_0110, sha_bytes)  # noqa: E402

VEC = {c['id']: c for c in RS.VEC}
PY = sys.executable
q = lambda t: f'{{{NS}}}{t}'  # noqa: E731


def code(fn):
    try:
        fn()
    except VP09Error as e:
        return e.code
    return None


def doc(cid='S-01', **kw):
    c = copy.deepcopy(VEC[cid])
    c.update(kw)
    return from_statements(c['context'], c['statements'], c['predicate'], c['projection'])


class Vectors(unittest.TestCase):
    def test_s01_s16_match_oracle(self):
        for c in RS.VEC:
            with self.subTest(id=c['id']):
                ok, why = RS.check(c, VEC)
                self.assertTrue(ok, why)


class Frozen(unittest.TestCase):
    def test_pins_0100_and_0101(self):
        for script, want in (('pin_0100_digests.py', '16/16'), ('pin_0101_digests.py', '9/9')):
            r = subprocess.run([PY, str(HERE/'scripts'/script)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout+r.stderr)
            self.assertIn(want, r.stdout)

    def test_locale_files(self):
        for name, pin in (('de.json', LOCALE_PINNED['de']), ('de-0101.json', LOCALE_PINNED_0101['de']), ('de-0110.json', LOCALE_PINNED_0110['de'])):
            self.assertEqual(sha_bytes((HERE/'vpcells/locales'/name).read_bytes()), pin)
        self.assertEqual(LOCALE_PINNED['de'], '73447ba2a023f9b1d1016d2ae017519ed2e46d84f5c782eb55650dd29fa3b831')


class Input(unittest.TestCase):
    def test_profile_and_shape(self):
        d = doc()
        self.assertEqual((d['profile'], d['home'], d['predicate']), (PROFILE_110, 'Y', 'dependsOn'))
        self.assertEqual([a['id'] for a in d['axis']], ['m:parser', 'm:resolver', 'm:validator', 'm:printer'])
        self.assertEqual(code(lambda: render_cells(dict(d, profile='P2-VP-CELLS/0.10.0'))), 'VP10_SOURCE_INVALID')

    def test_predicate_required_for_plain_sets(self):
        self.assertEqual(code(lambda: doc(predicate=None)), 'VP10_PREDICATE_INVALID')
        self.assertEqual(code(lambda: doc(predicate='nope')), 'VP10_STATEMENT_PREDICATE_INVALID')

    def test_context_must_be_v8(self):
        c = copy.deepcopy(VEC['S-01']); c['context']['format'] = 'aiaeao.cube.binding-context/7'
        self.assertEqual(code(lambda: from_statements(c['context'], c['statements'], 'dependsOn')), 'VP10_ADAPTER_INPUT')

    def test_projection_view_predicate(self):
        """DR-7: an aggregation view shows its derived_predicate; another predicate is refused."""
        self.assertEqual(doc('S-04')['predicate'], 'uses.derived')
        self.assertEqual(code(lambda: doc('S-04', predicate='uses')), 'VP10_STATEMENT_PREDICATE_INVALID')

    def test_projection_record_checks(self):
        """PR-3, PR-6: format, library_ref, method and input hash are checked; nothing is recomputed."""
        base = VEC['S-04']['projection']
        for mutate in (lambda r: r.update(format='x'), lambda r: r['library_ref'].update(sha256='abc'),
                       lambda r: r['result'].update(method_id='other/v1'), lambda r: r['result'].update(input_set_sha256='0'*64),
                       lambda r: r['result'].update(status='ERROR')):
            r = copy.deepcopy(base); mutate(r)
            with self.subTest(r=json.dumps(r)[:60]):
                self.assertEqual(code(lambda: doc('S-04', projection=r)), 'VP10_PROJECTION_INVALID')

    def test_aggregation_is_read_not_recomputed(self):
        """A record whose result lists a third source is drawn as given (the Cube does not recompute, Q-10)."""
        r = copy.deepcopy(VEC['S-04']['projection'])
        r['result']['statements'][0]['derived_from'] = ['s-1', 's-2', 's-3']
        rep, svg = render_cells(doc('S-04', projection=r))
        cells = {g.get('data-vp10-cell'): [t.text for t in g.iter(q('text'))] for g in ET.fromstring(svg).iter(q('g')) if g.get('data-vp10-cell')}
        self.assertEqual(cells['c4:shop/api|c4:shop/db'], ['d-1 · uses.derived · derived · 3 sources'])


class Drawing(unittest.TestCase):
    def test_states_differ_without_colour_and_no_active_content(self):
        rep, _ = render_cells(doc('S-02'))
        self.assertIn('STATES_DIFFER_WITHOUT_COLOUR', rep['invariants_passed'])
        self.assertIn('NO_ACTIVE_SVG_CONTENT_NO_PATTERN', rep['invariants_passed'])
        self.assertIn('EMBEDDED_LEDGER_MATCH', rep['invariants_passed'])

    def test_convention_in_legend_and_report(self):
        rep, svg = render_cells(doc())
        texts = [t.text for t in ET.fromstring(svg).iter(q('text'))]
        self.assertTrue(any(t.startswith('row = subject, column = object') for t in texts))
        self.assertIn('Rows are subjects, columns are objects; there is no transposed reading (D-6).', rep['notices'])

    def test_hide_empty(self):
        rep, _ = render_cells(doc('S-04'), hide_empty='rows')
        self.assertEqual(rep['hidden_rows'], ['c4:shop/db'])
        self.assertEqual(rep['cells']['c4:shop/db|c4:shop/api'], {'state': 'hidden'})

    def test_labels_in_ledger_only(self):
        _, svg = render_cells(doc('S-04'))
        root = ET.fromstring(svg)
        led = json.loads(next(m for m in root.iter(q('metadata')) if m.get('id') == 'vp10-cells-ledger').text)
        self.assertEqual(led['entries'][0]['label'], 'Writes orders to')
        self.assertNotIn('Writes orders to', [t.text for t in root.iter(q('text'))])

    def test_order_options(self):
        rep, _ = render_cells(doc(), axis_order=['m:printer', 'm:lexer'])
        self.assertEqual(sorted(w['code'] for w in rep['warnings']), ['VP10_COVERAGE_NONE', 'VP10_ORDER_NOT_IN_VIEW', 'VP10_ORDER_PARTIAL'])
        self.assertEqual(rep['row_values'][0], 'm:printer')
        self.assertEqual(code(lambda: render_cells(doc(), axis_order=['m:parser', 'm:parser'])), 'VP10_ORDER_INVALID')

    def test_deterministic(self):
        self.assertEqual(render_cells(doc('S-04'), locale='de')[1], render_cells(doc('S-04'), locale='de')[1])


class G6AndCli(unittest.TestCase):
    def test_api_round_trip(self):
        c = VEC['S-04']
        src = api.source(copy.deepcopy(c['context']), None, None, statements=copy.deepcopy(c['statements']), projection=copy.deepcopy(c['projection']))
        self.assertEqual(src['profile'], PROFILE_110)
        res = api.views(src['source'], locale='de')
        self.assertEqual(api.check(json.loads(json.dumps(res)))['status'], 'PASS')
        self.assertEqual(code(lambda: api.source(c['context'], 'mp-x', None, statements=c['statements'])), 'VP10_ADAPTER_INPUT')

    def test_cli_from_statements_and_print(self):
        c = VEC['S-04']
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            for n in ('context', 'statements', 'projection'):
                (t/f'{n}.json').write_text(json.dumps(c[n]))
            r = subprocess.run([PY, '-m', 'vpcells', 'from-statements', '--context', str(t/'context.json'), '--statements', str(t/'statements.json'),
                                '--projection', str(t/'projection.json'), '--out', str(t/'in.json')], capture_output=True, cwd=HERE)
            self.assertEqual(r.returncode, 0, r.stderr)
            r = subprocess.run([PY, '-m', 'vpcells', 'print-cells', '--input', str(t/'in.json'), '--out', str(t/'o')], capture_output=True, cwd=HERE)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual((t/'o/render.svg').read_bytes(), render_cells(doc('S-04'))[1])
            r = subprocess.run([PY, '-m', 'vpcells', 'from-statements', '--context', str(t/'context.json'), '--statements', str(t/'statements.json'),
                                '--out', str(t/'in2.json')], capture_output=True, cwd=HERE)
            self.assertEqual(r.returncode, 2)
            self.assertEqual(json.loads(r.stderr)['code'], 'VP10_PREDICATE_INVALID')


if __name__ == '__main__':
    unittest.main()
