"""VP-11 (instance view) local tests. Fixed oracle expectations; no network, no G5."""
import copy, hashlib, json, subprocess, sys, tempfile, unittest
from pathlib import Path
from xml.etree import ElementTree as ET
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE/'scripts')); sys.dont_write_bytecode = True
import run_vectors as RV  # noqa: E402
from vpinstances import api  # noqa: E402
from vpinstances.trace import from_trace, derived_trace, _result_shape  # noqa: E402
from vpinstances.view import render_instances  # noqa: E402
from vpinstances.common import VP09Error, NS, PROFILE, LOCALE_PINNED, sha_bytes  # noqa: E402

VEC = {c['id']: c for c in RV.VEC}
PY = sys.executable
LIB_SCHEMA = HERE.parents[2]/'lunados.lib/entries/analyze.trace-conformance/v1/schema/trace-conformance-result.v1.schema.json'
q = lambda t: f'{{{NS}}}{t}'  # noqa: E731


def code(fn):
    try:
        fn()
    except VP09Error as e:
        return e.code
    return None


def doc(cid, **kw):
    c = copy.deepcopy(VEC[cid]); c.update(kw)
    return from_trace(c['context'], c['trace'], c['records'])


class Vectors(unittest.TestCase):
    def test_i01_i34_match_oracle(self):
        for c in RV.VEC:
            with self.subTest(id=c['id']):
                ok, why = RV.check(c)
                self.assertTrue(ok, why)

    def test_vp10_0110_still_pinned(self):
        r = subprocess.run([PY, str(HERE/'scripts/pin_vp10_0110_digests.py')], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout+r.stderr)
        self.assertIn('15/15', r.stdout)


class Input(unittest.TestCase):
    def test_token_without_statement_counts(self):
        """TR-4: CF-13, a token at the gateway with no routing, yields the row {token, instance, at}."""
        d = doc('I-03')
        self.assertEqual(derived_trace(d['tokens'], d['statements']), [{'token': 'bpmn:i1/tok-route', 'instance': 'bpmn:i1', 'at': 'bpmn:xor'}])

    def test_conditions_are_not_compared(self):
        """RC-2: condition outcomes live only in the LIB call (P1.13 Q-6); the record still fits the trace."""
        self.assertTrue(any('conditions' in row for row in VEC['I-05']['records'][0]['call']['inputs']['trace']))
        self.assertEqual(len(doc('I-05')['records']), 1)

    def test_record_mismatch_on_coverage_and_flow(self):
        r = copy.deepcopy(VEC['I-01']['records']); r[0]['call']['inputs']['coverage'] = []
        self.assertEqual(code(lambda: doc('I-01', records=r)), 'VP11_RECORD_MISMATCH')
        r = copy.deepcopy(VEC['I-01']['records']); r[0]['call']['inputs']['control_flow']['gateways'][0]['outgoing'][0]['order'] = 2
        self.assertEqual(code(lambda: doc('I-01', records=r)), 'VP11_RECORD_MISMATCH')

    def test_result_shape_mutations(self):
        base = VEC['I-02']['records'][0]['result']
        for mut in (lambda x: x.update(status='PASS'), lambda x: x.update(value='nope'), lambda x: x.update(extra=1),
                    lambda x: x.pop('details'), lambda x: x.update(effectful_execution_authorized=True),
                    lambda x: x['details'][0].update(status='PASS'), lambda x: x.update(missing_scope={'needs': 'all', 'declarations': []})):
            res = copy.deepcopy(base); mut(res)
            with self.subTest(res=json.dumps(res)[:80]):
                self.assertFalse(_result_shape(res))
                r = copy.deepcopy(VEC['I-02']['records']); r[0]['result'] = res
                self.assertEqual(code(lambda: doc('I-02', records=r)), 'VP11_RECORD_INVALID')

    @unittest.skipUnless(LIB_SCHEMA.is_file(), 'lunados.lib checkout not next to lunados.cube')
    def test_hand_check_agrees_with_lib_schema(self):
        import jsonschema
        schema = json.loads(LIB_SCHEMA.read_text('utf-8'))
        v = jsonschema.Draft202012Validator(schema)
        results = [r['result'] for c in RV.VEC for r in c['records']]
        for res in results:
            self.assertTrue(_result_shape(res) and v.is_valid(res))
        for res in results[:6]:
            for k, val in (('status', 'UNRESOLVED'), ('runtime_authority', 'x'), ('activations', -1), ('foreign', ['a', 'a'])):
                bad = dict(copy.deepcopy(res), **{k: val})
                self.assertEqual(_result_shape(bad), v.is_valid(bad), k)


class Drawing(unittest.TestCase):
    def test_invariants(self):
        rep, _ = render_instances(doc('I-14'))
        for name in ('NO_ACTIVE_SVG_CONTENT_NO_PATTERN', 'EMBEDDED_LEDGER_MATCH', 'STATES_DIFFER_WITHOUT_COLOUR', 'VERDICTS_FROM_RECORDS_ONLY',
                     'MODEL_SEPARATE_FROM_TRACE'):
            self.assertIn(name, rep['invariants_passed'])

    def test_line_styles(self):
        _, svg = render_instances(doc('I-22'))
        style = {}
        for g in ET.fromstring(svg).iter(q('g')):
            st = g.get('data-vp11-state')
            if st and st != 'activation':
                style.setdefault(st, set()).add(g.find(q('line')).get('stroke-dasharray'))
        self.assertEqual(style, {'taken': {None}, 'not_taken': {'1 4'}, 'arrived': {None}, 'missing': {'1 4'}, 'token': {None}, 'no_token': {'1 4'}})

    def test_no_record_no_verdict(self):
        """D-5: without records every block reads "not checked" and nothing is hatched."""
        for cid in ('I-19', 'I-20', 'I-21'):
            rep, svg = render_instances(doc(cid))
            kinds = {v['kind'] for f in rep['frames'] for b in f['blocks'] for v in b['verdicts']}
            self.assertEqual((kinds, rep['violation_marks']), ({'not_checked'}, 0))
            self.assertNotIn(b'data-vp11-mark', svg)

    def test_foreign_only_on_missing_input(self):
        rep, _ = render_instances(doc('I-22'))
        rows = [r for f in rep['frames'] for b in f['blocks'] for r in b['rows'] if r.get('foreign')]
        self.assertEqual([(r['state'], r['foreign']) for r in rows], [('missing', ['bpmn:i1/tok-sd'])])

    def test_deterministic_and_locale(self):
        self.assertEqual(render_instances(doc('I-22'), 'de')[1], render_instances(doc('I-22'), 'de')[1])
        raw = (HERE/'vpinstances/locales/de.json').read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), LOCALE_PINNED['de'])
        self.assertEqual(code(lambda: render_instances(doc('I-01'), 'fr')), 'VP11_LOCALE_INVALID')

    def test_source_shape(self):
        d = doc('I-01'); d['extra'] = 1
        self.assertEqual(code(lambda: render_instances(d)), 'VP11_SOURCE_INVALID')


class G6AndCli(unittest.TestCase):
    def test_api_round_trip(self):
        c = VEC['I-22']
        src = api.source(copy.deepcopy(c['context']), copy.deepcopy(c['trace']), copy.deepcopy(c['records']))
        self.assertEqual(src['profile'], PROFILE)
        res = api.views(json.loads(json.dumps(src['source'])), locale='de')
        chk = api.check(json.loads(json.dumps(res)))
        self.assertEqual((chk['status'], chk['violation_marks']), ('PASS', 0))
        self.assertEqual(res['panels'][0]['svg'].encode('utf-8'), render_instances(doc('I-22'), 'de')[1])
        bad = json.loads(json.dumps(res)); bad['panels'][0]['svg'] += ' '
        self.assertEqual(code(lambda: api.check(bad)), 'VP11_PANEL_CHECK')
        self.assertEqual(code(lambda: api.views(src['source'], view='cube.cells')), 'VP11_VIEW_INVALID')

    def test_cli_from_trace_and_print(self):
        c = VEC['I-14']
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            (t/'ctx.json').write_text(json.dumps(c['context'])); (t/'trace.json').write_text(json.dumps(c['trace']))
            (t/'r1.json').write_text(json.dumps(c['records'][0]))
            r = subprocess.run([PY, '-m', 'vpinstances', 'from-trace', '--context', str(t/'ctx.json'), '--trace', str(t/'trace.json'),
                                '--record', str(t/'r1.json'), '--out', str(t/'in.json')], capture_output=True, cwd=HERE)
            self.assertEqual(r.returncode, 0, r.stderr)
            r = subprocess.run([PY, '-m', 'vpinstances', 'print-instances', '--input', str(t/'in.json'), '--out', str(t/'o')], capture_output=True, cwd=HERE)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual((t/'o/render.svg').read_bytes(), render_instances(doc('I-14'))[1])
            r = subprocess.run([PY, '-m', 'vpinstances', 'from-trace', '--context', str(t/'trace.json'), '--trace', str(t/'trace.json'),
                                '--out', str(t/'in2.json')], capture_output=True, cwd=HERE)
            self.assertEqual(r.returncode, 2)
            self.assertEqual(json.loads(r.stderr)['code'], 'VP11_ADAPTER_INPUT')
            r = subprocess.run([PY, '-m', 'vpinstances', 'capabilities'], capture_output=True, cwd=HERE)
            self.assertEqual(json.loads(r.stdout)['profile'], PROFILE)


if __name__ == '__main__':
    unittest.main()
