"""VP-10 local test suite. Fixed oracle expectations; no network, no G5."""
import copy, json, subprocess, sys, tempfile, unittest
from pathlib import Path
from xml.etree import ElementTree as ET
HERE = Path(__file__).resolve().parents[1]; P2 = HERE.parent; REPO = P2.parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE/'scripts')); sys.dont_write_bytecode = True
import run_vectors as RV  # noqa: E402
from vpcells.source import from_plan, project  # noqa: E402
from vpcells.cells import render_cells  # noqa: E402
from vpcells.common import VP09Error, NS, PROFILE, LOCALE_PINNED  # noqa: E402
from vpaxes.source import from_plan as axes_from_plan  # noqa: E402
from vpaxes.axes import render_axes  # noqa: E402

VEC = {c['id']: c for c in RV.VEC}
GOLD = json.loads((HERE/'fixtures/golden_cells.json').read_text())['cases']
R1 = json.loads((REPO/'docs/09-Research/visual-check/renders/R-1.json').read_text())
PY = sys.executable


def doc_of(c, **kw):
    return from_plan(copy.deepcopy(c['context']), c['plan_id'], c['predicate'], steps=c.get('steps'), **kw)[0]


def render(c, **kw):
    opts = {k: c.get(k) for k in ('hide_empty', 'locale')}
    opts.update(kw)
    return render_cells(doc_of(c), c.get('rows', 'Y:referent'), c.get('cols', 'Y:referent'), **opts)


def code(fn):
    try:
        fn()
    except VP09Error as e:
        return e.code
    return None


def ledger(svg, ident):
    root = ET.fromstring(svg)
    return json.loads(next(el for el in root.iter() if el.get('id') == ident).text)


class Oracle(unittest.TestCase):
    def test_vectors(self):
        self.assertEqual(sorted(VEC), sorted(RV.ORACLE)); self.assertEqual(len(VEC), 14)
        for i, c in sorted(VEC.items()):
            with self.subTest(id=i):
                self.assertEqual(c['expected'], RV.ORACLE[i]['expected'])
                ok, why = RV.check(c)
                self.assertTrue(ok, why)


class Frozen(unittest.TestCase):
    """VP10-01: VP-07, VP-09 and their pinned outputs unchanged."""
    def test_sha256sums(self):
        for d, f in (('visual-printer-migration-v1', 'VP07_SHA256SUMS.txt'), ('visual-printer-axes-v1', 'VP09_SHA256SUMS.txt')):
            with self.subTest(f=f):
                r = subprocess.run(['shasum', '-a', '256', '-c', f], cwd=P2/d, capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, r.stdout[-500:]+r.stderr[-500:])

    def test_pinned_vp09_digests(self):
        for s in ('pin_090_digests.py', 'pin_091_digests.py'):
            with self.subTest(s=s):
                args = [PY, '-B', f'scripts/{s}'] + (['--check'] if s == 'pin_090_digests.py' else [])
                r = subprocess.run(args, cwd=P2/'visual-printer-axes-v1', capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, r.stdout[-500:]+r.stderr[-500:])


class Regression(unittest.TestCase):
    def test_entries_equal_vp092_of_v7_twin(self):
        """VP10-02: without declarations, VP-10 draws exactly the entries of the 0.9.2 Y × Y view."""
        c8 = copy.deepcopy(R1['context']); c8['format'] = 'aiaeao.cube.binding-context/8'
        doc = from_plan(c8, R1['plan_id'], 'references')[0]
        _, svg = render_cells(doc)
        axes, _ = axes_from_plan(copy.deepcopy(R1['context']), R1['plan_id'], profile='P2-VP-AXES/0.9.2')
        rep, _ = render_axes(axes, 'Y:referent', 'Y:referent')
        self.assertEqual(ledger(svg, 'vp09-axes-ledger')['cells'], rep['cells'])
        self.assertEqual(doc['axes']['source']['cells'], axes['source']['cells'])   # source hashes differ only by the context bytes

    def test_projection(self):
        c = copy.deepcopy(VEC['J-11']['context'])
        c['referents'][0]['instance_ref'] = 'vp10:i1'
        p = project(c)
        self.assertEqual(p['format'], 'aiaeao.cube.binding-context/6')
        self.assertFalse({'coverage_declarations', 'population_rules'} & set(p))
        self.assertTrue(all('instance_ref' not in r for r in p['referents']))


class StatusRows(unittest.TestCase):
    """VP10-04: one test per row of spec §2."""
    def test_row1_no_coverage(self):
        rep, _ = render(VEC['J-01'])
        self.assertEqual([w['code'] for w in rep['warnings']], ['VP10_COVERAGE_NONE'])
        c5 = {**VEC['J-01'], 'context': copy.deepcopy(R1['context'])}       # a /5 context: same, drawn
        rep5, _ = render(c5)
        self.assertEqual(rep5['state_counts'], rep['state_counts'])

    def test_row2_ref_unknown(self):
        rep, _ = render(VEC['J-10'])
        self.assertEqual([w['code'] for w in rep['warnings']], ['VP10_COVERAGE_REF_UNKNOWN'])
        self.assertEqual(rep['ignored_declarations'], [{'declaration_id': 'cv-lexer', 'reason': 'ref_unknown'}])

    def test_row3_instance_ignored(self):
        rep, _ = render(VEC['J-11'])
        self.assertEqual([w['code'] for w in rep['warnings']], ['VP10_COVERAGE_INSTANCE_IGNORED'])

    def test_row4_predicate_invalid(self):
        c = VEC['J-02']
        self.assertEqual(code(lambda: from_plan(copy.deepcopy(c['context']), c['plan_id'], 'syncs-with')), 'VP10_PREDICATE_INVALID')
        self.assertEqual(code(lambda: from_plan(copy.deepcopy(c['context']), c['plan_id'], '')), 'VP10_PREDICATE_INVALID')

    def test_row5_pair_invalid(self):
        for rows, cols in (('Y:referent', 'T'), ('Y:kind', 'Y:kind'), ('Z:referent', 'Y:referent')):
            with self.subTest(rows=rows, cols=cols):
                self.assertEqual(code(lambda: render_cells(doc_of(VEC['J-02']), rows, cols)), 'VP10_PAIR_INVALID')

    def test_row6_out_of_slice_star(self):
        rep, svg = render(VEC['J-12'])
        self.assertEqual(rep['cells']['m:printer|m:validator'], {'state': 'marked', 'entries': ['d-pv* · references']})
        rep_nodecl, _ = render({**VEC['J-12'], 'context': {**copy.deepcopy(VEC['J-12']['context']), 'coverage_declarations': []}})
        self.assertEqual(rep_nodecl['cells']['m:printer|m:validator']['state'], 'unknown')   # uncovered: not drawn, as in VP-09

    def test_row7_vp09_codes_unchanged(self):
        c = VEC['J-02']
        self.assertEqual(code(lambda: from_plan(copy.deepcopy(c['context']), 'mp-none', 'references')), 'VP09_ADAPTER_INPUT')
        self.assertEqual(code(lambda: render_cells(doc_of(c), granularity='huge')), 'VP09_AXES_BUDGET')


class States(unittest.TestCase):
    def test_one_state_per_cell_and_counts(self):
        for i in ('J-02', 'J-08', 'J-12'):
            rep, _ = render(VEC[i])
            self.assertEqual(sum(rep['state_counts'].values()), 16, i)
            self.assertIn('ONE_STATE_PER_DRAWN_CELL', rep['invariants_passed'])

    def test_checked_only_for_declared_scope(self):
        """CS-2 (M-05C): a pair declaration does not make the row complete."""
        rep, _ = render(VEC['J-02'])
        row = {k: v['state'] for k, v in rep['cells'].items() if k.startswith('m:printer|') and k != 'm:printer|m:printer'}
        self.assertEqual(row, {'m:printer|m:parser': 'checked', 'm:printer|m:resolver': 'unknown', 'm:printer|m:validator': 'marked'})

    def test_colour_free(self):
        """CS-6: recolouring everything black leaves every state distinguishable (text and lines only)."""
        _, svg = render(VEC['J-08'])
        root = ET.fromstring(svg); q = lambda t: f'{{{NS}}}{t}'  # noqa: E731
        sig = {}
        for g in root.iter(q('g')):
            st = g.get('data-vp10-state')
            if not st or g.get('data-vp09-cell'):
                continue
            for el in g.iter():
                for a in ('fill', 'stroke'):
                    if a in el.attrib:
                        el.set(a, '#000000')
            sig.setdefault(st, set()).add((tuple(sorted({r.get('stroke-width') for r in g.iter(q('rect'))})),
                                           sum(1 for _ in g.iter(q('line'))) > 0, tuple(t.text for t in g.iter(q('text')))))
        self.assertEqual(set(sig), {'checked', 'unknown', 'element'})
        self.assertTrue(all(len(v) == 1 for v in sig.values()))
        self.assertEqual(len({next(iter(v)) for v in sig.values()}), 3)

    def test_no_pattern_no_active_content(self):
        _, svg = render(VEC['J-07'])
        self.assertNotIn(b'<pattern', svg); self.assertNotIn(b'url(', svg); self.assertNotIn(b'href', svg)

    def test_hidden_named_in_legend(self):
        rep, svg = render(VEC['J-08'])
        self.assertIn('hidden columns: m:printer', svg.decode())
        _, svg_de = render(VEC['J-08'], locale='de')
        self.assertIn('ausgeblendete Spalten: m:printer', svg_de.decode())

    def test_no_blank_line_and_view_id(self):
        _, svg = render(VEC['J-02'])
        s = svg.decode()
        self.assertNotIn('blank cell = nothing declared', s)
        self.assertIn('no blank cell: every cell carries a state', s)
        self.assertIn('>cube.cells</text>', s); self.assertIn('VP-10', s)
        root = ET.fromstring(svg)
        self.assertEqual((root.get('data-printer-profile'), root.get('data-cube-view')), (PROFILE, 'cube.cells'))

    def test_deterministic(self):
        self.assertEqual(render(VEC['J-07'])[1], render(VEC['J-07'])[1])


class Locale(unittest.TestCase):
    def test_pinned(self):
        import hashlib
        self.assertEqual(hashlib.sha256((HERE/'vpcells/locales/de.json').read_bytes()).hexdigest(), LOCALE_PINNED['de'])
        self.assertEqual(code(lambda: render(VEC['J-02'], locale='fr')), 'VP10_LOCALE_INVALID')

    def test_de_texts(self):
        rep, svg = render(VEC['J-07'], locale='de')
        texts = RV.cell_texts(svg)
        self.assertEqual(' '.join(texts['m:printer|m:parser'][1:]), 'keine „verweist auf“ · geprüft (Paar)')   # wrapped at the separator
        self.assertEqual(texts['m:validator|m:printer'][1:], ['„verweist auf“ · nicht erhoben'])
        self.assertEqual(rep['locale']['code'], 'de')


class Golden(unittest.TestCase):
    def test_golden(self):
        for g in GOLD:
            with self.subTest(id=g['id']):
                doc = from_plan(copy.deepcopy(g['context']), g['plan_id'], g['predicate'])[0]
                rep, _ = render_cells(doc, hide_empty=g['hide_empty'], locale=g['locale'])
                self.assertEqual(rep['state_counts'], g['expected_state_counts'])
                self.assertEqual(rep['hidden_cols'], g['expected_hidden_cols'])
                self.assertEqual({k: v['scope'] for k, v in rep['cells'].items() if v['state'] == 'checked'}, g['expected_checked'])

    def test_golden_context_passes_p112(self):
        for p in ('semantic-validator-v1', 'instantiation-profile-v1', 'simulation-profile-v1', 'comparison-profile-v1',
                  'migration-profile-v1', 'migration-profile-v2', 'migration-methods-v1', 'coverage-instance-profile-v1'):
            sys.path.insert(0, str(REPO/'P1'/p))
        from cube_p112.validator import P112Validator
        t = 'rel("references",Y:α:Resource["m:resolver"],Y:α:Resource["m:parser"])'
        r = P112Validator().validate_bytes(t.encode(), context=copy.deepcopy(GOLD[0]['context']))
        self.assertEqual((r['overall_status'], r['diagnostics']), ('PASS', []))


class CLI(unittest.TestCase):
    def test_cli(self):
        with tempfile.TemporaryDirectory() as d:
            ctx = Path(d)/'ctx.json'; ctx.write_text(json.dumps(GOLD[0]['context'], ensure_ascii=False))
            run = lambda *a: subprocess.run([PY, '-B', '-m', 'vpcells', *a], cwd=HERE, capture_output=True, text=True)  # noqa: E731
            self.assertEqual(json.loads(run('capabilities').stdout)['profile'], PROFILE)
            r = run('from-plan', '--context', str(ctx), '--plan', 'mp-dsm', '--predicate', 'references', '--out', f'{d}/in.json')
            self.assertEqual(r.returncode, 0, r.stderr)
            r = run('print-cells', '--input', f'{d}/in.json', '--hide-empty', 'cols', '--locale', 'de', '--out', f'{d}/out')
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(json.loads(r.stdout)['state_counts'], GOLD[1]['expected_state_counts'])
            r = run('print-cells', '--input', f'{d}/in.json', '--rows', 'T', '--out', f'{d}/bad')
            self.assertEqual((r.returncode, json.loads(r.stderr)['code']), (2, 'VP10_PAIR_INVALID'))


if __name__ == '__main__':
    unittest.main(verbosity=1)
