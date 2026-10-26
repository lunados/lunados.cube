"""P1.10 local test suite. Fixed oracle expectations; no G5 mutation, no network."""
import copy, hashlib, json, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
for p in ('semantic-validator-v1', 'instantiation-profile-v1', 'simulation-profile-v1', 'comparison-profile-v1', 'migration-profile-v1'):
    sys.path.insert(0, str(ROOT/p))
sys.dont_write_bytecode = True
from cube_p110.validator import P110Validator, CODES
from cube_p110 import migration
from cube_p110.migration import MigrationError, project_v4
from cube_p19.validator import P19Validator

HERE = ROOT/'migration-profile-v1'
VEC = {c['id']: c for c in json.loads((HERE/'fixtures/m01_m22_materialized.json').read_text())['cases']}
ORACLE = {c['id']: c for c in json.loads((HERE/'oracles/independent_m01_m22.json').read_text())['cases']}
CVEC = json.loads((ROOT/'comparison-profile-v1/fixtures/c01_c20_materialized.json').read_text())['cases']
SVEC = json.loads((ROOT/'simulation-profile-v1/fixtures/s01_s17_materialized.json').read_text())['cases']
RVEC = json.loads((ROOT.parent/'P3/charge3-p16/fixtures/r01_r13_materialized.json').read_text())['cases']
P19GOLD = sorted((ROOT/'comparison-profile-v1/fixtures').glob('golden_*.json'))
GOLDEN = json.loads((HERE/'fixtures/golden_migration_synthetic.json').read_text())
V = P110Validator()
NOPROMO = ('epistemic_warrant', 'current_authority', 'canonical_admission')


def run(text, ctx, qp=None):
    return V.validate_bytes(text.encode(), context=ctx, qualification_profiles=qp)


def codes(r): return [d['code'] for d in r['diagnostics']]


def base():
    c = VEC['M-01']; return c['input_text'], copy.deepcopy(c['context'])


def plan(c): return c['migration_plans'][0]
def dep(c, i): return next(d for d in plan(c)['dependencies'] if d['dependency_id'] == i)


class Oracle(unittest.TestCase):
    def test_vectors_match_independent_oracle(self):
        self.assertEqual(set(VEC), set(ORACLE)); self.assertEqual(len(VEC), 22)
        for i, c in sorted(VEC.items()):
            with self.subTest(id=i):
                self.assertEqual((c['expected_overall'], c['required_codes']),
                                 (ORACLE[i]['expected_overall'], ORACLE[i]['required_codes']))
                if c['expected_overall'] == 'MCP_ERROR':
                    with self.assertRaises(ValueError): run(c['input_text'], c['context'], c.get('qualification_profiles'))
                    continue
                r = run(c['input_text'], c['context'], c.get('qualification_profiles'))
                self.assertEqual(r['overall_status'], c['expected_overall'], r)
                for code in c['required_codes']: self.assertIn(code, codes(r))
                for k in NOPROMO: self.assertEqual(r[k], 'NOT_EVALUATED')       # P1.10-08
                if c['expected_overall'] == 'PASS': self.assertEqual(r['diagnostics'], [])


class Regression(unittest.TestCase):
    """P1.10-02: /1 ... /4 byte-identical to P1.9."""
    def _same(self, cases):
        p19 = P19Validator()
        for c in cases:
            with self.subTest(id=c['id']):
                a = b = None
                try: a = p19.validate_bytes(c['input_text'].encode(), input_format=c['input_format'], context=c['context'])
                except ValueError as e: a = ('err', type(e).__name__)
                try: b = V.validate_bytes(c['input_text'].encode(), input_format=c['input_format'], context=c['context'])
                except ValueError as e: b = ('err', type(e).__name__)
                self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))

    def test_c_vectors(self): self._same(CVEC)
    def test_s_vectors(self): self._same(SVEC)
    def test_r_vectors(self): self._same(RVEC)

    def test_p19_goldens(self):
        p19 = P19Validator()
        for f in P19GOLD:
            g = json.loads(f.read_text())
            text, ctx = g['input_text'], g['context']
            a = p19.validate_bytes(text.encode(), context=ctx); b = V.validate_bytes(text.encode(), context=ctx)
            self.assertEqual(a, b, f.name); self.assertEqual(b['overall_status'], 'PASS')


class Config(unittest.TestCase):
    def _err(self, ctx, text=None):
        with self.assertRaises(ValueError): run(text or base()[0], ctx)

    def test_profile_import_requires_scope_ref(self):
        _, c = base(); del c['scope_ref']; self._err(c)

    def test_library_ref_must_match_pinned_sha(self):
        t, c = base()
        sha = migration.PINNED['P1.10/migration-predicates-v1'][1]
        lib = {'library_id': 'lunados.lib', 'entry_id': 'migration-predicates', 'revision': 'v1', 'sha256': sha}
        c['predicate_profile_refs'] = [{'profile_id': 'P1.10/migration-predicates-v1', 'library_ref': lib}]
        self.assertEqual(run(t, c)['overall_status'], 'PASS')
        c['predicate_profile_refs'][0]['library_ref']['sha256'] = '0' * 64; self._err(c)

    def test_pinned_file_matches_sha256sums(self):
        line = (HERE/'SHA256SUMS.txt').read_text().split()
        raw = (HERE/line[1]).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), line[0])
        self.assertEqual(migration.PINNED['P1.10/migration-predicates-v1'][1], line[0])

    def test_tampered_profile_is_refused(self):
        saved = dict(migration.PINNED); cache = dict(migration._CACHE)
        try:
            migration._CACHE.clear()
            migration.PINNED['P1.10/migration-predicates-v1'] = ('migration-predicates-v1.json', 'f' * 64)
            self._err(base()[1])
        finally:
            migration.PINNED.clear(); migration.PINNED.update(saved); migration._CACHE.update(cache)

    def test_shape_errors(self):
        for mut in (lambda c: dep(c, 'd1').update(dropped=True),                       # successor + dropped
                    lambda c: plan(c)['dependencies'].append(copy.deepcopy(dep(c, 'd2'))),  # duplicate id
                    lambda c: dep(c, 'd1').update(kind='mailbox'),                      # DP-5 enum
                    lambda c: dep(c, 'd1').update(holds_in=[]),
                    lambda c: plan(c)['phases'][0].update(role='start'),
                    lambda c: c.update(migration_plans=[plan(c), copy.deepcopy(plan(c))])):
            with self.subTest(mut=mut):
                _, c = base(); mut(c); self._err(c)

    def test_v5_fields_rejected_in_v3(self):
        _, c = base(); c['format'] = 'aiaeao.cube.binding-context/3'; self._err(c)

    def test_projection_is_v4_with_bound_imports(self):
        _, c = base(); p = project_v4(c)
        self.assertEqual(p['format'], 'aiaeao.cube.binding-context/4')
        self.assertNotIn('migration_plans', p); self.assertNotIn('predicate_profile_refs', p)
        self.assertEqual(len(p['predicate_contracts']), 8)
        self.assertTrue(all(x['scope'] == 'mig' and x['origin'] == 'external_declaration_unverified' for x in p['predicate_contracts']))


class Rules(unittest.TestCase):
    """P1.10-07: rows of §2 not already isolated by an M vector."""
    def _st(self, c, text=None, qp=None):
        r = run(text or base()[0], c, qp); return r['overall_status'], codes(r)

    def test_duplicate_phase_id(self):
        _, c = base(); plan(c)['phases'][1]['phase_id'] = 'p0'
        st, cs = self._st(c); self.assertEqual(st, 'FAIL'); self.assertIn('P1_MIGRATION_PHASES', cs)

    def test_undeclared_dependency_referent(self):
        _, c = base(); dep(c, 'd2')['object'] = 'ghost'
        st, cs = self._st(c); self.assertIn('P1_MIGRATION_REFERENCE_MISSING', cs)

    def test_undeclared_successor(self):
        _, c = base(); dep(c, 'd1')['successor_ref'] = 'd-none'
        st, cs = self._st(c); self.assertEqual(st, 'UNRESOLVED'); self.assertIn('P1_MIGRATION_REFERENCE_MISSING', cs)

    def test_retired_before_introduced(self):
        _, c = base()
        plan(c)['transitions'].append({'transition_id': 't0', 'at_phase': 'p0', 'retires': ['new'], 'introduces': [],
                                       'T': {'role': 'scheduling'}, 'witness_ref': 'w'})
        st, cs = self._st(c); self.assertEqual(st, 'FAIL'); self.assertIn('P1_MIGRATION_TRANSITION_CONFLICT', cs)

    def test_transition_without_witness(self):
        _, c = base(); del plan(c)['transitions'][0]['witness_ref']
        st, cs = self._st(c); self.assertEqual(st, 'UNRESOLVED'); self.assertIn('P1_QUALIFIER_PROFILE_MISSING', cs)

    def test_unknown_dependency_predicate(self):
        _, c = base(); dep(c, 'd2')['predicate_id'] = 'mirrors'; dep(c, 'd1')['predicate_id'] = 'mirrors'
        st, cs = self._st(c); self.assertEqual(st, 'UNRESOLVED'); self.assertIn('P1_PREDICATE_PROFILE_MISSING', cs)

    def test_dependency_cannot_carry_required_t(self):
        _, c = base(); c['referents'][0]['concept_id'] = 'Z:module-body:provider'
        dep(c, 'd1')['predicate_id'] = dep(c, 'd2')['predicate_id'] = 'supersedes'
        st, cs = self._st(c, 'rel("depends-on",Z:α:ThirdPartyDependency["old"],Z:α:ThirdPartyDependency["old"])')
        self.assertIn('P1_PREDICATE_SIGNATURE', cs)

    def test_local_contract_for_other_predicate_is_usable(self):
        _, c = base(); c['referents'].append({'ref': 'doc', 'concept_id': 'Y:resource-object:resource', 'home': 'Y', 'layers': ['α'],
                                              'provenance_status': 'declared_unverified', 'scope_ref': 'mig'})
        c['predicate_contracts'] = [{'predicate_id': 'mentions', 'revision': 'local:v1', 'scope': 'mig', 'origin': 'illustrative_fixture',
                                     'subject_concept_ids': ['Y:resource-object:resource'], 'object_concept_ids': ['Z:module-body:provider'],
                                     'direction': 'subject_to_object'}]
        plan(c)['dependencies'].append({'dependency_id': 'd5', 'subject': 'doc', 'predicate_id': 'mentions', 'object': 'new',
                                        'kind': 'docs', 'holds_in': ['p1', 'p2'], 'witness_ref': 'w'})
        self.assertEqual(self._st(c), ('PASS', []))

    def test_supersedes_without_matching_transition(self):
        c18 = VEC['M-18']; c = copy.deepcopy(c18['context']); plan(c)['transitions'][0]['introduces'] = []
        dep(c, 'd2')['holds_in'] = ['p1', 'p2']
        st, cs = self._st(c, c18['input_text'], c18['qualification_profiles'])
        self.assertEqual(st, 'FAIL'); self.assertIn('P1_MIGRATION_EXPRESSION_MISMATCH', cs)

    def test_deterministic_plan_order(self):
        """P1.10-09: plan diagnostics ordered by plan, then item index; repeated runs identical."""
        _, c = base(); del dep(c, 'd1')['witness_ref']; dep(c, 'd2')['holds_in'] = ['p0', 'p1', 'p2']
        a = run(base()[0], c); b = run(base()[0], copy.deepcopy(c))
        self.assertEqual(a, b)
        paths = [d['message'].split(':')[0] for d in a['diagnostics'] if d['code'] in CODES]
        key = lambda p: [int(x) if x.isdigit() else x for x in p.split('/')[:5]]   # plan, section, item index
        self.assertEqual(paths, sorted(paths, key=key))

    def test_every_new_code_registered(self):
        reg = json.loads((HERE/'DIAGNOSTIC_EXTENSION.json').read_text())
        new = {x['code'] for x in reg['codes']}
        self.assertEqual(new, {c for c in CODES if c.startswith('P1_MIGRATION_')})
        self.assertTrue(all(x['reference_rule'] for x in reg['codes']))


class Golden(unittest.TestCase):
    def test_golden_negative_and_corrected(self):
        """P1.10-14."""
        cs = {c['id']: c for c in GOLDEN['cases']}
        self.assertEqual(set(cs), {'G-neg', 'G-pos'})
        pos = cs['G-pos']['context']; mp = plan(pos)
        self.assertGreaterEqual(len(mp['dependencies']), 15); self.assertGreaterEqual(len(mp['phases']), 3)
        for c in cs.values():
            r = run(c['input_text'], c['context'], c['qualification_profiles'])
            self.assertEqual(r['overall_status'], c['expected_overall'])
            for code in c['required_codes']: self.assertIn(code, codes(r))
            for k in NOPROMO: self.assertEqual(r[k], 'NOT_EVALUATED')
        self.assertTrue(all(r['ref'].startswith('acme:') for r in pos['referents']))


class Schema(unittest.TestCase):
    def test_vectors_valid_against_context_v5_schema(self):
        try:
            import jsonschema
            jsonschema.Draft202012Validator
        except (ImportError, AttributeError):
            self.skipTest('jsonschema >= 4.18 required')
        s5 = json.loads((HERE/'context-v5.schema.json').read_text())
        s4 = json.loads((ROOT/'comparison-profile-v1/context-v4.schema.json').read_text())
        v5, v4 = jsonschema.Draft202012Validator(s5), jsonschema.Draft202012Validator(s4)
        for i, c in sorted(VEC.items()):
            with self.subTest(id=i):
                errs = list(v5.iter_errors(c['context']))
                if i == 'M-20':
                    self.assertTrue(list(v4.iter_errors(c['context'])))          # /5 field in /4
                else:
                    self.assertEqual(errs, [], i)
        for c in GOLDEN['cases']:
            self.assertEqual(list(v5.iter_errors(c['context'])), [])
        for c in CVEC:                                                           # strict superset
            if c['context']['format'].endswith('/4'):
                c5 = dict(c['context'], format='aiaeao.cube.binding-context/5')
                self.assertEqual(list(v5.iter_errors(c5)), [], c['id'])


if __name__ == '__main__':
    unittest.main(verbosity=1)
