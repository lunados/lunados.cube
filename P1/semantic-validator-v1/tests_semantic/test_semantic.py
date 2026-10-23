"""P1.4 executable conformance and explicit negative controls."""
import copy
import json
import unittest
from pathlib import Path
from cube_semantic.validator import SemanticValidator,validate_qualification_profiles,ProfileError
from cube_resolver.resolver import load_context_bytes,ContextError

R=Path(__file__).resolve().parents[1]
F=R/'fixtures'/'semantic'

def J(p):return json.loads(Path(p).read_text(encoding='utf-8'))

def raw(s):return s.encode('utf-8')

class SemanticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s=SemanticValidator()
        cls.migration=J(R/'fixtures'/'migration.binding-context.json')
        cls.meta=J(R/'fixtures'/'metaphysics.binding-context.json')
        cls.method_ctx=J(F/'migration-with-method.binding-context.json')
        cls.qp=J(F/'migration.qualifier-profiles.json')

    def test_01_migration_golden(self):
        r=self.s.validate_bytes((R/'fixtures'/'migration.acg').read_bytes(),context=self.migration)
        self.assertEqual(r['overall_status'],'PASS')
        self.assertEqual(r['checks']['predicate_typing']['status'],'PASS')
        self.assertEqual(r['checks']['qualifier_typing']['status'],'NOT_EVALUATED')
        self.assertEqual(r['epistemic_warrant'],'NOT_EVALUATED')

    def test_02_metaphysics_golden(self):
        r=self.s.validate_bytes((R/'fixtures'/'metaphysics.acg').read_bytes(),context=self.meta)
        self.assertEqual(r['overall_status'],'PASS')
        self.assertEqual(r['current_authority'],'NOT_EVALUATED')

    def test_03_unknown_predicate_cannot_auto_bind(self):
        r=self.s.validate_bytes(raw('rel("causedBy",Y:α:Artifact["example:migration-plan"],Y:α:Resource["example:source-repository"])'),context=self.migration)
        self.assertEqual(r['checks']['predicate_typing']['status'],'UNRESOLVED')
        self.assertIn('P1_PREDICATE_PROFILE_MISSING',[d['code'] for d in r['diagnostics']])

    def test_04_wrong_direction_rejected(self):
        r=self.s.validate_bytes(raw('rel("references",Y:α:Resource["example:source-repository"],Y:α:Artifact["example:migration-plan"])'),context=self.migration)
        self.assertEqual(r['checks']['predicate_typing']['status'],'FAIL')
        self.assertEqual(r['overall_status'],'FAIL')

    def test_05_wrong_predicate_target(self):
        r=self.s.validate_bytes(raw('rel("references",Y:α:Artifact["example:migration-plan"],Y:α:Artifact["example:source-repository"])'),context=self.migration)
        self.assertEqual(r['checks']['predicate_typing']['status'],'FAIL')
        self.assertEqual(r['checks']['referent_binding']['status'],'FAIL')

    def test_06_duplicate_predicates_unresolved(self):
        c=copy.deepcopy(self.migration);c['predicate_contracts'].append(copy.deepcopy(c['predicate_contracts'][0]))
        r=self.s.validate_bytes((R/'fixtures'/'migration.acg').read_bytes(),context=c)
        self.assertEqual(r['checks']['predicate_typing']['status'],'UNRESOLVED')

    def test_07_cross_scope_signature_rejected(self):
        c=copy.deepcopy(self.migration);c['predicate_contracts'][0]['scope']='other-scope'
        r=self.s.validate_bytes((R/'fixtures'/'migration.acg').read_bytes(),context=c)
        self.assertEqual(r['checks']['scope_consistency']['status'],'FAIL')
        self.assertEqual(r['checks']['predicate_typing']['status'],'UNRESOLVED')

    def test_08_missing_scope_unresolved(self):
        c=copy.deepcopy(self.migration);del c['scope_ref']
        r=self.s.validate_bytes((R/'fixtures'/'migration.acg').read_bytes(),context=c)
        self.assertEqual(r['overall_status'],'UNRESOLVED')

    def test_09_referent_scope_conflict(self):
        c=copy.deepcopy(self.migration);c['referents'][0]['scope_ref']='wrong'
        r=self.s.validate_bytes((R/'fixtures'/'migration.acg').read_bytes(),context=c)
        self.assertEqual(r['checks']['scope_consistency']['status'],'FAIL')

    def test_10_referent_scope_unspecified(self):
        c=copy.deepcopy(self.migration);del c['referents'][0]['scope_ref']
        r=self.s.validate_bytes((R/'fixtures'/'migration.acg').read_bytes(),context=c)
        self.assertEqual(r['checks']['scope_consistency']['status'],'UNRESOLVED')

    def test_11_required_qualifier_absent(self):
        c=copy.deepcopy(self.migration);c['predicate_contracts'][0]['required_qualifiers']=['T']
        r=self.s.validate_bytes((R/'fixtures'/'migration.acg').read_bytes(),context=c)
        self.assertEqual(r['checks']['predicate_typing']['status'],'FAIL')

    def test_12_required_qualifier_no_profile_unresolved(self):
        c=copy.deepcopy(self.migration);c['predicate_contracts'][0]['required_qualifiers']=['T']
        expr='rel("references",Y:α:Artifact["example:migration-plan"],Y:α:Resource["example:source-repository"])@T(role="occurrence")'
        r=self.s.validate_bytes(raw(expr),context=c)
        self.assertEqual(r['checks']['predicate_typing']['status'],'PASS')
        self.assertEqual(r['checks']['qualifier_typing']['status'],'UNRESOLVED')

    def test_13_predicate_parameters_untyped(self):
        expr='rel("references",Y:α:Artifact["example:migration-plan"],Y:α:Resource["example:source-repository"];limit=2)'
        r=self.s.validate_bytes(raw(expr),context=self.migration)
        self.assertEqual(r['checks']['predicate_typing']['status'],'UNRESOLVED')

    def test_14_nested_predicate_output_type_unresolved(self):
        expr='rel("references",rel("related",Y:α:Artifact["example:migration-plan"],Y:α:Resource["example:source-repository"]),Y:α:Resource["example:source-repository"])'
        r=self.s.validate_bytes(raw(expr),context=self.migration)
        self.assertEqual(r['checks']['predicate_typing']['status'],'UNRESOLVED')

    def test_15_method_golden(self):
        r=self.s.validate_bytes((F/'example-method.acg').read_bytes(),context=self.method_ctx)
        self.assertEqual(r['overall_status'],'PASS')
        self.assertEqual(r['checks']['method_typing']['status'],'PASS')

    def test_16_method_absent(self):
        r=self.s.validate_bytes((F/'example-method.acg').read_bytes(),context=self.migration)
        self.assertEqual(r['checks']['method_typing']['status'],'UNRESOLVED')

    def test_17_method_argument_type_mismatch(self):
        expr='analysis.describe/v1(Y:α:Resource["example:source-repository"])'
        r=self.s.validate_bytes(raw(expr),context=self.method_ctx)
        self.assertEqual(r['checks']['method_typing']['status'],'FAIL')

    def test_18_method_wrong_arity(self):
        r=self.s.validate_bytes(raw('analysis.describe/v1()'),context=self.method_ctx)
        self.assertEqual(r['checks']['method_typing']['status'],'FAIL')

    def test_19_method_effectful_rejected(self):
        c=copy.deepcopy(self.method_ctx);c['method_contracts'][0]['effect_class']='effectful_declared'
        r=self.s.validate_bytes((F/'example-method.acg').read_bytes(),context=c)
        self.assertEqual(r['checks']['method_typing']['status'],'FAIL')
        self.assertEqual(r['canonical_admission'],'NOT_EVALUATED')

    def test_20_method_unknown_effect_unresolved(self):
        c=copy.deepcopy(self.method_ctx);c['method_contracts'][0]['effect_class']='unknown'
        r=self.s.validate_bytes((F/'example-method.acg').read_bytes(),context=c)
        self.assertEqual(r['checks']['method_typing']['status'],'UNRESOLVED')

    def test_21_method_missing_arg_signature(self):
        c=copy.deepcopy(self.method_ctx);del c['method_contracts'][0]['argument_concept_ids']
        r=self.s.validate_bytes((F/'example-method.acg').read_bytes(),context=c)
        self.assertEqual(r['checks']['method_typing']['status'],'UNRESOLVED')

    def test_22_method_untyped_keywords(self):
        expr='analysis.describe/v1(Y:α:Artifact["example:migration-plan"];quality="high")'
        r=self.s.validate_bytes(raw(expr),context=self.method_ctx)
        self.assertEqual(r['checks']['method_typing']['status'],'UNRESOLVED')

    def test_23_method_duplicate_signature(self):
        c=copy.deepcopy(self.method_ctx);c['method_contracts'].append(copy.deepcopy(c['method_contracts'][0]))
        r=self.s.validate_bytes((F/'example-method.acg').read_bytes(),context=c)
        self.assertEqual(r['checks']['method_typing']['status'],'UNRESOLVED')

    def test_24_method_nested_arg_return_unknown(self):
        expr='analysis.describe/v1(analysis.describe/v1(Y:α:Artifact["example:migration-plan"]))'
        r=self.s.validate_bytes(raw(expr),context=self.method_ctx)
        self.assertEqual(r['checks']['method_typing']['status'],'UNRESOLVED')

    def test_25_temporal_invalid(self):
        expr='Y:α:Artifact["example:migration-plan"]@T(role="strange")'
        r=self.s.validate_bytes(raw(expr),context=self.migration)
        self.assertEqual(r['checks']['qualifier_typing']['status'],'FAIL')

    def test_26_temporal_without_profile(self):
        expr='Y:α:Artifact["example:migration-plan"]@T(role="occurrence")'
        r=self.s.validate_bytes(raw(expr),context=self.migration)
        self.assertEqual(r['checks']['qualifier_typing']['status'],'UNRESOLVED')

    def test_27_T_and_O_declared_profiles(self):
        r=self.s.validate_bytes((F/'example-qualified.acg').read_bytes(),context=self.method_ctx,qualification_profiles=self.qp)
        self.assertEqual(r['checks']['qualifier_typing']['status'],'PASS')
        self.assertEqual(r['overall_status'],'PASS')
        self.assertEqual(r['epistemic_warrant'],'NOT_EVALUATED')

    def test_28_T_missing_declared_clock_and_origin(self):
        expr='Y:α:Artifact["example:migration-plan"]@T(role="occurrence",witness_ref="fixture:clock-01")'
        r=self.s.validate_bytes(raw(expr),context=self.method_ctx,qualification_profiles=self.qp)
        self.assertEqual(r['checks']['qualifier_typing']['status'],'FAIL')
        self.assertIn('P1_QUALIFIER_SIGNATURE',[d['code'] for d in r['diagnostics']])

    def test_29_T_unlisted_witness(self):
        expr='Y:α:Artifact["example:migration-plan"]@T(role="occurrence",clock="UTC",origin="fixture:clock-01",precision="second",source_ref="fixture:source",witness_ref="fabricated")'
        r=self.s.validate_bytes(raw(expr),context=self.method_ctx,qualification_profiles=self.qp)
        self.assertEqual(r['checks']['qualifier_typing']['status'],'UNRESOLVED')

    def test_30_O_requires_witness(self):
        expr='Y:α:Artifact["example:migration-plan"]@O(delivered=true)'
        r=self.s.validate_bytes(raw(expr),context=self.method_ctx,qualification_profiles=self.qp)
        self.assertEqual(r['checks']['qualifier_typing']['status'],'UNRESOLVED')
        self.assertIn('P1_OBSERVER_WITNESS',[d['code'] for d in r['diagnostics']])

    def test_31_M_without_profile_is_only_VG(self):
        expr='Y:α:Artifact["example:migration-plan"]@M(mode="Strict")'
        r=self.s.validate_bytes(raw(expr),context=self.method_ctx)
        self.assertEqual(r['checks']['qualifier_typing']['status'],'UNRESOLVED')

    def test_32_M_with_local_visual_profile(self):
        r=self.s.validate_bytes((F/'example-m.acg').read_bytes(),context=self.method_ctx,qualification_profiles=self.qp)
        self.assertEqual(r['checks']['qualifier_typing']['status'],'PASS')
        self.assertEqual(r['canonical_admission'],'NOT_EVALUATED')

    def test_33_M_bad_fixture_value(self):
        expr='Y:α:Artifact["example:migration-plan"]@M(mode="admin")'
        r=self.s.validate_bytes(raw(expr),context=self.method_ctx,qualification_profiles=self.qp)
        self.assertEqual(r['checks']['qualifier_typing']['status'],'FAIL')

    def test_34_F_pure_method_local(self):
        r=self.s.validate_bytes((F/'example-f.acg').read_bytes(),context=self.method_ctx,qualification_profiles=self.qp)
        self.assertEqual(r['checks']['qualifier_typing']['status'],'PASS')

    def test_35_F_missing_method(self):
        r=self.s.validate_bytes((F/'example-f.acg').read_bytes(),context=self.migration,qualification_profiles=self.qp)
        self.assertEqual(r['checks']['qualifier_typing']['status'],'UNRESOLVED')

    def test_36_profile_wrong_scope(self):
        q=copy.deepcopy(self.qp);q['scope']='foreign'
        r=self.s.validate_bytes((F/'example-m.acg').read_bytes(),context=self.method_ctx,qualification_profiles=q)
        self.assertEqual(r['checks']['scope_consistency']['status'],'FAIL')

    def test_37_profile_ambiguous_coordinate(self):
        q=copy.deepcopy(self.qp);m=copy.deepcopy(q['qualifiers'][2]);m['profile_ref']='fixture:M-extra/v1';q['qualifiers'].append(m)
        r=self.s.validate_bytes((F/'example-m.acg').read_bytes(),context=self.method_ctx,qualification_profiles=q)
        self.assertEqual(r['checks']['qualifier_typing']['status'],'UNRESOLVED')

    def test_38_explicit_profile_ref_breaks_tie(self):
        q=copy.deepcopy(self.qp);m=copy.deepcopy(q['qualifiers'][2]);m['profile_ref']='fixture:M-extra/v1';q['qualifiers'].append(m)
        a={'kind':'qualified','expression':{'kind':'reference','address':{'home':'Y','layer':'α','concept_key':'Artifact'},'referent_ref':'example:migration-plan'},
           'qualifiers':[{'coordinate':'M','parameters':{'mode':'Strict'},'profile_ref':'fixture:M-display/v1'}]}
        r=self.s.validate_bytes(json.dumps(a,ensure_ascii=False).encode(),input_format='json_ast',context=self.method_ctx,qualification_profiles=q)
        self.assertEqual(r['checks']['qualifier_typing']['status'],'PASS')
        self.assertEqual(r['checks']['syntax']['status'],'NOT_EVALUATED')

    def test_39_invalid_profile_rejected(self):
        q=copy.deepcopy(self.qp);q['qualifiers'][0]['required_parameters'].remove('witness_ref')
        with self.assertRaises(ProfileError):validate_qualification_profiles(q)

    def test_40_duplicate_profile_names_rejected(self):
        q=copy.deepcopy(self.qp);q['qualifiers'][1]['profile_ref']=q['qualifiers'][0]['profile_ref']
        with self.assertRaises(ProfileError):validate_qualification_profiles(q)

    def test_41_temporal_extension_illegal(self):
        q=copy.deepcopy(self.qp);q['qualifiers'][0]['allowed_values']['role']=['magic-time']
        with self.assertRaises(ProfileError):validate_qualification_profiles(q)

    def test_42_schema_static_not_trust(self):
        r=self.s.validate_bytes((R/'fixtures'/'migration.ast.json').read_bytes(),input_format='json_ast',context=self.migration)
        self.assertEqual(r['overall_status'],'PASS')
        self.assertEqual(r['checks']['syntax']['status'],'NOT_EVALUATED')
        self.assertEqual(r['canonical_admission'],'NOT_EVALUATED')

    def test_43_no_context_returns_unresolved(self):
        r=self.s.validate_bytes((R/'fixtures'/'migration.acg').read_bytes())
        self.assertEqual(r['overall_status'],'UNRESOLVED')

    def test_44_fail_precedence_over_unresolved(self):
        r=self.s.validate_bytes(raw('rel("related", X:α:Σ["x"], Y:α:Wizard["a"])'))
        self.assertEqual(r['overall_status'],'FAIL')

    def test_45_semantic_not_truth(self):
        r=self.s.validate_bytes((F/'example-qualified.acg').read_bytes(),context=self.method_ctx,qualification_profiles=self.qp)
        for key in ('epistemic_warrant','canonical_admission','current_authority'):
            self.assertEqual(r[key],'NOT_EVALUATED')

    def test_46_context_reject_invalid_required(self):
        c=copy.deepcopy(self.migration);del c['predicate_contracts']
        with self.assertRaises(ContextError):load_context_bytes(json.dumps(c).encode())

    def test_47_scope_conflict_both_present_deterministic(self):
        c=copy.deepcopy(self.method_ctx);c['referents'][0]['scope_ref']='other'
        one=self.s.validate_bytes((F/'example-method.acg').read_bytes(),context=c)
        two=self.s.validate_bytes((F/'example-method.acg').read_bytes(),context=c)
        self.assertEqual(one,two)

    def test_48_no_relation_not_evaluated(self):
        r=self.s.validate_bytes(raw('Y:α:Artifact["example:migration-plan"]'),context=self.method_ctx)
        self.assertEqual(r['checks']['predicate_typing']['status'],'NOT_EVALUATED')
        self.assertEqual(r['checks']['method_typing']['status'],'NOT_EVALUATED')


# Execute P1.1's 25 cases as *actual* end-to-end integration tests (not just design claims).
_cases=J(R/'baseline'/'P1_1_Contract_Freeze'/'fixtures'/'conformance_cases.json')['cases']

def _case_test(c):
    def test(self):
        if 'input_text' in c:
            data=raw(c['input_text'])
        elif c['id']=='F01':
            data=(R/'fixtures'/'migration.acg').read_bytes()
        elif c['id']=='F02':
            data=(R/'fixtures'/'metaphysics.acg').read_bytes()
        else:raise AssertionError('Unknown external fixture')
        ctx=None
        if c.get('context'):
            ctx=self.migration if 'migration.' in c['context'] else self.meta
        report=self.s.validate_bytes(data,context=ctx)
        self.assertEqual(report['overall_status'],c['expected_overall'],c['id'])
        if c.get('expect_code'):
            self.assertIn(c['expect_code'],[d['code'] for d in report['diagnostics']],c['id'])
        if c['id'] in ('F01','F02'):
            self.assertEqual(report['checks'][c['expect_check']]['status'],'PASS')
    return test

for _case in _cases:
    setattr(SemanticTests,'test_fixture_'+_case['id'],_case_test(_case))
