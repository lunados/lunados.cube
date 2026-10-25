"""P1.6 local runtime test suite. Fixed expectations, no G5 mutation."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SYS=ROOT/'semantic-validator-v1'
sys.path.insert(0,str(SYS))
sys.path.insert(0,str(ROOT/'instantiation-profile-v1'))
from cube_p16.validator import P16Validator, validate_context, load_context_bytes
from cube_resolver import Resolver, ContextError
from cube_p16.instantiation import reference, InstantiationError, InstantiationCheck

VOCAB=reference()
KEYS=json.loads((SYS/'baseline/P1_1_Contract_Freeze/contract/concept_keys.json').read_text())
BY_ID={e['concept_id']:(e['home'],e['concept_key']) for e in KEYS['entries']}
BASE=json.loads((ROOT/'instantiation-profile-v1/fixtures/valid_conclusion_context_v2.json').read_text())
SCOPE={v['concept_id']:v['pair_scope_concept_id'] for v in VOCAB.values()}

# The local helper constructs declarative fixtures ONLY. The expectation oracle
# is fixed independently in oracles/independent_r01_r13.json.
def fixture(endpoint, *, layer='α'):
    concept='X:endpoint:'+endpoint
    scope_concept=SCOPE[concept]
    scope_id=lambda c:'scope-'+c.rsplit(':',1)[-1]
    root_scope=scope_id(scope_concept)
    def decl(ref, concept_id, scope, layer='α'):
        return {'ref':ref,'concept_id':concept_id,'home':concept_id[0],
                'layers':[layer], 'provenance_status':'declared_unverified','scope_ref':scope}
    ctx={'format':'aiaeao.cube.binding-context/2','reference_version':'v9.4',
         'context_id':'p16-runtime-'+endpoint,'source_kind':'illustrative_fixture',
         'scope_ref':root_scope, 'referents':[], 'predicate_contracts':[], 'instantiation_profiles':[]}
    profiles=set()
    scopes=set()
    counter=[0]
    def ensure_scope(concept_id):
        sid=scope_id(concept_id)
        if sid not in scopes:
            ctx['referents'].append(decl(sid,concept_id,sid))
            scopes.add(sid)
        return sid
    def make(concept_id, ref=None, sublayer='α', parent_scope=None):
        if ref is None:
            counter[0]+=1
            ref='item-'+str(counter[0])
        scope=ensure_scope(SCOPE[concept_id]) if concept_id in VOCAB else parent_scope
        item=decl(ref,concept_id,scope,sublayer)
        ctx['referents'].append(item)
        if concept_id in VOCAB:
            v=VOCAB[concept_id]
            profile_key=(concept_id,scope)
            if profile_key not in profiles:
                ctx['instantiation_profiles'].append({'profile_ref':'p16-'+concept_id,
                    'concept_id':concept_id,'revision':'fixture/v1','scope':scope,
                    'origin':'illustrative_fixture','slots':copy.deepcopy(v['slots'])})
                profiles.add(profile_key)
            item['instantiation_profile_ref']='p16-'+concept_id
            slots={}
            for slot in v['slots']:
                if not slot['required']:continue
                name=slot['name']
                if slot['kind']=='string': slots[name]='declared-action'
                elif slot['kind']=='enum':
                    slots[name]=('refused' if concept_id.endswith(':admission') else
                                 'unresolved' if concept_id.endswith(':conclusion') else slot['values'][0])
                else:
                    target=slot['concept_ids'][0]
                    dest=scope if name=='pair_scope_ref' else make(target,parent_scope=scope)
                    slots[name]=[dest] if slot['cardinality']=='many' else dest
            item['slots']=slots
            if concept_id.endswith(':admission') and slots['decision']=='refused':
                item['slots']['refusal_ref']=make('Z:boundary:refusal',parent_scope=scope)
        return ref
    endpoint_ref=make(concept,ref='primary',sublayer=layer)
    ctx['referents'].sort(key=lambda r:r['ref'])
    return ctx,endpoint_ref


def run(ctx, concept, rid='primary', layer='α', relation=None):
    key=BY_ID[concept][1]
    home=BY_ID[concept][0]
    source=relation or f'{home}:{layer}:{key}["{rid}"]'
    return P16Validator().validate_bytes(source.encode('utf8'),context=ctx)


def statuses(report):
    return report['overall_status'],set(d['code'] for d in report['diagnostics'])


class PositiveEndpoints(unittest.TestCase):
    def test_ten_positive_endpoints(self):
        self.assertEqual(len(VOCAB),10)
        for concept in sorted(VOCAB):
            with self.subTest(concept=concept):
                ctx,_=fixture(concept.split(':')[-1])
                r=run(ctx,concept)
                self.assertEqual(statuses(r),('PASS',set()),r)
                self.assertEqual(r['checks']['referent_binding']['status'],'PASS')
                for k in ('current_authority','canonical_admission','epistemic_warrant'):
                    self.assertEqual(r[k],'NOT_EVALUATED')

    def test_v1_byte_exact_with_frozen_p14(self):
        from cube_semantic.validator import SemanticValidator as FrozenValidator
        from cube_parser.parser import json_dump
        for path in ('migration','metaphysics'):
            c=json.loads((SYS/'fixtures'/(path+'.binding-context.json')).read_text())
            raw=(SYS/'fixtures'/(path+'.acg')).read_bytes()
            a=P16Validator().validate_bytes(raw,context=c)
            b=FrozenValidator().validate_bytes(raw,context=c)
            self.assertEqual(json_dump(a),json_dump(b))

    def test_legacy_format_unchanged(self):
        ctx=copy.deepcopy(BASE)
        for x in ctx['referents']:
            x.pop('slots',None);x.pop('instantiation_profile_ref',None)
        ctx['format']='aiaeao.cube.binding-context/1';ctx.pop('instantiation_profiles',None)
        r=run(ctx,'X:endpoint:conclusion',rid='c1')
        self.assertEqual(statuses(r),('UNRESOLVED',{'P1_INSTANTIATION_PROFILE_REQUIRED'}))

class StructuralFailures(unittest.TestCase):
    def test_missing_required_slot(self):
        c,_=fixture('conclusion');next(r for r in c['referents'] if r['ref']=='primary')['slots'].pop('basis_refs')
        r=run(c,'X:endpoint:conclusion')
        self.assertEqual(statuses(r),('UNRESOLVED',{'P1_INSTANTIATION_SLOT_MISSING'}))
        self.assertIn('/referents/',r['diagnostics'][0]['message'])
    def test_missing_ref_is_unresolved(self):
        c,_=fixture('conclusion');next(r for r in c['referents'] if r['ref']=='primary')['slots']['basis_refs']=['unknown']
        self.assertEqual(statuses(run(c,'X:endpoint:conclusion')),('UNRESOLVED',{'P1_BINDING_CONTEXT_REQUIRED'}))
    def test_wrong_type_fail(self):
        c,_=fixture('conclusion');c['referents'].append({'ref':'bad','concept_id':'X:endpoint:satisfaction','home':'X','layers':['α'], 'provenance_status':'declared_unverified','scope_ref':c['scope_ref']})
        next(r for r in c['referents'] if r['ref']=='primary')['slots']['basis_refs']=['bad']
        self.assertEqual(statuses(run(c,'X:endpoint:conclusion')),('FAIL',{'P1_INSTANTIATION_SLOT_TYPE'}))
    def test_signature_fail(self):
        c,_=fixture('conclusion');next(r for r in c['referents'] if r['ref']=='primary')['slots']['basis_refs']='item-2'
        self.assertEqual(statuses(run(c,'X:endpoint:conclusion')),('FAIL',{'P1_INSTANTIATION_SLOT_SIGNATURE'}))
    def test_enum_fail(self):
        c,_=fixture('conclusion');next(r for r in c['referents'] if r['ref']=='primary')['slots']['disposition']='approved'
        self.assertEqual(statuses(run(c,'X:endpoint:conclusion')),('FAIL',{'P1_INSTANTIATION_SLOT_SIGNATURE'}))
    def test_extra_slot_fail(self):
        c,_=fixture('conclusion');next(r for r in c['referents'] if r['ref']=='primary')['slots']['made_up']='x'
        self.assertEqual(statuses(run(c,'X:endpoint:conclusion')),('FAIL',{'P1_INSTANTIATION_SLOT_SIGNATURE'}))
    def test_wrong_pair_scope_type_fail(self):
        c,_=fixture('conclusion')
        c['referents'].append({'ref':'policy','concept_id':'X:scope:policy','home':'X','layers':['α'], 'provenance_status':'declared_unverified','scope_ref':c['scope_ref']})
        next(r for r in c['referents'] if r['ref']=='primary')['slots']['pair_scope_ref']='policy'
        self.assertEqual(statuses(run(c,'X:endpoint:conclusion')),('FAIL',{'P1_INSTANTIATION_SLOT_TYPE'}))
    def test_wrong_pair_scope_identity_fail(self):
        c,_=fixture('conclusion')
        c['referents'].append({'ref':'other-obs','concept_id':'X:scope:observation','home':'X','layers':['α'], 'provenance_status':'declared_unverified','scope_ref':c['scope_ref']})
        next(r for r in c['referents'] if r['ref']=='primary')['slots']['pair_scope_ref']='other-obs'
        self.assertEqual(statuses(run(c,'X:endpoint:conclusion')),('FAIL',{'P1_SCOPE_CONFLICT'}))
    def test_cycle_fail(self):
        c,_=fixture('expectation');next(r for r in c['referents'] if r['ref']=='primary')['slots']['supersedes_ref']='primary'
        self.assertEqual(statuses(run(c,'X:endpoint:expectation')),('FAIL',{'P1_INSTANTIATION_CYCLE'}))
    def test_missing_admission_authority_conditional_fail(self):
        c,_=fixture('admission');ad=next(r for r in c['referents'] if r['ref']=='primary');ad['slots']['decision']='admitted';ad['slots'].pop('refusal_ref')
        self.assertEqual(statuses(run(c,'X:endpoint:admission')),('FAIL',{'P1_INSTANTIATION_CONDITION'}))
    def test_admitted_plus_refusal_fail(self):
        c,_=fixture('admission');ad=next(r for r in c['referents'] if r['ref']=='primary');ad['slots']['decision']='admitted';ad['slots']['authority_ref']=next(r['ref'] for r in c['referents'] if r['concept_id']=='X:endpoint:action');
        result=run(c,'X:endpoint:admission')
        self.assertIn('P1_INSTANTIATION_CONDITION',statuses(result)[1])
    def test_ambiguous_scoped_profile_unresolved(self):
        c,_=fixture('conclusion');r=next(r for r in c['referents'] if r['ref']=='primary');r.pop('instantiation_profile_ref')
        p=copy.deepcopy(c['instantiation_profiles'][0]);p['profile_ref']='second';c['instantiation_profiles'].append(p)
        self.assertEqual(statuses(run(c,'X:endpoint:conclusion')),('UNRESOLVED',{'P1_INSTANTIATION_PROFILE_AMBIGUOUS'}))
    def test_missing_v2_profile_unresolved(self):
        c,_=fixture('conclusion');c['instantiation_profiles'].clear()
        self.assertEqual(statuses(run(c,'X:endpoint:conclusion')),
                         ('UNRESOLVED',{'P1_INSTANTIATION_PROFILE_REQUIRED'}))
    def test_narrowed_profile_rejects_excluded_allowed_type(self):
        c,_=fixture('conclusion');p=c['instantiation_profiles'][0]
        next(s for s in p['slots'] if s['name']=='basis_refs')['concept_ids']=['X:endpoint:perception']
        primary=next(r for r in c['referents'] if r['ref']=='primary')
        primary['slots']['basis_refs']=[next(r['ref'] for r in c['referents'] if r['concept_id']=='Y:resource-object:evidence')]
        status,cs=statuses(run(c,'X:endpoint:conclusion'))
        self.assertEqual((status,cs),('FAIL',{'P1_INSTANTIATION_SLOT_TYPE'}))
    def test_profile_requiredness_cannot_be_removed(self):
        c,_=fixture('conclusion');next(s for s in c['instantiation_profiles'][0]['slots'] if s['name']=='basis_refs')['required']=False
        with self.assertRaises((ContextError,InstantiationError)):validate_context(c)
    def test_foreign_scoped_explicit_profile_fails(self):
        c,_=fixture('conclusion');c['instantiation_profiles'][0]['scope']='foreign'
        status,cs=statuses(run(c,'X:endpoint:conclusion'))
        self.assertEqual((status,cs),('FAIL',{'P1_SCOPE_CONFLICT'}))
    def test_p16_cli_valid_and_invalid_reports(self):
        import subprocess
        ctx_path=ROOT/'instantiation-profile-v1/fixtures/valid_conclusion_context_v2.json'
        script=ROOT/'instantiation-profile-v1/scripts/validate_p16.py'
        p=subprocess.run([sys.executable,str(script),'--input','-','--context',str(ctx_path)],
                         input='X:α:Conclusion["c1"]'.encode(),capture_output=True,timeout=15)
        self.assertEqual(p.returncode,0,p.stderr)
        report=json.loads(p.stdout)
        self.assertEqual(report['overall_status'],'PASS')
        self.assertEqual(report['epistemic_warrant'],'NOT_EVALUATED')

    def test_invalid_widened_profile_is_config_error(self):
        c,_=fixture('conclusion');p=c['instantiation_profiles'][0]
        next(s for s in p['slots'] if s['name']=='basis_refs')['concept_ids'].append('X:endpoint:satisfaction')
        with self.assertRaises((ContextError,InstantiationError)):validate_context(c)
    def test_invalid_unknown_descriptor_is_config_error(self):
        c,_=fixture('conclusion');p=c['instantiation_profiles'][0]
        p['slots'].append({'name':'self_asserted_warrant','kind':'string','required':True})
        with self.assertRaises((ContextError,InstantiationError)):validate_context(c)
    def test_beta_witness_precedes_slot(self):
        c,_=fixture('perception',layer='ζ');next(r for r in c['referents'] if r['ref']=='primary')['slots'].clear()
        self.assertEqual(statuses(run(c,'X:endpoint:perception',layer='ζ')),('UNRESOLVED',{'P1_LAYER_WITNESS_MISSING'}))
    def test_zone_deferred(self):
        c,_=fixture('conclusion')
        self.assertEqual(statuses(run(c,'Z:zone:ownership')),('UNRESOLVED',{'P1_INSTANTIATION_PROFILE_REQUIRED'}))
    def test_closed_schema_rejection(self):
        c,_=fixture('conclusion');c['referents'][0]['unexpected']='x'
        with self.assertRaises((ContextError,InstantiationError)):validate_context(c)

class AlignmentOracle(unittest.TestCase):
    def test_r01_r13_against_fixed_expected_vectors(self):
        expected=json.loads((ROOT/'instantiation-profile-v1/oracles/independent_r01_r13.json').read_text())
        self.assertEqual(len(expected['cases']),13)
        for case in expected['cases']:
            name=case['id']; ctx=None
            if case['profile']=='none':
                c,_=fixture('conclusion');c['format']='aiaeao.cube.binding-context/1'
                c.pop('instantiation_profiles',None)
                for r in c['referents']:r.pop('slots',None);r.pop('instantiation_profile_ref',None)
                ctx=c
            elif case['profile']=='zone':ctx,_=fixture('conclusion')
            else:ctx,_=fixture(case['profile'])
            primary=next((r for r in ctx['referents'] if r['ref']=='primary'),None)
            source=None
            if name=='R-01':
                ev=next(r['ref'] for r in ctx['referents'] if r['concept_id']=='Y:resource-object:evidence')
                ctx['predicate_contracts']=[{'predicate_id':'supports','revision':'fixture:v1','scope':ctx['scope_ref'],'origin':'illustrative_fixture',
                     'subject_concept_ids':['Y:resource-object:evidence'],'object_concept_ids':['X:endpoint:conclusion'],'direction':'subject_to_object'}]
                source=f'rel("supports",Y:α:Evidence["{ev}"],X:α:Conclusion["primary"])'
            elif name=='R-02':primary['slots'].pop('basis_refs')
            elif name=='R-03':
                ref=next(r['ref'] for r in ctx['referents'] if r['concept_id']=='X:endpoint:expectation')
                next(r for r in ctx['referents'] if r['ref']==ref)['concept_id']='X:endpoint:completion'
            elif name=='R-04':
                ctx['referents'].append({'ref':'bad-satisfaction','concept_id':'X:endpoint:satisfaction','home':'X','layers':['α'],'provenance_status':'declared_unverified','scope_ref':ctx['scope_ref']})
                primary['slots']['basis_refs']=['bad-satisfaction'];primary['slots']['disposition']='verifies'
            elif name=='R-05':primary['slots']['disposition']='verifies'
            elif name=='R-06':
                ctx['referents'].append({'ref':'cap','concept_id':'Z:boundary:capability','home':'Z','layers':['α'],'provenance_status':'declared_unverified','scope_ref':ctx['scope_ref']})
                primary['slots']['source_ref']='cap'
            elif name=='R-07':
                ctx['referents'].append({'ref':'role','concept_id':'Y:identity-anchor:role-binding','home':'Y','layers':['α'],'provenance_status':'declared_unverified','scope_ref':ctx['scope_ref']})
                primary['slots']['source_ref']='role'
            elif name=='R-08':primary['slots']['decision']='admitted';primary['slots'].pop('refusal_ref')
            elif name=='R-10':primary['slots'].pop('action_ref')
            elif name=='R-11':primary['layers']=['ζ'];primary['slots'].clear()
            concept=case['concept']
            r=run(ctx,concept,layer='ζ' if name=='R-11' else 'α',relation=source)
            with self.subTest(id=name):
                self.assertEqual(r['overall_status'],case['expected_overall'],(name,r))
                for code in case['required_codes']:
                    self.assertIn(code,[x['code'] for x in r['diagnostics']],(name,r))
                for k in ('current_authority','canonical_admission','epistemic_warrant'):
                    self.assertEqual(r[k],'NOT_EVALUATED')

if __name__=='__main__':unittest.main()
