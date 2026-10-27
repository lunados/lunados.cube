"""VP-07.3 local test suite (P2-VP-MIGRATION/0.7.3). Fixed oracle expectations; no network, no G5 mutation."""
import copy, hashlib, json, subprocess, sys, tempfile, unittest
from pathlib import Path
from xml.etree import ElementTree as ET
HERE = Path(__file__).resolve().parents[1]; REPO = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE/'scripts')); sys.dont_write_bytecode = True
import run_vectors_m as RM  # noqa: E402
import pin_070_digests as PIN0  # noqa: E402
import pin_071_digests as PIN1  # noqa: E402
import pin_072_digests as PIN2  # noqa: E402
from vpmigration import VP07Error, from_plan, print_panels, check_panels  # noqa: E402
from vpmigration.common import (publish_dir, NS, P071, P072, P073, METHOD_CATALOG, METHOD_CATALOG_SHA256, method_short,  # noqa: E402
                                method_sorted, no_active_content)

VEC = {c['id']: c for c in RM.VEC}
GOLD = json.loads((HERE/'fixtures/golden_v073.json').read_text('utf-8'))
G, T = f'{{{NS}}}g', f'{{{NS}}}text'
PHASES = ('cube.phases', 'subject', 'standard')


def code_of(fn, *a, **k):
    try:
        fn(*a, **k)
    except VP07Error as e:
        return e.code
    return 'PASS'


def ctx(i='M-01'):
    return copy.deepcopy(VEC[i]['input']['context'])


def src7(c=None, **k):
    return from_plan(c or ctx(), 'mp-methods', **k)


def panel_svgs(files):
    return [ET.fromstring(b) for n, b in sorted(files.items()) if n.startswith('panel-') and n.endswith('.svg')]


class Oracle(unittest.TestCase):
    def test_m_vectors(self):
        """VP073-02…04: M-01…M-12 against the independent oracle."""
        self.assertEqual(len(VEC), 12)
        for i, c in sorted(VEC.items()):
            with self.subTest(id=i), tempfile.TemporaryDirectory() as tmp:
                try:
                    out = RM.run(c, tmp)
                    status, codes, msg = 'PASS', [w['code'] for w in out['warnings']], ''
                except VP07Error as e:
                    out, status, codes, msg = None, 'FAIL', [e.code], str(e)
                self.assertEqual(status, c['expected_status'], msg)
                for k in c['required_codes']:
                    self.assertIn(k, codes)
                for k in c['forbidden_codes']:
                    self.assertNotIn(k, codes)
                if status == 'PASS':
                    self.assertTrue(RM.check(c, out, tmp))
                for s in c['expect'].get('message_contains', []):
                    self.assertIn(s, msg)

    def test_earlier_profiles_byte_identical(self):
        """VP073-01: pinned 0.7.0, 0.7.1 and 0.7.2 outputs unchanged."""
        for pin in (PIN0, PIN1, PIN2):
            want = json.loads(pin.OUT.read_text('utf-8'))['digests']
            got = pin.collect()
            with self.subTest(pin=pin.__name__):
                self.assertEqual({k: got.get(k) for k in want}, want)


class Rules(unittest.TestCase):
    def test_catalog_constant_matches_pinned_p111_file(self):     # D-6, shared with VP-09
        f = REPO/'P1/migration-methods-v1/cube_p111/profiles/migration-methods-v1.json'
        self.assertEqual(hashlib.sha256(f.read_bytes()).hexdigest(), METHOD_CATALOG_SHA256)
        self.assertEqual(tuple(m['method_id'] for m in json.loads(f.read_text('utf-8'))['methods']), METHOD_CATALOG)
        sys.path.insert(0, str(HERE.parent/'visual-printer-axes-v1'))
        from vpaxes.common import CATALOG_ORDER
        self.assertIs(CATALOG_ORDER, METHOD_CATALOG)

    def test_short_names_and_order(self):         # D-3, D-4
        self.assertEqual(method_short('migrate.reconfigure/v1'), 'reconfigure')
        self.assertEqual(method_short('acme.archive/v1'), 'acme.archive/v1')
        self.assertEqual(method_sorted(['acme.x/v1', 'migrate.retire/v1', 'migrate.import/v1', 'migrate.retire/v1']),
                         ['migrate.import/v1', 'migrate.retire/v1', 'acme.x/v1'])

    def test_profile_selection(self):         # D-1, MT-1
        self.assertEqual(src7()[0]['profile'], P073)
        self.assertEqual(from_plan(RM.strip7(ctx()), 'mp-methods')[0]['profile'], P071)
        for p in (P071, P072):
            self.assertEqual(code_of(from_plan, ctx(), 'mp-methods', profile=p), 'VP07_ADAPTER_INPUT')
        s, _ = from_plan(RM.strip7(ctx()), 'mp-methods', profile=P073)       # explicit 0.7.3 on /6: no method fields
        self.assertEqual(s['profile'], P073)
        self.assertFalse(any('methods' in t for t in s['transitions']))

    def test_row1_other_method_profile(self):
        c = ctx(); c['method_profile_refs'] = ['P1.11/migration-methods-v2']
        self.assertEqual(code_of(from_plan, c, 'mp-methods'), 'VP07_ADAPTER_INPUT')

    def test_row2_unknown_method_on_source(self):
        s, _ = src7()
        s['transitions'][0]['methods'][0]['method_id'] = 'acme.other/v1'
        self.assertEqual(code_of(print_panels, s, *PHASES), 'VP07_METHOD_UNKNOWN')
        s['local_methods'] = ['acme.other/v1']
        self.assertEqual(code_of(print_panels, s, *PHASES), 'PASS')

    def test_row2_unknown_method_outside_slice(self):     # no silent omission even when the owner is not shown
        c = ctx(); c['migration_plans'][0]['dependencies'][4]['method']['method_id'] = 'migrate.rewrit/v1'
        self.assertEqual(code_of(from_plan, c, 'mp-methods', subjects=['shop']), 'VP07_METHOD_UNKNOWN')

    def test_row3_method_fields_below_073(self):
        s, _ = src7()
        s['profile'] = P072
        s.pop('local_methods')
        self.assertEqual(code_of(print_panels, s, *PHASES), 'VP07_SOURCE_INVALID')

    def test_row4_hidden_argument_in_mapping_and_panels(self):
        s, m = src7(subjects=['crm-sync'])
        t = next(x for x in s['transitions'] if x['id'] == 't-mail')
        self.assertEqual(sorted(r for b in t['methods'] for r in b.get('hidden_roles', [])), ['retired', 'source'])
        self.assertEqual(t['methods'][0]['arguments']['retired'], 'legacy-mail')       # declared ref text kept (D-7)
        rep, _ = print_panels(s, *PHASES)
        self.assertEqual(sorted((w['owner'], w['role']) for w in rep['warnings'] if w['code'] == 'VP07_METHOD_ARGUMENT_HIDDEN'),
                         [('t-mail', 'retired'), ('t-mail', 'source')])
        self.assertEqual([w for w in m['warnings'] if w['code'] == 'VP07_METHOD_ARGUMENT_HIDDEN'],
                         [w for w in rep['warnings'] if w['code'] == 'VP07_METHOD_ARGUMENT_HIDDEN'])

    def test_row5_context7_without_bindings(self):
        c = RM.strip7(ctx()); c['format'] = 'aiaeao.cube.binding-context/7'; c['method_profile_refs'] = ['P1.11/migration-methods-v1']
        s, _ = from_plan(c, 'mp-methods')
        self.assertEqual(s['profile'], P073)
        rep, files = print_panels(s, *PHASES)
        self.assertFalse(any(g.get('data-vp07-methods') or g.get('data-vp07-method') for r in panel_svgs(files) for g in r.iter(G)))
        self.assertFalse(any('· verb' == (t.text or '') for r in panel_svgs(files) for t in r.iter(T)))    # MD-3 line only with methods


class Drawing(unittest.TestCase):
    def test_markers_unchanged_but_for_metadata(self):     # MD-1, D-2
        s7, _ = src7(); s6, _ = from_plan(RM.strip7(ctx()), 'mp-methods')
        f7 = print_panels(s7, *PHASES)[1]; f6 = print_panels(s6, *PHASES)[1]

        def markers(files):
            out = []
            for r in panel_svgs(files):
                for g in r.iter(G):
                    if g.get('data-vp07-code'):
                        out.append((g.get('data-vp07-code'), [(e.tag, sorted((k, v) for k, v in e.attrib.items())) for e in g if e.tag != f'{{{NS}}}title'],
                                    [t.text for t in g.iter(T)]))
            return out
        self.assertEqual(markers(f7), markers(f6))

    def test_ledger_and_panel_inputs(self):     # §1.6, MD-4
        s, _ = src7()
        rep, files = print_panels(s, 'cube.phases', 'subject', 'standard')
        led = json.loads(next(e for e in panel_svgs(files)[0].iter() if e.get('id') == 'vp07-phases-ledger').text)
        self.assertEqual(led['methods'], rep['panel_ledger'][0]['panel_report']['methods'])
        for r in panel_svgs(files):
            self.assertTrue(no_active_content(r))
        with tempfile.TemporaryDirectory() as tmp:
            d = publish_dir(files, Path(tmp)/'p')
            check_panels(d)
            name = next(n for n in sorted(files) if n.endswith('.input.json') and b'"methods"' in files[n])
            x = json.loads((d/name).read_text('utf-8'))
            next(t for t in x['plan']['transitions'] if t.get('methods'))['methods'].reverse()
            (d/name).write_text(json.dumps(x), 'utf-8')
            self.assertEqual(code_of(check_panels, d), 'VP07_PANEL_COVERAGE')

    def test_flow_panels_accept_073_sources(self):    # methods are not drawn in cube.flow (out of scope)
        s, _ = src7()
        rep, files = print_panels(s, 'cube.flow', 'subject', 'standard', 'cube.lens.execution')
        self.assertEqual(rep['coverage']['status'], 'COMPLETE')
        self.assertFalse(any(g.get('data-vp07-method') for r in panel_svgs(files) for g in r.iter(G)))


class Golden(unittest.TestCase):
    def test_gm_pos(self):     # VP073-06
        raw = (REPO/'P1/migration-methods-v1/fixtures/golden_methods_synthetic.json').read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), GOLD['gm_pos_sha256'])
        x = GOLD['expected']
        s, m = from_plan(GOLD['context'], GOLD['plan_id'])
        self.assertEqual(s['profile'], x['source_profile'])
        self.assertEqual(m['warnings'], [])
        v = x['view']
        rep, files = print_panels(s, v['view'], v['partition'], v['granularity'])
        self.assertEqual(rep['coverage']['status'], x['coverage'])
        roots = panel_svgs(files)
        self.assertEqual(sum(g.get('data-vp07-method') == 'migrate.rewrite/v1' for r in roots for g in r.iter(G)), x['rewrite_bars'])
        lines = {g.get('data-transition-id'): ' '.join(t.text or '' for t in g.iter(T)) for r in roots for g in r.iter(G) if g.get('data-vp07-legend-code')}
        for tid, want in x['transition_methods'].items():
            self.assertTrue(lines[tid].endswith(' · '+want), (tid, lines[tid]))


class Cli(unittest.TestCase):
    def test_cli_context7(self):
        with tempfile.TemporaryDirectory() as tmp:
            t = Path(tmp)
            (t/'ctx.json').write_text(json.dumps(ctx()), 'utf-8')
            run = lambda *a: subprocess.run([sys.executable, '-B', '-m', 'vpmigration', *a], cwd=HERE, capture_output=True)  # noqa: E731
            r = run('from-plan', '--context', str(t/'ctx.json'), '--plan', 'mp-methods', '--out', str(t/'src.json'))
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(json.loads((t/'src.json').read_text())['profile'], P073)
            r = run('print-panels', '--source', str(t/'src.json'), '--view', 'cube.phases', '--partition', 'subject',
                    '--granularity', 'standard', '--out', str(t/'p'))
            self.assertEqual(r.returncode, 0, r.stderr)
            r = run('check-panels', '--dir', str(t/'p'))
            self.assertEqual(json.loads(r.stdout)['status'], 'PASS')
            self.assertEqual(json.loads(run('capabilities').stdout)['latest_profile'], P073)


if __name__ == '__main__':
    unittest.main()
