import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('runner', ROOT/'scripts/research/comparison_runner.py')
r = importlib.util.module_from_spec(spec); spec.loader.exec_module(r)
FIX = ROOT/'docs/09-Research/analysis-readiness/cases'

class RunnerTests(unittest.TestCase):
    def test_all_fixtures_verified_against_archive(self):
        self.assertEqual({r.load_case(p,ROOT)['expected']['domain_status'] for p in FIX.glob('*.json')}, {'PASS','FAIL','UNRESOLVED'})

    def test_missing_binding_refused_before_invocation(self):
        case=json.loads((FIX/'P1-mode-display.json').read_text()); del case['bindings']['qualification_profiles_sha256']
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'case.json'; path.write_text(json.dumps(case))
            with self.assertRaisesRegex(ValueError,'binding'):
                r.load_case(path,ROOT)

    def test_changed_input_refused_even_if_hash_is_recomputed(self):
        case=json.loads((FIX/'P1-mode-display.json').read_text()); case['arguments']['input_text']='changed'; case['arguments_sha256']=r.digest(case['arguments'])
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'case.json'; path.write_text(json.dumps(case))
            with self.assertRaisesRegex(ValueError,'origin extraction'):
                r.load_case(path,ROOT)

    def test_domain_fail_is_expected_without_promoting_other_dimensions(self):
        case=r.load_case(FIX/'P1-method-arity-negative.json',ROOT)
        raw={'isError':False,'structuredContent':{'report':{'overall_status':'FAIL','diagnostics':[{'code':'P1_METHOD_SIGNATURE'}]}}}
        untouched=copy.deepcopy(raw); result=r.assess(case,raw)
        self.assertTrue(result['expectation_match']); self.assertEqual(result['domain_status'],'FAIL')
        self.assertEqual(result['dimensions']['visualization']['assessment'],'NOT_ASSESSED')
        self.assertEqual(result['dimensions']['utility']['assessment'],'NOT_ASSESSED'); self.assertEqual(raw,untouched)

    def test_tool_error_never_uses_embedded_domain_pass(self):
        result=r.interpret({'isError':True,'structuredContent':{'code':'P1_MCP_CONFIG_INVALID','report':{'overall_status':'PASS'}}})
        self.assertEqual(result['invocation_status'],'TOOL_ERROR'); self.assertIsNone(result['domain_status'])

    def test_malformed_response_is_not_success(self):
        for raw in ({}, {'isError':False}, {'isError':False,'structuredContent':{'report':{'overall_status':'PASS','diagnostics':None}}}):
            self.assertEqual(r.interpret(raw)['invocation_status'],'MALFORMED_RESPONSE')

    def test_run_metadata_is_excluded_from_semantic_comparison(self):
        base={'invocation_status':'RETURNED','domain_status':'UNRESOLVED','diagnostic_codes':['P1_QUALIFIER_PROFILE_MISSING'],'expectation_match':True,'run_id':'a'}
        changed={**base,'run_id':'b','at':'later'}
        self.assertEqual(r.semantic_signature(base),r.semantic_signature(changed))
        changed['domain_status']='PASS';self.assertNotEqual(r.semantic_signature(base),r.semantic_signature(changed))

    def test_existing_result_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'result.json';p.write_text('original')
            with self.assertRaises(FileExistsError):r.write_json(p,{'replacement':True})
            self.assertEqual(p.read_text(),'original')

class ComparisonTests(unittest.TestCase):
    def test_only_profile_addition_between_frozen_mode_cases(self):
        a = r.load_case(FIX/'P1-mode-unbound.json', ROOT)
        b = r.load_case(FIX/'P1-mode-display.json', ROOT)
        changes = r.argument_differences(a['arguments'], b['arguments'])
        self.assertEqual([c['pointer'] for c in changes], ['/qualification_profiles'])
        self.assertFalse(changes[0]['before_present']); self.assertTrue(changes[0]['after_present'])

    def test_absence_and_null_remain_distinct_and_pointer_is_escaped(self):
        changes = r.argument_differences({}, {'a/b~c': None})
        self.assertEqual(changes[0]['pointer'], '/a~1b~0c')
        self.assertFalse(changes[0]['before_present']); self.assertIsNone(changes[0]['after'])
        self.assertTrue(r.argument_differences({'x': True}, {'x': 1}))

    def test_comparison_keeps_distinct_hashes_and_observations(self):
        a = r.load_case(FIX/'P1-mode-unbound.json', ROOT)
        b = r.load_case(FIX/'P1-mode-display.json', ROOT)
        observations = [{'case_id': c['case_id'], 'invocation_status':'RETURNED',
                         'domain_status': c['expected']['domain_status'],
                         'diagnostic_codes': c['expected']['diagnostic_codes'], 'expectation_match':True} for c in (a,b)]
        report = {'cases':[a,b], 'runs':[{'run_id':'synthetic-unit-test','cases':observations}]}
        result = r.compare_cases(report, a['case_id'], b['case_id'])
        self.assertNotEqual(result['baseline_arguments_sha256'],result['variant_arguments_sha256'])
        self.assertEqual(result['observations'][0]['baseline']['domain_status'], 'UNRESOLVED')
        self.assertEqual(result['observations'][0]['variant']['domain_status'], 'PASS')
        with self.assertRaises(ValueError):r.compare_cases(report,a['case_id'],a['case_id'])

AUTH = ROOT/'docs/09-Research/grammar-sampling/cases'
PILOT = AUTH/'A-PILOT-01-relation-declared.json'

def _load_modified(mutate):
    case = json.loads(PILOT.read_text()); mutate(case)
    with tempfile.TemporaryDirectory() as d:
        path = Path(d)/'case.json'; path.write_text(json.dumps(case))
        return r.load_case(path, ROOT)

class AuthoredCaseTests(unittest.TestCase):
    def test_pilot_loads_as_authored_with_fixed_expectation(self):
        case = r.load_case(PILOT, ROOT)
        self.assertEqual(case['origin']['kind'], 'authored_synthetic')
        self.assertTrue(case['expected']['fixed_before_execution'])
        self.assertTrue(r.is_executable(case))

    def test_v1_cases_still_load_unchanged(self):
        for p in FIX.glob('*.json'):
            self.assertEqual(r.load_case(p, ROOT)['format'], r.CASE_FORMAT)

    def test_missing_provenance_refused(self):
        for key in ('rule_refs', 'source_register', 'profile_revision', 'authored_at'):
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'provenance'):
                _load_modified(lambda c: c['origin'].pop(key))

    def test_manipulated_input_refused(self):
        def change(c): c['arguments']['input_text'] = c['arguments']['input_text'].replace('references', 'depends_on')
        with self.assertRaisesRegex(ValueError, 'digest'):
            _load_modified(change)

    def test_changed_context_refused_even_with_recomputed_argument_hash(self):
        def change(c):
            c['arguments']['context']['predicate_contracts'] = []; c['arguments_sha256'] = r.digest(c['arguments'])
        with self.assertRaisesRegex(ValueError, 'binding: context'):
            _load_modified(change)

    def test_stale_register_hash_refused(self):
        with self.assertRaisesRegex(ValueError, 'register hash'):
            _load_modified(lambda c: c['origin']['source_register'].update(sha256='0'*64))

    def test_unknown_rule_and_matrix_case_refused(self):
        with self.assertRaisesRegex(ValueError, 'rule reference'):
            _load_modified(lambda c: c['origin'].update(rule_refs=['R-XX-9']))
        with self.assertRaisesRegex(ValueError, 'Cube rule reference'):
            _load_modified(lambda c: c['origin'].update(rule_refs=['cube:does/not/exist.md#1']))
        with self.assertRaisesRegex(ValueError, 'matrix case'):
            _load_modified(lambda c: c['origin'].update(matrix_case='C4-99'))
        self.assertEqual(_load_modified(lambda c: c['origin'].update(matrix_case='C4-01'))['origin']['matrix_case'], 'C4-01')

    def test_historical_origin_cannot_be_claimed(self):
        with self.assertRaisesRegex(ValueError, 'historical probe'):
            _load_modified(lambda c: c['origin'].update(probe_id='P1-relation-profile-missing'))
        with self.assertRaisesRegex(ValueError, 'authored_synthetic'):
            _load_modified(lambda c: c['origin'].update(kind='historical_exact'))

    def test_expectation_must_be_fixed_and_justified(self):
        with self.assertRaisesRegex(ValueError, 'fixed before'):
            _load_modified(lambda c: c['expected'].pop('fixed_before_execution'))
        with self.assertRaisesRegex(ValueError, 'rationale'):
            _load_modified(lambda c: c['expected'].update(rationale=' '))

    def test_non_executable_case_is_documented_not_invoked(self):
        def manual(c):
            for k in ('operation', 'arguments', 'arguments_sha256', 'bindings'): c.pop(k)
            c['invocation_kind'] = 'not_executable'
            c['non_execution'] = {'reason': 'Kein lokaler Prüfer für Token-Korrelation; Quellenanalyse im Fallbericht.'}
            c['expected'].update(domain_status=None, diagnostic_codes=[])
        case = _load_modified(manual)
        self.assertFalse(r.is_executable(case))
        result = r.not_executed(case)
        self.assertEqual(result['invocation_status'], 'NOT_EXECUTED'); self.assertIsNone(result['domain_status'])
        self.assertIsNone(result['expectation_match'])
        self.assertEqual(result['dimensions']['implemented_validation']['assessment'], 'NOT_ASSESSED')

    def test_non_executable_case_cannot_carry_an_invented_call_or_status(self):
        def bad(c):
            c['invocation_kind'] = 'not_executable'; c['non_execution'] = {'reason': 'x'}
        with self.assertRaisesRegex(ValueError, 'no operation'):
            _load_modified(bad)

if __name__=='__main__':unittest.main()
