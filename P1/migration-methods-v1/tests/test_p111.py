"""P1.11 local test suite. Fixed oracle expectations; no G5 mutation, no network."""
import copy, json, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
for p in ('semantic-validator-v1', 'instantiation-profile-v1', 'simulation-profile-v1', 'comparison-profile-v1',
          'migration-profile-v1', 'migration-profile-v2', 'migration-methods-v1'):
    sys.path.insert(0, str(ROOT/p))
sys.path.insert(0, str(ROOT/'migration-methods-v1'/'scripts'))
sys.dont_write_bytecode = True
import run_vectors as RV  # noqa: E402
from cube_p111.validator import P111Validator, CODES  # noqa: E402
from cube_p111.methods import project_v6, load_catalog, PINNED  # noqa: E402
from cube_p1101.validator import P1101Validator  # noqa: E402

HERE = ROOT/'migration-methods-v1'
VEC = {c['id']: c for c in RV.VEC}
ORACLE = RV.ORACLE
GOLD = {c['id']: c for c in json.loads((HERE/'fixtures/golden_methods_synthetic.json').read_text())['cases']}
MVEC = json.loads((ROOT/'migration-profile-v1/fixtures/m01_m22_materialized.json').read_text())['cases']
CVEC = json.loads((ROOT/'comparison-profile-v1/fixtures/c01_c20_materialized.json').read_text())['cases']
GVEC = json.loads((ROOT/'migration-profile-v2/fixtures/g01_g10_materialized.json').read_text())['cases']
V = P111Validator()
NOPROMO = ('epistemic_warrant', 'current_authority', 'canonical_admission')


def run(c):
    return V.validate_bytes(c['input_text'].encode(), context=c['context'], qualification_profiles=c.get('qualification_profiles'))


def codes(r): return [d['code'] for d in r['diagnostics']]


def base():
    return copy.deepcopy(VEC['F-01'])


def t0(c):
    return c['context']['migration_plans'][0]['transitions'][0]


def status(c):
    try:
        return run(c)['overall_status']
    except ValueError:
        return 'MCP_ERROR'


class Oracle(unittest.TestCase):
    def test_vectors_match_independent_oracle(self):
        self.assertEqual(set(VEC), set(ORACLE)); self.assertEqual(len(VEC), 16)
        for i, c in sorted(VEC.items()):
            with self.subTest(id=i):
                o = ORACLE[i]
                self.assertEqual((c['expected_overall'], c['required_codes'], c['forbidden_codes']),
                                 (o['expected_overall'], o['required_codes'], o['forbidden_codes']))
                if c.get('tamper_catalog'):
                    with RV.tampered_catalog():
                        r, _ = RV.run(copy.deepcopy(c))
                else:
                    r, _ = RV.run(copy.deepcopy(c))
                self.assertEqual(r['overall_status'], c['expected_overall'], r)
                for x in c['required_codes']:
                    self.assertIn(x, [d['code'] for d in r['diagnostics']])
                if r['overall_status'] != 'MCP_ERROR':
                    for k in NOPROMO: self.assertEqual(r[k], 'NOT_EVALUATED')
                if c['expected_overall'] == 'PASS':
                    self.assertEqual(r['diagnostics'], [])


class Regression(unittest.TestCase):
    """P1.11-01: /1…/6 reports byte-identical to P1.10.1."""
    def _same(self, cases):
        p1101 = P1101Validator()
        for c in cases:
            with self.subTest(id=c['id']):
                a = b = None
                try: a = p1101.validate_bytes(c['input_text'].encode(), input_format=c['input_format'], context=c['context'],
                                              qualification_profiles=c.get('qualification_profiles'))
                except ValueError as e: a = ('err', type(e).__name__)
                try: b = V.validate_bytes(c['input_text'].encode(), input_format=c['input_format'], context=c['context'],
                                          qualification_profiles=c.get('qualification_profiles'))
                except ValueError as e: b = ('err', type(e).__name__)
                self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))

    def test_m_vectors(self): self._same(MVEC)
    def test_c_vectors(self): self._same(CVEC)
    def test_g_vectors(self): self._same(GVEC)

    def test_v7_without_bindings_equals_v6(self):
        """A /7 context without catalog and bindings reports exactly like its /6 twin."""
        for c in GVEC:
            if c['context']['format'] != 'aiaeao.cube.binding-context/6':
                continue
            with self.subTest(id=c['id']):
                c7 = copy.deepcopy(c['context']); c7['format'] = 'aiaeao.cube.binding-context/7'
                a = P1101Validator().validate_bytes(c['input_text'].encode(), context=c['context'])
                b = V.validate_bytes(c['input_text'].encode(), context=c7)
                self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))


class StatusRules(unittest.TestCase):
    """P1.11-06: one test per row of spec §2."""
    def test_row1_unknown_or_altered_catalog(self):
        self.assertEqual(status(VEC['F-02']), 'MCP_ERROR')
        with RV.tampered_catalog():
            self.assertEqual(status(VEC['F-03']), 'MCP_ERROR')
        c = base(); c['context']['method_profile_refs'] = ['P1.11/migration-methods-v1', 'P1.11/migration-methods-v1']
        self.assertEqual(status(c), 'MCP_ERROR')

    def test_row2_local_redefinition(self):
        self.assertEqual(status(VEC['F-04']), 'MCP_ERROR')

    def test_row3_unknown_method(self):
        r = run(VEC['F-06']); self.assertEqual(r['overall_status'], 'UNRESOLVED'); self.assertIn('P1_MIGRATION_METHOD_UNKNOWN', codes(r))
        c = base(); del c['context']['method_profile_refs']; t0(c)['methods'] = [{'method_id': 'migrate.retire/v1', 'arguments': {'retired': 'legacy-mail'}}]
        self.assertIn('P1_MIGRATION_METHOD_UNKNOWN', codes(run(c)))  # catalog not imported

    def test_row4_signature(self):
        for i in ('F-07', 'F-08'):
            r = run(VEC[i]); self.assertEqual(r['overall_status'], 'FAIL'); self.assertIn('P1_MIGRATION_METHOD_SIGNATURE', codes(r))
        c = base(); t0(c)['methods'] = [{'method_id': 'migrate.retire/v1', 'arguments': {'gone': 'legacy-mail'}}]
        self.assertIn('P1_MIGRATION_METHOD_SIGNATURE', codes(run(c)))

    def test_row5_reference_missing(self):
        r = run(VEC['F-09']); self.assertEqual(r['overall_status'], 'UNRESOLVED'); self.assertIn('P1_MIGRATION_REFERENCE_MISSING', codes(r))

    def test_row6_plan_fit(self):
        for i in ('F-10', 'F-11', 'F-12', 'F-13'):
            with self.subTest(id=i):
                r = run(VEC[i]); self.assertEqual(r['overall_status'], 'FAIL'); self.assertIn('P1_MIGRATION_METHOD_PLAN', codes(r))
        c = base(); t0(c)['methods'] = [{'method_id': 'migrate.rewrite/v1', 'arguments': {'dependant': 'shop', 'new_object': 'new-mail'}}]
        self.assertIn('P1_MIGRATION_METHOD_PLAN', codes(run(c)))   # MV-2: rewrite binds to a dependency
        c = base(); t0(c)['methods'] = [{'method_id': 'migrate.reconfigure/v1', 'arguments': {'target': 'legacy-mail'}}]
        self.assertIn('P1_MIGRATION_METHOD_PLAN', codes(run(c)))   # MP-4
        c = base(); c['context']['migration_plans'][0]['dependencies'][0]['method'] = \
            {'method_id': 'migrate.rewrite/v1', 'arguments': {'dependant': 'support', 'new_object': 'new-mail'}}
        self.assertIn('P1_MIGRATION_METHOD_PLAN', codes(run(c)))   # MV-3

    def test_row7_witness_not_required_in_v1(self):
        """D-8: no catalog entry requires a witness in v1; a binding without witness_ref is accepted."""
        self.assertEqual(run(VEC['F-05'])['overall_status'], 'PASS')
        self.assertTrue(all('requires_witness' not in m for m in load_catalog('P1.11/migration-methods-v1')['methods']))

    def test_row8_bindings_in_v6(self):
        self.assertEqual(status(VEC['F-16']), 'MCP_ERROR')

    def test_row9_f_qualifier(self):
        self.assertEqual(run(VEC['F-14'])['overall_status'], 'PASS')
        r = run(VEC['F-15']); self.assertIn('P1_QUALIFIER_PROFILE_MISSING', codes(r))

    def test_binding_shape_is_config_error(self):
        for bad in ({'method_id': 'migrate.retire/v1'}, {'method_id': 'migrate.retire/v1', 'arguments': {}},
                    {'method_id': 'migrate.retire/v1', 'arguments': {'retired': 3}}, {'method_id': 'migrate.retire/v1', 'arguments': {'retired': 'x'}, 'extra': 1}):
            c = base(); t0(c)['methods'] = [bad]
            self.assertEqual(status(c), 'MCP_ERROR', bad)

    def test_local_method_binding(self):
        """MV-5: local methods bind positionally (arg1…argN), typed by argument_concept_ids."""
        c = base()
        c['context']['method_contracts'] = [{'method_id': 'acme.notify/v1', 'revision': 'v1', 'scope': 'acme:migration', 'origin': 'illustrative_fixture',
                                             'argument_min': 1, 'argument_max': 1, 'argument_concept_ids': ['Y:identity-anchor:actor'],
                                             'effect_class': 'pure_declarative'}]
        t0(c)['methods'] = [{'method_id': 'acme.notify/v1', 'arguments': {'arg1': 'support'}}]
        self.assertEqual(run(c)['overall_status'], 'PASS')
        t0(c)['methods'] = [{'method_id': 'acme.notify/v1', 'arguments': {'arg1': 'shop'}}]
        self.assertIn('P1_MIGRATION_METHOD_SIGNATURE', codes(run(c)))
        t0(c)['methods'] = [{'method_id': 'acme.notify/v1', 'arguments': {'who': 'support'}}]
        self.assertIn('P1_MIGRATION_METHOD_SIGNATURE', codes(run(c)))


class Projection(unittest.TestCase):
    def test_projection_scopes_and_strips(self):
        p = project_v6(VEC['F-05']['context'])
        self.assertEqual(p['format'], 'aiaeao.cube.binding-context/6')
        self.assertNotIn('method_profile_refs', p)
        ids = [m['method_id'] for m in p['method_contracts']]
        self.assertEqual(len(ids), 5)
        for m in p['method_contracts']:
            self.assertEqual((m['scope'], m['origin'], m['effect_class']), ('acme:migration', 'external_declaration_unverified', 'pure_declarative'))
            self.assertFalse({'roles', 'primitive', 'binding_points', 'notes'} & set(m))
        self.assertTrue(all('methods' not in t for t in p['migration_plans'][0]['transitions']))
        self.assertTrue(all('method' not in d for d in p['migration_plans'][0]['dependencies']))

    def test_catalog_pinned_and_deterministic(self):
        self.assertEqual(set(PINNED), {'P1.11/migration-methods-v1'})
        sums = (HERE/'SHA256SUMS.txt').read_text().split()
        self.assertEqual(sums[0], PINNED['P1.11/migration-methods-v1'][1])
        c = VEC['F-05']
        self.assertEqual(run(c), run(copy.deepcopy(c)))

    def test_codes_registered(self):
        reg = json.loads((HERE/'DIAGNOSTIC_EXTENSION.json').read_text())
        self.assertEqual({x['code'] for x in reg['codes']},
                         {'P1_MIGRATION_METHOD_UNKNOWN', 'P1_MIGRATION_METHOD_SIGNATURE', 'P1_MIGRATION_METHOD_PLAN'})
        self.assertTrue({x['code'] for x in reg['codes']} <= set(CODES))


class Golden(unittest.TestCase):
    def test_golden(self):
        for gid, c in GOLD.items():
            with self.subTest(id=gid):
                r = run(c)
                self.assertEqual(r['overall_status'], c['expected_overall'])
                for x in c['required_codes']: self.assertIn(x, codes(r))
                for k, n in c.get('expected_code_count', {}).items():
                    self.assertEqual(codes(r).count(k), n)
                if 'expected_bindings' in c:
                    mp = c['context']['migration_plans'][0]
                    self.assertEqual(sum(len(t.get('methods', [])) for t in mp['transitions']), c['expected_bindings']['transitions'])
                    self.assertEqual(sum('method' in d for d in mp['dependencies']), c['expected_bindings']['dependencies'])


class Schema(unittest.TestCase):
    def test_contexts_valid_against_context_v7_schema(self):
        import jsonschema, warnings
        warnings.simplefilter('ignore')
        s = json.loads((HERE/'context-v7.schema.json').read_text())
        s.pop('$id', None); s.pop('$schema', None)
        v = jsonschema.Draft7Validator(s)
        for i, c in sorted(VEC.items()):
            if c['context']['format'].endswith('/7'):
                with self.subTest(id=i): self.assertEqual([e.message for e in v.iter_errors(c['context'])], [])
        for c in GOLD.values():
            self.assertEqual(list(v.iter_errors(c['context'])), [])


if __name__ == '__main__':
    unittest.main(verbosity=1)
