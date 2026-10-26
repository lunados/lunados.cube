"""VP-07 local test suite. Fixed oracle expectations; no network, no G5 mutation."""
import copy, hashlib, json, subprocess, sys, tempfile, unittest
from pathlib import Path
from xml.etree import ElementTree as ET
HERE = Path(__file__).resolve().parents[1]; P2 = HERE.parent; REPO = P2.parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE/'scripts')); sys.dont_write_bytecode = True
import run_vectors as RV  # noqa: E402
from vpmigration import VP07Error, render_plan, render_styled, from_plan, print_panels, check_panels  # noqa: E402
from vpmigration.common import publish_dir, no_active_content, PROFILE  # noqa: E402
from vpmigration.phases import PhasesPrinter  # noqa: E402
from vpprint.core import render_job  # noqa: E402

VEC = {c['id']: c for c in RV.VEC}
ORACLE = {c['id']: c for c in json.loads((HERE/'oracles/independent_v01_v28.json').read_text())['cases']}
GOLD = json.loads((HERE/'fixtures/golden_migration_views.json').read_text())
NOPROMO = ('epistemic_warrant', 'current_authority', 'canonical_admission')


def plan():
    return copy.deepcopy(VEC['V-01']['input']['plan'])


def code_of(fn, *a, **k):
    try:
        fn(*a, **k)
    except VP07Error as e:
        return e.code
    return 'PASS'


def svg_ok(svg):
    return no_active_content(ET.fromstring(svg))


class Oracle(unittest.TestCase):
    def test_vectors_match_independent_oracle(self):
        self.assertEqual(set(VEC), set(ORACLE)); self.assertEqual(len(VEC), 28)
        for i, c in sorted(VEC.items()):
            with self.subTest(id=i):
                self.assertEqual((c['expected_status'], c['required_codes'], c['expect']),
                                 (ORACLE[i]['expected_status'], ORACLE[i]['required_codes'], ORACLE[i]['expect']))
                tmp = tempfile.mkdtemp()
                try:
                    out, svg = RV.run(c, tmp)
                    self.assertEqual(c['expected_status'], 'PASS', i)
                    self.assertTrue(RV.check(c, out, svg), i)
                except VP07Error as e:
                    self.assertEqual(c['expected_status'], 'FAIL', (i, str(e)))
                    self.assertIn(e.code, c['required_codes'])


class Regression(unittest.TestCase):
    """VP07-01: VP-01…VP-06 byte-identical; VP-06 examples re-render byte-identically."""
    def test_frozen_checksums(self):
        for f in ('visual-printer-2d-lab/VP02_SHA256SUMS.txt', 'visual-printer-2d-lab/VP03_SHA256SUMS.txt',
                  'visual-printer-granularity-v1/VP04_SHA256SUMS.txt', 'visual-printer-conformance-v1/VP05_SHA256SUMS.txt',
                  'visual-printer-release-v1/VP06_SHA256SUMS.txt'):
            base = (P2/f).parent
            for ln in (P2/f).read_text().splitlines():
                if not ln.strip():
                    continue
                digest, name = ln.split(None, 1)
                with self.subTest(file=name):
                    self.assertEqual(hashlib.sha256((base/name.lstrip('*')).read_bytes()).hexdigest(), digest)

    def test_vp06_examples_unchanged(self):
        for job in sorted((P2/'visual-printer-release-v1/examples').glob('*.job.json')):
            with self.subTest(job=job.name):
                _, svg = render_job(json.loads(job.read_text()))
                self.assertEqual(svg, job.with_name(job.name.replace('.job.json', '.svg')).read_bytes())
                env = {'format': 'aiaeao.cube.vp07-styled-print/1', 'profile': PROFILE, 'reference_version': 'v9.4',
                       'job': json.loads(job.read_text())}
                _, svg2 = render_styled(env)
                self.assertEqual(svg2, svg)  # ES-5: no edge_styles → identical bytes


class Rules(unittest.TestCase):
    """VP07-06: §2 rows not isolated by a vector."""
    def test_phases_structure(self):
        p = plan(); p['transitions'][0]['at'] = 'p9'; self.assertEqual(code_of(render_plan, p), 'VP07_PHASES_REFERENCE')
        p = plan(); p['cells'][0]['row'] = 'ghost'; self.assertEqual(code_of(render_plan, p), 'VP07_PHASES_REFERENCE')
        p = plan(); p['steps'][1]['id'] = 'p0'; self.assertEqual(code_of(render_plan, p), 'VP07_PHASES_STEPS')
        p = plan(); p['view'] = 'cube.flow'; self.assertEqual(code_of(render_plan, p), 'VP07_PHASES_PLAN')
        p = plan(); p['cells'][0]['declaration_ref'] = 'acme:x'; self.assertEqual(code_of(render_plan, p), 'VP07_PHASES_PLAN')

    def test_budgets(self):
        p = plan(); p['granularity'] = 'overview'; p['steps'].append({'id': 'p4', 'label': 'p4'})
        self.assertEqual(code_of(render_plan, p, 'summarize'), 'VP07_PHASES_BUDGET')  # steps never summarized
        p = copy.deepcopy(VEC['V-07']['input']['plan']); p['granularity'] = 'detail'
        p['rows'] += [dict(p['rows'][0], id='rx')]; p['cells'] += [dict(p['cells'][0], id='cx', row='rx')]
        self.assertEqual(code_of(render_plan, p, 'summarize'), 'PASS')  # 8 rows fit detail
        p['rows'] += [dict(p['rows'][0], id='ry')]; p['cells'] += [dict(p['cells'][0], id='cy', row='ry')]
        self.assertEqual(code_of(render_plan, p, 'summarize'), 'VP07_PHASES_BUDGET')  # detail never omits

    def test_summarize_ledger(self):
        rep, svg = render_plan(VEC['V-07']['input']['plan'], 'summarize')
        self.assertEqual(rep['omitted_row_ids'], ['r6'])
        self.assertEqual([x['id'] for x in rep['omitted_cells']], ['c6'])
        self.assertEqual(rep['completeness'], 'PARTIAL_EXPLICIT')
        meta = next(x for x in ET.fromstring(svg).iter() if x.get('id') == 'vp07-phases-ledger')
        self.assertEqual(json.loads(meta.text)['omitted_cells'], rep['omitted_cells'])

    def test_edge_styles(self):
        p = plan(); p['edge_styles'] = [{'predicate_id': 'sends-via', 'style': 'dotted', 'legend': 'x'*41}]
        self.assertEqual(code_of(render_plan, p), 'VP07_EDGE_STYLE')
        p = plan(); p['edge_styles'] = [{'predicate_id': 'sends-via', 'style': 'dotted'}]
        self.assertEqual(code_of(render_plan, p), 'VP07_EDGE_STYLE')
        p = plan(); p['edge_styles'] = [{'predicate_id': 'other', 'style': 'dotted', 'legend': 'other'}]
        rep, svg = render_plan(p)
        self.assertIn({'code': 'VP07_EDGE_STYLE_DEFAULT', 'predicate_id': 'sends-via'}, rep['warnings'])
        env = copy.deepcopy(VEC['V-09']['input']['envelope']); env['edge_styles'] = env['edge_styles'][:1]
        res, svg = render_styled(env)
        self.assertIn({'code': 'VP07_EDGE_STYLE_DEFAULT', 'predicate_id': 'recovers-via'}, res['warnings'])
        self.assertEqual(res['vp06_result']['svg_sha256'], res['base_svg_sha256'])

    def test_styled_geometry_only(self):
        env = copy.deepcopy(VEC['V-09']['input']['envelope'])
        env['edge_styles'][1]['style'] = 'double'
        res, svg = render_styled(env)
        root = ET.fromstring(svg)
        ns = '{http://www.w3.org/2000/svg}'
        g = next(x for x in root.iter(ns+'g') if x.get('data-predicate-id') == 'recovers-via')
        self.assertEqual(len([x for x in g if x.tag == ns+'line' and x.get('data-vp07-double')]), 3)
        self.assertTrue(all(x.get('stroke') == '#64748B' for x in g if x.tag == ns+'line'))  # colour unchanged
        self.assertEqual(len([x for x in g if x.tag == ns+'path']), 1)  # arrowhead untouched (ES-2)

    def test_panels_and_source(self):
        src = copy.deepcopy(VEC['V-13']['input']['source'])
        self.assertEqual(code_of(print_panels, src, 'cube.phases', 'track', 'overview'), 'VP07_PANEL_PARTITION')
        self.assertEqual(code_of(print_panels, src, 'cube.phases', 'subject', 'overview', 'cube.lens.execution'), 'VP07_PHASES_LENS')
        self.assertEqual(code_of(print_panels, src, 'cube.flow', 'subject', 'standard'), 'VP07_PANEL_PARTITION')  # flow needs --lens
        s = copy.deepcopy(src); s['cells'] = [dict(s['cells'][0], id=f'k{i}') for i in range(5001)]
        self.assertEqual(code_of(print_panels, s, 'cube.phases', 'subject', 'overview'), 'VP07_SOURCE_INVALID')
        s = copy.deepcopy(src); s['rows'].append({'id': 'lonely', 'anchor_id': 'module-bodies.integration', 'form_id': 'form.module-block', 'label': 'lonely'})
        self.assertEqual(code_of(print_panels, s, 'cube.phases', 'subject', 'overview'), 'VP07_SOURCE_INVALID')
        self.assertEqual(code_of(print_panels, src, 'cube.phases', 'step', 'overview'), 'VP07_PANEL_PARTITION')  # 12 cells in one window > 6
        rep, files = print_panels(src, 'cube.phases', 'step', 'standard')
        self.assertEqual((rep['panel_count'], rep['coverage']['status']), (1, 'COMPLETE'))

    def test_check_panels_extra_file(self):
        with tempfile.TemporaryDirectory() as t:
            _, files = print_panels(VEC['V-13']['input']['source'], 'cube.phases', 'subject', 'overview')
            d = publish_dir(files, Path(t)/'out')
            self.assertEqual(check_panels(d)['status'], 'PASS')
            (d/'notes.txt').write_text('x')
            self.assertEqual(code_of(check_panels, d), 'VP07_PANEL_COVERAGE')

    def test_adapter_rules(self):
        m = json.loads((REPO/'P1/migration-profile-v1/fixtures/m01_m22_materialized.json').read_text())['cases'][0]['context']
        self.assertEqual(code_of(from_plan, m, 'mp-x'), 'VP07_ADAPTER_INPUT')
        self.assertEqual(code_of(from_plan, m, 'mp-1', subjects=['nobody']), 'VP07_ADAPTER_INPUT')
        self.assertEqual(code_of(from_plan, m, 'mp-1', track='a'), 'VP07_ADAPTER_INPUT')
        ctx = RV_rename(m, 'job', 'contact job')
        labels = {'format': 'aiaeao.cube.vp07-label-map/1', 'labels': {'contact job': {'id': 'contact-job', 'label': 'contact job'}}}
        src, mapping = from_plan(ctx, 'mp-1', labels=labels)
        self.assertEqual(src['rows'][0]['id'], 'contact-job')
        src, mapping = from_plan(m, 'mp-1', steps='p1:p2')
        self.assertEqual(mapping['empty_steps'], [])
        self.assertEqual([c['steps'] for c in src['cells']], [['p1', 'p2']])
        src, mapping = from_plan(m, 'mp-1', witness_prefixes={'format': 'aiaeao.cube.vp07-witness-prefixes/1',
                                                              'prefixes': [{'prefix': 'witness:', 'note': 'declared witness'}]})
        self.assertTrue(any(b['lens'] == 'cube.lens.epistemology' for b in src['facet_bindings']))
        self.assertFalse(mapping['p1_validation_performed'])

    def test_determinism(self):
        a = render_plan(plan()); b = render_plan(plan())
        self.assertEqual(a, b)
        m = GOLD['context']
        self.assertEqual(from_plan(m, 'mp-acme'), from_plan(copy.deepcopy(m), 'mp-acme'))
        src, _ = from_plan(m, 'mp-acme')
        self.assertEqual(print_panels(src, 'cube.phases', 'subject', 'standard')[1], print_panels(copy.deepcopy(src), 'cube.phases', 'subject', 'standard')[1])


def RV_rename(ctx, old, new):
    return json.loads(json.dumps(ctx, ensure_ascii=False).replace(f'"{old}"', f'"{new}"'))


class Golden(unittest.TestCase):
    """VP07-08: synthetic plan, ≥ 30 dependencies, 4 steps, 2 tracks, one declared conflict."""
    def setUp(self):
        g = GOLD
        self.src, self.mapping = from_plan(g['context'], 'mp-acme', tracks=g['tracks'], edge_styles=g['edge_styles'],
                                           witness_prefixes=g['witness_prefixes'])

    def test_shape(self):
        e = GOLD['expected']
        self.assertEqual(len(self.src['cells']), e['dependencies'])
        self.assertGreaterEqual(e['dependencies'], 30)
        self.assertEqual(len(self.src['steps']), e['steps'])
        self.assertEqual(len({r['track'] for r in self.src['rows']}), e['tracks'])
        self.assertTrue(all(r['ref'].startswith('acme:') for r in GOLD['context']['referents']))

    def test_phases_panels(self):
        e = GOLD['expected']['phases_subject_standard']
        rep, files = print_panels(self.src, 'cube.phases', 'subject', 'standard')
        self.assertEqual((rep['panel_count'], rep['coverage']['status'], rep['coverage']['units_total']), (e['panels'], e['coverage'], e['units']))
        conf = [{k: x[k] for k in ('cell_id', 'kind', 'steps')} for x in rep['declared_conflicts']]
        self.assertEqual(conf, GOLD['expected']['declared_conflicts'])
        hatched = [n for n, b in files.items() if n.endswith('.svg') and b'data-vp07-hatch="A"' in b]
        self.assertEqual(len(hatched), 1)
        self.assertTrue(all(svg_ok(b) for n, b in files.items() if n.endswith('.svg')))
        for k in NOPROMO:
            self.assertEqual(rep[k], 'NOT_EVALUATED')
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(check_panels(publish_dir(files, Path(t)/'o'))['status'], 'PASS')

    def test_flow_panels(self):
        e = GOLD['expected']['flow_subject_standard_execution']
        rep, files = print_panels(self.src, 'cube.flow', 'subject', 'standard', 'cube.lens.execution')
        self.assertEqual((rep['coverage']['status'], rep['coverage']['units_total']), (e['coverage'], e['units']))
        self.assertTrue(all(b'data-vp07-edge-style' in b for n, b in files.items() if n.startswith('panel-') and n.endswith('.svg')))
        for p in rep['panel_ledger']:
            self.assertEqual(p['panel_report']['vp06_result']['conformance']['status'], 'PASS')  # VP-05 audit nested

    def test_track_slice(self):
        e = GOLD['expected']['phases_track_mail_standard_subject']
        src, _ = from_plan(GOLD['context'], 'mp-acme', tracks=GOLD['tracks'], track='mail')
        rep, _ = print_panels(src, 'cube.phases', 'subject', 'standard')
        self.assertEqual((rep['panel_count'], rep['coverage']['status']), (e['panels'], e['coverage']))

    def test_p1_10_agrees(self):
        for p in ('semantic-validator-v1', 'instantiation-profile-v1', 'simulation-profile-v1', 'comparison-profile-v1', 'migration-profile-v1'):
            sys.path.insert(0, str(REPO/'P1'/p))
        from cube_p110.validator import P110Validator
        r = P110Validator().validate_bytes('rel("depends-on",Z:α:Integration["acme:mail-job-01"],Z:α:ThirdPartyDependency["acme:legacy-mail"])'.encode(),
                                           context=GOLD['context'])
        codes = [d['code'] for d in r['diagnostics']]
        self.assertEqual(r['overall_status'], GOLD['expected']['p1_10_overall'])
        self.assertEqual(codes.count(GOLD['expected']['p1_10_code']), 1)


class Cli(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, '-m', 'vpmigration', *args], cwd=HERE, capture_output=True)

    def test_capabilities_and_errors(self):
        r = self.run_cli('capabilities')
        self.assertEqual(r.returncode, 0)
        cap = json.loads(r.stdout)
        self.assertFalse(cap['mcp_tool']); self.assertEqual(cap['profile'], PROFILE)
        with tempfile.TemporaryDirectory() as t:
            f = Path(t)/'plan.json'; f.write_text(json.dumps(VEC['V-04']['input']['plan']))
            r = self.run_cli('check-phases', '--plan', str(f))
            self.assertEqual(r.returncode, 2)
            d = json.loads(r.stderr)
            self.assertEqual((d['code'], d['files_written']), ('VP07_PHASES_REFERENCE', False))
            f.write_text(json.dumps(plan()))
            out = Path(t)/'o'
            self.assertEqual(self.run_cli('print-phases', '--plan', str(f), '--out', str(out)).returncode, 0)
            self.assertEqual(sorted(p.name for p in out.iterdir()), ['render.svg', 'report.json'])
            r = self.run_cli('print-phases', '--plan', str(f), '--out', str(out))
            self.assertEqual((r.returncode, json.loads(r.stderr)['code']), (2, 'VP07_OUTPUT_EXISTS'))

    def test_from_plan_and_panels_cli(self):
        with tempfile.TemporaryDirectory() as t:
            c = Path(t)/'ctx.json'; c.write_text(json.dumps(GOLD['context']))
            tr = Path(t)/'tracks.json'; tr.write_text(json.dumps(GOLD['tracks']))
            src = Path(t)/'src.json'
            r = self.run_cli('from-plan', '--context', str(c), '--plan', 'mp-acme', '--tracks', str(tr), '--out', str(src))
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue((Path(t)/'src.mapping.json').is_file())
            r = self.run_cli('print-panels', '--source', str(src), '--view', 'cube.phases', '--partition', 'track', '--granularity', 'detail',
                             '--out', str(Path(t)/'p'))
            self.assertEqual(r.returncode, 2)  # one track (9 rows) exceeds detail rows
            self.assertEqual(json.loads(r.stderr)['code'], 'VP07_PANEL_PARTITION')
            r = self.run_cli('print-panels', '--source', str(src), '--view', 'cube.phases', '--partition', 'subject', '--granularity', 'standard',
                             '--out', str(Path(t)/'p'))
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(self.run_cli('check-panels', '--dir', str(Path(t)/'p')).returncode, 0)


if __name__ == '__main__':
    unittest.main(verbosity=1)
