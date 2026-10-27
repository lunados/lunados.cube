"""VP-09.1 local test suite (P2-VP-AXES/0.9.1). Fixed oracle expectations; no network, no G5 mutation."""
import copy, hashlib, json, subprocess, sys, tempfile, unittest
from pathlib import Path
from xml.etree import ElementTree as ET
HERE = Path(__file__).resolve().parents[1]; REPO = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE/'scripts')); sys.dont_write_bytecode = True
import run_vectors_b as RB  # noqa: E402
import pin_090_digests as PIN  # noqa: E402
from vpaxes import VP09Error, from_plan, render_axes, print_panels, check_panels, P090, P091  # noqa: E402
from vpaxes.common import publish_dir, no_active_content, CATALOG_ORDER, CATALOG_SHA256  # noqa: E402

VEC = {c['id']: c for c in RB.VEC}
NOPROMO = ('epistemic_warrant', 'current_authority', 'canonical_admission')


def ctx(vid='B-01'):
    return copy.deepcopy(VEC[vid]['input']['context'])


def doc91(c=None, **kw):
    return from_plan(c or ctx(), 'mp-axes', profile=P091, **kw)[0]


def code_of(fn, *a, **k):
    try:
        fn(*a, **k)
    except VP09Error as e:
        return e.code
    return None


class Vectors(unittest.TestCase):
    def test_b01_b20(self):
        with tempfile.TemporaryDirectory() as tmp:
            for c in RB.VEC:
                with self.subTest(c['id']):
                    try:
                        out = RB.run(c, tmp+'/'+c['id'])
                        status, codes, msg = 'PASS', [w['code'] for w in out['warnings']], ''
                    except VP09Error as e:
                        out, status, codes, msg = None, 'FAIL', [e.code], str(e)
                    self.assertEqual(status, c['expected_status'])
                    for k in c['required_codes']:
                        self.assertIn(k, codes)
                    for k in c['forbidden_codes']:
                        self.assertNotIn(k, codes)
                    if status == 'PASS':
                        self.assertTrue(RB.check(c, out))
                    else:
                        for s in c['expect'].get('message_contains', []):
                            self.assertIn(s, msg)

    def test_090_outputs_byte_identical(self):      # VP091-01
        want = json.loads(PIN.OUT.read_text('utf-8'))['digests']
        self.assertEqual(PIN.collect(), want)


class Methods(unittest.TestCase):
    def test_catalog_constant_matches_pinned_p111_file(self):      # FM-1, D-5
        f = REPO/'P1/migration-methods-v1/cube_p111/profiles/migration-methods-v1.json'
        self.assertEqual(hashlib.sha256(f.read_bytes()).hexdigest(), CATALOG_SHA256)
        self.assertEqual(tuple(m['method_id'] for m in json.loads(f.read_text('utf-8'))['methods']), CATALOG_ORDER)

    def test_unknown_method_in_hand_written_input(self):      # §2 row 1 via normalize
        d = doc91()
        d['method_bindings'][0]['method_id'] = 'acme.unknown/v1'
        self.assertEqual(code_of(render_axes, d, 'F', 'Z:referent'), 'VP09_METHOD_UNKNOWN')
        d['local_methods'] = ['acme.unknown/v1']
        self.assertIsNone(code_of(render_axes, d, 'F', 'Z:referent'))

    def test_unknown_method_in_owner_outside_slice(self):     # no silent omission even when the owner is not shown
        c = ctx(); c['migration_plans'][0]['dependencies'][4]['method']['method_id'] = 'migrate.rewrit/v1'
        self.assertEqual(code_of(from_plan, c, 'mp-axes', profile=P091, subjects=['shop']), 'VP09_METHOD_UNKNOWN')

    def test_other_method_profile(self):      # §2 row 2
        c = ctx(); c['method_profile_refs'] = ['P1.11/migration-methods-v2']
        self.assertEqual(code_of(from_plan, c, 'mp-axes', profile=P091), 'VP09_ADAPTER_INPUT')

    def test_090_keeps_old_method_handling(self):     # D-1: 0.9.0 unchanged (unknown IDs appended, no check)
        c = ctx(); c['migration_plans'][0]['transitions'][0]['methods'][0]['method_id'] = 'migrate.imprt/v1'
        d, _ = from_plan(c, 'mp-axes')
        rep, _ = render_axes(d, 'F', 'T')
        self.assertEqual(rep['row_values'][-1], 'migrate.imprt/v1')
        self.assertEqual(rep['profile'], P090)


class Pairs(unittest.TestCase):
    def test_f_y_only_in_091(self):        # FP-1
        self.assertEqual(code_of(render_axes, from_plan(ctx(), 'mp-axes')[0], 'F', 'Y:referent'), 'VP09_AXIS_INVALID')
        rep, _ = render_axes(doc91(), 'Y:referent', 'F')          # swapped orientation
        self.assertIn('t-store · source', rep['cells']['old-store|migrate.import/v1'])

    def test_entry_text_090_vs_091(self):     # D-6
        r0, _ = render_axes(from_plan(ctx(), 'mp-axes')[0], 'F', 'Z:referent')
        r1, _ = render_axes(doc91(), 'F', 'Z:referent')
        self.assertIn('t-mail (source)', r0['cells']['migrate.import/v1|legacy-mail'])
        self.assertIn('t-mail · source', r1['cells']['migrate.import/v1|legacy-mail'])

    def test_step_rule_090_vs_091(self):      # D-3
        r0, _ = render_axes(from_plan(ctx(), 'mp-axes')[0], 'F', 'T')
        r1, _ = render_axes(doc91(), 'F', 'T')
        self.assertIn('d1', r0['cells']['migrate.rewrite/v1|p1'])
        self.assertIn('d1', r1['cells']['migrate.rewrite/v1|p2'])
        self.assertNotIn('migrate.rewrite/v1|p1', r1['cells'])

    def test_same_vp07_source_under_both_profiles(self):     # 0.9.1 only adds to the axes input, never changes the source
        for vid in ('B-01', 'B-03', 'B-09', 'B-12', 'B-19'):
            c = VEC[vid]['input']
            self.assertEqual(from_plan(c['context'], c['plan_id'])[0]['source'],
                             from_plan(c['context'], c['plan_id'], profile=P091)[0]['source'], vid)

    def test_non_f_pairs_unchanged_under_091(self):
        r0, s0 = render_axes(from_plan(ctx(), 'mp-axes')[0], 'Z:referent', 'T')
        r1, s1 = render_axes(doc91(), 'Z:referent', 'T')
        self.assertEqual(r0['cells'], r1['cells'])
        self.assertNotIn('binding_ledger', r1)


class Ledger(unittest.TestCase):
    def test_methods_none(self):       # §2 row 3, D-4
        rep, svg = render_axes(from_plan(ctx('B-09'), 'mp-axes', profile=P091)[0], 'F', 'T')
        self.assertEqual([w['code'] for w in rep['warnings']], ['VP09_METHODS_NONE'])
        self.assertEqual(rep['binding_coverage'], {'units_total': 0, 'drawn': 0, 'off_axis': 0, 'out_of_slice': 0, 'status': 'COMPLETE'})
        legend = next(g for g in ET.fromstring(svg).iter('{http://www.w3.org/2000/svg}g') if g.get('data-vp09-legend'))
        self.assertIn('VP09_METHODS_NONE', ' '.join(t.text or '' for t in legend.iter()))
        with tempfile.TemporaryDirectory() as tmp:
            _, files = print_panels(from_plan(ctx('B-09'), 'mp-axes', profile=P091)[0], 'F', 'Z:referent')
            check_panels(publish_dir(files, Path(tmp)/'p'))

    def test_every_unit_one_state(self):       # FL-2 over all F pairs and the slice case
        for kw in ({}, {'subjects': ['shop', 'crm-sync']}):
            d = doc91(**kw)
            for cols in ('Z:referent', 'Y:referent', 'Z:kind', 'Y:kind', 'T'):
                with self.subTest(kw=kw, cols=cols):
                    rep, _ = render_axes(d, 'F', cols, 'detail')
                    units = [u['unit'] for u in rep['binding_ledger']]
                    self.assertEqual(len(units), len(set(units)))
                    self.assertEqual(rep['binding_coverage']['status'], 'COMPLETE')
                    drawn = sorted(u['unit'] for u in rep['binding_ledger'] if u['state'] == 'drawn')
                    self.assertEqual(drawn, rep['binding_units'])

    def test_off_axis_and_y_views_add_up(self):    # every argument is drawn in exactly one of F × Z and F × Y
        d = doc91()
        z, _ = render_axes(d, 'F', 'Z:referent'); y, _ = render_axes(d, 'F', 'Y:referent')
        dz = {u['unit'] for u in z['binding_ledger'] if u['state'] == 'drawn'}
        dy = {u['unit'] for u in y['binding_ledger'] if u['state'] == 'drawn'}
        self.assertFalse(dz & dy)
        self.assertEqual(dz | dy, {u['unit'] for u in z['binding_ledger']})

    def test_ledger_embedded_and_svg_safe(self):
        rep, svg = render_axes(doc91(), 'F', 'Z:referent')
        root = ET.fromstring(svg)
        self.assertTrue(no_active_content(root))
        self.assertEqual(root.get('data-printer-profile'), P091)
        led = json.loads(next(e for e in root.iter() if e.get('id') == 'vp09-axes-ledger').text)
        self.assertEqual(led['binding_coverage'], rep['binding_coverage'])
        for k in NOPROMO:
            self.assertEqual(rep[k], 'NOT_EVALUATED')

    def test_panels_re_render_and_tamper(self):
        with tempfile.TemporaryDirectory() as tmp:
            rep, files = print_panels(from_plan(ctx('B-16'), 'mp-axes', profile=P091)[0], 'F', 'Z:referent')
            d = publish_dir(files, Path(tmp)/'p')
            self.assertEqual(check_panels(d)['profile'], P091)
            x = json.loads((d/'report.json').read_text('utf-8'))
            x['binding_ledger'][0]['state'] = 'off_axis'
            (d/'report.json').write_text(json.dumps(x), 'utf-8')
            self.assertEqual(code_of(check_panels, d), 'VP09_PANEL_COVERAGE')

    def test_bad_hand_written_ledger_fields(self):
        d = doc91(); del d['dropped_arguments']
        self.assertEqual(code_of(render_axes, d, 'F', 'T'), 'VP09_SOURCE_INVALID')
        d = doc91(); next(b for b in d['method_bindings'] if b['owner_kind'] == 'dependency').pop('step')
        self.assertEqual(code_of(render_axes, d, 'F', 'T'), 'VP09_SOURCE_INVALID')


class Cli(unittest.TestCase):
    def test_from_plan_profile_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            c = Path(tmp)/'ctx.json'; c.write_text(json.dumps(ctx()), 'utf-8')
            run = lambda *a: subprocess.run([sys.executable, '-B', '-m', 'vpaxes', *a], cwd=HERE, capture_output=True)  # noqa: E731
            r = run('from-plan', '--context', str(c), '--plan', 'mp-axes', '--out', str(Path(tmp)/'a.json'), '--profile', P091)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(json.loads((Path(tmp)/'a.json').read_text('utf-8'))['profile'], P091)
            r = run('from-plan', '--context', str(c), '--plan', 'mp-axes', '--out', str(Path(tmp)/'b.json'))
            self.assertEqual(json.loads((Path(tmp)/'b.json').read_text('utf-8'))['profile'], P090)
            r = run('check-axes', '--input', str(Path(tmp)/'a.json'), '--rows', 'F', '--cols', 'Y:referent')
            self.assertEqual(json.loads(r.stdout)['binding_coverage']['status'], 'COMPLETE')


if __name__ == '__main__':
    unittest.main()
