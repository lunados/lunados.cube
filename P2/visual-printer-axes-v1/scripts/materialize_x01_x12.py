#!/usr/bin/env python3
"""VP-09.3 TASK-078: materialize X-01…X-12 (spec §2a) from one synthetic binding-context/10.

Expected values come only from oracles/independent_x01_x12.json, committed before any 0.9.3 runtime code.
"""
import copy, hashlib, json
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
ORACLE = json.loads((HERE/'oracles/independent_x01_x12.json').read_text('utf-8'))
S = 'ctx:xy'
REF = lambda r, c, scope=S, **kw: {'ref': r, 'concept_id': c, 'home': c[0], 'layers': ['α'], 'provenance_status': 'declared_unverified', 'scope_ref': scope, **kw}  # noqa: E731
SLOTS = {
 'X:endpoint:action': [('pair_scope_ref', 'ref', True, ['X:scope:event']), ('performed_by_ref', 'ref', True, ['Y:identity-anchor:actor']),
                       ('executed_as_ref', 'ref', False, ['Y:identity-anchor:principal'])],
 'X:endpoint:authority': [('pair_scope_ref', 'ref', True, ['X:scope:policy']), ('holder_ref', 'ref', True, ['Y:identity-anchor:actor']),
                          ('source_ref', 'ref', True, ['Z:boundary:grant']), ('action_kind', 'string', True, None),
                          ('resource_scope_ref', 'ref', True, ['Y:resource-object:resource', 'Z:boundary:project-boundary', 'Z:boundary:thread-boundary'])],
 'X:endpoint:admission': [('pair_scope_ref', 'ref', True, ['X:scope:policy']), ('request_ref', 'ref', True, ['X:endpoint:action']),
                          ('principal_ref', 'ref', True, ['Y:identity-anchor:principal']), ('decision', 'enum', True, ['admitted', 'refused']),
                          ('authority_ref', 'ref', False, ['X:endpoint:authority']), ('refusal_ref', 'ref', False, ['Z:boundary:refusal'])],
}


def prof(c, scope):
    slots = []
    for n, k, req, ids in SLOTS[c]:
        d = {'name': n, 'kind': k, 'required': req}
        if k == 'ref':
            d.update(cardinality='one', concept_ids=ids)
        elif k == 'enum':
            d['values'] = ids
        slots.append(d)
    return {'profile_ref': f"xy:{c.split(':')[2]}", 'concept_id': c, 'revision': 'xy/1', 'scope': scope, 'origin': 'illustrative_fixture', 'slots': slots}


def pred(pid, subj, obj):
    return {'predicate_id': pid, 'revision': 'xy:pred/1', 'scope': S, 'origin': 'illustrative_fixture', 'subject_concept_ids': subj,
            'object_concept_ids': obj, 'direction': 'subject_to_object', 'required_qualifiers': [], 'additional_constraints': []}


def base():
    refs = [REF('mod.core', 'Z:module-body:core'), REF('act:caller', 'Y:identity-anchor:actor'), REF('act:holder', 'Y:identity-anchor:actor'),
            REF('pr:person', 'Y:identity-anchor:principal'), REF('res:store', 'Y:resource-object:resource'),
            REF('rev:v1', 'Y:resource-object:revision'), REF('gr:key', 'Z:boundary:grant'), REF('ref:no', 'Z:boundary:refusal'),
            REF('x:policy', 'X:scope:policy', 'x:policy'), REF('x:event', 'X:scope:event', 'x:event'),
            REF('act-call', 'X:endpoint:action', 'x:event', instantiation_profile_ref='xy:action',
                slots={'pair_scope_ref': 'x:event', 'performed_by_ref': 'act:caller', 'executed_as_ref': 'pr:person'}),
            REF('auth', 'X:endpoint:authority', 'x:policy', instantiation_profile_ref='xy:authority',
                slots={'pair_scope_ref': 'x:policy', 'holder_ref': 'act:holder', 'source_ref': 'gr:key', 'action_kind': 'resolve',
                       'resource_scope_ref': 'res:store'}),
            REF('adm', 'X:endpoint:admission', 'x:policy', instantiation_profile_ref='xy:admission',
                slots={'pair_scope_ref': 'x:policy', 'request_ref': 'act-call', 'principal_ref': 'pr:person', 'decision': 'admitted',
                       'authority_ref': 'auth'})]
    deps = [('d1', 'mod.core', 'gated-by', 'adm'), ('d2', 'mod.core', 'reads', 'res:store'), ('d3', 'act:caller', 'invoked-by', 'mod.core')]
    plan = {'plan_id': 'pm-xy', 'revision': 'xy/1', 'scope': S, 'origin': 'illustrative_fixture',
            'phases': [{'phase_id': 'current', 'role': 'current'}, {'phase_id': 'beta', 'role': 'target'}], 'transitions': [],
            'dependencies': [{'dependency_id': i, 'subject': a, 'predicate_id': p, 'object': o, 'kind': 'other', 'holds_in': ['current', 'beta']}
                             for i, a, p, o in deps]}
    return {'format': 'aiaeao.cube.binding-context/10', 'reference_version': 'v9.4', 'context_id': 'vp093-xy', 'source_kind': 'illustrative_fixture',
            'scope_ref': S, 'referents': refs,
            'predicate_contracts': [pred('gated-by', ['Z:module-body:core'], ['X:endpoint:admission']),
                                    pred('reads', ['Z:module-body:core'], ['Y:resource-object:resource']),
                                    pred('invoked-by', ['Y:identity-anchor:actor'], ['Z:module-body:core'])],
            'predicate_profile_refs': [], 'method_profile_refs': ['P1.11/migration-methods-v1'],
            'instantiation_profiles': [prof('X:endpoint:action', 'x:event'), prof('X:endpoint:authority', 'x:policy'), prof('X:endpoint:admission', 'x:policy')],
            'migration_plans': [plan]}


def R(ctx, r):
    return next(x for x in ctx['referents'] if x['ref'] == r)


def case(o):
    ctx, profile = base(), 'P2-VP-AXES/0.9.3'
    i = o['id']
    if i == 'X-04': R(ctx, 'adm')['slots'].pop('principal_ref')
    if i == 'X-05': R(ctx, 'auth')['slots'].pop('source_ref')
    if i == 'X-06': ctx['referents'].append(REF('adm-other', 'X:endpoint:admission', 'x:policy', instantiation_profile_ref='xy:admission',
                                                slots={'pair_scope_ref': 'x:policy', 'request_ref': 'act-call', 'principal_ref': 'pr:person',
                                                       'decision': 'refused', 'refusal_ref': 'ref:no'}))
    if i == 'X-07': ctx['migration_plans'][0]['dependencies'] = [d for d in ctx['migration_plans'][0]['dependencies'] if d['dependency_id'] != 'd1']
    if i == 'X-10': ctx.pop('instantiation_profiles'); [R(ctx, r).pop('instantiation_profile_ref') for r in ('adm', 'auth', 'act-call')]
    out = {'id': i, 'context': ctx, 'plan_id': 'pm-xy', 'profile': profile, 'rows': o['rows'], 'cols': o['cols'],
           'locale': o.get('locale'), 'granularity': ORACLE['granularity']}
    if i == 'X-08':  # an axes input labelled 0.9.2 (0.9.3 keys removed) asks for X × Y
        out['input_profile'] = 'P2-VP-AXES/0.9.2'
    return out


out = {'format': 'aiaeao.cube.vp093-vectors/1', 'oracle_sha256': hashlib.sha256((HERE/'oracles/independent_x01_x12.json').read_bytes()).hexdigest(),
       'cases': [case(o) for o in ORACLE['cases']]}
(HERE/'fixtures/x01_x12_materialized.json').write_text(json.dumps(out, ensure_ascii=False, indent=1)+'\n', 'utf-8')
print(len(out['cases']), 'cases')
