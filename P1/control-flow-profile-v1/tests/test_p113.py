"""P1.13 oracle, shape, semantic rows, golden and byte-for-byte regression checks."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / 'control-flow-profile-v1'
for name in ('semantic-validator-v1', 'instantiation-profile-v1', 'simulation-profile-v1',
             'comparison-profile-v1', 'migration-profile-v1', 'migration-profile-v2',
             'migration-methods-v1', 'coverage-instance-profile-v1', 'control-flow-profile-v1'):
    sys.path.insert(0, str(ROOT / name))
sys.path.insert(0, str(HERE / 'scripts'))
sys.dont_write_bytecode = True
import jsonschema  # noqa: E402
import run_vectors as RV  # noqa: E402
from cube_p112.validator import P112Validator  # noqa: E402
from cube_p113.control_flow import project_v8  # noqa: E402
from cube_p113.validator import CODES, PROFILE, P113Validator  # noqa: E402

V = P113Validator()
VEC = {case['id']: case for case in RV.VEC}
ORACLE = RV.ORACLE
GOLDEN = json.loads((HERE / 'fixtures/golden_control_flow.json').read_text('utf-8'))['cases'][0]
PREVIOUS = []
for path in ('migration-profile-v1/fixtures/m01_m22_materialized.json',
             'comparison-profile-v1/fixtures/c01_c20_materialized.json',
             'migration-profile-v2/fixtures/g01_g10_materialized.json',
             'migration-methods-v1/fixtures/f01_f16_materialized.json',
             'migration-methods-v1/fixtures/golden_methods_synthetic.json',
             'coverage-instance-profile-v1/fixtures/k01_k21_materialized.json'):
    PREVIOUS += json.loads((ROOT / path).read_text('utf-8'))['cases']


def clone(id):
    return copy.deepcopy(VEC[id])


def run(case):
    return V.validate_bytes(case['input_text'].encode(), input_format=case['input_format'],
                            context=case['context'], qualification_profiles=case.get('qualification_profiles'))


def codes(report):
    return [d['code'] for d in report['diagnostics']]


class Oracle(unittest.TestCase):
    def test_fixed_expectations(self):
        self.assertEqual(set(VEC), set(ORACLE))
        self.assertEqual(len(VEC), 9)
        for id, case in VEC.items():
            with self.subTest(id=id):
                expected = ORACLE[id]
                self.assertEqual((case['expected_overall'], case['required_codes'], case['forbidden_codes']),
                                 (expected['expected_overall'], expected['required_codes'], expected['forbidden_codes']))
                report = run(case)
                self.assertEqual(report['overall_status'], expected['expected_overall'], report)
                for code in expected['required_codes']:
                    self.assertIn(code, codes(report))
                for code in expected['forbidden_codes']:
                    self.assertNotIn(code, codes(report))
                for key in RV.NOPROMO:
                    self.assertEqual(report[key], 'NOT_EVALUATED')
                if expected['expected_overall'] == 'PASS':
                    self.assertEqual(report['diagnostics'], [])


class StatusRows(unittest.TestCase):
    def test_invalid_exclusive_declarations(self):
        for id in ('KF-02', 'KF-03'):
            self.assertIn('P1_CONTROL_FLOW_INVALID', codes(run(VEC[id])))
        case = clone('KF-01')
        case['context']['control_flow']['gateways'][0]['outgoing'][0].pop('order')
        self.assertIn('P1_CONTROL_FLOW_INVALID', codes(run(case)))

    def test_invalid_parallel_declarations(self):
        self.assertIn('P1_CONTROL_FLOW_INVALID', codes(run(VEC['KF-04'])))
        for field, value in (('order', 1), ('condition_ref', 'model:condition')):
            case = clone('KF-01')
            case['context']['control_flow']['gateways'][2]['outgoing'][0][field] = value
            self.assertIn('P1_CONTROL_FLOW_INVALID', codes(run(case)))

    def test_flow_ownership(self):
        for side, first, second in (('outgoing', 0, 1), ('incoming', 1, 2)):
            case = clone('KF-01')
            gateways = case['context']['control_flow']['gateways']
            value = gateways[first][side][0]
            gateways[second][side].append(copy.deepcopy(value))
            self.assertIn('P1_CONTROL_FLOW_INVALID', codes(run(case)))

    def test_unsupported_gateway_is_unresolved(self):
        report = run(VEC['KF-05'])
        self.assertEqual((report['overall_status'], codes(report)),
                         ('UNRESOLVED', ['P1_CONTROL_FLOW_UNSUPPORTED']))
        case = clone('KF-05')
        case['input_text'] = ('rel("onFlow",Y:α:Evidence["bpmn:i1/tok-route"],'
                              'Y:α:WorkItem["bpmn:f-manual"])')
        contract = copy.deepcopy(VEC['KF-07']['context']['predicate_contracts'][-1])
        case['context']['predicate_contracts'].append(contract)
        self.assertEqual(codes(run(case)), ['P1_CONTROL_FLOW_UNSUPPORTED'])

    def test_routing_and_on_flow_are_bound(self):
        for id in ('KF-06', 'KF-07'):
            report = run(VEC[id])
            self.assertEqual((report['overall_status'], codes(report)), ('FAIL', ['P1_FLOW_UNDECLARED']))
        case = clone('KF-01')
        token = next(r for r in case['context']['referents'] if r['ref'] == 'bpmn:i1/tok-route')
        token['at_gateway'] = 'bpmn:split'
        self.assertIn('P1_FLOW_UNDECLARED', codes(run(case)))

    def test_missing_position_is_unresolved(self):
        report = run(VEC['KF-09'])
        self.assertEqual((report['overall_status'], codes(report)),
                         ('UNRESOLVED', ['P1_TOKEN_POSITION_UNDECLARED']))

    def test_predicate_without_role_is_unchanged(self):
        case = clone('KF-06')
        for predicate in case['context']['predicate_contracts']:
            predicate.pop('control_flow_role', None)
        self.assertEqual((run(case)['overall_status'], codes(run(case))), ('PASS', []))

    def test_unresolved_referents(self):
        for path, field, value in ((0, 'gateway', 'bpmn:unknown-gateway'),
                                   (0, 'incoming', 'bpmn:unknown-flow'),
                                   (0, 'target', 'bpmn:unknown-target')):
            case = clone('KF-01')
            g = case['context']['control_flow']['gateways'][path]
            if field == 'gateway': g['gateway'] = value
            elif field == 'incoming': g['incoming'][0] = value
            else: g['outgoing'][0]['target'] = value
            self.assertIn('P1_BINDING_CONTEXT_REQUIRED', codes(run(case)))
        case = clone('KF-01')
        token = next(r for r in case['context']['referents'] if r['ref'] == 'bpmn:i1/tok-route')
        token['at_gateway'] = 'bpmn:unknown-gateway'
        self.assertIn('P1_BINDING_CONTEXT_REQUIRED', codes(run(case)))

    def test_malformed_fields_are_configuration_errors(self):
        for edit in (
            lambda c: c['context'].update(control_flow=None),
            lambda c: c['context']['control_flow']['gateways'][0]['outgoing'][0].update(order=True),
            lambda c: c['context']['control_flow']['gateways'][0]['outgoing'][0].update(extra=1),
            lambda c: c['context']['predicate_contracts'][0].update(control_flow_role='unknown'),
            lambda c: c['context']['referents'][0].update(at_gateway=''),
        ):
            case = clone('KF-01'); edit(case)
            with self.assertRaises(ValueError): run(case)

    def test_p113_fields_in_older_context_are_configuration_errors(self):
        for field in ('control_flow', 'at_gateway', 'control_flow_role'):
            for format in ('aiaeao.cube.binding-context/1', 'aiaeao.cube.binding-context/8'):
                case = clone('KF-01')
                case['context']['format'] = format
                if field != 'control_flow': case['context'].pop('control_flow')
                if field != 'at_gateway':
                    for ref in case['context']['referents']: ref.pop('at_gateway', None)
                if field != 'control_flow_role':
                    for pred in case['context']['predicate_contracts']: pred.pop('control_flow_role', None)
                with self.subTest(field=field, format=format):
                    with self.assertRaises(ValueError): run(case)

    def test_fail_outranks_unresolved(self):
        case = clone('KF-05')
        case['context']['control_flow']['gateways'][2]['outgoing'][0]['default'] = True
        report = run(case)
        self.assertEqual(report['overall_status'], 'FAIL')
        self.assertTrue({'P1_CONTROL_FLOW_INVALID', 'P1_CONTROL_FLOW_UNSUPPORTED'} <= set(codes(report)))


class ProjectionAndRegression(unittest.TestCase):
    def test_projection_removes_only_p113(self):
        case = clone('KF-01')
        out = project_v8(case['context'])
        self.assertEqual(out['format'], 'aiaeao.cube.binding-context/8')
        self.assertNotIn('control_flow', out)
        self.assertTrue(all('at_gateway' not in r for r in out['referents']))
        self.assertTrue(all('control_flow_role' not in p for p in out['predicate_contracts']))
        self.assertTrue(any('instance_ref' in r for r in out['referents']))
        self.assertIn('control_flow', case['context'])

    def test_previous_reports_byte_identical(self):
        previous = P112Validator()
        for case in PREVIOUS:
            with self.subTest(id=case['id']):
                outputs = []
                for validator in (previous, V):
                    try:
                        outputs.append(validator.validate_bytes(case['input_text'].encode(),
                            input_format=case['input_format'], context=case['context'],
                            qualification_profiles=case.get('qualification_profiles')))
                    except ValueError as exc:
                        outputs.append(('error', type(exc).__name__, str(exc)))
                self.assertEqual(json.dumps(outputs[0], sort_keys=True), json.dumps(outputs[1], sort_keys=True))

    def test_v9_without_p113_fields_matches_v8(self):
        prior = P112Validator()
        for case in PREVIOUS:
            if case['context'].get('format') != 'aiaeao.cube.binding-context/8':
                continue
            with self.subTest(id=case['id']):
                lifted = copy.deepcopy(case)
                lifted['context']['format'] = 'aiaeao.cube.binding-context/9'
                a = prior.validate_bytes(case['input_text'].encode(), context=case['context'])
                b = run(lifted)
                self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))


class SchemaAndGolden(unittest.TestCase):
    def test_schema_and_strict_superset(self):
        s8 = json.loads((ROOT / 'coverage-instance-profile-v1/context-v8.schema.json').read_text('utf-8'))
        s9 = json.loads((HERE / 'context-v9.schema.json').read_text('utf-8'))
        self.assertTrue(set(s8['properties']) < set(s9['properties']))
        self.assertTrue(set(s8['$defs']) < set(s9['$defs']))
        for name in s8['$defs']:
            self.assertTrue(set(s8['$defs'][name].get('properties', {})) <=
                            set(s9['$defs'][name].get('properties', {})), name)
        schema = jsonschema.Draft7Validator(s9)
        for case in RV.VEC:
            if case['context']['format'].endswith('/9'):
                with self.subTest(id=case['id']):
                    self.assertEqual([e.message for e in schema.iter_errors(case['context'])], [])
        self.assertEqual([e.message for e in schema.iter_errors(GOLDEN['context'])], [])

    def test_golden_contains_model_trace_binding_and_coverage(self):
        context = GOLDEN['context']
        self.assertTrue(context['control_flow']['gateways'])
        self.assertTrue(context['coverage_declarations'])
        self.assertTrue(any('at_gateway' in r for r in context['referents']))
        self.assertEqual((run(GOLDEN)['overall_status'], codes(run(GOLDEN))), ('PASS', []))

    def test_code_register(self):
        register = json.loads((HERE / 'DIAGNOSTIC_EXTENSION.json').read_text('utf-8'))
        self.assertEqual({x['code'] for x in register['codes']}, set(CODES) - {'P1_BINDING_CONTEXT_REQUIRED'})
        for item in register['codes']:
            self.assertEqual(item['stage'], CODES[item['code']][0])
        self.assertEqual(PROFILE, 'P1.13/control-flow-profile-v1')


if __name__ == '__main__':
    unittest.main(verbosity=1)
