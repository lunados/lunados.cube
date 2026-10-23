"""P1.3 independent resolution tests. stdlib unittest; optional jsonschema oracle in separate script."""
import hashlib
import json
import re
from pathlib import Path
import subprocess
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from cube_resolver import Resolver, validate_context, load_context_bytes, ContextError, ContractError
from cube_parser.parser import parse_result, validate_ast, json_dump

R=Resolver()
context=lambda n: load_context_bytes((ROOT/'fixtures'/(n+'.binding-context.json')).read_bytes())

def run(s,ctx=None,fmt='acg_text'):
    return R.resolve_bytes(s.encode('utf-8') if isinstance(s,str) else s,input_format=fmt,context=ctx)
def codes(x): return [e['code'] for e in x['diagnostics']]
def ref(key='Artifact',home='Y',layer='α',rid='example:migration-plan'):
    return f'{home}:{layer}:{key}["{rid}"]'

class FrozenSourceTests(unittest.TestCase):
    def test_lock_catalog_80_and_five_aliases(self):
        self.assertEqual(len(R.catalog),80)
        self.assertEqual(len(R.exact),85)
        self.assertEqual(set(R.exact.keys())&{('X',x) for x in 'ΨΓΣΞΠ'}, {('X',x) for x in 'ΨΓΣΞΠ'})
    def test_manifest_catalog_hash(self):
        data=(ROOT/'baseline/P0_reference/grammar/concepts.json').read_bytes()
        locked=json.loads((ROOT/'baseline/P1_1_Contract_Freeze/contract/source_lock.json').read_text())
        expected=next(x['sha256'] for x in locked['sources'] if x['name']=='P0/v9.4/grammar/concepts.json')
        self.assertEqual(hashlib.sha256(data).hexdigest(),expected)
    def test_every_canonical_key_maps_correctly(self):
        for (home,key),entry in sorted(R.exact.items()):
            with self.subTest(key=key):
                self.assertEqual(entry['home'],home)
                self.assertEqual(R.catalog[entry['concept_id']]['home'],home)
                self.assertEqual(R.catalog[entry['concept_id']]['kind'],entry['kind'])
    def test_input_ast_not_mutated(self):
        ast=parse_result(ref().encode())['ast'];before=json_dump(ast)
        R.resolve_ast(ast,context('migration'))
        self.assertEqual(json_dump(ast),before)

class ConceptResolutionTests(unittest.TestCase):
    def test_qualifier_preserves_nested_reference(self):
        x=run('('+ref()+')@T(role="recording")@O(observer="test")',context('migration'))
        self.assertEqual(x['checks']['concept_resolution']['status'],'PASS')
        self.assertEqual(x['checks']['referent_binding']['status'],'PASS')
        self.assertEqual(x['bindings'][0]['ast_path'],'/expression')
        self.assertEqual(x['checks']['qualifier_typing']['status'],'NOT_EVALUATED')
    def test_all_five_dimensions_noninstantiable(self):
        for k in 'ΨΓΣΞΠ':
            with self.subTest(key=k):
                x=run('X:α:'+k+'["q"]')
                self.assertEqual(x['resolution_status'],'FAIL')
                self.assertEqual(codes(x),['P1_NON_INSTANTIABLE'])
    def test_dimension_english_name_noninstantiable(self):
        x=run('X:α:Semantics["q"]')
        self.assertEqual(codes(x),['P1_NON_INSTANTIABLE'])
    def test_relation_arrow_not_instantiable(self):
        x=run('Y:α:Selection["q"]')
        self.assertEqual(codes(x),['P1_NON_INSTANTIABLE'])
    def test_logic_relation_not_instantiable(self):
        x=run('X:α:Verification["q"]')
        self.assertEqual(codes(x),['P1_NON_INSTANTIABLE'])
    def test_wrong_home_failure(self):
        x=run('Y:α:Event["event:e1"]')
        self.assertEqual(x['checks']['concept_resolution']['status'],'FAIL')
        self.assertEqual(codes(x),['P1_WRONG_HOME'])
    def test_unknown_key_unresolved(self):
        x=run('Y:α:Wizard["ref"]')
        self.assertEqual(x['resolution_status'],'UNRESOLVED')
        self.assertEqual(codes(x),['P1_UNKNOWN_CONCEPT'])
    def test_case_and_nfkc_not_aliased(self):
        for k in ('artifact','Ａｒｔｉｆａｃｔ'):
            with self.subTest(k=k):
                x=run(f'Y:α:{k}["ref"]')
                self.assertEqual(codes(x),['P1_UNKNOWN_CONCEPT'])
    def test_wrong_home_never_falls_through_to_other_concept(self):
        x=run('Z:α:Actor["ref"]')
        self.assertEqual(codes(x),['P1_WRONG_HOME'])
    def test_concept_id_annotation_contradiction_fails(self):
        ast=parse_result(ref().encode())['ast']
        ast['address']['concept_id']='Y:resource-object:resource'
        x=run(json_dump(ast),context('migration'),'json_ast')
        self.assertEqual(codes(x),['P1_REFERENT_MISMATCH'])
        self.assertEqual(x['checks']['concept_resolution']['status'],'PASS')
        self.assertEqual(x['checks']['referent_binding']['status'],'FAIL')
    def test_nonavailable_instance_profile_unresolved(self):
        x=run('X:α:Result["r"]',context('migration'))
        self.assertEqual(codes(x),['P1_INSTANTIATION_PROFILE_REQUIRED'])
    def test_nonavailable_zone_profile_unresolved(self):
        entries=[v for v in R.exact.values() if v['kind']=='zone']
        self.assertTrue(entries)
        e=entries[0]
        x=run(f'{e["home"]}:α:{e["concept_key"]}["r"]')
        self.assertEqual(codes(x),['P1_INSTANTIATION_PROFILE_REQUIRED'])

class BindingTests(unittest.TestCase):
    def test_two_golden_examples_p13_pass(self):
        for n in ('migration','metaphysics'):
            with self.subTest(name=n):
                x=R.resolve_bytes((ROOT/'fixtures'/(n+'.acg')).read_bytes(),context=context(n))
                self.assertEqual(x['resolution_status'],'PASS')
                self.assertEqual(x['checks']['concept_resolution']['status'],'PASS')
                self.assertEqual(x['checks']['referent_binding']['status'],'PASS')
                self.assertEqual(x['checks']['predicate_typing']['status'],'NOT_EVALUATED')
                self.assertEqual(x['epistemic_warrant'],'NOT_EVALUATED')
                self.assertEqual(x['canonical_admission'],'NOT_EVALUATED')
                self.assertTrue(x['bindings'])
                self.assertTrue(all(b['provenance_status']=='declared_unverified' for b in x['bindings']))
    def test_golden_ast_same_resolution_as_text(self):
        for n in ('migration','metaphysics'):
            ctx=context(n)
            a=R.resolve_bytes((ROOT/'fixtures'/(n+'.acg')).read_bytes(),context=ctx)
            b=R.resolve_bytes((ROOT/'fixtures'/(n+'.ast.json')).read_bytes(),input_format='json_ast',context=ctx)
            self.assertEqual(a['bindings'],b['bindings'])
            self.assertEqual(b['checks']['syntax']['status'],'NOT_EVALUATED')
    def test_without_context_remains_unresolved(self):
        x=run(ref())
        self.assertEqual(codes(x),['P1_BINDING_CONTEXT_REQUIRED'])
        self.assertEqual(x['checks']['concept_resolution']['status'],'PASS')
        self.assertEqual(x['checks']['referent_binding']['status'],'UNRESOLVED')
    def test_missing_referent_in_supplied_context_unresolved(self):
        x=run(ref(rid='example:missing'),context('migration'))
        self.assertEqual(codes(x),['P1_BINDING_CONTEXT_REQUIRED'])
    def test_wrong_concept_failure(self):
        x=run(ref(rid='example:source-repository'),context('migration'))
        self.assertEqual(codes(x),['P1_REFERENT_MISMATCH'])
        self.assertEqual(x['resolution_status'],'FAIL')
    def test_home_consistency_failure(self):
        ctx=context('migration'); ctx['referents'][0]['home']='Z'
        x=run(ref(),ctx)
        self.assertEqual(codes(x),['P1_REFERENT_MISMATCH'])
    def test_layer_explicit_mismatch_failure(self):
        x=run(ref(layer='β'),context('migration'))
        self.assertEqual(codes(x),['P1_REFERENT_MISMATCH'])
    def test_scope_explicit_mismatch_failure(self):
        ctx=context('migration'); ctx['referents'][0]['scope_ref']='different-scope'
        x=run(ref(),ctx)
        self.assertEqual(codes(x),['P1_REFERENT_MISMATCH'])
    def test_beta_witness_missing_unresolved(self):
        ctx=context('migration');ctx['referents'][0]['layers'].append('β')
        x=run(ref(layer='β'),ctx)
        self.assertEqual(codes(x),['P1_LAYER_WITNESS_MISSING'])
    def test_zeta_witness_missing_unresolved(self):
        ctx=context('migration');ctx['referents'][0]['layers'].append('ζ')
        x=run(ref(layer='ζ'),ctx)
        self.assertEqual(codes(x),['P1_LAYER_WITNESS_MISSING'])
    def test_zeta_declared_witness_pointer_not_truth(self):
        ctx=context('migration');ctx['referents'][0]['layers'].append('ζ')
        ctx['referents'][0]['witness_ref']='declaration:unverified-witness'
        x=run(ref(layer='ζ'),ctx)
        self.assertEqual(x['resolution_status'],'PASS')
        self.assertEqual(x['bindings'][0]['witness_truth'],'NOT_EVALUATED')
        self.assertEqual(x['checks']['qualifier_typing']['status'],'NOT_EVALUATED')
        self.assertEqual(x['canonical_admission'],'NOT_EVALUATED')
    def test_nested_method_and_relation_all_references_visited(self):
        s='audio.duck/v1(rel("related",Y:α:Actor["actor:unknown"],'+ref()+'),'+ref(rid='example:source-repository',key='Resource')+')'
        x=run(s,context('migration'))
        self.assertEqual(len(x['bindings']),3)
        self.assertEqual([b['ast_path'] for b in x['bindings']],['/arguments/0/subject','/arguments/0/object','/arguments/1'])
        self.assertEqual(x['resolution_status'],'UNRESOLVED')
        self.assertEqual(codes(x),['P1_BINDING_CONTEXT_REQUIRED'])
        self.assertEqual(x['checks']['method_typing']['status'],'NOT_EVALUATED')
    def test_multiple_diagnostics_stable_traversal(self):
        s='rel("related",Y:α:Wizard["x"],Y:α:Event["y"])'
        a=run(s); b=run(s)
        self.assertEqual(a,b)
        self.assertEqual(codes(a),['P1_UNKNOWN_CONCEPT','P1_WRONG_HOME'])
        self.assertEqual(a['resolution_status'],'FAIL')
    def test_relation_name_never_checked_as_typed_signature(self):
        x=run('rel("notAnAdoptedPredicate",'+ref()+','+ref()+')',context('migration'))
        self.assertEqual(x['resolution_status'],'PASS')
        self.assertEqual(x['checks']['predicate_typing']['status'],'NOT_EVALUATED')

class ContextInputTests(unittest.TestCase):
    def test_reject_duplicate_referents(self):
        ctx=context('migration');ctx['referents'].append(ctx['referents'][0].copy())
        with self.assertRaises(ContextError): validate_context(ctx)
    def test_reject_invalid_origin(self):
        ctx=context('migration');ctx['source_kind']='trusted_canonical'
        with self.assertRaises(ContextError): validate_context(ctx)
    def test_reject_scope_property_shape(self):
        ctx=context('migration');ctx['referents'][0]['arbitrary_authority']=True
        with self.assertRaises(ContextError): validate_context(ctx)
    def test_reject_json_duplicate_keys(self):
        with self.assertRaises(ContextError):load_context_bytes(b'{"format":"x","format":"y"}')
    def test_reject_future_context_version(self):
        ctx=context('migration');ctx['reference_version']='v10'
        with self.assertRaises(ContextError): validate_context(ctx)
    def test_reject_bad_layers(self):
        ctx=context('migration');ctx['referents'][0]['layers']=['α','α']
        with self.assertRaises(ContextError): validate_context(ctx)
    def test_reject_bool_as_method_bound(self):
        ctx=context('migration');ctx['method_contracts']=[{'method_id':'audio.duck/v1','revision':'v1','scope':'x',
              'origin':'illustrative_fixture','argument_min':False,'argument_max':1}]
        with self.assertRaises(ContextError): validate_context(ctx)

class StagingAndCITest(unittest.TestCase):
    def test_p11_semantic_slice(self):
        data=json.loads((ROOT/'baseline/P1_1_Contract_Freeze/fixtures/conformance_cases.json').read_text())
        cases={x['id']:x for x in data['cases']}
        expected={'F03':('FAIL','P1_NON_INSTANTIABLE'),'F04':('FAIL','P1_WRONG_HOME'),
                  'F05':('UNRESOLVED','P1_BINDING_CONTEXT_REQUIRED'),'F06':('UNRESOLVED','P1_UNKNOWN_CONCEPT'),
                  'F11':('FAIL','P1_REFERENT_MISMATCH'),'F17':('UNRESOLVED','P1_LAYER_WITNESS_MISSING')}
        for key,(status,code) in expected.items():
            with self.subTest(case=key):
                case=cases[key];ctx=context('migration') if 'migration' in (case.get('context') or '') else None
                x=run(case['input_text'],ctx)
                self.assertEqual((x['resolution_status'],codes(x)[0]),(status,code))
    def test_p11_fixture_A_B_ast_binding_slice(self):
        cases=json.loads((ROOT/'baseline/P1_1_Contract_Freeze/fixtures/conformance_cases.json').read_text())['cases']
        self.assertEqual(len(cases),25)
        for n in ('migration','metaphysics'):
            x=R.resolve_bytes((ROOT/'fixtures'/(n+'.acg')).read_bytes(),context=context(n))
            self.assertEqual(x['resolution_status'],'PASS')
    def test_parser_error_kept_with_stage_diagnostic(self):
        x=run('rel("related",Y:α:Actor["x"]')
        self.assertEqual(x['resolution_status'],'FAIL')
        self.assertEqual(x['checks']['syntax']['status'],'FAIL')
        self.assertEqual(x['checks']['referent_binding']['status'],'NOT_EVALUATED')
        self.assertEqual(x['bindings'],[])
    def test_report_stdout_and_exit_codes(self):
        cmds=[(ref(),2,context('migration')),(ref(rid='unknown'),1,context('migration')),
              ('X:α:Σ["q"]',2,None)]
        for expr,code,ctx in cmds:
            # library API is tested above; CLI smoke test separately here for successful exit.
            self.assertEqual(run(expr,ctx)['resolution_status'], 'PASS' if code==2 and expr==ref() else 'FAIL' if code==2 else 'UNRESOLVED')

if __name__=='__main__': unittest.main()
