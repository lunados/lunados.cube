#!/usr/bin/env python3
"""Materialise M-01..M-22 from P1_10_ACCEPTANCE_SPEC.md §5 into explicit vectors.

Expected values are NOT computed here: they are copied from the independent
oracle (oracles/independent_m01_m22.json), which was transcribed before code.
All names are synthetic (D-7).
"""
import copy, json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ORACLE = json.loads((HERE/'oracles/independent_m01_m22.json').read_text('utf-8'))

A = 'α'
SCOPE = 'mig'
PROFILE = 'P1.10/migration-predicates-v1'
INT, RES = 'Z:module-body:integration', 'Y:resource-object:resource'
PRV, DEP = 'Z:module-body:provider', 'Z:module-body:third-party-dependency'
HOME = {INT: 'Z', RES: 'Y', PRV: 'Z', DEP: 'Z'}

def ref(r, cid):
    return {'ref': r, 'concept_id': cid, 'home': HOME[cid], 'layers': [A],
            'provenance_status': 'declared_unverified', 'scope_ref': SCOPE}

TEXT = f'rel("depends-on",Z:{A}:Integration["job"],Z:{A}:ThirdPartyDependency["old"])'
T_TEXT = '@T(role="scheduling",witness_ref="witness:mig/cutover")'
SUP = f'rel("supersedes",Z:{A}:Provider["new"],Z:{A}:ThirdPartyDependency["old"]) {T_TEXT}'
SUP_REV = f'rel("supersedes",Z:{A}:ThirdPartyDependency["old"],Z:{A}:Provider["new"]) {T_TEXT}'
QPROF = {'format': 'aiaeao.cube.qualifier-profiles/1', 'reference_version': 'v9.4',
         'profile_id': 'mig:qualifiers', 'scope': SCOPE, 'origin': 'illustrative_fixture',
         'witness_refs': ['witness:mig/cutover'],
         'qualifiers': [{'profile_ref': 'mig:T-scheduling/v1', 'coordinate': 'T',
                         'required_parameters': ['role', 'witness_ref'], 'allowed_parameters': ['role', 'witness_ref'],
                         'allowed_values': {'role': ['scheduling']}, 'requires_witness': True}]}

def dep(did, subj, pred, obj, holds, **kw):
    d = {'dependency_id': did, 'subject': subj, 'predicate_id': pred, 'object': obj,
         'kind': 'job', 'holds_in': holds, 'witness_ref': f'witness:mig/{did}'}
    d.update(kw); return d

def base():
    """M-01: p0 current, p1 intermediate, p2 target; t1 at p1 retires old, introduces new;
    d1 (job -> old, p0) with successor d2 (job -> new, p1, p2)."""
    return {
        'format': 'aiaeao.cube.binding-context/5', 'reference_version': 'v9.4',
        'context_id': 'p110-mig', 'source_kind': 'illustrative_fixture', 'scope_ref': SCOPE,
        'predicate_profile_refs': [PROFILE],
        'referents': [ref('job', INT), ref('old', DEP), ref('new', PRV)],
        'predicate_contracts': [],
        'migration_plans': [{
            'plan_id': 'mp-1', 'revision': 'v1', 'scope': SCOPE, 'origin': 'illustrative_fixture',
            'phases': [{'phase_id': 'p0', 'role': 'current'}, {'phase_id': 'p1', 'role': 'intermediate'},
                       {'phase_id': 'p2', 'role': 'target'}],
            'transitions': [{'transition_id': 't1', 'at_phase': 'p1', 'retires': ['old'], 'introduces': ['new'],
                             'T': {'role': 'scheduling', 'value': 'TBD'}, 'witness_ref': 'witness:mig/t1'}],
            'dependencies': [dep('d1', 'job', 'depends-on', 'old', ['p0'], successor_ref='d2'),
                             dep('d2', 'job', 'depends-on', 'new', ['p1', 'p2'])]}],
    }

def plan(c): return c['migration_plans'][0]
def deps(c): return {d['dependency_id']: d for d in plan(c)['dependencies']}

def build():
    v = {}
    v['M-01'] = base()
    c = base(); c['predicate_profile_refs'] = ['P1.10/unknown-predicates-v1']; v['M-02'] = c
    c = base(); c['predicate_contracts'] = [{'predicate_id': 'depends-on', 'revision': 'local:v1', 'scope': SCOPE,
        'origin': 'illustrative_fixture', 'subject_concept_ids': [INT], 'object_concept_ids': [DEP],
        'direction': 'subject_to_object'}]; v['M-03'] = c
    c = base(); plan(c)['phases'][2]['role'] = 'intermediate'; v['M-04'] = c
    c = base(); plan(c)['phases'][1]['role'] = 'target'; plan(c)['phases'][2]['role'] = 'intermediate'; v['M-05'] = c
    c = base(); plan(c)['transitions'][0]['at_phase'] = 'p9'; v['M-06'] = c
    c = base(); plan(c)['transitions'].append({'transition_id': 't2', 'at_phase': 'p2', 'retires': ['old'], 'introduces': [],
        'T': {'role': 'scheduling', 'value': 'TBD'}, 'witness_ref': 'witness:mig/t2'}); v['M-07'] = c
    c = base(); del plan(c)['transitions'][0]['T']; v['M-08'] = c
    c = base(); deps(c)['d1']['holds_in'] = ['p0', 'p1']; v['M-09'] = c
    c = base(); del deps(c)['d1']['successor_ref']; v['M-10'] = c
    c = copy.deepcopy(v['M-10']); deps(c)['d1']['dropped'] = True; v['M-11'] = c
    c = base(); c['referents'].append(ref('interim', PRV))
    plan(c)['transitions'].append({'transition_id': 't2', 'at_phase': 'p2', 'retires': ['interim'], 'introduces': [],
        'T': {'role': 'scheduling', 'value': 'TBD'}, 'witness_ref': 'witness:mig/t2'})
    deps(c)['d2']['object'] = 'interim'; v['M-12'] = c
    c = base(); deps(c)['d2']['holds_in'] = ['p0', 'p1', 'p2']; v['M-13'] = c
    c = base(); c['referents'][0] = ref('job', RES)
    for d in plan(c)['dependencies']: d['predicate_id'] = 'sends-via'
    v['M-14'] = c
    c = base(); del deps(c)['d1']['witness_ref']; v['M-15'] = c
    c = base(); c['referents'].append(ref('stable', RES))
    plan(c)['dependencies'].append(dep('d9', 'job', 'depends-on', 'stable', ['p0', 'p2'])); v['M-16'] = c
    c = base(); c['referents'].append(ref('mailbox', RES))
    plan(c)['dependencies'].append(dep('d3', 'mailbox', 'recovers-via', 'old', ['p0', 'p1'], kind='account')); v['M-17'] = c
    v['M-18'] = base()
    v['M-19'] = base()
    c = base(); c['format'] = 'aiaeao.cube.binding-context/4'; del c['predicate_profile_refs']
    c['predicate_contracts'] = [{'predicate_id': 'depends-on', 'revision': 'local:v1', 'scope': SCOPE,
        'origin': 'illustrative_fixture', 'subject_concept_ids': [INT], 'object_concept_ids': [DEP, PRV],
        'direction': 'subject_to_object'}]; v['M-20'] = c
    c = base(); plan(c)['scope'] = 'other-scope'; v['M-21'] = c
    c = base(); plan(c)['transitions'][0]['T']['role'] = 'effective-interval'; v['M-22'] = c
    return v

TEXTS = {'M-18': SUP, 'M-19': SUP_REV}

def main():
    vecs = build(); exp = {c['id']: c for c in ORACLE['cases']}
    assert set(vecs) == set(exp), 'oracle/vector id mismatch'
    cases = []
    for k in sorted(vecs):
        case = {'id': k, 'input_text': TEXTS.get(k, TEXT), 'input_format': 'acg_text', 'context': vecs[k],
                'expected_overall': exp[k]['expected_overall'], 'required_codes': exp[k]['required_codes']}
        if k in TEXTS: case['qualification_profiles'] = QPROF
        cases.append(case)
    out = {'format': 'aiaeao.cube.p1.10-vectors/1', 'reference_version': 'v9.4',
           'source': 'P1_10_ACCEPTANCE_SPEC.md §5 + oracles/independent_m01_m22.json', 'cases': cases}
    (HERE/'fixtures/m01_m22_materialized.json').write_text(json.dumps(out, ensure_ascii=False, sort_keys=True, indent=2)+'\n', 'utf-8')
    print('wrote', len(cases), 'vectors')

if __name__ == '__main__': main()
