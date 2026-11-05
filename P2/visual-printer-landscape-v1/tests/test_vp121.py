"""VP-12.1 (MILE-018 E18-1): LA-01…LA-06 against oracles/independent_la01_la06.json, 0.12.0 byte-identical."""
import hashlib
import json
import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE/'tests'))
from test_vp12 import CASES, doc_of  # noqa: E402
from vplandscape.common import VP12Error, NS  # noqa: E402
from vplandscape.source import from_plan  # noqa: E402
from vplandscape.landscape import render_landscape  # noqa: E402
from vplandscape.panels import print_panels, check_files  # noqa: E402

ORACLE = json.loads((HERE/'oracles/independent_la01_la06.json').read_text('utf-8'))
EXP = {c['id']: c for c in ORACLE['cases']}
REG = json.loads((HERE/'fixtures/regression_0120_digests.json').read_text('utf-8'))['cases']


def doc121(base, profile='P2-VP-LANDSCAPE/0.12.1', locale='en'):
    c = CASES[base]
    return from_plan(c['context'], c['plan_id'], c['layers'], None, c['steps'], c['placement_predicates'], locale, c['granularity'], profile)[0]


def headers(svg):
    return [(g.get('data-vp12-column-header'), g.get('data-anchor-id'), [t.text for t in g.iter(f'{{{NS}}}text')])
            for g in ET.fromstring(svg).iter(f'{{{NS}}}g') if g.get('data-vp12-column-header')]


class Pins(unittest.TestCase):
    def test_pins(self):
        self.assertEqual(ORACLE['spec_sha256'], hashlib.sha256((HERE/'VP12_1_ACCEPTANCE_SPEC.md').read_bytes()).hexdigest())
        self.assertEqual(ORACLE['regression_digests_sha256'], hashlib.sha256((HERE/'fixtures/regression_0120_digests.json').read_bytes()).hexdigest())


class Vectors(unittest.TestCase):
    def check_headers(self, cid):
        e = EXP[cid]
        rep, svg = render_landscape(doc121(e['base']))
        h = headers(svg)
        self.assertEqual([x[0] for x in h], e['headers'])
        self.assertTrue(all(x[1] == ORACLE['anchor'] and x[2][0] == ORACLE['glyph'] for x in h))
        return rep, svg

    def test_la01(self):
        rep, svg = self.check_headers('LA-01')
        self.assertEqual(rep['column_anchor'], EXP['LA-01']['column_anchor'])
        self.assertIn(EXP['LA-01']['invariant'], rep['invariants_passed'])
        meta = [x for x in ET.fromstring(svg).iter() if x.get('id') == 'vp12-landscape-ledger'][0]
        self.assertEqual(json.loads(meta.text)['column_anchor'], ORACLE['anchor'])

    def test_la02_la03(self):
        self.check_headers('LA-02')
        self.check_headers('LA-03')

    def test_la04_same_units(self):
        new, _ = render_landscape(doc121('L-01'))
        old, _ = render_landscape(doc_of('L-01'))
        for k in EXP['LA-04']['same_as_0120']:
            self.assertEqual(new[k], old[k], k)

    def test_la05_0120_byte_identical(self):
        n = 0
        for key, want in REG.items():
            cid, loc = key.split('|')
            doc = doc_of(cid, loc)
            _, svg = render_landscape(doc)
            _, files = print_panels(doc)
            self.assertEqual(hashlib.sha256(svg).hexdigest(), want['svg'], key)
            self.assertEqual({k: hashlib.sha256(v).hexdigest() for k, v in files.items()}, want['files'], key)
            self.assertEqual(headers(svg), [], key)
            n += 1
        self.assertEqual(n, len(REG))

    def test_la06_unknown_profile(self):
        with self.assertRaises(VP12Error) as cm:
            doc121('L-01', EXP['LA-06']['profile'])
        self.assertEqual(cm.exception.code, EXP['LA-06']['expected'])

    def test_panels_roundtrip_0121(self):
        rep, files = print_panels(doc121('L-04', locale='de'))
        self.assertEqual(rep['profile'], 'P2-VP-LANDSCAPE/0.12.1')
        self.assertEqual(check_files(files)['status'], 'PASS')


if __name__ == '__main__':
    unittest.main()
