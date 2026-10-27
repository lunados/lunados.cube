"""VP-09 local test suite (P2-VP-AXES/0.9.0). Fixed oracle expectations; no network, no G5 mutation."""
import copy, json, re, subprocess, sys, tempfile, unittest
from pathlib import Path
from xml.etree import ElementTree as ET
HERE = Path(__file__).resolve().parents[1]; P2 = HERE.parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE/'scripts')); sys.dont_write_bytecode = True
import run_vectors as RV  # noqa: E402
from vpaxes import VP09Error, from_plan, render_axes, print_panels, check_panels  # noqa: E402
from vpaxes.common import publish_dir, no_active_content, NS, PROFILE  # noqa: E402

VEC = {c['id']: c for c in RV.VEC}
GOLD = json.loads((HERE/'fixtures/golden_axes.json').read_text('utf-8'))
NOPROMO = ('epistemic_warrant', 'current_authority', 'canonical_admission')


def code_of(fn, *a, **k):
    try:
        fn(*a, **k)
    except VP09Error as e:
        return e.code
    return 'PASS'


def doc(i='A-01'):
    inp = VEC[i]['input']
    return from_plan(copy.deepcopy(inp['context']), inp['plan_id'], layers=inp.get('layers'))[0]


class Oracle(unittest.TestCase):
    def test_a_vectors(self):
        """VP09-02…05: A-01…A-20 against the independent oracle."""
        self.assertEqual(len(VEC), 20)
        for i, c in sorted(VEC.items()):
            with self.subTest(id=i), tempfile.TemporaryDirectory() as tmp:
                try:
                    out = RV.run(c, tmp)
                    status, codes = 'PASS', [w['code'] for w in out['warnings']]
                except VP09Error as e:
                    out, status, codes = None, 'FAIL', [e.code]
                self.assertEqual(status, c['expected_status'])
                for k in c['required_codes']:
                    self.assertIn(k, codes)
                if status == 'PASS':
                    self.assertTrue(RV.check(c, out))
                    for k in NOPROMO:
                        self.assertEqual(out['report'][k], 'NOT_EVALUATED')


class StatusRules(unittest.TestCase):
    """VP09-06: one test per row of spec §2."""
    def test_row1_axis_or_pair_invalid(self):
        d = doc()
        for rows, cols in (('Q', 'T'), ('O', 'X'), ('T', 'X'), ('F', 'Y:referent'), ('Z:any', 'T')):
            self.assertEqual(code_of(render_axes, d, rows, cols), 'VP09_AXIS_INVALID', (rows, cols))

    def test_row2_same_axis_twice(self):
        self.assertEqual(code_of(render_axes, doc(), 'Z:referent', 'Z:kind'), 'VP09_AXIS_INVALID')
        self.assertEqual(code_of(render_axes, doc(), 'X', 'X'), 'PASS')

    def test_row3_axis_empty(self):
        self.assertEqual(code_of(render_axes, doc('A-04'), 'F', 'Z:referent', 'detail'), 'VP09_AXIS_EMPTY')
        d = doc(); d['source']['facet_bindings'] = []
        self.assertEqual(code_of(render_axes, d, 'X', 'Z:referent', 'detail'), 'VP09_AXIS_EMPTY')

    def test_row4_source_without_home(self):
        d = doc(); del d['source']['objects'][0]['semantic_ref']
        self.assertEqual(code_of(render_axes, d, 'Z:referent', 'T'), 'VP09_SOURCE_INVALID')
        d = doc(); d['source']['profile'] = 'P2-VP-MIGRATION/0.7.0'
        self.assertEqual(code_of(render_axes, d, 'Z:referent', 'T'), 'VP09_SOURCE_INVALID')

    def test_row5_budget(self):
        self.assertEqual(code_of(render_axes, doc('A-18'), 'Z:referent', 'T', 'standard'), 'VP09_AXES_BUDGET')
        self.assertEqual(code_of(print_panels, doc('A-18'), 'Z:referent', 'T', 'detail'), 'VP09_AXES_BUDGET')  # detail never splits

    def test_row6_cell_overflow_is_warning(self):
        rep, svg = render_axes(doc(), 'Z:referent', 'T', 'standard')
        ov = [w for w in rep['warnings'] if w['code'] == 'VP09_CELL_OVERFLOW' and w['row'] == 'hosting' and w['col'] == 'p0']
        self.assertEqual(ov, [{'code': 'VP09_CELL_OVERFLOW', 'row': 'hosting', 'col': 'p0', 'count': 7, 'shown': 3}])
        self.assertEqual(rep['render_status'], 'PASS')

    def test_row7_panel_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, files = print_panels(doc('A-19'), 'Z:referent', 'T', 'standard')
            d = publish_dir(files, Path(tmp)/'p')
            self.assertEqual(check_panels(d)['status'], 'PASS')
            f = d/'panel-02.svg'; f.write_bytes(f.read_bytes().replace(b'CUBE.AXES', b'CUBE.AXEZ', 1))
            self.assertEqual(code_of(check_panels, d), 'VP09_PANEL_COVERAGE')

    def test_row8_audit(self):
        from vpaxes.axes import AxesPrinter
        p = AxesPrinter(); pr = p.project(doc(), 'Y:referent', 'T')
        svg, drawn = p.render(pr)
        self.assertEqual(code_of(p.report, pr, svg.replace(b'</svg>', b'<script>x</script></svg>'), drawn), 'VP09_AUDIT')


class Rules(unittest.TestCase):
    def test_orientation_swaps(self):
        """AQ-2: transposed request lists the same entries with rows and columns swapped."""
        a, _ = render_axes(doc(), 'Y:referent', 'T')
        b, _ = render_axes(doc(), 'T', 'Y:referent')
        self.assertEqual({k: v for k, v in a['cells'].items()}, {f"{k.split('|')[1]}|{k.split('|')[0]}": v for k, v in b['cells'].items()})

    def test_kind_axis_and_x_z(self):
        rep, _ = render_axes(doc(), 'Z:kind', 'T')
        self.assertEqual(rep['row_values'], ['Integration', 'Provider', 'ThirdPartyDependency'])
        self.assertIn('d3', rep['cells']['ThirdPartyDependency|p0'])
        d = doc('A-09')
        rep, _ = render_axes(d, 'X', 'Z:referent', 'detail')
        self.assertTrue(any(e.startswith('d1: kind job') for e in rep['cells']['execution|shop']))

    def test_f_by_step(self):
        rep, _ = render_axes(doc(), 'F', 'T')
        self.assertEqual(rep['cells']['migrate.import/v1|p2'], ['t-mail'])
        self.assertEqual(rep['cells']['migrate.rewrite/v1|p1'], ['d1'])  # dependency binding sits at its last step

    def test_slice_drops_unseen_bindings(self):
        inp = VEC['A-01']['input']
        d, _ = from_plan(inp['context'], inp['plan_id'], steps='p0:p1')
        self.assertEqual([b['owner'] for b in d['method_bindings']], ['d1'])

    def test_no_numeric_encoding(self):
        _, svg = render_axes(doc(), 'Z:referent', 'T', 'standard')
        root = ET.fromstring(svg)
        fills = {r.get('fill') for g in root.iter(f'{{{NS}}}g') if g.get('data-vp09-cell') for r in g.iter(f'{{{NS}}}rect')}
        self.assertEqual(fills, {'#F8FAFC'})
        self.assertTrue(no_active_content(root))

    def test_deterministic(self):
        self.assertEqual(render_axes(doc('A-11'), 'Y:referent', 'Z:referent', 'detail'),
                         render_axes(doc('A-11'), 'Y:referent', 'Z:referent', 'detail'))

    def test_vp07_unchanged(self):
        """VP09-01: VP-07 SHA256SUMS and pinned digests unchanged."""
        r = subprocess.run(['sha256sum', '-c', '--quiet', 'VP07_SHA256SUMS.txt'], cwd=P2/'visual-printer-migration-v1', capture_output=True)
        self.assertEqual(r.returncode, 0, r.stdout+r.stderr)
        for s in ('pin_070_digests.py', 'pin_071_digests.py'):
            r = subprocess.run([sys.executable, 'scripts/'+s, '--check'], cwd=P2/'visual-printer-migration-v1', capture_output=True)
            self.assertEqual(r.returncode, 0, r.stdout+r.stderr)


class Golden(unittest.TestCase):
    def test_golden(self):
        """VP09-07."""
        e = GOLD['expected']
        d, _ = from_plan(GOLD['context'], GOLD['plan_id'])
        self.assertEqual(len(d['method_bindings']), e['method_bindings'])
        with tempfile.TemporaryDirectory() as tmp:
            for k, v in enumerate(e['views']):
                rep, files = print_panels(d, v['rows'], v['cols'], 'standard')
                self.assertEqual(rep['coverage']['status'], v['coverage'])
                self.assertEqual(check_panels(publish_dir(files, Path(tmp)/str(k)))['status'], 'PASS')
        self.assertEqual(render_axes(d, 'Z:kind', 'T')[0]['row_values'], e['z_kind_order'])
        self.assertEqual(render_axes(d, 'F', 'T')[0]['row_values'], e['method_order'])
        full = print_panels(d, 'F', 'Z:referent', 'standard')[0]
        units = set(full['all_units'])
        for c in e['f_cells']:
            self.assertIn(f"{c['row']}|{c['col']}|{c['entry']}", units)
        y = render_axes(d, 'Y:referent', 'T')[0]
        for c in e['y_cells']:
            self.assertIn(c['entry'], y['cells'][f"{c['row']}|{c['col']}"])

    def test_no_client_data(self):
        """VP09-08."""
        for f in [HERE/'fixtures/golden_axes.json', HERE/'fixtures/a01_a20_materialized.json', HERE/'oracles/independent_a01_a20.json']:
            t = f.read_text('utf-8')
            self.assertIsNone(re.search(r'@[a-z0-9-]+\.[a-z]{2,}', t), f.name)
            self.assertIsNone(re.search(r'https?://', t), f.name)


class Cli(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, '-m', 'vpaxes', *args], cwd=HERE, capture_output=True)

    def test_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            t = Path(tmp)
            (t/'ctx.json').write_text(json.dumps(GOLD['context']), 'utf-8')
            r = self.run_cli('from-plan', '--context', str(t/'ctx.json'), '--plan', 'mp-acme', '--out', str(t/'in.json'))
            self.assertEqual(r.returncode, 0, r.stderr)
            r = self.run_cli('print-panels', '--input', str(t/'in.json'), '--rows', 'F', '--cols', 'Z:referent', '--out', str(t/'out'))
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(self.run_cli('check-panels', '--dir', str(t/'out')).returncode, 0)
            r = self.run_cli('check-axes', '--input', str(t/'in.json'), '--rows', 'M', '--cols', 'T')
            self.assertEqual(r.returncode, 2); self.assertEqual(json.loads(r.stderr)['code'], 'VP09_AXIS_INVALID')
            cap = json.loads(self.run_cli('capabilities').stdout)
            self.assertEqual((cap['profile'], cap['numeric_encoding'], cap['mcp_tool']), (PROFILE, False, False))


if __name__ == '__main__':
    unittest.main(verbosity=1)
