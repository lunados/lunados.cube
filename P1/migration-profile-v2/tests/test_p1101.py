"""P1.10.1 local test suite. Fixed oracle expectations; no G5 mutation, no network."""
import copy, json, subprocess, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
for p in ('semantic-validator-v1', 'instantiation-profile-v1', 'simulation-profile-v1', 'comparison-profile-v1',
          'migration-profile-v1', 'migration-profile-v2'):
    sys.path.insert(0, str(ROOT/p))
sys.dont_write_bytecode = True
from cube_p1101.validator import P1101Validator, CODES  # noqa: E402
from cube_p1101.migration import project_v5  # noqa: E402
from cube_p110.validator import P110Validator  # noqa: E402

HERE = ROOT/'migration-profile-v2'
VEC = {c['id']: c for c in json.loads((HERE/'fixtures/g01_g10_materialized.json').read_text())['cases']}
ORACLE = {c['id']: c for c in json.loads((HERE/'oracles/independent_g01_g10.json').read_text())['cases']}
GOLD = {c['id']: c for c in json.loads((HERE/'fixtures/golden_gap_synthetic.json').read_text())['cases']}
MVEC = json.loads((ROOT/'migration-profile-v1/fixtures/m01_m22_materialized.json').read_text())['cases']
CVEC = json.loads((ROOT/'comparison-profile-v1/fixtures/c01_c20_materialized.json').read_text())['cases']
P110GOLD = json.loads((ROOT/'migration-profile-v1/fixtures/golden_migration_synthetic.json').read_text())['cases']
V = P1101Validator()
NOPROMO = ('epistemic_warrant', 'current_authority', 'canonical_admission')


def run(c, ctx=None):
    return V.validate_bytes(c['input_text'].encode(), context=ctx if ctx is not None else c['context'],
                            qualification_profiles=c.get('qualification_profiles'))


def codes(r): return [d['code'] for d in r['diagnostics']]


def base():
    return copy.deepcopy(VEC['G-01'])


class Oracle(unittest.TestCase):
    def test_vectors_match_independent_oracle(self):
        self.assertEqual(set(VEC), set(ORACLE)); self.assertEqual(len(VEC), 10)
        for i, c in sorted(VEC.items()):
            with self.subTest(id=i):
                o = ORACLE[i]
                self.assertEqual((c['expected_overall'], c['required_codes'], c['forbidden_codes']),
                                 (o['expected_overall'], o['required_codes'], o['forbidden_codes']))
                r = run(c)
                self.assertEqual(r['overall_status'], c['expected_overall'], r)
                for x in c['required_codes']: self.assertIn(x, codes(r))
                for x in c['forbidden_codes']: self.assertNotIn(x, codes(r))
                for k in NOPROMO: self.assertEqual(r[k], 'NOT_EVALUATED')
                if c['expected_overall'] == 'PASS': self.assertEqual(r['diagnostics'], [])


class Regression(unittest.TestCase):
    """P1.10.1-02, -06: /1…/5 byte-identical to P1.10; M-01…M-22 as /6 unchanged."""
    def _same(self, cases):
        p110 = P110Validator()
        for c in cases:
            with self.subTest(id=c['id']):
                a = b = None
                try: a = p110.validate_bytes(c['input_text'].encode(), input_format=c['input_format'], context=c['context'],
                                             qualification_profiles=c.get('qualification_profiles'))
                except ValueError as e: a = ('err', type(e).__name__)
                try: b = V.validate_bytes(c['input_text'].encode(), input_format=c['input_format'], context=c['context'],
                                          qualification_profiles=c.get('qualification_profiles'))
                except ValueError as e: b = ('err', type(e).__name__)
                self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))

    def test_m_vectors_v5(self): self._same(MVEC)
    def test_c_vectors_v4(self): self._same(CVEC)
    def test_p110_golden_v5(self): self._same(P110GOLD)

    def test_m_vectors_as_v6_identical_reports(self):
        p110 = P110Validator()
        for c in MVEC:
            if c['context']['format'] != 'aiaeao.cube.binding-context/5':
                continue
            with self.subTest(id=c['id']):
                c6 = copy.deepcopy(c['context']); c6['format'] = 'aiaeao.cube.binding-context/6'
                try: a = p110.validate_bytes(c['input_text'].encode(), context=c['context'], qualification_profiles=c.get('qualification_profiles'))
                except ValueError: a = 'err'
                try: b = V.validate_bytes(c['input_text'].encode(), context=c6, qualification_profiles=c.get('qualification_profiles'))
                except ValueError: b = 'err'
                self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))


class Rules(unittest.TestCase):
    def test_ends_reason_rejected_in_v5(self):
        c = base(); c['context']['format'] = 'aiaeao.cube.binding-context/5'
        c['context']['migration_plans'][0]['dependencies'][0]['ends_reason'] = 'scope_end'
        with self.assertRaises(ValueError): run(c)

    def test_ends_reason_shape(self):
        c = base(); c['context']['migration_plans'][0]['dependencies'][0]['ends_reason'] = ''
        with self.assertRaises(ValueError): run(c)
        c['context']['migration_plans'][0]['dependencies'][0]['ends_reason'] = 'x'*41
        with self.assertRaises(ValueError): run(c)

    def test_undeclared_reason_is_gap(self):
        c = base(); c['context']['migration_plans'][0]['dependencies'][0]['ends_reason'] = 'because'
        r = run(c); self.assertEqual(r['overall_status'], 'UNRESOLVED'); self.assertIn('P1_MIGRATION_DEPENDENCY_GAP', codes(r))

    def test_reason_without_witness_is_gap(self):
        c = base(); d = c['context']['migration_plans'][0]['dependencies'][0]
        d['ends_reason'] = 'other'; del d['witness_ref']
        r = run(c)
        self.assertIn('P1_MIGRATION_DEPENDENCY_GAP', codes(r)); self.assertIn('P1_EVALUATION_WITNESS_MISSING', codes(r))

    def test_successor_with_other_predicate_invalid(self):
        c = copy.deepcopy(VEC['G-08']); c['context']['migration_plans'][0]['dependencies'][1]['predicate_id'] = 'stores-in'
        r = run(c); self.assertEqual(r['overall_status'], 'FAIL'); self.assertIn('P1_MIGRATION_SUCCESSOR_INVALID', codes(r))

    def test_no_double_report_for_dangling(self):
        c = base(); mp = c['context']['migration_plans'][0]
        mp['transitions'] = [{'transition_id': 't', 'at_phase': 'p1', 'retires': ['mailbox-x'], 'introduces': [],
                              'T': {'role': 'scheduling'}, 'witness_ref': 'w'}]
        r = run(c)
        self.assertIn('P1_MIGRATION_DANGLING_DEPENDENCY', codes(r)); self.assertNotIn('P1_MIGRATION_DEPENDENCY_GAP', codes(r))

    def test_invalid_phases_skip_gap(self):
        c = base(); c['context']['migration_plans'][0]['phases'][3]['role'] = 'intermediate'
        r = run(c)
        self.assertIn('P1_MIGRATION_PHASES', codes(r)); self.assertNotIn('P1_MIGRATION_DEPENDENCY_GAP', codes(r))

    def test_deterministic_and_projection(self):
        c = base()
        self.assertEqual(run(c), run(copy.deepcopy(c)))
        c['context']['migration_plans'][0]['dependencies'][0]['ends_reason'] = 'other'
        p = project_v5(c['context'])
        self.assertEqual(p['format'], 'aiaeao.cube.binding-context/5')
        self.assertNotIn('ends_reason', p['migration_plans'][0]['dependencies'][0])

    def test_codes_registered(self):
        reg = json.loads((HERE/'DIAGNOSTIC_EXTENSION.json').read_text())
        self.assertEqual({x['code'] for x in reg['codes']}, {'P1_MIGRATION_DEPENDENCY_GAP'})


class Golden(unittest.TestCase):
    def test_golden(self):
        for gid, c in GOLD.items():
            with self.subTest(id=gid):
                r = run(c)
                self.assertEqual(r['overall_status'], c['expected_overall'])
                for x in c['required_codes']: self.assertIn(x, codes(r))
                if 'expected_gap_count' in c:
                    self.assertEqual(codes(r).count('P1_MIGRATION_DEPENDENCY_GAP'), c['expected_gap_count'])


class Schema(unittest.TestCase):
    def test_vectors_valid_against_context_v6_schema(self):
        import jsonschema, warnings
        warnings.simplefilter('ignore')
        s = json.loads((HERE/'context-v6.schema.json').read_text())
        s.pop('$id', None); s.pop('$schema', None)
        v = jsonschema.Draft7Validator(s)
        for i, c in sorted(VEC.items()):
            if c['context']['format'].endswith('/6'):
                with self.subTest(id=i): self.assertEqual([e.message for e in v.iter_errors(c['context'])], [])
        for c in GOLD.values():
            self.assertEqual(list(v.iter_errors(c['context'])), [])


if __name__ == '__main__':
    unittest.main(verbosity=1)
