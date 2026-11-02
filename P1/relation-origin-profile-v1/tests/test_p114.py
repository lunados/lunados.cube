"""Independent HO oracle, semantic status rows, schemas, golden and regression."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / 'relation-origin-profile-v1'
for name in ('semantic-validator-v1', 'instantiation-profile-v1', 'simulation-profile-v1',
             'comparison-profile-v1', 'migration-profile-v1', 'migration-profile-v2',
             'migration-methods-v1', 'coverage-instance-profile-v1', 'control-flow-profile-v1',
             'relation-origin-profile-v1'):
    sys.path.insert(0, str(ROOT / name))
sys.path.insert(0, str(ROOT.parent / 'P3/adapters/mcp-local'))
sys.dont_write_bytecode = True
import jsonschema  # noqa: E402
from cube_p113.validator import P113Validator  # noqa: E402
from cube_p114.origin import project_v9  # noqa: E402
from cube_p114.validator import P114Validator  # noqa: E402
from aiaeao_mcp_local import p1_adapter  # noqa: E402

V = P114Validator()
VEC = {c['id']: c for c in json.loads((HERE / 'fixtures/ho01_ho12_materialized.json').read_text())['cases']}
ORACLE = {c['id']: c for c in json.loads((HERE / 'oracles/independent_ho01_ho12.json').read_text())['cases']}


def run_case(case):
    return V.validate_bytes(case['input_text'].encode(), input_format=case['input_format'], context=case['context'])


def codes(report):
    return [d['code'] for d in report['diagnostics']]


def clone(id):
    return copy.deepcopy(VEC[id])


class P114Tests(unittest.TestCase):
    def test_independent_oracle(self):
        self.assertEqual(set(VEC), set(ORACLE))
        self.assertEqual(len(VEC), 12)
        for id, case in VEC.items():
            with self.subTest(id=id):
                o = ORACLE[id]
                self.assertEqual((case['expected_overall'], case['required_codes'], case['forbidden_codes']),
                                 (o['expected_overall'], o['required_codes'], o['forbidden_codes']))
                report = run_case(case)
                self.assertEqual(report['overall_status'], o['expected_overall'], report)
                for code in o['required_codes']:
                    self.assertIn(code, codes(report))
                for code in o['forbidden_codes']:
                    self.assertNotIn(code, codes(report))
                if o['expected_overall'] == 'PASS':
                    self.assertEqual(report['diagnostics'], [])
                if 'required_pointer_prefix' in o:
                    self.assertTrue(any(d['message'].startswith(o['required_pointer_prefix'])
                                        for d in report['diagnostics']))
                for field in ('epistemic_warrant', 'current_authority', 'canonical_admission'):
                    self.assertEqual(report[field], 'NOT_EVALUATED')

    def test_status_rows(self):
        self.assertEqual(codes(run_case(VEC['HO-01'])), ['P1_ORIGIN_UNDECLARED'])
        self.assertEqual(codes(run_case(VEC['HO-04'])), ['P1_ORIGIN_BASIS_MISSING'])
        self.assertEqual(codes(run_case(VEC['HO-05'])), ['P1_ORIGIN_INVALID'])
        self.assertEqual(codes(run_case(VEC['HO-06'])), ['P1_ORIGIN_INVALID'])
        self.assertEqual(codes(run_case(VEC['HO-09'])), ['P1_BINDING_CONTEXT_REQUIRED'])
        c = clone('HO-08'); c['input_text'] = c['input_text'].replace('"declared"', '12')
        self.assertEqual((run_case(c)['overall_status'], codes(run_case(c))), ('FAIL', ['P1_ORIGIN_INVALID']))
        c = clone('HO-07'); c['input_text'] = c['input_text'].replace('"unknown"', '"declared",basis="b-api-db"')
        self.assertEqual((run_case(c)['overall_status'], codes(run_case(c))), ('FAIL', ['P1_ORIGIN_INVALID']))

    def test_unopted_and_extra_parameters(self):
        self.assertEqual(codes(run_case(VEC['HO-10'])), ['P1_PREDICATE_PROFILE_MISSING'])
        c = clone('HO-02'); c['input_text'] = c['input_text'].replace('basis="b-api-db"',
                         'basis="b-api-db",other="x"')
        self.assertEqual((run_case(c)['overall_status'], codes(run_case(c))),
                         ('UNRESOLVED', ['P1_PREDICATE_PROFILE_MISSING']))

    def test_no_hardcoded_predicate(self):
        c = clone('HO-02')
        c['input_text'] = c['input_text'].replace('"uses"', '"links"')
        contract = copy.deepcopy(next(p for p in c['context']['predicate_contracts'] if p['predicate_id'] == 'uses'))
        contract['predicate_id'] = 'links'
        c['context']['predicate_contracts'].append(contract)
        self.assertEqual((run_case(c)['overall_status'], codes(run_case(c))), ('PASS', []))

    def test_plan_origin_rows(self):
        self.assertEqual(codes(run_case(VEC['HO-12'])), ['P1_ORIGIN_UNDECLARED'])
        for value, expected, status in (('derived', 'P1_ORIGIN_BASIS_MISSING', 'UNRESOLVED'),
                                         ('inferred', 'P1_ORIGIN_INVALID', 'FAIL')):
            c = clone('HO-12'); c['context']['migration_plans'][0]['dependencies'][1]['origin'] = value
            r = run_case(c)
            self.assertEqual((r['overall_status'], codes(r)), (status, [expected]))
        c = clone('HO-12'); c['context']['migration_plans'][0]['dependencies'][1]['origin'] = 'unknown'
        self.assertEqual((run_case(c)['overall_status'], codes(run_case(c))), ('PASS', []))

    def test_bad_contexts(self):
        edits = (
            lambda c: c['context'].update(origin_bases=None),
            lambda c: c['context']['origin_bases'].append(copy.deepcopy(c['context']['origin_bases'][0])),
            lambda c: c['context']['origin_bases'][0]['statement_ids'].append('s-1'),
            lambda c: c['context']['origin_bases'][0].update(extra=1),
            lambda c: c['context']['origin_bases'][1].update(record_sha256='abc'),
            lambda c: c['context']['predicate_contracts'][0].update(origin_binding='optional'),
        )
        for edit in edits:
            c = clone('HO-02'); edit(c)
            with self.subTest(edit=str(edit)), self.assertRaises(ValueError):
                run_case(c)

    def test_old_format_rejects_new_fields(self):
        c = clone('HO-02'); c['context']['format'] = 'aiaeao.cube.binding-context/9'
        with self.assertRaises(ValueError):
            run_case(c)
        c = clone('HO-12'); c['context']['format'] = 'aiaeao.cube.binding-context/9'
        with self.assertRaises(ValueError):
            run_case(c)

    def test_schemas_and_projection(self):
        schema = json.loads((HERE / 'context-v10.schema.json').read_text())
        previous = json.loads((ROOT / 'control-flow-profile-v1/context-v9.schema.json').read_text())
        jsonschema.Draft202012Validator.check_schema(schema)
        for c in VEC.values():
            if c['context']['format'].endswith('/10'):
                jsonschema.validate(c['context'], schema)
                jsonschema.validate(project_v9(c['context']), previous)
        c = clone('HO-02')['context']; old = project_v9(c)
        self.assertNotIn('origin_bases', old)
        self.assertNotIn('origin_binding', old['predicate_contracts'][0])
        self.assertEqual(c['format'], 'aiaeao.cube.binding-context/10')
        self.assertEqual(set(schema['required']), set(previous['required']))

    def test_statement_set_schema(self):
        base = json.loads((HERE / 'statement-set-v1.baseline.schema.json').read_text())
        new = json.loads((HERE / 'statement-set-v2.schema.json').read_text())
        for schema in (base, new):
            jsonschema.Draft202012Validator.check_schema(schema)
        s = {'format': 'aiaeao.cube.statement-set/1', 'set_id': 'synthetic', 'context_id': 'p114-c4',
             'referents': ['c4:shop/api', 'c4:shop/db'], 'witness_ref': 'synthetic:c4',
             'statements': [{'statement_id': 's-1', 'subject': 'c4:shop/api',
                             'predicate_id': 'uses', 'object': 'c4:shop/db'}]}
        jsonschema.validate(s, base)
        s['format'] = 'aiaeao.cube.statement-set/2'
        jsonschema.validate(s, new)
        s['statements'][0].update(origin='derived', basis='b-api-db')
        jsonschema.validate(s, new)
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(s, base)

    def test_golden(self):
        golden = json.loads((HERE / 'fixtures/golden_relation_origin.json').read_text())
        self.assertEqual({x['origin'] for x in golden['relations']}, {'declared', 'derived', 'unknown'})
        self.assertEqual({x['basis_kind'] for x in golden['relations']}, {None, 'statements', 'projection_record'})
        for relation in golden['relations']:
            r = V.validate_bytes(relation['input_text'].encode(), context=golden['context'])
            self.assertEqual((r['overall_status'], codes(r)), ('PASS', []))

    def test_prior_reports(self):
        prior = P113Validator()
        for file in ('control-flow-profile-v1/fixtures/kf01_kf09_materialized.json',
                     'coverage-instance-profile-v1/fixtures/k01_k21_materialized.json',
                     'migration-methods-v1/fixtures/f01_f16_materialized.json'):
            for c in json.loads((ROOT / file).read_text())['cases']:
                with self.subTest(id=c['id']):
                    args = (c['input_text'].encode(),)
                    kw = {'input_format': c.get('input_format', 'acg_text'), 'context': c['context'],
                          'qualification_profiles': c.get('qualification_profiles')}
                    def result(validator):
                        try:
                            return validator.validate_bytes(*args, **kw)
                        except ValueError as exc:
                            return ('config_error', type(exc).__name__, str(exc))
                    a, b = result(prior), result(V)
                    self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))


if __name__ == '__main__':
    unittest.main()
