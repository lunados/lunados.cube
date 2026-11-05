"""VP-09.3 (TASK-078): X × Y from declared P1.6 instances, crossing status; independent oracle X-01…X-12."""
import hashlib
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True
from vpaxes.source import from_plan  # noqa: E402
from vpaxes.axes import render_axes  # noqa: E402
from vpaxes.panels import print_panels  # noqa: E402
from vpaxes.common import VP09Error, LOCALE_0093, P093, PROFILES  # noqa: E402

ORACLE_DOC = json.loads((HERE/'oracles/independent_x01_x12.json').read_text('utf-8'))
ORACLE = {c['id']: c for c in ORACLE_DOC['cases']}
VEC = json.loads((HERE/'fixtures/x01_x12_materialized.json').read_text('utf-8'))


def run(c):
    doc, _ = from_plan(c['context'], c['plan_id'], profile=c['profile'])
    if c.get('input_profile'):
        doc = {k: v for k, v in doc.items() if k not in ('x_instances', 'x_report')}
        doc['profile'] = c['input_profile']
    return render_axes(doc, c['rows'], c['cols'], c['granularity'], locale=c['locale'])


class VP093(unittest.TestCase):
    def test_oracle_pins(self):
        self.assertEqual(ORACLE_DOC['spec_sha256'], hashlib.sha256((HERE/'VP09_3_ACCEPTANCE_SPEC.md').read_bytes()).hexdigest())
        self.assertEqual(VEC['oracle_sha256'], hashlib.sha256((HERE/'oracles/independent_x01_x12.json').read_bytes()).hexdigest())
        self.assertEqual(set(ORACLE), {c['id'] for c in VEC['cases']})

    def test_vectors(self):
        for c in VEC['cases']:
            o = ORACLE[c['id']]
            with self.subTest(id=c['id']):
                if o['expected'] != 'PASS':
                    with self.assertRaises(VP09Error) as e:
                        run(c)
                    self.assertEqual(e.exception.code, o['expected'])
                    continue
                rep, svg = run(c)
                self.assertEqual(rep['render_status'], 'PASS')
                if 'cells' in o:
                    self.assertEqual(rep['cells'], o['cells'])
                for k, v in o.get('report', {}).items():
                    self.assertEqual(rep[k], v)
                for w in o.get('warnings', []):
                    self.assertIn(w, [x['code'] for x in rep['warnings']])
                if 'status_line' in o:
                    self.assertIn(o['status_line'].encode('utf-8'), svg)
                for k, v in o.get('x_coverage', {}).items():
                    self.assertEqual(rep['x_coverage'][k], v)
                for f in ('epistemic_warrant', 'current_authority', 'canonical_admission'):
                    self.assertEqual(rep[f], 'NOT_EVALUATED')

    def test_status_on_every_093_panel_and_deterministic(self):
        c = VEC['cases'][0]
        doc, _ = from_plan(c['context'], c['plan_id'], profile=P093)
        r1, f1 = print_panels(doc, 'X', 'Y:kind', 'detail')
        r2, f2 = print_panels(doc, 'X', 'Y:kind', 'detail')
        self.assertEqual(f1, f2)
        self.assertEqual(r1['crossing_status'], {'status': 'canonical', 'source': 'Morphology §3.3'})
        self.assertEqual(r1['x_coverage']['status'], 'COMPLETE')
        for name, b in f1.items():
            if name.startswith('panel-') and name.endswith('.svg'):
                self.assertIn(b'X \xc3\x97 Y \xc2\xb7 canonical', b)

    def test_locale_pin_and_profiles(self):
        raw = (HERE/'vpaxes/locales/de-0093.json').read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), LOCALE_0093['de'])
        self.assertEqual(PROFILES[-1], P093)


if __name__ == '__main__':
    unittest.main()
