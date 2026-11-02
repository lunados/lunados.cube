"""P1.12 local test suite. Fixed oracle expectations; no G5 mutation, no network."""
import copy, json, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
for p in ('semantic-validator-v1', 'instantiation-profile-v1', 'simulation-profile-v1', 'comparison-profile-v1',
          'migration-profile-v1', 'migration-profile-v2', 'migration-methods-v1', 'coverage-instance-profile-v1'):
    sys.path.insert(0, str(ROOT/p))
sys.path.insert(0, str(ROOT/'coverage-instance-profile-v1'/'scripts'))
sys.dont_write_bytecode = True
import run_vectors as RV  # noqa: E402
from cube_p112.validator import P112Validator, CODES, PROFILE  # noqa: E402
from cube_p112.coverage import project_v7, covering  # noqa: E402
from cube_p111.validator import P111Validator  # noqa: E402

HERE = ROOT/'coverage-instance-profile-v1'
VEC = {c['id']: c for c in RV.VEC}
ORACLE = RV.ORACLE
GOLD = {c['id']: c for c in json.loads((HERE/'fixtures/golden_coverage_instance.json').read_text())['cases']}
PREV = []
for f in ('migration-profile-v1/fixtures/m01_m22_materialized.json', 'comparison-profile-v1/fixtures/c01_c20_materialized.json',
          'migration-profile-v2/fixtures/g01_g10_materialized.json', 'migration-methods-v1/fixtures/f01_f16_materialized.json',
          'migration-methods-v1/fixtures/golden_methods_synthetic.json'):
    PREV += json.loads((ROOT/f).read_text())['cases']
V = P112Validator()
NOPROMO = ('epistemic_warrant', 'current_authority', 'canonical_admission')


def run(c, ctx=None):
    return V.validate_bytes(c['input_text'].encode(), context=ctx if ctx is not None else c['context'])


def codes(r): return [d['code'] for d in r['diagnostics']]


def status(c, ctx=None):
    try:
        return run(c, ctx)['overall_status']
    except ValueError:
        return 'MCP_ERROR'


def k(i): return copy.deepcopy(VEC[i])


class Oracle(unittest.TestCase):
    def test_vectors_match_independent_oracle(self):
        self.assertEqual(set(VEC), set(ORACLE)); self.assertEqual(len(VEC), 21)
        for i, c in sorted(VEC.items()):
            with self.subTest(id=i):
                o = ORACLE[i]
                self.assertEqual((c['expected_overall'], c['required_codes'], c['forbidden_codes']),
                                 (o['expected_overall'], o['required_codes'], o['forbidden_codes']))
                self.assertEqual(c.get('lib_expected'), o.get('lib_expected'))
                r = RV.run(copy.deepcopy(c))
                self.assertEqual(r['overall_status'], c['expected_overall'], r)
                for x in c['required_codes']: self.assertIn(x, codes(r))
                for x in c['forbidden_codes']: self.assertNotIn(x, codes(r))
                for n in NOPROMO: self.assertEqual(r[n], 'NOT_EVALUATED')
                if c['expected_overall'] == 'PASS':
                    self.assertEqual(r['diagnostics'], [])


class Regression(unittest.TestCase):
    """P1.12-02: /1…/7 reports byte-identical to P1.11."""
    def test_previous_suites_byte_identical(self):
        p111 = P111Validator()
        for c in PREV:
            with self.subTest(id=c['id']):
                outs = []
                for v in (p111, V):
                    try: outs.append(v.validate_bytes(c['input_text'].encode(), input_format=c['input_format'], context=c['context'],
                                                      qualification_profiles=c.get('qualification_profiles')))
                    except ValueError as e: outs.append(('err', type(e).__name__, str(e)))
                self.assertEqual(json.dumps(outs[0], sort_keys=True), json.dumps(outs[1], sort_keys=True))

    def test_v8_without_p112_fields_equals_v7(self):
        """A /8 context without declarations, rules and instance fields reports exactly like its /7 twin."""
        for c in PREV:
            if c['context'].get('format') != 'aiaeao.cube.binding-context/7':
                continue
            with self.subTest(id=c['id']):
                c8 = copy.deepcopy(c['context']); c8['format'] = 'aiaeao.cube.binding-context/8'
                a = b = None
                try: a = P111Validator().validate_bytes(c['input_text'].encode(), context=c['context'])
                except ValueError as e: a = ('err', type(e).__name__)
                try: b = V.validate_bytes(c['input_text'].encode(), context=c8)
                except ValueError as e: b = ('err', type(e).__name__)
                self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))

    def test_report_profile_field_unchanged(self):
        """P1.12 adds diagnostics only; the report keys stay the P1 report keys."""
        r = run(VEC['K-01'])
        self.assertEqual(set(r), set(P111Validator().validate_bytes(VEC['K-01']['input_text'].encode(),
                                                                   context=project_v7(VEC['K-01']['context']))))


class StatusRules(unittest.TestCase):
    """P1.12-05: one test per row of spec §2."""
    def test_row1_coverage_undeclared(self):
        for i in ('K-01', 'K-05', 'K-09', 'K-13', 'K-16'):
            with self.subTest(id=i):
                r = run(VEC[i]); self.assertEqual(r['overall_status'], 'UNRESOLVED'); self.assertEqual(codes(r), ['P1_COVERAGE_UNDECLARED'])
                self.assertEqual(r['checks']['scope_consistency']['status'], 'UNRESOLVED')

    def test_row2_instance_mismatch(self):
        r = run(VEC['K-17']); self.assertEqual(r['overall_status'], 'FAIL'); self.assertEqual(codes(r), ['P1_INSTANCE_MISMATCH'])

    def test_row3_instance_undeclared(self):
        r = run(VEC['K-20']); self.assertEqual(r['overall_status'], 'UNRESOLVED'); self.assertEqual(codes(r), ['P1_INSTANCE_UNDECLARED'])
        c = k('K-17')
        for x in c['context']['referents']: x.pop('instance_ref', None)
        r = run(c); self.assertEqual(codes(r), ['P1_INSTANCE_UNDECLARED'])

    def test_row4_bad_instance_ref(self):
        c = k('K-17')
        for x in c['context']['referents']:
            if x['ref'] == 'bpmn:i2/tok-credit': x['instance_ref'] = 'bpmn:i9'           # undeclared
        r = run(c); self.assertEqual(r['overall_status'], 'UNRESOLVED'); self.assertEqual(codes(r), ['P1_BINDING_CONTEXT_REQUIRED'])
        c = k('K-17')
        for x in c['context']['referents']:
            if x['ref'] == 'bpmn:i2/tok-credit': x['instance_ref'] = 'bpmn:i1/tok-stock'  # wrong concept
        r = run(c); self.assertEqual(codes(r), ['P1_BINDING_CONTEXT_REQUIRED'])
        self.assertEqual(r['checks']['referent_binding']['status'], 'UNRESOLVED')

    def test_row5_unresolvable_declaration_or_rule(self):
        c = k('K-08'); c['context']['coverage_declarations'][0]['referent'] = 'am:nowhere'
        r = run(c); self.assertIn('P1_BINDING_CONTEXT_REQUIRED', codes(r)); self.assertEqual(r['overall_status'], 'UNRESOLVED')
        c = k('K-08'); c['context']['population_rules'][0]['referent'] = 'am:nowhere'
        r = run(c); self.assertEqual(codes(r), ['P1_BINDING_CONTEXT_REQUIRED'])            # no double report (§2 precedence)
        c = k('K-08'); c['context']['population_rules'][0]['predicate_id'] = 'unknownPred'
        r = run(c); self.assertEqual(codes(r), ['P1_BINDING_CONTEXT_REQUIRED'])
        c = k('K-14'); c['context']['population_rules'][0]['instance_ref'] = 'bpmn:i1/tok-stock'
        self.assertIn('P1_BINDING_CONTEXT_REQUIRED', codes(run(c)))

    def test_row6_malformed_is_config_error(self):
        bad_decls = [{'declaration_id': 'x', 'scope': 'view', 'predicate_id': 'composedOf', 'witness_ref': 'w'},
                     {'declaration_id': 'x', 'scope': 'pair', 'subject': 'a', 'predicate_id': 'p', 'object': 'b'},
                     {'declaration_id': 'x', 'scope': 'referent_relation_direction', 'referent': 'a', 'predicate_id': 'p', 'direction': 'both', 'witness_ref': 'w'},
                     {'declaration_id': 'x', 'scope': 'pair', 'subject': 'a', 'predicate_id': 'p', 'object': 'b', 'witness_ref': 'w', 'extra': 1}]
        for d in bad_decls:
            c = k('K-08'); c['context']['coverage_declarations'] = [d]
            self.assertEqual(status(c), 'MCP_ERROR', d)
        c = k('K-08'); c['context']['coverage_declarations'] *= 2
        self.assertEqual(status(c), 'MCP_ERROR')                                           # duplicate declaration_id
        rule = VEC['K-08']['context']['population_rules'][0]
        for patch in ({'max': 1}, {'min': -1}, {'min': True}, {'kind': 'ratio'}, {'direction': 'sideways'}):
            c = k('K-08'); c['context']['population_rules'] = [dict(rule, **patch)]
            self.assertEqual(status(c), 'MCP_ERROR', patch)
        c = k('K-02'); r = c['context']['population_rules'][0]; r.pop('subject'); r.pop('object')
        self.assertEqual(status(c), 'MCP_ERROR')
        c = k('K-14'); f = c['context']['population_rules'][0]['incoming_flows']; f.append(dict(f[0]))
        self.assertEqual(status(c), 'MCP_ERROR')                                           # duplicate flow
        c = k('K-14'); c['context']['population_rules'][0]['incoming_flows'][0]['min'] = 0
        self.assertEqual(status(c), 'MCP_ERROR')
        c = k('K-17'); c['context']['predicate_contracts'][1]['requires_same_instance'] = 'yes'
        self.assertEqual(status(c), 'MCP_ERROR')
        c = k('K-17'); c['context']['referents'][0]['instance_ref'] = ''
        self.assertEqual(status(c), 'MCP_ERROR')
        c = k('K-08'); c['context']['coverage_view'] = []
        self.assertEqual(status(c), 'MCP_ERROR')

    def test_row7_p112_fields_in_older_formats(self):
        for fmt in ('aiaeao.cube.binding-context/1', 'aiaeao.cube.binding-context/7'):
            for i in ('K-08', 'K-17'):                                                      # declarations+rules / instance fields
                with self.subTest(fmt=fmt, id=i):
                    c = k(i); c['context']['format'] = fmt
                    self.assertEqual(status(c), 'MCP_ERROR')
            c = k('K-17'); c['context']['format'] = fmt
            for x in c['context']['referents']: x.pop('instance_ref', None)
            self.assertEqual(status(c), 'MCP_ERROR')                                       # requires_same_instance alone

    def test_row8_scope_per_instance_unchanged(self):
        r = run(VEC['K-18'])
        self.assertEqual(r['overall_status'], 'FAIL')
        self.assertTrue({'P1_REFERENT_MISMATCH', 'P1_SCOPE_CONFLICT'} <= set(codes(r)))
        c1 = copy.deepcopy(VEC['K-18']['context']); c1['format'] = 'aiaeao.cube.binding-context/1'
        a = P111Validator().validate_bytes(VEC['K-18']['input_text'].encode(), context=c1)
        self.assertEqual(r['diagnostics'], a['diagnostics']); self.assertEqual(r['checks'], a['checks'])

    def test_row9_p111_rows_unchanged(self):
        """Covered by Regression; spot check a /7 F vector through P1.12."""
        f = next(c for c in PREV if c['id'] == 'F-07')
        self.assertIn('P1_MIGRATION_METHOD_SIGNATURE', codes(V.validate_bytes(f['input_text'].encode(), context=f['context'])))

    def test_precedence_fail_outranks_unresolved(self):
        c = k('K-17'); c['context']['coverage_declarations'] = []
        c['context']['population_rules'] = [{'rule_id': 'r', 'kind': 'count', 'referent': 'bpmn:i1/tok-stock', 'predicate_id': 'joins',
                                             'direction': 'outgoing', 'min': 1, 'witness_ref': 'w'}]
        r = run(c); self.assertEqual(r['overall_status'], 'FAIL')
        self.assertEqual(sorted(codes(r)), ['P1_COVERAGE_UNDECLARED', 'P1_INSTANCE_MISMATCH'])


class Coverage(unittest.TestCase):
    """CV-2…CV-4 details beyond the vectors."""
    def test_pair_does_not_cover_other_pair_or_direction(self):
        d = VEC['K-04']['context']['coverage_declarations']
        self.assertTrue(covering({'kind': 'absence', 'predicate_id': 'dependsOn', 'subject': 'm:printer', 'object': 'm:parser'}, d))
        self.assertFalse(covering({'kind': 'absence', 'predicate_id': 'dependsOn', 'subject': 'm:parser', 'object': 'm:printer'}, d))
        self.assertFalse(covering({'kind': 'absence', 'predicate_id': 'maintains', 'subject': 'm:printer', 'object': 'm:parser'}, d))

    def test_direction_matters(self):
        d = VEC['K-06']['context']['coverage_declarations']    # outgoing dependsOn of printer
        self.assertTrue(covering({'kind': 'absence', 'predicate_id': 'dependsOn', 'subject': 'm:printer', 'object': 'm:parser'}, d))
        self.assertFalse(covering({'kind': 'absence', 'predicate_id': 'dependsOn', 'subject': 'm:parser', 'object': 'm:printer'}, d))
        self.assertFalse(covering({'kind': 'count', 'referent': 'm:printer', 'predicate_id': 'dependsOn', 'direction': 'incoming', 'min': 0}, d))

    def test_instance_restriction(self):
        d = VEC['K-14']['context']['coverage_declarations']    # restricted to i1
        rule = VEC['K-14']['context']['population_rules'][0]
        self.assertEqual(len(covering(rule, d)), 2)
        self.assertEqual(covering(dict(rule, instance_ref='bpmn:i2'), d), [])
        unrestricted = [{k2: v for k2, v in x.items() if k2 != 'instance_ref'} for x in d]
        self.assertEqual(len(covering(dict(rule, instance_ref='bpmn:i2'), unrestricted)), 2)

    def test_join_needs_every_flow(self):
        d = VEC['K-14']['context']['coverage_declarations'][:1]
        self.assertEqual(covering(VEC['K-14']['context']['population_rules'][0], d), [])

    def test_imported_profile_predicate_resolves(self):
        """Q-4: a predicate imported through predicate_profile_refs (P1.10) is declared; a declaration on it resolves."""
        c = json.loads((ROOT.parent/'docs/09-Research/visual-check/renders/R-1.json').read_text())
        ctx = copy.deepcopy(c['context']); ctx['format'] = 'aiaeao.cube.binding-context/8'
        ctx['coverage_declarations'] = [{'declaration_id': 'cv-pp', 'scope': 'pair', 'subject': 'm:printer', 'predicate_id': 'references',
                                         'object': 'm:parser', 'witness_ref': 'synthetic:survey'}]
        ctx['population_rules'] = [{'rule_id': 'pr-pp', 'kind': 'absence', 'subject': 'm:printer', 'predicate_id': 'references',
                                    'object': 'm:parser', 'witness_ref': 'synthetic:rule'}]
        t = 'rel("references",Y:α:Resource["m:resolver"],Y:α:Resource["m:parser"])'
        r = V.validate_bytes(t.encode(), context=ctx)
        self.assertEqual((r['overall_status'], codes(r)), ('PASS', []))
        ctx['coverage_declarations'][0]['predicate_id'] = 'depends-on-nothing'
        self.assertIn('P1_BINDING_CONTEXT_REQUIRED', codes(V.validate_bytes(t.encode(), context=ctx)))

    def test_no_inference_from_statements(self):
        """CV-5: a statement set never creates coverage; K-12 has two statements and its coverage comes only from the declaration."""
        c = k('K-12'); c['context']['coverage_declarations'] = []
        self.assertEqual(codes(run(c)), ['P1_COVERAGE_UNDECLARED'])


class Instances(unittest.TestCase):
    def test_in4_unconstrained_predicate(self):
        r = run(VEC['K-21']); self.assertEqual(r['overall_status'], 'PASS')
        c = k('K-17')
        for p in c['context']['predicate_contracts']: p.pop('requires_same_instance', None)
        self.assertEqual(run(c)['overall_status'], 'PASS')

    def test_reversed_endpoints_also_mismatch(self):
        t = 'rel("joins",Y:α:Evidence["bpmn:i2/tok-credit"],Y:α:Evidence["bpmn:i1/tok-stock"])'
        self.assertEqual(codes(V.validate_bytes(t.encode(), context=VEC['K-17']['context'])), ['P1_INSTANCE_MISMATCH'])


class Projection(unittest.TestCase):
    def test_projection_strips(self):
        p = project_v7(VEC['K-17']['context'])
        self.assertEqual(p['format'], 'aiaeao.cube.binding-context/7')
        self.assertFalse({'coverage_declarations', 'population_rules'} & set(p))
        self.assertTrue(all('instance_ref' not in r for r in p['referents']))
        self.assertTrue(all('requires_same_instance' not in x for x in p['predicate_contracts']))
        self.assertIn('instance_ref', VEC['K-17']['context']['referents'][0])          # input untouched

    def test_deterministic(self):
        for i in ('K-01', 'K-17', 'K-20'):
            self.assertEqual(run(VEC[i]), run(copy.deepcopy(VEC[i])))

    def test_codes_registered(self):
        reg = json.loads((HERE/'DIAGNOSTIC_EXTENSION.json').read_text())
        new = {x['code'] for x in reg['codes']}
        self.assertEqual(new, {'P1_COVERAGE_UNDECLARED', 'P1_INSTANCE_MISMATCH', 'P1_INSTANCE_UNDECLARED'})
        self.assertTrue(new <= set(CODES))
        for x in reg['codes']: self.assertEqual(x['stage'], CODES[x['code']][0])
        self.assertEqual(PROFILE, 'P1.12/coverage-instance-profile-v1')


class Golden(unittest.TestCase):
    def test_golden(self):
        for gid, c in GOLD.items():
            with self.subTest(id=gid):
                r = run(c)
                self.assertEqual(r['overall_status'], c['expected_overall'])
                for x in c['required_codes']: self.assertIn(x, codes(r))
                for x, n in c.get('expected_code_count', {}).items(): self.assertEqual(codes(r).count(x), n)
                if 'expected_blocks' in c:
                    e = c['expected_blocks']; ctx = c['context']
                    self.assertEqual(len(ctx['coverage_declarations']), e['coverage_declarations'])
                    self.assertEqual(len(ctx['population_rules']), e['population_rules'])
                    self.assertEqual(sum('instance_ref' in x for x in ctx['referents']), e['instance_refs'])


class Schema(unittest.TestCase):
    def setUp(self):
        import jsonschema, warnings
        warnings.simplefilter('ignore')
        self.s8 = json.loads((HERE/'context-v8.schema.json').read_text())
        s = copy.deepcopy(self.s8); s.pop('$id', None); s.pop('$schema', None)
        self.v = jsonschema.Draft7Validator(s)

    def test_contexts_valid_against_context_v8_schema(self):
        for i, c in sorted(VEC.items()):
            with self.subTest(id=i): self.assertEqual([e.message for e in self.v.iter_errors(c['context'])], [])
        for c in GOLD.values():
            self.assertEqual(list(self.v.iter_errors(c['context'])), [])

    def test_strict_superset_of_v7(self):
        s7 = json.loads((ROOT/'migration-methods-v1/context-v7.schema.json').read_text())
        self.assertTrue(set(s7['properties']) < set(self.s8['properties']))
        self.assertTrue(set(s7['$defs']) < set(self.s8['$defs']))
        for d in s7['$defs']:
            self.assertTrue(set(s7['$defs'][d].get('properties', {})) <= set(self.s8['$defs'][d].get('properties', {})), d)

    def test_schema_rejects_view_scope(self):
        c = k('K-08'); c['context']['coverage_declarations'][0]['scope'] = 'view'
        self.assertTrue(list(self.v.iter_errors(c['context'])))


if __name__ == '__main__':
    unittest.main(verbosity=1)
