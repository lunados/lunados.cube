"""Independent SN oracle, regression of /1…/10, configuration errors and reference v2 (P1.15-01…04)."""
import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / 'scope-nesting-profile-v1'
for name in ('semantic-validator-v1', 'instantiation-profile-v1', 'simulation-profile-v1', 'comparison-profile-v1',
             'migration-profile-v1', 'migration-profile-v2', 'migration-methods-v1', 'coverage-instance-profile-v1',
             'control-flow-profile-v1', 'relation-origin-profile-v1', 'scope-nesting-profile-v1'):
    sys.path.insert(0, str(ROOT / name))
sys.dont_write_bytecode = True
import jsonschema  # noqa: E402
from cube_p112.coverage import CoverageProfileError  # noqa: E402
from cube_p114.validator import P114Validator  # noqa: E402
from cube_p115.nesting import project_v10, reference_v2  # noqa: E402
from cube_p115.validator import P115Validator  # noqa: E402

V = P115Validator()
VEC = {c['id']: c for c in json.loads((HERE / 'fixtures/sn01_sn14_materialized.json').read_text())['cases']}
ORACLE_DOC = json.loads((HERE / 'oracles/independent_sn01_sn14.json').read_text())
ORACLE = {c['id']: c for c in ORACLE_DOC['cases']}


def run(case, ctx=None):
    return V.validate_bytes(case['input_text'].encode(), input_format=case['input_format'], context=ctx or case['context'])


def codes(report):
    return [d['code'] for d in report['diagnostics']]


class P115Tests(unittest.TestCase):
    def test_oracle_independent_of_spec_drift(self):
        self.assertEqual(ORACLE_DOC['spec_sha256'], hashlib.sha256((HERE / 'P1_15_ACCEPTANCE_SPEC.md').read_bytes()).hexdigest())

    def test_independent_oracle(self):
        self.assertEqual(set(VEC), set(ORACLE))
        self.assertEqual(len(VEC), 14)
        for id, case in VEC.items():
            with self.subTest(id=id):
                o = ORACLE[id]
                report = run(case)
                self.assertEqual(report['overall_status'], o['expected_overall'], report['diagnostics'])
                for code in o['required_codes']:
                    self.assertIn(code, codes(report))
                for code in o['forbidden_codes']:
                    self.assertNotIn(code, codes(report))
                if o['expected_overall'] == 'PASS':
                    self.assertEqual(report['diagnostics'], [])
                for field in ('epistemic_warrant', 'current_authority', 'canonical_admission'):
                    self.assertEqual(report[field], 'NOT_EVALUATED')

    def test_schema(self):
        schema = json.loads((HERE / 'context-v11.schema.json').read_text())
        for case in VEC.values():
            jsonschema.validate(case['context'], schema)

    def test_regression_v10_and_older(self):
        p114 = P114Validator()
        ho = json.loads((ROOT / 'relation-origin-profile-v1/fixtures/ho01_ho12_materialized.json').read_text())['cases']
        kf = json.loads((ROOT / 'control-flow-profile-v1/fixtures/kf01_kf09_materialized.json').read_text())['cases']
        for case in ho + kf:
            with self.subTest(id=case['id']):
                a = p114.validate_bytes(case['input_text'].encode(), input_format=case['input_format'], context=copy.deepcopy(case['context']))
                b = V.validate_bytes(case['input_text'].encode(), input_format=case['input_format'], context=copy.deepcopy(case['context']))
                self.assertEqual(a, b)
        p16 = json.loads((ROOT / 'instantiation-profile-v1/fixtures/valid_conclusion_context_v2.json').read_text())
        text = 'X:α:Conclusion["c1"]'.encode()
        self.assertEqual(p114.validate_bytes(text, context=copy.deepcopy(p16)), V.validate_bytes(text, context=copy.deepcopy(p16)))

    def test_config_errors(self):
        base = VEC['SN-02']['context']
        bad = [
            lambda c: c['scope_nesting'].append({'inner': 'x:policy/project', 'outer': 'x:policy/org'}),  # duplicate inner
            lambda c: c['scope_nesting'].append({'inner': 'x:policy/org'}),                                 # missing outer
            lambda c: c['scope_nesting'].append({'inner': 'x:policy/org', 'outer': 'x:policy/org'}),       # inner == outer
            lambda c: c.__setitem__('scope_nesting', {}),                                                  # not an array
            lambda c: c.__setitem__('unknown_field', 1),
            lambda c: next(p for p in c['instantiation_profiles'] if p['concept_id'] == 'X:endpoint:authority')['slots'][4]['concept_ids'].append('Y:resource-object:source'),
        ]
        for i, mutate in enumerate(bad):
            with self.subTest(i=i):
                ctx = copy.deepcopy(base)
                mutate(ctx)
                with self.assertRaises((CoverageProfileError, ValueError)):
                    V.validate_context(ctx)

    def test_reference_v2(self):
        v1 = json.loads((ROOT / 'instantiation-profile-v1/instantiation_reference_v1.json').read_text())
        eps2, doc2 = reference_v2()
        eps1 = {e['concept_id']: e for e in v1['endpoints']}
        self.assertEqual(set(eps1), set(eps2))
        for cid in eps1:
            for s1, s2 in zip(eps1[cid]['slots'], eps2[cid]['slots']):
                if cid == 'X:endpoint:authority' and s1['name'] == 'resource_scope_ref':
                    self.assertEqual(set(s2['concept_ids']) - set(s1['concept_ids']),
                                     {'Y:resource-object:revision', 'Y:resource-object:artifact'})
                else:
                    self.assertEqual(s1, s2)
        self.assertEqual(doc2['conditions'], v1['conditions'])
        # projection narrows to v1 so the unchanged lower layers accept the profile
        ctx = copy.deepcopy(VEC['SN-09']['context'])
        next(p for p in ctx['instantiation_profiles'] if p['concept_id'] == 'X:endpoint:authority')
        low = project_v10(ctx)
        self.assertEqual(low['format'], 'aiaeao.cube.binding-context/10')
        self.assertNotIn('scope_nesting', low)
        auth = next(p for p in low['instantiation_profiles'] if p['concept_id'] == 'X:endpoint:authority')
        self.assertNotIn('Y:resource-object:revision', next(s for s in auth['slots'] if s['name'] == 'resource_scope_ref')['concept_ids'])

    def test_parallel_gateway_untouched(self):
        ctx = copy.deepcopy(VEC['SN-12']['context'])
        g = ctx['control_flow']['gateways'][0]
        g['type'] = 'parallel'
        for o in g['outgoing']:
            o.pop('order', None); o.pop('default', None)
        report = run(VEC['SN-12'], ctx)
        self.assertNotIn('P1_ADMISSION_OUTCOME_CONFLICT', codes(report))


if __name__ == '__main__':
    unittest.main()
