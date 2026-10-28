"""VP-09.2 local test suite (P2-VP-AXES/0.9.2). Fixed oracle expectations; no network, no G5 mutation."""
import copy, json, subprocess, sys, tempfile, unittest
from pathlib import Path
from xml.etree import ElementTree as ET
HERE = Path(__file__).resolve().parents[1]; REPO = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE/'scripts')); sys.dont_write_bytecode = True
import run_vectors_h as RH  # noqa: E402
import materialize_h01_h16 as MH  # noqa: E402
import materialize_b01_b20 as B  # noqa: E402
import pin_090_digests as PIN0  # noqa: E402
import pin_091_digests as PIN1  # noqa: E402
from vpaxes import VP09Error, from_plan, render_axes, print_panels, check_panels  # noqa: E402
from vpaxes.common import publish_dir, NS, P091, P092, ROLE_ORDER, wrap_sep, wrap_words, no_active_content  # noqa: E402

VEC = {c['id']: c for c in RH.VEC}
GOLD = json.loads((HERE/'fixtures/golden_v092.json').read_text('utf-8'))
T = f'{{{NS}}}text'


def err(fn, *a, **k):
    try:
        fn(*a, **k)
    except VP09Error as e:
        return e
    return None


def doc(profile=P092, ctx=None, **kw):
    return from_plan(ctx or B.context(), 'mp-axes', profile=profile, **kw)[0]


def texts(svg):
    return [t.text or '' for t in ET.fromstring(svg).iter(T)]


class Oracle(unittest.TestCase):
    def test_h_vectors(self):
        """VP092-02…06: H-01…H-16 against the independent oracle."""
        self.assertEqual(len(VEC), 16)
        for i, c in sorted(VEC.items()):
            with self.subTest(id=i), tempfile.TemporaryDirectory() as tmp:
                diag = None
                try:
                    out = RH.run(c, tmp)
                    status, codes = 'PASS', [w['code'] for w in out['warnings']]
                except VP09Error as e:
                    out, status, codes, diag = None, 'FAIL', [e.code], e.diagnostic()
                self.assertEqual(status, c['expected_status'])
                for k in c['required_codes']:
                    self.assertIn(k, codes)
                for k in c['forbidden_codes']:
                    self.assertNotIn(k, codes)
                if status == 'PASS':
                    self.assertTrue(RH.check(c, out))
                if 'diagnostic_profile' in c['expect']:
                    self.assertEqual(diag['profile'], c['expect']['diagnostic_profile'])

    def test_earlier_profiles_byte_identical(self):
        """VP092-01: pinned 0.9.0 and 0.9.1 outputs unchanged."""
        for pin in (PIN0, PIN1):
            want = json.loads(pin.OUT.read_text('utf-8'))['digests']
            got = pin.collect()
            with self.subTest(pin=pin.__name__):
                self.assertEqual({k: got.get(k) for k in want}, want)


class Rules(unittest.TestCase):
    """VP092-07: one test per §2 row, plus FA-1 and WR-1."""

    def test_yy_needs_092(self):      # §2 row 1
        for p in (None, P091):
            self.assertEqual(err(render_axes, doc(p, MH.with_yy()), 'Y:referent', 'Y:referent').code, 'VP09_AXIS_INVALID')

    def test_options_need_092(self):      # §2 row 2
        d1 = doc(P091)
        self.assertEqual(err(render_axes, d1, 'F', 'Z:referent', hide_empty='cols').code, 'VP09_SOURCE_INVALID')
        self.assertEqual(err(render_axes, d1, 'F', 'T', locale='de').code, 'VP09_LOCALE_INVALID')
        self.assertEqual(err(print_panels, d1, 'F', 'T', 'standard', None, 'de').code, 'VP09_LOCALE_INVALID')
        self.assertEqual(err(render_axes, doc(), 'F', 'T', locale='xx').code, 'VP09_LOCALE_INVALID')
        self.assertEqual(err(render_axes, doc(), 'F', 'T', hide_empty='cells').code, 'VP09_AXIS_INVALID')

    def test_all_empty(self):      # §2 row 3
        rep, svg = render_axes(doc(subjects=['shop', 'crm-sync']), 'Y:referent', 'Y:referent', hide_empty='both')
        self.assertEqual([w['code'] for w in rep['warnings']], ['VP09_ALL_EMPTY'])
        self.assertEqual((rep['row_values'], rep['col_values'], rep['cells']), ([], [], {}))
        self.assertTrue(any('VP09_ALL_EMPTY' in t for t in texts(svg)))
        self.assertTrue(no_active_content(ET.fromstring(svg)))
        rep, files = print_panels(doc(subjects=['shop', 'crm-sync']), 'Y:referent', 'Y:referent', 'standard', 'both')
        self.assertEqual([w['code'] for w in rep['warnings']], ['VP09_ALL_EMPTY'])
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(check_panels(publish_dir(files, Path(tmp)/'p'))['status'], 'PASS')

    def test_shortened_text_keeps_title(self):      # §2 row 4
        rep, svg = render_axes(doc(ctx=MH.renamed(MH.LONG)), 'F', 'Z:referent')
        g = next(x for x in ET.fromstring(svg).iter(f'{{{NS}}}g') if x.get('data-vp09-cell') == 'migrate.retire/v1|legacy-mail')
        self.assertTrue(any((t.text or '').endswith('…') for t in g.iter(T)))
        self.assertIn(MH.LONG, g.find(f'{{{NS}}}title').text)

    def test_diagnostic_profile(self):      # §2 row 5, D-8
        d = err(render_axes, doc(), 'Q', 'T').diagnostic()
        self.assertEqual((d['profile'], d['printer_profile']), (P092, 'P2-VP-AXES/0.9.0'))
        d1 = err(render_axes, doc(P091), 'Q', 'T').diagnostic()
        self.assertEqual(d1['profile'], 'P2-VP-AXES/0.9.0')               # D-8: 0.9.1 error output unchanged (known, README)
        self.assertNotIn('printer_profile', d1)
        self.assertEqual(err(print_panels, doc(), 'Q', 'T').diagnostic()['profile'], P092)
        self.assertEqual(err(from_plan, {'format': 'x'}, 'mp-axes', profile=P092).diagnostic()['profile'], P092)

    def test_role_order_matches_pinned_catalog(self):      # FA-1
        f = REPO/'P1/migration-methods-v1/cube_p111/profiles/migration-methods-v1.json'
        cat = {m['method_id']: tuple(r['role'] for r in m['roles']) for m in json.loads(f.read_text('utf-8'))['methods']}
        self.assertEqual(cat, ROLE_ORDER)

    def test_wrap_helper(self):      # WR-1 / D-5
        self.assertEqual(wrap_sep('acme:legacy-calendar · target', 14)[0], ['acme:legacy-', 'calendar ·', 'target'])
        lines, short = wrap_sep('x'*30, 10)
        self.assertEqual((lines, short), (['x'*9+'…'], True))
        self.assertEqual(wrap_sep('short text', 40), (['short text'], False))
        self.assertEqual(wrap_words('abcdefghij', 4), ['abcd', 'efgh', 'ij'])   # 0.9.0 / 0.9.1 helper unchanged

    def test_en_is_identity(self):      # D-6, LC-1
        d = doc()
        self.assertEqual(render_axes(d, 'F', 'T', locale='en'), render_axes(d, 'F', 'T'))

    def test_yy_directed(self):      # D-2
        rep, _ = render_axes(doc(ctx=MH.with_yy()), 'Y:referent', 'Y:referent')
        self.assertNotIn('admin-mailbox|support', rep['cells'])
        self.assertNotIn('archive-box|admin-mailbox', rep['cells'])

    def test_hidden_values_do_not_count(self):      # HE-1 (D-4)
        d = doc(ctx=B.context(jobs=17))
        self.assertEqual(err(render_axes, d, 'F', 'Z:referent').code, 'VP09_AXES_BUDGET')
        rep, _ = render_axes(d, 'F', 'Z:referent', hide_empty='cols')
        self.assertEqual(len(rep['col_values'])+rep['hidden_counts']['cols'], len(rep['col_values_all']))

    def test_summary_keeps_warnings(self):      # D-7
        rep, _ = render_axes(doc(ctx=MH.out_of_slice_41(), subjects=['shop', 'crm-sync', 'support']), 'F', 'Z:referent')
        s = rep['warning_summary']
        self.assertEqual(sum(x['count'] for x in s), len(rep['warnings']))
        self.assertNotIn('code', s[0]['items'][0])
        self.assertNotIn('warning_summary', render_axes(doc(P091), 'F', 'T')[0])

    def test_de_ids_unchanged(self):      # D-6: method IDs, referent IDs and ledger stay
        d = doc(ctx=MH.with_yy())
        rep, svg = render_axes(d, 'Y:referent', 'Y:referent', locale='de')
        self.assertEqual(rep['cells']['support|admin-mailbox'], ['d9 · depends-on'])
        self.assertIn('d9 · hängt ab von', texts(svg))
        self.assertIn('NUR DARSTELLUNG · keine ACG-Validierung, keine Gewähr, keine Autoritätsentscheidung', texts(svg))


class Golden(unittest.TestCase):
    def test_gm_pos(self):     # VP092-08
        x = GOLD['expected']
        d = from_plan(GOLD['context'], GOLD['plan_id'], profile=GOLD['profile'])[0]
        rep, _ = render_axes(d, x['yy']['rows'], x['yy']['cols'])
        self.assertEqual(rep['cells'], x['yy']['cells'])
        h = x['yy_hidden']
        rep, _ = render_axes(d, h['rows'], h['cols'], hide_empty=h['hide_empty'])
        self.assertEqual((rep['row_values'], rep['col_values'], rep['hidden_rows'], rep['hidden_cols']),
                         (h['row_values'], h['col_values'], h['hidden_rows'], h['hidden_cols']))
        rep, files = print_panels(d, x['ft']['rows'], x['ft']['cols'], 'standard', None, x['locale']['code'])
        for w in x['ft']['cell_contains']:
            self.assertIn(f"{w['row']}|{w['col']}|{w['entry']}", rep['all_units'])
        tx = [t for n, b in files.items() if n.startswith('panel-') and n.endswith('.svg') for t in texts(b)]
        for t in x['locale']['texts_contain']:
            self.assertIn(t, tx)
        fz = x['fz']
        rep, files = print_panels(d, fz['rows'], fz['cols'], 'standard', fz['hide_empty'])
        self.assertEqual((rep['coverage']['status'], rep['hidden_cols']), (fz['coverage'], fz['hidden_cols']))
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(check_panels(publish_dir(files, Path(tmp)/'p'))['status'], 'PASS')


class Cli(unittest.TestCase):
    def test_cli_options(self):
        with tempfile.TemporaryDirectory() as tmp:
            t = Path(tmp)
            (t/'ctx.json').write_text(json.dumps(MH.with_yy()), 'utf-8')
            run = lambda *a: subprocess.run([sys.executable, '-B', '-m', 'vpaxes', *a], cwd=HERE, capture_output=True)  # noqa: E731
            r = run('from-plan', '--context', str(t/'ctx.json'), '--plan', 'mp-axes', '--profile', P092, '--out', str(t/'in.json'))
            self.assertEqual(r.returncode, 0, r.stderr)
            r = run('print-panels', '--input', str(t/'in.json'), '--rows', 'Y:referent', '--cols', 'Y:referent', '--hide-empty', 'both',
                    '--locale', 'de', '--out', str(t/'p'))
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn('warning_summary', json.loads(r.stdout))
            self.assertEqual(json.loads(run('check-panels', '--dir', str(t/'p')).stdout)['status'], 'PASS')
            r = run('check-axes', '--input', str(t/'in.json'), '--rows', 'Q', '--cols', 'T')
            self.assertEqual(r.returncode, 2)
            self.assertEqual(json.loads(r.stderr)['profile'], P092)
            caps = json.loads(run('capabilities', '--profile', P092).stdout)
            self.assertIn(['Y', 'Y'], caps['pairs'])
            self.assertEqual(caps['display_options']['hide_empty'], ['rows', 'cols', 'both'])


if __name__ == '__main__':
    unittest.main()
