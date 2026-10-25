#!/usr/bin/env python3
"""Materialise S-01..S-17 from P1_8_ACCEPTANCE_SPEC.md §5 into explicit vectors.

Expected values are NOT computed here: they are copied from the independent
oracle (oracles/independent_s01_s17.json), which was transcribed before code.
"""
import copy, hashlib, json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parents[1]
ORACLE = json.loads((HERE/'oracles/independent_s01_s17.json').read_text('utf-8'))
R = json.loads((REPO/'P3/charge3-p16/fixtures/r01_r13_materialized.json').read_text('utf-8'))
R10 = next(c for c in R['cases'] if c['id'] == 'R-10')['context']
P16_PROFILES = copy.deepcopy(R10['instantiation_profiles'])   # X Result + X Action, scope "scope-event"

A = 'α'
def ref(r, cid, home, scope='sim', **kw):
    return {'ref': r, 'concept_id': cid, 'home': home, 'layers': [A],
            'provenance_status': 'declared_unverified', 'scope_ref': scope, **kw}

METHOD = 'verify.qualified-reuse/v1'
DIGEST = 'sha256:' + hashlib.sha256(b'EXP-010 central profile seeds 8-11').hexdigest()
REL_APP = f'rel("supports",{METHOD}(Y:{A}:Artifact["a1"]),Y:{A}:Annotation["claim1"])'

def base():
    return {
        'format': 'aiaeao.cube.binding-context/3', 'reference_version': 'v9.4',
        'context_id': 'p18-sim', 'source_kind': 'illustrative_fixture', 'scope_ref': 'sim',
        'referents': [ref('a1','Y:resource-object:artifact','Y'),
                      ref('ev-out','Y:resource-object:evidence','Y'),
                      ref('claim1','Y:identified-object:annotation','Y')],
        'predicate_contracts': [{'predicate_id':'supports','revision':'p18:v1','scope':'sim','origin':'illustrative_fixture',
                                 'subject_concept_ids':['Y:resource-object:evidence'],
                                 'object_concept_ids':['Y:identified-object:annotation'],'direction':'subject_to_object'}],
        'method_contracts': [{'method_id':METHOD,'revision':'lib:v1','scope':'sim','origin':'illustrative_fixture',
                              'argument_min':1,'argument_max':1,'argument_concept_ids':['Y:resource-object:artifact'],
                              'effect_class':'pure_declarative',
                              'return_concept_ids':['Y:resource-object:evidence'],'return_cardinality':'one',
                              'library_ref':{'library_id':'aiaeao.functions','entry_id':'verify.qualified_reuse',
                                             'revision':'v1','sha256':hashlib.sha256(b'library entry placeholder').hexdigest()}}],
    }

def framed(c):
    c['evaluation_frame'] = {'scenario_ref':'sc-010-central'}
    c['scenarios'] = [{'scenario_id':'sc-010-central','revision':'exp010:v1','scope':'sim','origin':'illustrative_fixture',
                       'mode':'simulation','world_refs':['a1','ev-out','claim1'],
                       'parameters':{'cost_profile':'central','seed':8},
                       'assumption_refs':['claim1'],'method_ids':[METHOD]}]
    return c

def recorded(c):
    c['evaluators'] = [{'evaluator_id':'eval:exp010-python','revision':'v1','scope':'sim','origin':'illustrative_fixture',
                        'kind':'local_script','method_ids':[METHOD],
                        'output_concept_ids':['Y:resource-object:evidence','Y:resource-object:artifact']}]
    c['evaluation_records'] = [{'record_id':'run-1','scenario_ref':'sc-010-central','evaluator_ref':'eval:exp010-python',
                                'method_id':METHOD,'input_digest':DIGEST,'output_refs':['ev-out'],
                                'witness_ref':'witness:exp010/RESULTS.json','status':'declared'}]
    return c

def with_result(c, action_ref=True):
    c['instantiation_profiles'] = copy.deepcopy(P16_PROFILES)
    res_slots = {'pair_scope_ref':'scope-event'}
    if action_ref: res_slots['action_ref'] = 'run-1-action'
    c['referents'] += [
        ref('scope-event','X:scope:event','X',scope='scope-event'),
        ref('eval-actor','Y:identity-anchor:actor','Y',scope='scope-event'),
        ref('run-1-action','X:endpoint:action','X',scope='scope-event',
            instantiation_profile_ref='p16-X:endpoint:action',
            slots={'pair_scope_ref':'scope-event','performed_by_ref':'eval-actor'}),
        ref('res-out','X:endpoint:result','X',scope='scope-event',
            instantiation_profile_ref='p16-X:endpoint:result', slots=res_slots)]
    c['scenarios'][0]['world_refs'] += ['scope-event','eval-actor','run-1-action','res-out']
    c['evaluators'][0]['output_concept_ids'].append('X:endpoint:result')
    c['evaluation_records'][0]['output_refs'] = ['res-out']
    return c

def build():
    v = {}
    v['S-01'] = (REL_APP, base())
    c = base(); del c['method_contracts'][0]['return_concept_ids']; del c['method_contracts'][0]['return_cardinality']
    v['S-02'] = (REL_APP, c)
    c = base(); c['method_contracts'][0]['return_concept_ids'] = ['Y:identified-object:annotation']
    v['S-03'] = (REL_APP, c)
    v['S-04'] = (f'rel("supports",rel("supports",Y:{A}:Evidence["ev-out"],Y:{A}:Annotation["claim1"]),Y:{A}:Annotation["claim1"])', base())
    v['S-05'] = (REL_APP, framed(base()))
    c = framed(base()); c['scenarios'][0]['world_refs'] = ['ev-out','claim1']
    v['S-06'] = (REL_APP, c)
    c = framed(base()); c['method_contracts'][0]['effect_class'] = 'effectful_declared'
    v['S-07'] = (REL_APP, c)
    c = framed(base()); c['scenarios'][0]['mode'] = 'operative'
    v['S-08'] = (REL_APP, c)
    v['S-09'] = (REL_APP, recorded(framed(base())))
    c = recorded(framed(base())); del c['evaluation_records'][0]['witness_ref']
    v['S-10'] = (REL_APP, c)
    c = recorded(framed(base())); c['evaluators'][0]['method_ids'] = ['other.method/v1']
    v['S-11'] = (REL_APP, c)
    c = recorded(framed(base())); c['referents'].append(ref('concl-out','X:endpoint:conclusion','X'))
    c['scenarios'][0]['world_refs'].append('concl-out'); c['evaluation_records'][0]['output_refs'] = ['concl-out']
    v['S-12'] = (REL_APP, c)
    c = recorded(framed(base())); c['evaluation_records'][0]['input_digest'] = 'md5:0123456789abcdef0123456789abcdef'
    v['S-13'] = (REL_APP, c)
    c = framed(base()); c['format'] = 'aiaeao.cube.binding-context/2'
    v['S-14'] = (REL_APP, c)
    c = framed(base()); c['evaluation_frame']['scenario_ref'] = 'sc-missing'
    v['S-15'] = (REL_APP, c)
    v['S-16'] = (REL_APP, with_result(recorded(framed(base()))))
    v['S-17'] = (REL_APP, with_result(recorded(framed(base())), action_ref=False))
    return v

def main():
    vecs = build(); exp = {c['id']: c for c in ORACLE['cases']}
    assert set(vecs) == set(exp), 'oracle/vector id mismatch'
    cases = []
    for k in sorted(vecs):
        text, ctx = vecs[k]
        cases.append({'id':k,'input_text':text,'input_format':'acg_text','context':ctx,
                      'expected_overall':exp[k]['expected_overall'],'required_codes':exp[k]['required_codes']})
    out = {'format':'aiaeao.cube.p1.8-vectors/1','reference_version':'v9.4',
           'source':'P1_8_ACCEPTANCE_SPEC.md §5 + oracles/independent_s01_s17.json','cases':cases}
    (HERE/'fixtures/s01_s17_materialized.json').write_text(json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)+'\n','utf-8')
    print('wrote', len(cases), 'vectors')

if __name__ == '__main__': main()
