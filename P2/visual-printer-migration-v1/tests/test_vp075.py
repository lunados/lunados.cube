"""VP-07.5 local test suite (P2-VP-MIGRATION/0.7.5). Fixed oracle expectations; no network, no G5 mutation."""
import copy, json, subprocess, sys, tempfile, unittest
from pathlib import Path
from xml.etree import ElementTree as ET
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE/'scripts')); sys.dont_write_bytecode = True
import run_vectors_o as RO  # noqa: E402
import materialize_m01_m12 as M  # noqa: E402
import materialize_o01_o15 as MO  # noqa: E402
import pin_070_digests as PIN0  # noqa: E402
import pin_071_digests as PIN1  # noqa: E402
import pin_072_digests as PIN2  # noqa: E402
import pin_073_digests as PIN3  # noqa: E402
import pin_074_digests as PIN4  # noqa: E402
from vpmigration import VP07Error, from_plan, print_panels, check_panels  # noqa: E402
from vpmigration import locale as LC  # noqa: E402
from vpmigration.common import publish_dir, sha_bytes, NS, P074, P075, no_active_content  # noqa: E402

VEC = {c['id']: c for c in RO.VEC}
GOLD = json.loads((HERE/'fixtures/golden_v075.json').read_text('utf-8'))
G, T = f'{{{NS}}}g', f'{{{NS}}}text'
PH = ('cube.phases', 'subject', 'standard')
FLOW = ('cube.flow', 'subject', 'standard', 'cube.lens.execution')


def err(fn, *a, **k):
    try:
        fn(*a, **k)
    except VP07Error as e:
        return e
    return None


def src(profile=P075, ctx=None):
    return from_plan(ctx or M.context(), 'mp-methods', profile=profile)[0]


def texts(files):
    return [t.text or '' for n, b in sorted(files.items()) if n.endswith('.svg') for t in ET.fromstring(b).iter(T)]


class Oracle(unittest.TestCase):
    def test_o_vectors(self):
        """VP075-02…05: O-01…O-15 against the independent oracle."""
        self.assertEqual(len(VEC), 15)
        for i, c in sorted(VEC.items()):
            with self.subTest(id=i), tempfile.TemporaryDirectory() as tmp:
                diag = None
                try:
                    out = RO.run(c, tmp)
                    status, codes = 'PASS', [w['code'] for w in out['warnings']]
                except VP07Error as e:
                    out, status, codes, diag = None, 'FAIL', [e.code], e.diagnostic()
                self.assertEqual(status, c['expected_status'])
                for k in c['required_codes']:
                    self.assertIn(k, codes)
                for k in c['forbidden_codes']:
                    self.assertNotIn(k, codes)
                if status == 'PASS':
                    self.assertTrue(RO.check(c, out, tmp))
                if 'diagnostic_profile' in c['expect']:
                    self.assertEqual(diag['profile'], c['expect']['diagnostic_profile'])

    def test_earlier_profiles_byte_identical(self):
        """VP075-01: pinned 0.7.0 … 0.7.4 outputs unchanged."""
        for pin in (PIN0, PIN1, PIN2, PIN3, PIN4):
            want = json.loads(pin.OUT.read_text('utf-8'))['digests']
            got = pin.collect()
            with self.subTest(pin=pin.__name__):
                self.assertEqual({k: got.get(k) for k in want}, want)


class Rules(unittest.TestCase):
    """VP075-06: one test per §2 row, plus LC-1 and D-3 audits."""

    def test_options_need_075(self):      # §2 row 1
        s4 = src(P074)
        self.assertEqual(err(print_panels, s4, *PH, hide_ledger=True).code, 'VP07_PANEL_PARTITION')
        self.assertEqual(err(print_panels, s4, 'cube.phases', 'method-sets', 'standard').code, 'VP07_PANEL_PARTITION')
        self.assertEqual(err(print_panels, s4, *PH, locale='de').code, 'VP07_LOCALE_INVALID')
        self.assertEqual(err(print_panels, s4, *PH, locale='en').code, 'VP07_LOCALE_INVALID')

    def test_unknown_or_unpinned_locale(self):      # §2 row 2
        self.assertEqual(err(print_panels, src(), *PH, locale='fr').code, 'VP07_LOCALE_INVALID')
        orig = dict(LC.PINNED)
        try:
            LC._CACHE.pop('de', None)
            LC.PINNED['de'] = '0'*64
            self.assertEqual(err(print_panels, src(), *PH, locale='de').code, 'VP07_LOCALE_INVALID')
        finally:
            LC.PINNED.clear(); LC.PINNED.update(orig); LC._CACHE.pop('de', None)

    def test_fallback_is_a_grouped_warning(self):      # §2 row 3
        rep, files = print_panels(src(ctx=MO.with_unknown_predicate()), *PH, locale='de')
        self.assertEqual([w for w in rep['warnings'] if w['code'] == 'VP07_LOCALE_FALLBACK'],
                         [{'code': 'VP07_LOCALE_FALLBACK', 'predicate_id': 'acme-mirrors-to', 'locale': 'de'}])
        self.assertIn('VP07_LOCALE_FALLBACK', [s['code'] for s in rep['warning_summary']])

    def test_set_over_budget_fails(self):      # §2 row 4: a set split by subject still exceeds the budget
        e = err(print_panels, src(ctx=MO.many_import_bars()), 'cube.flow', 'method-sets', 'overview', 'cube.lens.execution')
        self.assertIsNotNone(e)
        self.assertEqual(e.code, 'VP07_PANEL_PARTITION')
        self.assertEqual(e.diagnostic()['profile'], P075)

    def test_diagnostic_profile(self):      # §2 row 5, D-8
        d = err(print_panels, src(), 'cube.phases', 'banana', 'standard').diagnostic()
        self.assertEqual((d['profile'], d['printer_profile']), (P075, 'P2-VP-MIGRATION/0.7.0'))
        d4 = err(print_panels, src(P074), 'cube.phases', 'banana', 'standard').diagnostic()
        self.assertEqual(d4['profile'], 'P2-VP-MIGRATION/0.7.0')               # older inputs: error output unchanged
        self.assertNotIn('printer_profile', d4)

    def test_en_is_identity(self):      # LC-1
        a = print_panels(src(), *FLOW)[1]
        self.assertEqual(print_panels(src(), *FLOW, locale='en')[1], a)
        self.assertNotIn('locale', json.loads(a['report.json']))

    def test_flow_de_and_hidden_ledger(self):      # D-3 (a): one language, ledger block dropped, frozen geometry kept
        rep, files = print_panels(src(), *FLOW, locale='de', hide_ledger=True)
        tx = texts(files)
        self.assertIn('CUBE.FLOW · DEKLARIERTE BEZIEHUNGEN · keine erschlossene Chronologie oder Kausalität', tx)
        for en in ('DECLARATION LEDGER · each edge is a fixture assertion, not P1 proof', 'DISPLAY-ONLY · not an ACG validation, warrant or authority decision'):
            self.assertNotIn(en, tx)
        self.assertTrue(any(t.startswith('Schritt ') for t in tx))
        self.assertTrue(any(t.startswith('ÜBERGÄNGE BEI ') for t in tx))
        for n, b in files.items():
            if n.endswith('.svg'):
                self.assertTrue(no_active_content(ET.fromstring(b)), n)
        self.assertEqual(rep['locale']['code'], 'de')
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(check_panels(publish_dir(files, Path(tmp)/'p'))['status'], 'PASS')

    def test_frozen_text_change_is_an_audit_failure(self):      # D-3: a required replacement must match
        _, files = print_panels(src(), *FLOW)
        svg = files['panel-01.svg'].replace(b'DISPLAY-ONLY \xc2\xb7 not an ACG', b'DISPLAY ONLY \xc2\xb7 not an ACG')
        e = err(LC.load('de').post, svg, 'flow')
        self.assertEqual(e.code, 'VP07_AUDIT')
        self.assertEqual(err(LC.hide_flow_ledger, svg).code, 'VP07_AUDIT')

    def test_ids_never_translated(self):      # D-4
        rep, files = print_panels(src(), 'cube.phases', 'method-sets', 'standard', locale='de')
        self.assertEqual(list(rep['method_sets']), ['migrate.import/v1', 'migrate.retire/v1', 'migrate.rewrite/v1', 'none'])
        tx = ' '.join(texts(files))
        self.assertIn('import', tx)
        self.assertIn('decl:', files['panel-01.svg'].decode())   # embedded ledger keeps decl: references

    def test_method_sets_check_recomputes(self):      # MS-3: a consistent forgery of the memberships is caught
        with tempfile.TemporaryDirectory() as tmp:
            _, files = print_panels(src(), 'cube.phases', 'method-sets', 'standard')
            d = publish_dir(files, Path(tmp)/'p')
            check_panels(d)
            rep = json.loads((d/'report.json').read_text('utf-8'))
            rep['memberships']['d3'] = ['migrate.import/v1']
            (d/'report.json').write_text(json.dumps(rep), 'utf-8')
            e = err(check_panels, d)
            self.assertEqual(e.code, 'VP07_PANEL_COVERAGE')

    def test_partition_method_unchanged(self):      # D-5: --partition method of 0.7.4 stays as it is on 0.7.5
        r4, _ = print_panels(src(P074), 'cube.phases', 'method', 'standard')
        r5, _ = print_panels(src(), 'cube.phases', 'method', 'standard')
        self.assertEqual([e['shown_cell_ids'] for e in r4['panel_ledger']], [e['shown_cell_ids'] for e in r5['panel_ledger']])

    def test_summary_keeps_warnings(self):      # D-7, WS-1
        rep, _ = print_panels(src(ctx=MO.hidden_41()), 'cube.flow', 'object', 'standard', 'cube.lens.execution')
        s = rep['warning_summary']
        self.assertEqual(sum(x['count'] for x in s), len(rep['warnings']))
        first = [w['code'] for w in rep['warnings']]
        self.assertEqual([x['code'] for x in s], list(dict.fromkeys(first)))
        self.assertNotIn('code', s[0]['items'][0])
        self.assertNotIn('warning_summary', print_panels(src(P074), *PH)[0])


class Golden(unittest.TestCase):
    def test_gm_pos(self):     # VP075-07
        x = GOLD['expected']
        s = from_plan(GOLD['context'], GOLD['plan_id'], profile=GOLD['profile'])[0]
        p = x['phases']
        rep, files = print_panels(s, p['view'], p['partition'], p['granularity'], locale=p['locale'], hide_ledger=p['hide_ledger'])
        self.assertEqual(list(rep['method_sets']), x['set_order'])
        self.assertEqual({m: len(v['cells']) for m, v in rep['method_sets'].items()}, x['set_sizes'])
        self.assertEqual(rep['method_sets']['none']['cells'], x['none_cells'])
        self.assertEqual(rep['coverage']['status'], x['coverage'])
        tx = texts(files)
        for t in x['texts_contain']:
            self.assertIn(t, tx)
        for t in x['texts_exclude']:
            self.assertNotIn(t, tx)
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(check_panels(publish_dir(files, Path(tmp)/'p'))['status'], 'PASS')


class Cli(unittest.TestCase):
    def test_cli_locale_hide_and_sets(self):
        with tempfile.TemporaryDirectory() as tmp:
            t = Path(tmp)
            (t/'ctx.json').write_text(json.dumps(M.context()), 'utf-8')
            run = lambda *a: subprocess.run([sys.executable, '-B', '-m', 'vpmigration', *a], cwd=HERE, capture_output=True)  # noqa: E731
            r = run('from-plan', '--context', str(t/'ctx.json'), '--plan', 'mp-methods', '--profile', P075, '--out', str(t/'src.json'))
            self.assertEqual(r.returncode, 0, r.stderr)
            r = run('print-panels', '--source', str(t/'src.json'), '--view', 'cube.phases', '--partition', 'method-sets',
                    '--granularity', 'standard', '--locale', 'de', '--hide-ledger', '--out', str(t/'p'))
            self.assertEqual(r.returncode, 0, r.stderr)
            res = json.loads(r.stdout)
            self.assertEqual(list(res['method_sets']), ['migrate.import/v1', 'migrate.retire/v1', 'migrate.rewrite/v1', 'none'])
            self.assertIn('warning_summary', res)
            self.assertEqual(json.loads(run('check-panels', '--dir', str(t/'p')).stdout)['status'], 'PASS')
            r = run('print-panels', '--source', str(t/'src.json'), '--view', 'cube.phases', '--partition', 'subject',
                    '--granularity', 'standard', '--locale', 'xx', '--out', str(t/'q'))
            self.assertEqual(r.returncode, 2)
            d = json.loads(r.stderr)
            self.assertEqual((d['code'], d['profile']), ('VP07_LOCALE_INVALID', P075))
            caps = json.loads(run('capabilities').stdout)
            self.assertEqual(caps['display_options']['locale'], ['de', 'en'])


if __name__ == '__main__':
    unittest.main()
