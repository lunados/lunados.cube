"""VP-07.4 local test suite (P2-VP-MIGRATION/0.7.4). Fixed oracle expectations; no network, no G5 mutation."""
import copy, json, subprocess, sys, tempfile, unittest
from pathlib import Path
from xml.etree import ElementTree as ET
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE/'scripts')); sys.dont_write_bytecode = True
import run_vectors_n as RN  # noqa: E402
import pin_070_digests as PIN0  # noqa: E402
import pin_071_digests as PIN1  # noqa: E402
import pin_072_digests as PIN2  # noqa: E402
import pin_073_digests as PIN3  # noqa: E402
from vpmigration import VP07Error, from_plan, print_panels, check_panels  # noqa: E402
from vpmigration.panels import render_input  # noqa: E402
from vpmigration.common import publish_dir, encode, sha_bytes, NS, P073, P074, no_active_content  # noqa: E402

VEC = {c['id']: c for c in RN.VEC}
GOLD = json.loads((HERE/'fixtures/golden_v074.json').read_text('utf-8'))
G, T = f'{{{NS}}}g', f'{{{NS}}}text'
FLOW = ('cube.flow', 'subject', 'standard', 'cube.lens.execution')


def code_of(fn, *a, **k):
    try:
        fn(*a, **k)
    except VP07Error as e:
        return e.code
    return 'PASS'


def src(i='N-07', **k):
    inp = VEC[i]['input']
    return from_plan(copy.deepcopy(inp['context']), inp['plan_id'], **k)[0]


def lines(files):
    out = {}
    for n, b in sorted(files.items()):
        if n.startswith('panel-') and n.endswith('.svg'):
            g = next((x for x in ET.fromstring(b).iter(G) if x.get('data-vp07-methods-line') is not None), None)
            if g is not None:
                out[n] = g
    return out


class Oracle(unittest.TestCase):
    def test_n_vectors(self):
        """VP074-02…05: N-01…N-14 against the independent oracle."""
        self.assertEqual(len(VEC), 14)
        for i, c in sorted(VEC.items()):
            with self.subTest(id=i), tempfile.TemporaryDirectory() as tmp:
                try:
                    out = RN.run(c, tmp)
                    status, codes = 'PASS', [w['code'] for w in out['warnings']]
                except VP07Error as e:
                    out, status, codes = None, 'FAIL', [e.code]
                self.assertEqual(status, c['expected_status'])
                for k in c['required_codes']:
                    self.assertIn(k, codes)
                if status == 'PASS':
                    self.assertTrue(RN.check(c, out, tmp))

    def test_earlier_profiles_byte_identical(self):
        """VP074-01: pinned 0.7.0, 0.7.1, 0.7.2 and 0.7.3 outputs unchanged."""
        for pin in (PIN0, PIN1, PIN2, PIN3):
            want = json.loads(pin.OUT.read_text('utf-8'))['digests']
            got = pin.collect()
            with self.subTest(pin=pin.__name__):
                self.assertEqual({k: got.get(k) for k in want}, want)


class Rules(unittest.TestCase):
    def test_profile_selection(self):     # D-1
        self.assertEqual(src()['profile'], P073)                       # a /7 context still selects 0.7.3
        self.assertEqual(src(profile=P074)['profile'], P074)
        self.assertEqual(lines(print_panels(src(), *FLOW)[1]), {})       # no line, no edge metadata on 0.7.3
        self.assertFalse(any(g.get('data-vp07-method') for b in print_panels(src(), *FLOW)[1].values()
                             if b.startswith(b'<?xml') for g in ET.fromstring(b).iter(G)))

    def test_method_partition_on_073_and_074(self):     # D-1: the key needs no new profile
        for p in (None, P074):
            rep, _ = print_panels(src(profile=p), 'cube.phases', 'method', 'standard')
            self.assertEqual(rep['coverage']['status'], 'COMPLETE')

    def test_method_partition_needs_method_fields(self):     # §2 row 1
        s6 = from_plan(_strip7(VEC['N-07']['input']['context']), 'mp-methods')[0]          # a 0.7.1 source without method fields
        for part in ('method', 'track,method', 'method,subject'):
            self.assertEqual(code_of(print_panels, s6, 'cube.phases', part, 'standard'), 'VP07_PANEL_PARTITION', part)

    def test_subtitle_short_index_full(self):      # PM-5
        rep, files = print_panels(src(), 'cube.phases', 'method', 'standard')
        texts = ' '.join(t.text or '' for t in ET.fromstring(files['panel-01.svg']).iter(T))
        self.assertIn('method: rewrite', texts)
        self.assertEqual(rep['panel_ledger'][0]['key_values'], ['migrate.rewrite/v1'])

    def test_flow_line_follows_source(self):      # check-panels recomputes line and edge methods from the source
        with tempfile.TemporaryDirectory() as tmp:
            _, files = print_panels(src(profile=P074), *FLOW)
            d = publish_dir(files, Path(tmp)/'p')
            check_panels(d)
            name = next(n for n in lines(files))
            inp_name = name.replace('.svg', '.input.json')
            inp = json.loads((d/inp_name).read_text('utf-8'))
            inp['methods_line']['transitions'][0]['methods'] = ['migrate.rebuild/v1']
            _, svg = render_input(inp)                         # a consistent forgery: input, SVG and digests all agree
            raw = encode(inp)
            (d/inp_name).write_bytes(raw); (d/name).write_bytes(svg)
            rep = json.loads((d/'report.json').read_text('utf-8'))
            rep['files'][inp_name], rep['files'][name] = sha_bytes(raw), sha_bytes(svg)
            e = next(e for e in rep['panel_ledger'] if e['panel']+'.svg' == name)
            e['svg_sha256'], e['input_sha256'] = sha_bytes(svg), sha_bytes(raw)
            (d/'report.json').write_text(json.dumps(rep), 'utf-8')
            with self.assertRaises(VP07Error) as cm:
                check_panels(d)
            self.assertEqual(cm.exception.code, 'VP07_PANEL_COVERAGE')
            self.assertIn('differ from the embedded source', str(cm.exception))

    def test_line_overlap_is_an_audit_failure(self):      # D-7: never moved silently
        _, files = print_panels(src(profile=P074), *FLOW)
        name = next(n for n in lines(files))
        inp = json.loads(files[name.replace('.svg', '.input.json')])
        from vpmigration import panels as PN
        orig = PN.ML_Y
        try:
            PN.ML_Y = (129, 144)                                # onto the CUBE.FLOW header line
            self.assertEqual(code_of(render_input, inp), 'VP07_AUDIT')
        finally:
            PN.ML_Y = orig

    def test_line_texts_safe_and_bounded(self):     # FL-3
        _, files = print_panels(src('N-11', profile=P074), 'cube.flow', 'object,subject', 'standard', 'cube.lens.execution')
        for name, g in lines(files).items():
            ts = [t.text for t in g.iter(T)]
            self.assertLessEqual(len(ts), 2)
            self.assertTrue(all(len(t) <= 118 for t in ts))
            self.assertTrue(no_active_content(ET.fromstring(files[name])))

    def test_flow_result_keeps_inner_audit(self):     # FL-4
        _, files = print_panels(src(profile=P074, layers=VEC['N-14']['input']['layers']), *FLOW)
        rep = json.loads(files['report.json'])
        for e in rep['panel_ledger']:
            r = e['panel_report']
            if r['format'] == 'aiaeao.cube.vp07-methods-print-result/1':
                self.assertEqual(r['inner_result']['format'], 'aiaeao.cube.vp07-layered-print-result/1')


def _strip7(ctx):
    sys.path.insert(0, str(HERE/'scripts'))
    import run_vectors_m as RM
    return RM.strip7(ctx)


class Golden(unittest.TestCase):
    def test_gm_pos(self):     # VP074-07
        x = GOLD['expected']
        s = from_plan(GOLD['context'], GOLD['plan_id'], profile=GOLD['profile'])[0]
        p = x['phases']
        rep, _ = print_panels(s, p['view'], p['partition'], p['granularity'])
        seq = []
        for e in rep['panel_ledger']:
            if e['key_values'] not in seq:
                seq.append(e['key_values'])
        self.assertEqual(seq, x['groups'])
        self.assertEqual(sum(len(e['shown_cell_ids']) for e in rep['panel_ledger'] if e['key_values'] == ['migrate.rewrite/v1']), x['rewrite_cells'])
        f = x['flow']
        rep, files = print_panels(s, f['view'], f['partition'], f['granularity'], f['lens'])
        self.assertEqual(rep['coverage']['status'], x['coverage'])
        by = {st: set() for st in x['line_codes_by_step']}
        for e in rep['panel_ledger']:
            g = lines({e['panel']+'.svg': files[e['panel']+'.svg']}).get(e['panel']+'.svg')
            if g is not None:
                by[e['step']] |= set(g.get('data-vp07-methods-line').split())
        self.assertEqual({k: sorted(v) for k, v in by.items()}, x['line_codes_by_step'])


class Cli(unittest.TestCase):
    def test_cli_profile_and_partition(self):
        with tempfile.TemporaryDirectory() as tmp:
            t = Path(tmp)
            (t/'ctx.json').write_text(json.dumps(VEC['N-07']['input']['context']), 'utf-8')
            run = lambda *a: subprocess.run([sys.executable, '-B', '-m', 'vpmigration', *a], cwd=HERE, capture_output=True)  # noqa: E731
            r = run('from-plan', '--context', str(t/'ctx.json'), '--plan', 'mp-methods', '--profile', P074, '--out', str(t/'src.json'))
            self.assertEqual(r.returncode, 0, r.stderr)
            r = run('print-panels', '--source', str(t/'src.json'), '--view', 'cube.phases', '--partition', 'method',
                    '--granularity', 'standard', '--out', str(t/'p'))
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(json.loads(run('check-panels', '--dir', str(t/'p')).stdout)['status'], 'PASS')
            self.assertIn('method', json.loads(run('capabilities').stdout)['partitions'])


if __name__ == '__main__':
    unittest.main()
