#!/usr/bin/env python3
"""P1.15 TASK-076: materialize SN-01..SN-14 from one synthetic base context (spec §5).

Expected values come only from oracles/independent_sn01_sn14.json, committed before any P1.15 runtime code.
Profiles copy the slot descriptors of reference v2 unchanged (no widening).
"""
import copy, hashlib, json
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
ORACLE = json.loads((HERE / 'oracles/independent_sn01_sn14.json').read_text('utf-8'))
V2 = {e['concept_id']: e for e in json.loads((HERE / 'instantiation_reference_v2.json').read_text('utf-8'))['endpoints']}
S = 'ctx:sheet'
REL = 'rel("gated-by",Z:α:Core["mod.core"],X:α:Admission["adm"])'


def ref(r, c, scope=S, **kw):
    return {'ref': r, 'concept_id': c, 'home': c[0], 'layers': ['α'], 'provenance_status': 'declared_unverified', 'scope_ref': scope, **kw}


def prof(c, scope):
    name = c.split(':')[-1]
    return {'profile_ref': f'sn:{name}@{scope}', 'concept_id': c, 'revision': 'sn/1', 'scope': scope,
            'origin': 'illustrative_fixture', 'slots': copy.deepcopy(V2[c]['slots'])}


def base():
    pol, org, ev = 'x:policy/project', 'x:policy/org', 'x:event/call'
    refs = [
        ref('mod.core', 'Z:module-body:core'), ref('act:holder', 'Y:identity-anchor:actor'),
        ref('act:caller', 'Y:identity-anchor:actor'), ref('pr:person', 'Y:identity-anchor:principal'),
        ref('gr:key', 'Z:boundary:grant'), ref('ref:no', 'Z:boundary:refusal'),
        ref('res:store', 'Y:resource-object:resource'), ref('rev:v1', 'Y:resource-object:revision'),
        ref('res:foreign', 'Y:resource-object:resource', pol),
        ref(org, 'X:scope:policy', org), ref(pol, 'X:scope:policy', pol), ref(ev, 'X:scope:event', ev),
        ref('act-call', 'X:endpoint:action', ev, instantiation_profile_ref=f'sn:action@{ev}',
            slots={'pair_scope_ref': ev, 'performed_by_ref': 'act:caller', 'executed_as_ref': 'pr:person'}),
        ref('auth', 'X:endpoint:authority', pol, instantiation_profile_ref=f'sn:authority@{pol}',
            slots={'pair_scope_ref': pol, 'holder_ref': 'act:holder', 'source_ref': 'gr:key', 'action_kind': 'resolve',
                   'resource_scope_ref': 'res:store'}),
        ref('adm', 'X:endpoint:admission', pol, instantiation_profile_ref=f'sn:admission@{pol}',
            slots={'pair_scope_ref': pol, 'request_ref': 'act-call', 'principal_ref': 'pr:person', 'decision': 'admitted',
                   'authority_ref': 'auth'}),
    ]
    pred = {'predicate_id': 'gated-by', 'revision': 'sn:pred/1', 'scope': S, 'origin': 'illustrative_fixture',
            'subject_concept_ids': ['Z:module-body:core'], 'object_concept_ids': ['X:endpoint:admission'],
            'direction': 'subject_to_object', 'required_qualifiers': [], 'additional_constraints': []}
    return {'format': 'aiaeao.cube.binding-context/11', 'reference_version': 'v9.4', 'context_id': 'p115-sn',
            'source_kind': 'illustrative_fixture', 'scope_ref': S, 'referents': refs, 'predicate_contracts': [pred],
            'instantiation_profiles': [prof('X:endpoint:admission', pol), prof('X:endpoint:authority', pol),
                                       prof('X:endpoint:action', ev)]}


def R(ctx, r):
    return next(x for x in ctx['referents'] if x['ref'] == r)


def nested(ctx):
    ctx['scope_nesting'] = [{'inner': 'x:policy/project', 'outer': S}]
    return ctx


def outcomes(ctx):
    ctx['referents'].append(ref('adm-no', 'X:endpoint:admission', 'x:policy/project', instantiation_profile_ref='sn:admission@x:policy/project',
                                slots={'pair_scope_ref': 'x:policy/project', 'request_ref': 'act-call', 'principal_ref': 'pr:person',
                                       'decision': 'refused', 'refusal_ref': 'ref:no'}))
    for r in ('g:decide', 'f:in', 'f:yes', 'f:no'):
        ctx['referents'].append(ref(r, 'Y:identified-object:work-item'))
    ctx['control_flow'] = {'gateways': [{'gateway': 'g:decide', 'type': 'exclusive', 'incoming': ['f:in'],
                                         'outgoing': [{'flow': 'f:yes', 'target': 'adm', 'order': 1},
                                                      {'flow': 'f:no', 'target': 'adm-no', 'default': True}]}]}
    return ctx


def case(id):
    ctx, text = base(), REL
    if id == 'SN-02': nested(ctx)
    elif id == 'SN-03': ctx['scope_nesting'] = [{'inner': 'x:policy/project', 'outer': 'x:policy/org'}, {'inner': 'x:policy/org', 'outer': S}]
    elif id == 'SN-04': ctx['scope_nesting'] = [{'inner': 'x:policy/project', 'outer': 'x:elsewhere'}]
    elif id == 'SN-05': ctx['scope_nesting'] = [{'inner': 'x:policy/project', 'outer': 'x:policy/org'}, {'inner': 'x:policy/org', 'outer': 'x:policy/project'}]
    elif id == 'SN-06': ctx['scope_nesting'] = [{'inner': 'mod.core', 'outer': S}]
    elif id == 'SN-07': nested(ctx); R(ctx, 'adm')['slots'].pop('principal_ref')
    elif id == 'SN-08': nested(ctx); R(ctx, 'adm')['slots'].pop('authority_ref')
    elif id == 'SN-09': nested(ctx); R(ctx, 'auth')['slots']['resource_scope_ref'] = 'rev:v1'
    elif id == 'SN-10': outcomes(nested(ctx))
    elif id == 'SN-11':
        outcomes(nested(ctx)); ctx['referents'].append(ref('act-other', 'X:endpoint:action', 'x:event/call', instantiation_profile_ref='sn:action@x:event/call',
                                                         slots={'pair_scope_ref': 'x:event/call', 'performed_by_ref': 'act:caller'}))
        R(ctx, 'adm-no')['slots']['request_ref'] = 'act-other'
    elif id == 'SN-12':
        outcomes(nested(ctx)); s = R(ctx, 'adm-no')['slots']; s['decision'] = 'admitted'; s.pop('refusal_ref'); s['authority_ref'] = 'auth'
    elif id == 'SN-13': outcomes(nested(ctx)); R(ctx, 'adm-no')['slots'].pop('refusal_ref')
    elif id == 'SN-14':
        nested(ctx); ctx['predicate_contracts'][0]['object_concept_ids'].append('Y:resource-object:resource')
        text = 'rel("gated-by",Z:α:Core["mod.core"],Y:α:Resource["res:foreign"])'
    return ctx, text


cases = []
for o in ORACLE['cases']:
    ctx, text = case(o['id'])
    cases.append({'id': o['id'], 'case': o['case'], 'input_text': text, 'input_format': 'acg_text', 'context': ctx,
                  'expected_overall': o['expected_overall'], 'required_codes': o['required_codes'], 'forbidden_codes': o['forbidden_codes']})
out = {'format': 'aiaeao.cube.p1.15-vectors/1', 'reference_version': 'v9.4',
       'oracle_sha256': hashlib.sha256((HERE / 'oracles/independent_sn01_sn14.json').read_bytes()).hexdigest(), 'cases': cases}
(HERE / 'fixtures/sn01_sn14_materialized.json').write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n', 'utf-8')
print(len(cases), 'cases')
