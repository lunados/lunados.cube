"""P1.9 local test suite. Fixed oracle expectations; no G5 mutation, no network."""
import copy, json, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
for p in ('semantic-validator-v1', 'instantiation-profile-v1', 'simulation-profile-v1', 'comparison-profile-v1'):
    sys.path.insert(0, str(ROOT/p))
sys.dont_write_bytecode = True
from cube_p19.validator import P19Validator
from cube_p19.comparison import ComparisonError, project_v3
from cube_p18.validator import P18Validator

HERE = ROOT/'comparison-profile-v1'
VEC = {c['id']: c for c in json.loads((HERE/'fixtures/c01_c20_materialized.json').read_text())['cases']}
ORACLE = {c['id']: c for c in json.loads((HERE/'oracles/independent_c01_c20.json').read_text())['cases']}
SVEC = json.loads((ROOT/'simulation-profile-v1/fixtures/s01_s17_materialized.json').read_text())['cases']
RVEC = json.loads((ROOT.parent/'P3/charge3-p16/fixtures/r01_r13_materialized.json').read_text())['cases']
P18GOLD = [json.loads((ROOT/'simulation-profile-v1/fixtures'/f).read_text()) for f in ('golden_exp010.json', 'golden_exp024.json')]
GOLDEN = sorted((HERE/'fixtures').glob('golden_*.json'))
V = P19Validator()
NOPROMO = ('epistemic_warrant', 'current_authority', 'canonical_admission')


def run(text, ctx):
    return V.validate_bytes(text.encode(), context=ctx)


def codes(r): return [d['code'] for d in r['diagnostics']]


def base():
    c = VEC['C-01']; return c['input_text'], copy.deepcopy(c['context'])


class Oracle(unittest.TestCase):
    def test_vectors_match_independent_oracle(self):
        self.assertEqual(set(VEC), set(ORACLE)); self.assertEqual(len(VEC), 20)
        for i, c in sorted(VEC.items()):
            with self.subTest(id=i):
                self.assertEqual((c['expected_overall'], c['required_codes']),
                                 (ORACLE[i]['expected_overall'], ORACLE[i]['required_codes']))
                if c['expected_overall'] == 'MCP_ERROR':
                    with self.assertRaises(ValueError): run(c['input_text'], c['context'])
                    continue
                r = run(c['input_text'], c['context'])
                self.assertEqual(r['overall_status'], c['expected_overall'], r)
                for code in c['required_codes']: self.assertIn(code, codes(r))
                for k in NOPROMO: self.assertEqual(r[k], 'NOT_EVALUATED')
                if c['expected_overall'] == 'PASS': self.assertEqual(r['diagnostics'], [])


class Regression(unittest.TestCase):
    """P1.9-02: /1, /2, /3 byte-identical to P1.8."""
    def test_lower_formats_identical_to_p18(self):
        p18 = P18Validator()
        cases = [(c['id'], c['input_text'], c['input_format'], c['context']) for c in RVEC + SVEC]
        cases += [(g['id'], g['input_text'], g['input_format'], g['context']) for g in P18GOLD]
        for cid, text, fmt, ctx in cases:
            with self.subTest(id=cid):
                try:
                    a = p18.validate_bytes(text.encode(), input_format=fmt, context=copy.deepcopy(ctx))
                except ValueError as e:
                    with self.assertRaises(type(e)): V.validate_bytes(text.encode(), input_format=fmt, context=copy.deepcopy(ctx))
                    continue
                b = V.validate_bytes(text.encode(), input_format=fmt, context=copy.deepcopy(ctx))
                self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))

    def test_projection_drops_only_v4_fields(self):
        _, ctx = base(); ctx['evaluation_records'] = [{'record_id': 'r', 'replay_of': 'x', 'output_digest': 'sha256:' + '0' * 64}]
        p = project_v3(ctx)
        self.assertEqual(p['format'], 'aiaeao.cube.binding-context/3')
        self.assertNotIn('comparisons', p); self.assertNotIn('comparison_protocols', p)
        self.assertEqual(p['evaluation_records'], [{'record_id': 'r'}])
        self.assertEqual(ctx['format'], 'aiaeao.cube.binding-context/4')   # input untouched


class Config(unittest.TestCase):
    """Invalid caller configuration is an MCP config error, never a semantic FAIL."""
    def bad(self, mutate):
        t, c = base(); mutate(c)
        with self.assertRaises(ComparisonError): run(t, c)

    def test_unknown_top_level(self): self.bad(lambda c: c.__setitem__('rankings', []))
    def test_bad_direction(self): self.bad(lambda c: c['comparison_protocols'][0]['criteria'][0].__setitem__('direction', 'up'))
    def test_aggregation_must_be_declared_pure_method(self):
        self.bad(lambda c: c['comparison_protocols'][0].__setitem__('aggregation', 'weighted.sum/v1'))
    def test_bad_role(self): self.bad(lambda c: c['comparisons'][0]['arms'][0].__setitem__('role', 'winner'))
    def test_shared_and_varied_overlap(self):
        self.bad(lambda c: c['comparisons'][0]['pairing']['varied_parameters'].append('seed_set'))
    def test_same_arm_twice_in_outcome(self): self.bad(lambda c: c['comparisons'][0]['outcomes'][0].__setitem__('b', 'trt'))
    def test_metric_id_and_metric_ids(self):
        self.bad(lambda c: c['comparisons'][0]['outcomes'][0].__setitem__('metric_ids', ['cost']))
    def test_interval_order(self):
        self.bad(lambda c: c['comparisons'][0]['outcomes'][0].__setitem__('statistic', {'kind': 'interval_a_minus_b', 'declared_value': [1, -1]}))
    def test_malformed_output_digest(self):
        def m(c):
            c['evaluation_records'] = [{'record_id': 'r', 'scenario_ref': 'sc-trt', 'evaluator_ref': 'e', 'method_id': 'compare.fixture-run/v1',
                                        'input_digest': 'sha256:' + '0' * 64, 'output_refs': ['ev-trt'], 'status': 'declared',
                                        'output_digest': 'md5:abc'}]
        self.bad(m)
    def test_self_replay(self):
        def m(c):
            c['evaluation_records'] = [{'record_id': 'r', 'scenario_ref': 'sc-trt', 'evaluator_ref': 'e', 'method_id': 'compare.fixture-run/v1',
                                        'input_digest': 'sha256:' + '0' * 64, 'output_refs': ['ev-trt'], 'status': 'declared', 'replay_of': 'r'}]
        self.bad(m)


class Rules(unittest.TestCase):
    def status(self, mutate):
        t, c = base(); mutate(c); r = run(t, c)
        for k in NOPROMO: self.assertEqual(r[k], 'NOT_EVALUATED')
        return r['overall_status'], codes(r)

    def test_mirrored_outcome_is_not_a_conflict(self):
        def m(c):
            o = copy.deepcopy(c['comparisons'][0]['outcomes'][0])
            o.update(outcome_id='o-2', a='ctl', b='trt', outcome='b_preferred'); o['statistic']['declared_value'] = 1.5
            c['comparisons'][0]['outcomes'].append(o)
        self.assertEqual(self.status(m), ('PASS', []))

    def test_mirrored_outcome_conflict(self):
        def m(c):
            o = copy.deepcopy(c['comparisons'][0]['outcomes'][0])
            o.update(outcome_id='o-2', a='ctl', b='trt', outcome='a_preferred'); o['statistic']['declared_value'] = -1.5
            c['comparisons'][0]['outcomes'].append(o)
        self.assertIn('P1_COMPARISON_OUTCOME_CONFLICT', self.status(m)[1])

    def test_higher_better_sign(self):
        def m(c): c['comparison_protocols'][0]['criteria'][0]['direction'] = 'higher_better'
        self.assertIn('P1_COMPARISON_OUTCOME_INCONSISTENT', self.status(m)[1])

    def test_interval_spanning_zero_allows_undetermined_only(self):
        def und(c): c['comparisons'][0]['outcomes'][0].update(outcome='undetermined_with_available_evidence',
                                                             statistic={'kind': 'interval_a_minus_b', 'declared_value': [-2.0, 0.5]})
        self.assertEqual(self.status(und), ('PASS', []))
        def pref(c): c['comparisons'][0]['outcomes'][0].update(statistic={'kind': 'interval_a_minus_b', 'declared_value': [-2.0, 0.5]})
        self.assertIn('P1_COMPARISON_OUTCOME_INCONSISTENT', self.status(pref)[1])

    def test_equivalence_inside_margin(self):
        def m(c):
            c['comparison_protocols'][0]['equivalence_margin'] = {'cost': 0.5}
            c['comparisons'][0]['outcomes'][0].update(outcome='equivalent_under_criteria', statistic={'kind': 'delta_a_minus_b', 'declared_value': 0.2})
        self.assertEqual(self.status(m), ('PASS', []))

    def test_ratio_sign(self):
        def m(c): c['comparisons'][0]['outcomes'][0]['statistic'] = {'kind': 'ratio_a_over_b', 'declared_value': 0.8}
        self.assertEqual(self.status(m), ('PASS', []))

    def test_direction_none_cannot_prefer(self):
        def m(c): c['comparison_protocols'][0]['criteria'][0]['direction'] = 'none'
        self.assertIn('P1_COMPARISON_OUTCOME_INVALID', self.status(m)[1])

    def test_required_parity_missing_then_present(self):
        def miss(c): c['comparison_protocols'][0]['required_parity'] = ['coverage']
        self.assertEqual(self.status(miss)[0], 'UNRESOLVED')
        def ok(c):
            miss(c); c['comparisons'][0]['parity'] = [{'parity_id': 'p', 'kind': 'coverage', 'witness_ref': 'w:cov'}]
        self.assertEqual(self.status(ok), ('PASS', []))

    def test_outcome_witness_required(self):
        def m(c): del c['comparisons'][0]['outcomes'][0]['witness_ref']
        self.assertEqual(self.status(m), ('UNRESOLVED', ['P1_EVALUATION_WITNESS_MISSING']))

    def test_scope_must_be_declared_level(self):
        def m(c): c['comparisons'][0]['outcomes'][0]['scope'] = {'depth': 4}
        self.assertIn('P1_COMPARISON_OUTCOME_INVALID', self.status(m)[1])

    def test_mixed_modes(self):
        def m(c): c['scenarios'][1]['mode'] = 'replay'
        self.assertIn('P1_COMPARISON_PAIRING', self.status(m)[1])

    def test_unknown_protocol(self):
        def m(c): c['comparisons'][0]['protocol_ref'] = 'cp-x'
        self.assertEqual(self.status(m)[0], 'UNRESOLVED')

    def test_replay_of_requires_replay_mode(self):
        t, c = copy.deepcopy(VEC['C-16']['input_text']), copy.deepcopy(VEC['C-16']['context'])
        for s in c['scenarios']: s['mode'] = 'simulation'
        r = run(t, c); self.assertEqual(r['overall_status'], 'FAIL'); self.assertIn('P1_SCENARIO_MODE', codes(r))


class Schema(unittest.TestCase):
    def test_vectors_valid_against_context_v4_schema(self):
        try:
            import jsonschema
            jsonschema.Draft202012Validator
        except (ImportError, AttributeError):
            self.skipTest('jsonschema >= 4.18 required')
        s = json.loads((HERE/'context-v4.schema.json').read_text())
        v = jsonschema.Draft202012Validator(s)
        for i, c in VEC.items():
            if i == 'C-20': continue
            with self.subTest(id=i):
                self.assertEqual(list(v.iter_errors(c['context'])), [])

    def test_reports_valid_against_frozen_report_schema(self):
        try:
            import jsonschema
            jsonschema.Draft202012Validator
        except (ImportError, AttributeError):
            self.skipTest('jsonschema with Draft 2020-12 not installed')
        s = json.loads((ROOT/'semantic-validator-v1/baseline/P1_1_Contract_Freeze/contract/report.schema.json').read_text())
        v = jsonschema.Draft202012Validator(s)
        for i, c in VEC.items():
            if c['expected_overall'] == 'MCP_ERROR': continue
            with self.subTest(id=i):
                self.assertEqual([e.message for e in v.iter_errors(run(c['input_text'], c['context']))], [])


class Golden(unittest.TestCase):
    """P1.9-15: golden comparisons PASS; and they are not trivially passing."""
    def test_goldens_pass(self):
        if not GOLDEN: self.skipTest('no golden fixtures yet')
        for f in GOLDEN:
            g = json.loads(f.read_text())
            with self.subTest(golden=f.name):
                r = V.validate_bytes(g['input_text'].encode(), input_format=g['input_format'], context=g['context'])
                self.assertEqual(r['overall_status'], g['expected_overall'], r['diagnostics'])
                for k in NOPROMO: self.assertEqual(r[k], 'NOT_EVALUATED')

    def test_goldens_negative_controls(self):
        if not GOLDEN: self.skipTest('no golden fixtures yet')
        for f in GOLDEN:
            g = json.loads(f.read_text())
            def go(mutate):
                c = copy.deepcopy(g['context']); mutate(c)
                return V.validate_bytes(g['input_text'].encode(), input_format=g['input_format'], context=c)
            with self.subTest(golden=f.name, control='flip first outcome'):
                def flip(c):
                    o = c['comparisons'][0]['outcomes'][0]
                    o['outcome'] = {'a_preferred': 'b_preferred', 'b_preferred': 'a_preferred'}.get(o['outcome'], 'a_preferred')
                r = go(flip); self.assertEqual(r['overall_status'], 'FAIL')
                self.assertTrue({'P1_COMPARISON_OUTCOME_INCONSISTENT', 'P1_COMPARISON_OUTCOME_INVALID'} & set(codes(r)))
            with self.subTest(golden=f.name, control='confound arms'):
                def conf(c):
                    sc = {s['scenario_id']: s for s in c['scenarios']}
                    sc[c['comparisons'][0]['arms'][1]['scenario_ref']].setdefault('parameters', {})['hidden_change'] = 1
                r = go(conf); self.assertIn('P1_COMPARISON_CONFOUNDED', codes(r))


if __name__ == '__main__':
    unittest.main(verbosity=1)
