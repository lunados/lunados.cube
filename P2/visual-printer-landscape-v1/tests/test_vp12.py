"""VP-12 TASK-079: L-01…L-14 against oracles/independent_l01_l14.json (transcribed before code)."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from vplandscape.common import VP12Error, NS, PROFILE, sha_bytes  # noqa: E402
from vplandscape.source import from_plan  # noqa: E402
from vplandscape.landscape import render_landscape  # noqa: E402
from vplandscape.panels import print_panels, check_files  # noqa: E402
from vplandscape import api  # noqa: E402

ORACLE = json.loads((HERE/'oracles/independent_l01_l14.json').read_text('utf-8'))
FIX = json.loads((HERE/'fixtures/l01_l14_materialized.json').read_text('utf-8'))
CASES = {c['id']: c for c in FIX['cases']}
EXP = {o['id']: o for o in ORACLE['cases']}


def doc_of(i, locale='en'):
    c = CASES[i]
    return from_plan(c['context'], c['plan_id'], c['layers'], None, c['steps'], c['placement_predicates'], locale, c['granularity'])[0]


def run(i, locale='en'):
    return render_landscape(doc_of(i, locale))


def band(rep, step):
    return next(b for b in rep['bands'] if b['step'] == step)


def nodes(b):
    return [n for col in b['columns'].values() for n in col]


class Pins(unittest.TestCase):
    def test_oracle_pins_spec_and_fixture_pins_oracle(self):
        import hashlib
        self.assertEqual(ORACLE['spec_sha256'], hashlib.sha256((HERE/'VP12_ACCEPTANCE_SPEC.md').read_bytes()).hexdigest())
        self.assertEqual(FIX['oracle_sha256'], hashlib.sha256((HERE/'oracles/independent_l01_l14.json').read_bytes()).hexdigest())
        self.assertEqual(sorted(CASES), sorted(EXP))


class Vectors(unittest.TestCase):
    def test_l01_declared_layers(self):
        e = EXP['L-01']; rep, _ = run('L-01')
        self.assertEqual(rep['columns'], e['columns'])
        for eb in e['bands']:
            b = band(rep, eb['step'])
            self.assertEqual(b['columns'], eb['columns'])
            self.assertEqual([x['cell'] for x in b['edges']], eb['edges'])
        self.assertEqual(rep['warnings'], [])

    def test_l02_default_families(self):
        e = EXP['L-02']; rep, _ = run('L-02')
        self.assertEqual(rep['columns'], e['columns'])
        for col, want in e['column_order'].items():
            seen = list(dict.fromkeys(n for b in rep['bands'] for n in b['columns'][col]))
            self.assertEqual(sorted(seen, key=want.index), seen)
            self.assertEqual(set(seen), set(want))

    def test_l03_partial_layer(self):
        e = EXP['L-03']; rep, _ = run('L-03')
        self.assertEqual(rep['columns'], e['columns'])
        self.assertEqual(band(rep, 'beta')['columns']['unassigned'], e['band_beta_unassigned'])
        self.assertEqual(rep['warnings'], e['warnings'])

    def test_l04_three_bands(self):
        e = EXP['L-04']; rep, _ = run('L-04')
        self.assertEqual([b['step'] for b in rep['bands']], ['current', 'mvp', 'beta'])
        m = band(rep, 'mvp')
        self.assertEqual(sorted(nodes(m)), sorted(e['band_mvp']['nodes']))
        self.assertEqual([x['cell'] for x in m['edges']], e['band_mvp']['edges'])
        for step, want in e['markers'].items():
            self.assertEqual(band(rep, step)['markers'], want, step)

    def test_l05_l06_rejects(self):
        for i in ('L-05', 'L-06'):
            with self.assertRaises(VP12Error) as cm:
                run(i)
            self.assertEqual(cm.exception.code, EXP[i]['expected'], i)

    def edges(self, i):
        rep, _ = run(i)
        return {x['cell']: x for b in rep['bands'] for x in b['edges']}

    def test_l07_placement(self):
        ed = self.edges('L-07')
        self.assertEqual({k: v['placement'] for k, v in ed.items()}, EXP['L-07']['placement'])

    def test_l08_origin_styles(self):
        ed = self.edges('L-08')
        self.assertEqual({k: v['style'] for k, v in ed.items()}, EXP['L-08']['styles'])
        self.assertEqual({k: v['origin'] for k, v in ed.items()}, EXP['L-08']['origins'])

    def test_l08_svg_styles(self):
        _, svg = run('L-08')
        root = ET.fromstring(svg)
        for g in root.iter(f'{{{NS}}}g'):
            if g.get('data-edge-id'):
                style = EXP['L-08']['styles'][g.get('data-edge-id')]
                dash = {ln.get('stroke-dasharray') for ln in g.iter(f'{{{NS}}}line')}
                self.assertEqual(dash, {None} if style == 'solid' else {'8 5'} if style == 'dashed' else {'2 4'})

    def test_l09_markers_default_steps(self):
        rep, svg = run('L-09')
        for step, want in EXP['L-09']['markers'].items():
            self.assertEqual(band(rep, step)['markers'], want, step)
        root = ET.fromstring(svg)
        ret = [g for g in root.iter(f'{{{NS}}}g') if g.get('data-vp12-marker') == 'retired']
        self.assertEqual([g.get('data-vp12-node') for g in ret], ['res:mail-old'])
        self.assertEqual(ret[0].find(f'{{{NS}}}rect').get('stroke-dasharray'), '8 5')

    def test_l10_x_outside(self):
        rep, svg = run('L-10')
        self.assertEqual(rep['x_outside'], EXP['L-10']['x_outside'])
        drawn = {g.get('data-vp12-node') for g in ET.fromstring(svg).iter(f'{{{NS}}}g') if g.get('data-vp12-node')}
        self.assertFalse(drawn & set(EXP['L-10']['absent_nodes']))

    def test_l11_status_locale(self):
        for loc, want in EXP['L-11']['status'].items():
            rep, svg = run('L-11', loc)
            self.assertEqual(rep['crossing_status']['text'], want)
            self.assertIn(want, svg.decode('utf-8'))

    def test_l12_determinism_ledger(self):
        r1, s1 = run('L-12'); r2, s2 = run('L-12')
        self.assertEqual(s1, s2)
        root = ET.fromstring(s1)
        meta = [x for x in root.iter() if x.get('id') == 'vp12-landscape-ledger']
        led = json.loads(meta[0].text)
        self.assertEqual(led['units'], r1['units'])
        self.assertEqual(led['bands'], r1['bands'])
        self.assertEqual(len(r1['units']), len(set(r1['units'])))
        self.assertIn('EACH_UNIT_DRAWN_ONCE', r1['invariants_passed'])

    def test_l13_no_placement(self):
        self.assertEqual([k for k, v in self.edges('L-13').items() if v['placement']], EXP['L-13']['placement_true'])

    def test_l14_reversed_steps(self):
        r14, s14 = run('L-14'); r01, s01 = run('L-01')
        self.assertEqual([b['step'] for b in r14['bands']], EXP['L-14']['band_order'])
        self.assertEqual(r14['bands'], r01['bands'])
        self.assertEqual(s14, s01)


class Panels(unittest.TestCase):
    def test_print_check_roundtrip_and_tamper(self):
        rep, files = print_panels(doc_of('L-04', 'de'))
        self.assertEqual(rep['panel_count'], 1)
        self.assertEqual(check_files(files)['status'], 'PASS')
        bad = dict(files); bad['panel-01.svg'] = files['panel-01.svg'].replace(b'mail-new', b'mail-neu', 1)
        with self.assertRaises(VP12Error):
            check_files(bad)

    def test_api_roundtrip(self):
        src = api.source(CASES['L-01']['context'], 'pm-ls', CASES['L-01']['layers'])
        res = api.views(src['source'])
        self.assertEqual(res['printer'], 'vplandscape')
        self.assertEqual(api.check(res)['status'], 'PASS')

    def test_cli(self):
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            (t/'ctx.json').write_text(json.dumps(CASES['L-01']['context']))
            (t/'layers.json').write_text(json.dumps(CASES['L-01']['layers']))
            env = dict(cwd=str(HERE), capture_output=True)
            r = subprocess.run([sys.executable, '-m', 'vplandscape', 'from-plan', '--context', str(t/'ctx.json'), '--plan', 'pm-ls',
                                '--layers', str(t/'layers.json'), '--out', str(t/'in.json')], **env)
            self.assertEqual(r.returncode, 0, r.stderr)
            r = subprocess.run([sys.executable, '-m', 'vplandscape', 'print-panels', '--input', str(t/'in.json'), '--out', str(t/'out')], **env)
            self.assertEqual(r.returncode, 0, r.stderr)
            r = subprocess.run([sys.executable, '-m', 'vplandscape', 'check-panels', '--dir', str(t/'out')], **env)
            self.assertEqual(json.loads(r.stdout)['status'], 'PASS')
            r = subprocess.run([sys.executable, '-m', 'vplandscape', 'from-plan', '--context', str(t/'ctx.json'), '--plan', 'pm-ls',
                                '--steps', 'current,gamma', '--out', str(t/'in2.json')], **env)
            self.assertEqual(r.returncode, 2)
            self.assertEqual(json.loads(r.stderr)['code'], 'VP12_STEP_UNKNOWN')
            self.assertFalse((t/'in2.json').exists())


if __name__ == '__main__':
    unittest.main()
