"""VP-07.2 local test suite (P2-VP-MIGRATION/0.7.2). Fixed oracle expectations; no network, no G5 mutation."""
import copy, json, re, subprocess, sys, tempfile, unittest
from pathlib import Path
from xml.etree import ElementTree as ET
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE/'scripts')); sys.dont_write_bytecode = True
import run_vectors_l as RL  # noqa: E402
import pin_070_digests as PIN0  # noqa: E402
import pin_071_digests as PIN1  # noqa: E402
from vpmigration import VP07Error, from_plan, print_panels, check_panels  # noqa: E402
from vpmigration.common import publish_dir, NS, P071, P072  # noqa: E402

VEC = {c['id']: c for c in RL.VEC}
GOLD = json.loads((HERE/'fixtures/golden_v072.json').read_text('utf-8'))
G = f'{{{NS}}}g'


def code_of(fn, *a, **k):
    try:
        fn(*a, **k)
    except VP07Error as e:
        return e.code
    return 'PASS'


def gold_src(**k):
    return from_plan(GOLD['context'], 'mp-acme', tracks=GOLD['tracks'], layers=GOLD['layers'], **k)


def l_src(i='L-06'):
    inp = VEC[i]['input']
    return from_plan(copy.deepcopy(inp['context']), inp['plan_id'], layers=copy.deepcopy(inp['layers']))[0]


class Oracle(unittest.TestCase):
    def test_l_vectors(self):
        """VP072-02…04: L-01…L-13 against the independent oracle."""
        self.assertEqual(len(VEC), 13)
        for i, c in sorted(VEC.items()):
            with self.subTest(id=i), tempfile.TemporaryDirectory() as tmp:
                try:
                    out = RL.run(c, tmp)
                    status, codes = 'PASS', [w['code'] for w in out['warnings']]
                except VP07Error as e:
                    out, status, codes = None, 'FAIL', [e.code]
                self.assertEqual(status, c['expected_status'])
                for k in c['required_codes']:
                    self.assertIn(k, codes)
                for k in c['forbidden_codes']:
                    self.assertNotIn(k, codes)
                if status == 'PASS':
                    self.assertTrue(RL.check(c, out, tmp))


class Regression(unittest.TestCase):
    def test_070_and_071_outputs_byte_identical(self):
        """VP072-01: pinned 0.7.0 (14) and 0.7.1 (16) output digests reproduced byte for byte."""
        self.assertEqual(PIN0.collect(), json.loads(PIN0.OUT.read_text('utf-8'))['digests'])
        self.assertEqual(PIN1.collect(), json.loads(PIN1.OUT.read_text('utf-8'))['digests'])

    def test_profile_selection(self):
        """LS-1: 0.7.1 without a layer map, 0.7.2 with one; a layer map with an older profile FAILs."""
        inp = VEC['L-06']['input']
        self.assertEqual(from_plan(inp['context'], inp['plan_id'])[0]['profile'], P071)
        self.assertEqual(from_plan(inp['context'], inp['plan_id'], layers=inp['layers'])[0]['profile'], P072)
        self.assertEqual(code_of(from_plan, inp['context'], inp['plan_id'], layers=inp['layers'], profile=P071), 'VP07_ADAPTER_INPUT')


class StatusRules(unittest.TestCase):
    """VP072-05: one test per row of spec §2."""
    def test_row1_map_shape(self):
        inp = VEC['L-06']['input']
        for mut in (lambda m: m.update(format='x'), lambda m: m.update(layer_order=[]), lambda m: m.update(layer_order=['a', 'a']),
                    lambda m: m['layers'].update(cloud=[]), lambda m: m['layers']['dns'].append('hosting'),
                    lambda m: m.update(layer_order=m['layer_order']+['unassigned'])):
            m = copy.deepcopy(inp['layers']); mut(m)
            self.assertEqual(code_of(from_plan, inp['context'], inp['plan_id'], layers=m), 'VP07_ADAPTER_INPUT')

    def test_row2_undeclared_ref(self):
        self.assertEqual(code_of(RL.run, VEC['L-04'], None), 'VP07_ADAPTER_INPUT')

    def test_row3_unassigned(self):
        inp = VEC['L-05']['input']
        src, mapping = from_plan(inp['context'], inp['plan_id'], layers=inp['layers'])
        self.assertEqual(mapping['warnings'], [{'code': 'VP07_LAYER_UNASSIGNED', 'item_id': 'support'}])
        rep, _ = print_panels(src, 'cube.phases', 'subject', 'standard')
        self.assertIn({'code': 'VP07_LAYER_UNASSIGNED', 'item_id': 'support'}, rep['warnings'])

    def test_row4_layer_partition_without_layers(self):
        inp = VEC['L-08']['input']
        src, _ = from_plan(inp['context'], inp['plan_id'])
        self.assertEqual(code_of(print_panels, src, 'cube.phases', 'layer', 'standard'), 'VP07_PANEL_PARTITION')
        self.assertEqual(code_of(print_panels, src, 'cube.phases', 'track,layer', 'standard'), 'VP07_PANEL_PARTITION')

    def test_row5_source_layer_consistency(self):
        for mut in (lambda s: s['rows'][0].update(layer='cloud'), lambda s: s.update(layer_sequence=list(reversed(s['layer_sequence']))),
                    lambda s: s['layer_sequence'].pop(), lambda s: s.update(layer_order=['unassigned']+s['layer_order']),
                    lambda s: s['objects'][0].pop('layer')):
            s = l_src(); mut(s)
            self.assertEqual(code_of(print_panels, s, 'cube.phases', 'subject', 'standard'), 'VP07_SOURCE_INVALID')

    def test_row6_layer_fields_in_older_source(self):
        s = l_src(); s['profile'] = P071
        self.assertEqual(code_of(print_panels, s, 'cube.phases', 'subject', 'standard'), 'VP07_SOURCE_INVALID')
        s = l_src(); s['profile'] = P071; del s['layer_order']; del s['layer_sequence']
        self.assertEqual(code_of(print_panels, s, 'cube.phases', 'subject', 'standard'), 'VP07_SOURCE_INVALID')  # item layer fields remain


class Rules(unittest.TestCase):
    def test_layer_partition_splits_large_layer_by_subject(self):
        src, _ = gold_src()
        rep, _ = print_panels(src, 'cube.phases', 'layer', 'standard')
        lay = {r['id']: r['layer'] for r in src['rows']}
        self.assertTrue(all(len({lay[r] for r in e['shown_row_ids']}) == 1 for e in rep['panel_ledger']))
        self.assertGreater(sum(1 for e in rep['panel_ledger'] if e['key_values'] == ['system']), 1)

    def test_nested_and_flow(self):
        src, _ = gold_src()
        with tempfile.TemporaryDirectory() as tmp:
            for k, args in enumerate((('cube.phases', 'layer,subject', 'standard'), ('cube.phases', 'track,layer', 'standard'),
                                      ('cube.flow', 'layer,subject', 'standard', 'cube.lens.execution'), ('cube.phases', 'step,layer', 'standard'))):
                rep, files = print_panels(src, *args)
                self.assertEqual(rep['coverage']['status'], 'COMPLETE', args)
                self.assertEqual(check_panels(publish_dir(files, Path(tmp)/str(k)))['status'], 'PASS')

    def test_lanes_unchanged_within_row(self):
        """D-6: layers order rows only; the cell order inside a row stays declared."""
        src, _ = gold_src()
        rep, files = print_panels(src, 'cube.phases', 'subject', 'detail')
        plan = json.loads(files['panel-01.input.json'])['plan']
        shop = [c['id'] for c in plan['cells'] if c['row'] == 'shop']
        self.assertEqual(shop, ['s1', 's2', 's3', 's4'])

    def test_no_layer_colour(self):
        src, _ = gold_src()
        _, files = print_panels(src, 'cube.phases', 'subject', 'detail')
        bands = [g for g in ET.fromstring(files['panel-01.svg']).iter(G) if g.get('data-vp07-layer')]
        self.assertEqual([b.get('data-vp07-layer') for b in bands], ['system', 'actor'])
        self.assertTrue(all(r.get('fill') == 'none' for b in bands for r in b.iter(f'{{{NS}}}rect')))

    def test_deterministic(self):
        a = print_panels(gold_src()[0], 'cube.phases', 'track,layer', 'standard')[1]
        b = print_panels(gold_src()[0], 'cube.phases', 'track,layer', 'standard')[1]
        self.assertEqual(a, b)


class Golden(unittest.TestCase):
    def test_golden(self):
        """VP072-06."""
        e = GOLD['expected']
        src, mapping = gold_src()
        self.assertEqual((len(src['cells']), len(GOLD['layers']['layer_order']), len(GOLD['tracks']['tracks'])),
                         (e['dependencies'], e['layers'], e['tracks']))
        self.assertEqual([r['id'] for r in src['rows']], e['row_order'])
        self.assertEqual(mapping['warnings'], e['unassigned'])
        rep, files = print_panels(src, 'cube.phases', 'track,layer', 'standard')
        x = e['track_layer_standard']
        self.assertEqual([o['outer_value'] for o in rep['outer_ledger']], x['outer_values'])
        self.assertEqual(rep['coverage']['status'], x['coverage'])
        self.assertTrue(all(len(p['layers']) == 1 for p in rep['panel_ledger']))
        rep, files = print_panels(src, 'cube.flow', 'subject', 'standard', 'cube.lens.execution')
        hit = next(p for p in rep['panel_ledger'] if p['step'] == 'p0' and p['key_values'] == ['shop'])
        order = json.loads(files[hit['panel']+'.input.json'])['job']['source_bundle']['view_plan']['order']
        self.assertEqual(order, e['flow_shop_p0']['order'])
        cap = next(g for g in ET.fromstring(files[hit['panel']+'.svg']).iter(G) if g.get('data-vp07-layers'))
        self.assertEqual(cap.get('data-vp07-layers').split(), e['flow_shop_p0']['caption'])

    def test_no_client_data(self):
        """VP072-07."""
        for f in [HERE/'fixtures/golden_v072.json', HERE/'fixtures/l01_l13_materialized.json', HERE/'oracles/independent_l01_l13.json']:
            t = f.read_text('utf-8')
            self.assertIsNone(re.search(r'@[a-z0-9-]+\.[a-z]{2,}', t), f.name)
            self.assertIsNone(re.search(r'https?://', t), f.name)


class Cli(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, '-m', 'vpmigration', *args], cwd=HERE, capture_output=True)

    def test_cli_layers(self):
        with tempfile.TemporaryDirectory() as tmp:
            t = Path(tmp)
            for name, doc in (('ctx', GOLD['context']), ('tracks', GOLD['tracks']), ('layers', GOLD['layers'])):
                (t/f'{name}.json').write_text(json.dumps(doc), 'utf-8')
            r = self.run_cli('from-plan', '--context', str(t/'ctx.json'), '--plan', 'mp-acme', '--tracks', str(t/'tracks.json'),
                             '--layers', str(t/'layers.json'), '--out', str(t/'src.json'))
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(json.loads((t/'src.json').read_text())['profile'], P072)
            r = self.run_cli('print-panels', '--source', str(t/'src.json'), '--view', 'cube.phases', '--partition', 'track,layer',
                             '--granularity', 'standard', '--out', str(t/'out'))
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(self.run_cli('check-panels', '--dir', str(t/'out')).returncode, 0)
            r = self.run_cli('from-plan', '--context', str(t/'ctx.json'), '--plan', 'mp-acme', '--layers', str(t/'layers.json'),
                             '--profile', P071, '--out', str(t/'bad.json'))
            self.assertEqual(r.returncode, 2); self.assertEqual(json.loads(r.stderr)['code'], 'VP07_ADAPTER_INPUT')


if __name__ == '__main__':
    unittest.main(verbosity=1)
