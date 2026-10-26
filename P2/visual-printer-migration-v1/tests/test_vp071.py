"""VP-07.1 local test suite (P2-VP-MIGRATION/0.7.1). Fixed oracle expectations; no network, no G5 mutation."""
import copy, json, re, subprocess, sys, tempfile, unittest
from pathlib import Path
from xml.etree import ElementTree as ET
HERE = Path(__file__).resolve().parents[1]; P2 = HERE.parent; REPO = P2.parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE/'scripts')); sys.dont_write_bytecode = True
import run_vectors_w as RW  # noqa: E402
import pin_070_digests as PIN  # noqa: E402
from vpmigration import VP07Error, render_plan, from_plan, print_panels, check_panels  # noqa: E402
from vpmigration.common import publish_dir, no_active_content, NS, P070, P071  # noqa: E402
from vpmigration.phases import LW1, GAP_LEGEND  # noqa: E402

VEC = {c['id']: c for c in RW.VEC}
GOLD = json.loads((HERE/'fixtures/golden_v071.json').read_text('utf-8'))
NOPROMO = ('epistemic_warrant', 'current_authority', 'canonical_admission')


def code_of(fn, *a, **k):
    try:
        fn(*a, **k)
    except VP07Error as e:
        return e.code
    return 'PASS'


def w(i):
    return copy.deepcopy(VEC[i]['input'])


def gold_src(**k):
    return from_plan(GOLD['context'], 'mp-acme', tracks=GOLD['tracks'], **k)[0]


class Oracle(unittest.TestCase):
    def test_w_vectors(self):
        """VP071-02…05: W-01…W-17 against the independent oracle."""
        self.assertEqual(len(VEC), 17)
        for i, c in sorted(VEC.items()):
            with self.subTest(id=i), tempfile.TemporaryDirectory() as tmp:
                try:
                    out = RW.run(c, tmp)
                    status, codes = 'PASS', [x['code'] for x in out['warnings']]
                except VP07Error as e:
                    out, status, codes = None, 'FAIL', [e.code]
                self.assertEqual(status, c['expected_status'])
                for k in c['required_codes']:
                    self.assertIn(k, codes)
                for k in c['forbidden_codes']:
                    self.assertNotIn(k, codes)
                if status == 'PASS':
                    self.assertTrue(RW.check(c, out))


class Regression(unittest.TestCase):
    def test_070_outputs_byte_identical(self):
        """VP071-01 / PD-4: every pinned 0.7.0 output is reproduced byte for byte."""
        pinned = json.loads(PIN.OUT.read_text('utf-8'))
        self.assertEqual(pinned['profile'], P070)
        self.assertEqual(PIN.collect(), pinned['digests'])

    def test_from_plan_default_and_070_flag(self):
        """PD-2: from-plan emits 0.7.1 by default; --profile 0.7.0 keeps the old source."""
        g = PIN.GOLD
        a, _ = from_plan(g['context'], 'mp-acme', tracks=g['tracks'])
        b, _ = from_plan(g['context'], 'mp-acme', tracks=g['tracks'], profile=P070)
        self.assertEqual((a['profile'], b['profile']), (P071, P070))
        self.assertNotIn('target_step', b)
        self.assertTrue(all('code' not in t for t in b['transitions']))
        self.assertTrue(all('declared_end' in c for c in a['cells']))

    def test_070_rejects_v6_context(self):
        c = copy.deepcopy(GOLD['context'])
        self.assertEqual(code_of(from_plan, c, 'mp-acme', profile=P070), 'VP07_ADAPTER_INPUT')
        self.assertEqual(code_of(from_plan, c, 'mp-acme', profile='P2-VP-MIGRATION/0.7.9'), 'VP07_ADAPTER_INPUT')


class StatusRules(unittest.TestCase):
    """VP071-06: one test per row of spec §2."""
    def src2(self):
        return w('W-01')['source']

    def test_more_than_two_keys_repeated_key_and_flow_step_outer(self):
        s = self.src2()
        self.assertEqual(code_of(print_panels, s, 'cube.phases', 'track,subject,object', 'standard'), 'VP07_PANEL_PARTITION')
        self.assertEqual(code_of(print_panels, s, 'cube.phases', 'track,track', 'standard'), 'VP07_PANEL_PARTITION')
        self.assertEqual(code_of(print_panels, s, 'cube.flow', 'step,subject', 'standard', 'cube.lens.execution'), 'VP07_PANEL_PARTITION')
        self.assertEqual(code_of(print_panels, s, 'cube.phases', 'track,colour', 'standard'), 'VP07_PANEL_PARTITION')

    def test_outer_track_missing(self):
        s = self.src2(); del s['rows'][3]['track']
        self.assertEqual(code_of(print_panels, s, 'cube.phases', 'track,subject', 'standard'), 'VP07_PANEL_PARTITION')

    def test_inner_group_too_large_names_outer_and_inner(self):
        s = self.src2()
        for i in range(3, 10):  # one subject with 8 cells over 4 steps needs > 3 lanes at standard
            s['objects'].append({'id': f'x{i}', 'anchor_id': 'resource-objects.resource', 'form_id': 'form.resource-card', 'label': f'x {i}'})
            s['cells'].append({'id': f'mail-1-x{i}', 'row': 'mail-1', 'object': f'x{i}', 'predicate_id': 'stores-in', 'steps': ['p0', 'p1'],
                               'declaration_ref': f'fixture:vp071/x{i}'})
        with self.assertRaises(VP07Error) as e:
            print_panels(s, 'cube.phases', 'track,subject', 'standard')
        self.assertEqual(e.exception.code, 'VP07_PANEL_PARTITION')
        self.assertIn("track 'mail'", str(e.exception)); self.assertIn("'mail-1'", str(e.exception))

    def test_outer_ledger_tamper(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(code_of(RW.panels, w('W-06'), tmp), 'VP07_PANEL_COVERAGE')

    def test_marker_stack_budget(self):
        self.assertEqual(code_of(render_plan, w('W-11')['plan']), 'VP07_PHASES_BUDGET')
        p = w('W-11')['plan']; p['transitions'] = p['transitions'][:4]
        self.assertEqual(code_of(render_plan, p), 'PASS')

    def test_gap_is_warning_not_verdict(self):
        rep, svg = render_plan(w('W-13')['plan'])
        self.assertEqual(rep['render_status'], 'PASS')
        self.assertEqual([x for x in rep['warnings'] if x['code'] == 'VP07_DECLARED_GAP'], [{'code': 'VP07_DECLARED_GAP', 'cell_id': 'c1', 'shown': True}])
        for k in NOPROMO:
            self.assertEqual(rep[k], 'NOT_EVALUATED')
        root = ET.fromstring(svg)
        self.assertEqual([g.get('data-vp07-gap') for g in root.iter(f'{{{NS}}}g') if g.get('data-vp07-gap')], ['c1'])
        self.assertIn(GAP_LEGEND, [t.text for t in root.iter(f'{{{NS}}}text')])
        self.assertTrue(no_active_content(root))

    def test_071_feature_on_070_document(self):
        s = copy.deepcopy(next(c for c in PIN.VEC if c['id'] == 'V-13')['input']['source'])
        self.assertEqual(s['profile'], P070)
        self.assertEqual(code_of(print_panels, s, 'cube.phases', 'subject,object', 'overview'), 'VP07_PANEL_PARTITION')
        t = copy.deepcopy(s); t['cells'][0]['dropped'] = True
        self.assertEqual(code_of(print_panels, t, 'cube.phases', 'subject', 'overview'), 'VP07_SOURCE_INVALID')
        t = copy.deepcopy(s); t['target_step'] = s['steps'][-1]['id']
        self.assertEqual(code_of(print_panels, t, 'cube.phases', 'subject', 'overview'), 'VP07_SOURCE_INVALID')
        p = copy.deepcopy(next(c for c in PIN.VEC if c['id'] == 'V-01')['input']['plan']); p['target_step'] = 'p1'
        self.assertEqual(code_of(render_plan, p), 'VP07_PHASES_PLAN')


class Rules(unittest.TestCase):
    def test_gap_explanations_mirror_p1101(self):
        """GM-1: retirement of object or subject at k+1, successor, drop and listed end reasons explain the end."""
        base = w('W-13')['plan']
        variants = {
            'successor': lambda p: p['cells'][0].update(successor='c2'),
            'dropped': lambda p: p['cells'][0].update(dropped=True),
            'ends_reason': lambda p: p['cells'][0].update(ends_reason='scope_end'),
            'object_retired': lambda p: p['transitions'].append({'id': 'tr', 'at': 'p2', 'retires': ['old'], 'introduces': [], 'declaration_ref': 'fixture:x'}),
            'subject_retired': lambda p: p['transitions'].append({'id': 'tr', 'at': 'p2', 'retires': ['outbox'], 'introduces': [], 'declaration_ref': 'fixture:x'}),
            'target_beyond_is_still_gap_free_if_ending_at_target': lambda p: (p['cells'][0].update(steps=['p0', 'p1', 'p2', 'p3'])),
            'declared_end_wins': lambda p: p['cells'][0].update(declared_end='dropped'),
        }
        for name, f in variants.items():
            with self.subTest(name):
                p = copy.deepcopy(base); f(p)
                if name == 'target_beyond_is_still_gap_free_if_ending_at_target':
                    p['transitions'] = []
                rep, _ = render_plan(p)
                self.assertNotIn('VP07_DECLARED_GAP', [x['code'] for x in rep['warnings']])
        p = copy.deepcopy(base); p['cells'][0]['ends_reason'] = 'because'
        self.assertIn('VP07_DECLARED_GAP', [x['code'] for x in render_plan(p)[0]['warnings']])
        p = copy.deepcopy(w('W-15')['plan']); p['cells'][0]['declared_end'] = 'unexplained'
        self.assertIn('VP07_DECLARED_GAP', [x['code'] for x in render_plan(p)[0]['warnings']])
        p = copy.deepcopy(base); p['target_step'] = 'p1'
        self.assertNotIn('VP07_DECLARED_GAP', [x['code'] for x in render_plan(p)[0]['warnings']])

    def test_conflicted_cell_not_double_marked(self):
        rep, _ = render_plan(w('W-12')['plan'])
        self.assertNotIn('VP07_DECLARED_GAP', [x['code'] for x in rep['warnings']])

    def test_codes_and_validation(self):
        p = w('W-08')['plan']
        rep, svg = render_plan(p)
        self.assertEqual(rep['transition_codes'], {'t-ret': 'T1', 't-intro': 'T2'})
        root = ET.fromstring(svg)
        sizes = [float(t.get('font-size')) for g in root.iter(f'{{{NS}}}g') if g.get('data-vp07-code') for t in g.iter(f'{{{NS}}}text')]
        self.assertTrue(sizes and min(sizes) >= 11)
        for bad in ('t1', 'T', 'T1234', 'X1'):
            q = copy.deepcopy(p); q['transitions'][0]['code'] = bad
            self.assertEqual(code_of(render_plan, q), 'VP07_PHASES_PLAN', bad)
        q = copy.deepcopy(p); q['transitions'][0]['code'] = 'T2'
        self.assertEqual(code_of(render_plan, q), 'VP07_PHASES_PLAN')
        q = copy.deepcopy(p); q['cells'][0]['declared_end'] = 'maybe'
        self.assertEqual(code_of(render_plan, q), 'VP07_PHASES_PLAN')

    def test_long_labels_wrap_not_truncate(self):
        p = w('W-07')['plan']
        p['objects'][0]['label'] = 'legacy outbound mail relay service with a long label'
        p['objects'][1]['label'] = 'new outbound mail relay service with an even longer label'
        rep, svg = render_plan(p)
        root = ET.fromstring(svg)
        leg = next(g for g in root.iter(f'{{{NS}}}g') if g.get('data-vp07-legend-code') == 'T1')
        text = ' '.join(t.text for t in leg.iter(f'{{{NS}}}text'))
        self.assertIn('retires legacy outbound mail relay service with a long label', text)
        self.assertIn('introduces new outbound mail relay service with an even longer', text)
        self.assertNotIn('…', text)

    def test_legend_rows_exact(self):
        self.assertEqual(sorted(LW1.values()), sorted(VEC['W-12']['expect']['legend_rows']))

    def test_nested_flow_and_step_outer(self):
        g = gold_src()
        rep, files = print_panels(g, 'cube.flow', 'track,subject', 'standard', 'cube.lens.execution')
        self.assertEqual([o['status'] for o in rep['outer_ledger']], ['COMPLETE']*3)
        s = w('W-01')['source']
        rep, _ = print_panels(s, 'cube.phases', 'step,track', 'overview')
        self.assertEqual(rep['coverage']['status'], 'COMPLETE')
        self.assertTrue(all(o['status'] == 'COMPLETE' for o in rep['outer_ledger']))
        with tempfile.TemporaryDirectory() as tmp:
            for src, args in ((g, ('cube.flow', 'track,subject', 'standard', 'cube.lens.execution')), (s, ('cube.phases', 'step,track', 'overview')),
                              (s, ('cube.phases', 'track,step', 'overview'))):
                _, files = print_panels(src, *args)
                d = publish_dir(files, Path(tmp)/args[1].replace(',', '-')/args[0])
                self.assertEqual(check_panels(d)['status'], 'PASS')
        with self.assertRaises(VP07Error) as e:  # one track at one step exceeds the flow budget: message names both
            print_panels(g, 'cube.flow', 'track,step', 'detail', 'cube.lens.execution')
        self.assertEqual(e.exception.code, 'VP07_PANEL_PARTITION'); self.assertIn("track 'mail' / step p0", str(e.exception))

    def test_deterministic(self):
        a = print_panels(gold_src(), 'cube.phases', 'track,subject', 'standard')[1]
        b = print_panels(gold_src(), 'cube.phases', 'track,subject', 'standard')[1]
        self.assertEqual(a, b)

    def test_slice_keeps_codes_and_gap(self):
        """GM-3 / TM-1: a step slice keeps full-plan codes and the full-plan gap decision."""
        full = gold_src()
        part = gold_src(steps='p1:p2')
        cf = {t['id']: t['code'] for t in full['transitions']}
        self.assertTrue(all(cf[t['id']] == t['code'] for t in part['transitions']))
        rep, _ = print_panels(part, 'cube.phases', 'track,subject', 'standard')
        self.assertEqual([x['cell_id'] for x in rep['declared_gaps']], ['g01'])
        ends = {c['id']: c['declared_end'] for c in part['cells']}
        self.assertEqual(ends['m01a'], 'object_retired'); self.assertEqual(ends['m01b'], 'target')


class Golden(unittest.TestCase):
    def test_golden(self):
        """VP071-07."""
        e = GOLD['expected']
        src = gold_src()
        self.assertEqual((len(src['cells']), len(src['steps'])), (e['dependencies'], e['steps']))
        self.assertEqual({t['id']: t['code'] for t in src['transitions']}, e['transition_codes'])
        self.assertEqual([t['id'] for t in src['transitions'] if t['at'] == 'p2'], e['boundary_p2_transitions'])
        rep, files = print_panels(src, 'cube.phases', 'track,subject', 'standard')
        x = e['phases_track_subject_standard']
        self.assertEqual({o['outer_value']: len(o['panels']) for o in rep['outer_ledger']}, x['outer_panels'])
        self.assertEqual((rep['coverage']['status'], rep['coverage']['units_total']), (x['coverage'], e['units']))
        self.assertEqual([g['cell_id'] for g in rep['declared_gaps']], e['declared_gaps'])
        self.assertEqual(sorted({w['cell_id'] for w in rep['warnings'] if w['code'] == 'VP07_DECLARED_GAP'}), e['declared_gaps'])
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(check_panels(publish_dir(files, Path(tmp)/'g'))['status'], 'PASS')

    def test_three_markers_one_boundary(self):
        src = gold_src(subjects=['acme:mail-job-09', 'acme:file-job-01', 'acme:account-01'])
        rep, files = print_panels(src, 'cube.phases', 'subject', 'standard')
        root = ET.fromstring(files['panel-01.svg'])
        b = RW.boxes(files['panel-01.svg'])
        at_p2 = [g for g in root.iter(f'{{{NS}}}g') if g.get('data-vp07-code') and g.get('data-step-id') == 'p2']
        self.assertEqual(len(at_p2), 3)
        self.assertTrue(all(not RW.overlap(p, q) for i, p in enumerate(b) for q in b[i+1:]))

    def test_p1101_agrees(self):
        for p in ('semantic-validator-v1', 'instantiation-profile-v1', 'simulation-profile-v1', 'comparison-profile-v1',
                  'migration-profile-v1', 'migration-profile-v2'):
            sys.path.insert(0, str(REPO/'P1'/p))
        from cube_p1101.validator import P1101Validator
        r = P1101Validator().validate_bytes(GOLD['p1_input_text'].encode(), context=GOLD['context'])
        gaps = [d for d in r['diagnostics'] if d['code'] == GOLD['expected']['p1_10_1_code']]
        self.assertEqual(len(gaps), 1)
        self.assertTrue(gaps[0]['message'].startswith(GOLD['expected']['p1_10_1_gap_pointer']+':'))

    def test_no_client_data(self):
        """VP071-08: fixtures and previews use the synthetic acme/fixture namespace only."""
        for f in [HERE/'fixtures/golden_v071.json', HERE/'fixtures/w01_w17_materialized.json', HERE/'oracles/independent_w01_w17.json']:
            t = f.read_text('utf-8')
            self.assertIsNone(re.search(r'@[a-z0-9-]+\.[a-z]{2,}', t), f.name)
            self.assertIsNone(re.search(r'https?://', t), f.name)


class Cli(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, '-m', 'vpmigration', *args], cwd=HERE, capture_output=True)

    def test_cli_profile_and_nested(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx = Path(tmp)/'ctx.json'; ctx.write_text(json.dumps(GOLD['context']), 'utf-8')
            tr = Path(tmp)/'tracks.json'; tr.write_text(json.dumps(GOLD['tracks']), 'utf-8')
            r = self.run_cli('from-plan', '--context', str(ctx), '--plan', 'mp-acme', '--tracks', str(tr), '--out', str(Path(tmp)/'src.json'))
            self.assertEqual(r.returncode, 0, r.stderr)
            r = self.run_cli('print-panels', '--source', str(Path(tmp)/'src.json'), '--view', 'cube.phases', '--partition', 'track,subject',
                             '--granularity', 'standard', '--out', str(Path(tmp)/'out'))
            self.assertEqual(r.returncode, 0, r.stderr)
            r = self.run_cli('check-panels', '--dir', str(Path(tmp)/'out'))
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(len(json.loads(r.stdout)['outer_ledger']), 3)
            r = self.run_cli('from-plan', '--context', str(ctx), '--plan', 'mp-acme', '--profile', P070, '--out', str(Path(tmp)/'old.json'))
            self.assertEqual(r.returncode, 2)
            self.assertEqual(json.loads(r.stderr)['code'], 'VP07_ADAPTER_INPUT')
            cap = json.loads(self.run_cli('capabilities').stdout)
            self.assertEqual(cap['profiles'], [P070, P071]); self.assertEqual(cap['latest_profile'], P071)


if __name__ == '__main__':
    unittest.main(verbosity=1)
