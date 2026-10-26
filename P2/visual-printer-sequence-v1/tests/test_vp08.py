"""VP-08 local test suite (P2-VP-SEQUENCE/0.8.0). Fixed oracle expectations; no network, no G5 mutation."""
import copy, json, re, subprocess, sys, tempfile, unittest
from pathlib import Path
from xml.etree import ElementTree as ET
HERE = Path(__file__).resolve().parents[1]; P2 = HERE.parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE/'scripts')); sys.dont_write_bytecode = True
import run_vectors as RV  # noqa: E402
from vpsequence import VP08Error, render_sequence, print_panels, check_panels, SequencePrinter  # noqa: E402
from vpsequence.common import publish_dir, no_active_content, NS, PROFILE  # noqa: E402

VEC = {c['id']: c for c in RV.VEC}
GOLD = json.loads((HERE/'fixtures/golden_sequence.json').read_text('utf-8'))
NOPROMO = ('epistemic_warrant', 'current_authority', 'canonical_admission')


def code_of(fn, *a, **k):
    try:
        fn(*a, **k)
    except VP08Error as e:
        return e.code
    return 'PASS'


def src(i='S-01'):
    return copy.deepcopy(VEC[i]['input']['source'])


def warn_codes(s, trig='btn-1', g='standard', o='summarize'):
    return [w['code'] for w in render_sequence(s, trig, g, o)[0]['warnings']]


class Oracle(unittest.TestCase):
    def test_s_vectors(self):
        """VP08-02…05: S-01…S-20 against the independent oracle."""
        self.assertEqual(len(VEC), 20)
        for i, c in sorted(VEC.items()):
            with self.subTest(id=i), tempfile.TemporaryDirectory() as tmp:
                try:
                    out = RV.run(c, tmp)
                    status, codes = 'PASS', [w['code'] for w in out['warnings']]
                except VP08Error as e:
                    out, status, codes = None, 'FAIL', [e.code]
                self.assertEqual(status, c['expected_status'])
                for k in c['required_codes']:
                    self.assertIn(k, codes)
                if status == 'PASS':
                    self.assertTrue(RV.check(c, out))
                    for k in NOPROMO:
                        self.assertEqual(out['report'][k], 'NOT_EVALUATED')


class StatusRules(unittest.TestCase):
    """VP08-06: one test per row of spec §2."""
    def test_row1_source_shape_and_limits(self):
        for mut in (lambda s: s.update(format='x'), lambda s: s.update(profile='P2-VP-SEQUENCE/0.9.0'), lambda s: s.update(extra=1),
                    lambda s: s.update(declaration_status='verified'),
                    lambda s: s['triggers'][0].update(sequence=[RV.VEC[0]['input']['source']['triggers'][0]['sequence'][0]]*301)):
            s = src(); mut(s)
            self.assertEqual(code_of(render_sequence, s, 'btn-1'), 'VP08_SOURCE_INVALID')

    def test_row2_participants(self):
        s = src(); s['participants'][1]['form_id'] = 'form.resource-card'
        self.assertEqual(code_of(render_sequence, s, 'btn-1'), 'VP08_SOURCE_INVALID')
        s = src(); s['participants'].append(copy.deepcopy(s['participants'][0]))
        self.assertEqual(code_of(render_sequence, s, 'btn-1'), 'VP08_SOURCE_INVALID')

    def test_row3_references(self):
        s = src(); s['triggers'][0]['sequence'][0]['to'] = 'a'
        self.assertEqual(code_of(render_sequence, s, 'btn-1'), 'VP08_SEQUENCE_REFERENCE')
        s = src(); s['triggers'][0]['sequence'][0]['from'] = 'nobody'
        self.assertEqual(code_of(render_sequence, s, 'btn-1'), 'VP08_SEQUENCE_REFERENCE')

    def test_row4_trigger(self):
        s = src(); s['triggers'][0]['enters'] = 'nobody'
        self.assertEqual(code_of(render_sequence, s, 'btn-1'), 'VP08_TRIGGER_INVALID')
        self.assertEqual(code_of(render_sequence, src(), 'btn-unknown'), 'VP08_TRIGGER_INVALID')

    def test_row5_fragments(self):
        for i in ('S-12', 'S-14', 'S-15'):
            self.assertEqual(code_of(render_sequence, src(i), 'btn-1', 'detail'), 'VP08_FRAGMENT_INVALID', i)
        s = src('S-13'); s['triggers'][0]['sequence'][1]['operands'][0] = {'guard': 'x', 'sequence': s['triggers'][0]['sequence'][1]['operands'][0]['sequence']}
        self.assertEqual(code_of(render_sequence, s, 'btn-1'), 'VP08_FRAGMENT_INVALID')  # loop needs bound
        s = src('S-13'); s['triggers'][0]['sequence'][1]['operands'][0]['sequence'] = []
        self.assertEqual(code_of(render_sequence, s, 'btn-1'), 'VP08_FRAGMENT_INVALID')

    def test_row6_budget(self):
        self.assertEqual(code_of(render_sequence, src('S-16'), 'btn-1', 'standard', 'reject'), 'VP08_SEQUENCE_BUDGET')
        s = src('S-16')
        s['triggers'][0]['sequence'] = [dict(m, id=f'z{i}') for i, m in enumerate(s['triggers'][0]['sequence']*2)]
        self.assertEqual(code_of(render_sequence, s, 'btn-1', 'detail', 'summarize'), 'VP08_SEQUENCE_BUDGET')  # detail never continues
        self.assertEqual(code_of(render_sequence, src('S-08'), 'btn-1', 'overview', 'summarize'), 'PASS')  # depth 1 fits overview
        # fragment depth over the overview budget is never summarized
        s = src('S-08'); f = s['triggers'][0]['sequence'][1]
        f['operands'][0]['sequence'].append({'fragment': 'opt', 'id': 'f9', 'operands': [{'guard': 'g', 'sequence': [
            {'id': 'm9', 'kind': 'call', 'from': 'b', 'to': 'c', 'label': 'x', 'declaration_ref': 'fixture:x'}]}]})
        self.assertEqual(code_of(render_sequence, s, 'btn-1', 'overview', 'summarize'), 'VP08_SEQUENCE_BUDGET')

    def test_row7_continued(self):
        rep, svgs = render_sequence(src('S-17'), 'btn-1', 'standard', 'summarize')
        self.assertIn('VP08_SEQUENCE_CONTINUED', [w['code'] for w in rep['warnings']])
        self.assertEqual(len(svgs), 2)
        self.assertEqual(len([g for g in ET.fromstring(svgs[1]).iter(f'{{{NS}}}g') if g.get('data-vp08-continued-from') == '16']), 1)

    def test_row8_return_unmatched(self):
        self.assertIn('VP08_RETURN_UNMATCHED', warn_codes(src('S-10')))
        self.assertNotIn('VP08_RETURN_UNMATCHED', warn_codes(src('S-08')))  # return inside an alt operand matches the outer call

    def test_row9_return_undeclared(self):
        s = src(); s['triggers'][0]['sequence'] = s['triggers'][0]['sequence'][:1]
        self.assertNotIn('VP08_RETURN_UNDECLARED', warn_codes(s))
        s['triggers'][0]['returns'] = 'expected'
        self.assertIn('VP08_RETURN_UNDECLARED', warn_codes(s))

    def test_row10_method_unknown(self):
        self.assertIn('VP08_METHOD_UNKNOWN', warn_codes(src('S-11')))
        s = src('S-11'); del s['method_contracts']
        self.assertNotIn('VP08_METHOD_UNKNOWN', warn_codes(s))  # no list supplied: nothing to compare against

    def test_row11_panel_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, files = print_panels(src('S-18'), 'trigger', 'standard', 'reject')
            d = publish_dir(files, Path(tmp)/'p')
            f = d/'panel-02.svg'
            f.write_bytes(f.read_bytes().replace(b'CUBE.SEQUENCE', b'CUBE.SEQUENCF', 1))
            self.assertEqual(code_of(check_panels, d), 'VP08_PANEL_COVERAGE')
            self.assertEqual(code_of(print_panels, src('S-18'), 'subject'), 'VP08_PANEL_COVERAGE')

    def test_row12_audit(self):
        p = SequencePrinter()
        s = src('S-07')
        pr = p.project(s, 'btn-1', 'standard', 'reject')
        svg, lay = p.render_window(pr, 0)
        bad = svg.replace(b'</svg>', b'<script>x</script></svg>')
        self.assertFalse(no_active_content(ET.fromstring(bad)))
        self.assertEqual(code_of(p.report, s, pr, [(bad, lay)]), 'VP08_AUDIT')


class Golden(unittest.TestCase):
    def test_golden(self):
        """VP08-07."""
        e, s = GOLD['expected'], GOLD['sequence_source']
        self.assertEqual((len(s['participants']), len(s['triggers'])), (e['participants'], e['triggers']))
        self.assertEqual(sum(t['kind'] == 'ui_button' for t in s['triggers']), e['ui_buttons'])
        rep, files = print_panels(s, 'trigger', 'standard', 'summarize')
        x = e['panels_trigger_standard']
        self.assertEqual((rep['panel_count'], rep['coverage']['status'], rep['coverage']['units_total']), (x['panels'], x['coverage'], x['units']))
        self.assertEqual(len([p for p in rep['panel_ledger'] if p['trigger_id'] == x['continued_trigger']]), x['windows'])
        self.assertEqual([{'code': w['code'], 'trigger_id': w['trigger_id']} for w in rep['warnings']], e['warnings'])
        r, svgs = render_sequence(s, 'btn-checkout', 'standard', 'reject')
        self.assertEqual(r['numbering'], e['checkout_numbering'])
        frames = {g.get('data-vp08-frame'): g.get('data-vp08-fragment') for g in ET.fromstring(svgs[0]).iter(f'{{{NS}}}g') if g.get('data-vp08-frame')}
        self.assertEqual(frames, e['checkout_frames'])
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(check_panels(publish_dir(files, Path(tmp)/'g'))['status'], 'PASS')

    def test_use_case_partition_and_determinism(self):
        s = GOLD['sequence_source']
        a = print_panels(s, 'use_case', 'standard', 'summarize')
        b = print_panels(copy.deepcopy(s), 'use_case', 'standard', 'summarize')
        self.assertEqual(a[1], b[1])
        self.assertEqual([e['trigger_id'] for e in a[0]['panel_ledger']][:2], ['btn-checkout', 'btn-cancel'])

    def test_no_client_data(self):
        """VP08-08: fixtures use the synthetic acme/fixture namespace only."""
        for f in [HERE/'fixtures/golden_sequence.json', HERE/'fixtures/s01_s20_materialized.json', HERE/'oracles/independent_s01_s20.json']:
            t = f.read_text('utf-8')
            self.assertIsNone(re.search(r'@[a-z0-9-]+\.[a-z]{2,}', t), f.name)
            self.assertIsNone(re.search(r'https?://', t), f.name)


class Regression(unittest.TestCase):
    def test_vp07_outputs_unchanged(self):
        """VP08-01: VP-07 0.7.0 pinned digests reproduced; VP-07.1 package files match its SHA256SUMS."""
        sys.path.insert(0, str(P2/'visual-printer-migration-v1'/'scripts'))
        import pin_070_digests as PIN
        self.assertEqual(PIN.collect(), json.loads(PIN.OUT.read_text('utf-8'))['digests'])
        r = subprocess.run(['sha256sum', '-c', '--quiet', 'VP07_SHA256SUMS.txt'], cwd=P2/'visual-printer-migration-v1', capture_output=True)
        self.assertEqual(r.returncode, 0, r.stdout+r.stderr)


class Cli(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, '-m', 'vpsequence', *args], cwd=HERE, capture_output=True)

    def test_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            sp = Path(tmp)/'src.json'; sp.write_text(json.dumps(GOLD['sequence_source']), 'utf-8')
            r = self.run_cli('print-panels', '--source', str(sp), '--out', str(Path(tmp)/'out'))
            self.assertEqual(r.returncode, 0, r.stderr)
            r = self.run_cli('check-panels', '--dir', str(Path(tmp)/'out'))
            self.assertEqual(r.returncode, 0, r.stderr)
            r = self.run_cli('print-sequence', '--source', str(sp), '--trigger', 'sched-reminder', '--out', str(Path(tmp)/'one'))
            self.assertEqual(r.returncode, 0, r.stderr); self.assertEqual(json.loads(r.stdout)['windows'], 2)
            r = self.run_cli('check-sequence', '--source', str(sp), '--trigger', 'sched-reminder', '--overflow', 'reject')
            self.assertEqual(r.returncode, 2); self.assertEqual(json.loads(r.stderr)['code'], 'VP08_SEQUENCE_BUDGET')
            cap = json.loads(self.run_cli('capabilities').stdout)
            self.assertEqual((cap['profile'], cap['mcp_tool'], cap['time_axis']), (PROFILE, False, False))


if __name__ == '__main__':
    unittest.main(verbosity=1)
