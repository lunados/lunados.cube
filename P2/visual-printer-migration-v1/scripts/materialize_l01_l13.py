#!/usr/bin/env python3
"""Materialise L-01..L-13 from VP07_2_ACCEPTANCE_SPEC.md §5 into explicit vectors.

Expected values are copied from oracles/independent_l01_l13.json (transcribed before code).
All names are synthetic. The dependency inventory is deliberately listed against the layer
order (actor first, platform last) so that layer ordering is observable.
"""
import copy, json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ORACLE = json.loads((HERE/'oracles/independent_l01_l13.json').read_text('utf-8'))
INT, RES, ACT = 'Z:module-body:integration', 'Y:resource-object:resource', 'Y:identity-anchor:actor'
PRV, DEP = 'Z:module-body:provider', 'Z:module-body:third-party-dependency'
HOME = {INT: 'Z', RES: 'Y', ACT: 'Y', PRV: 'Z', DEP: 'Z'}
SCOPE = 'acme:migration'


def ref(r, cid):
    return {'ref': r, 'concept_id': cid, 'home': HOME[cid], 'layers': ['α'], 'provenance_status': 'declared_unverified', 'scope_ref': SCOPE}


def dep(i, s, pred, o, holds, **kw):
    d = {'dependency_id': i, 'subject': s, 'predicate_id': pred, 'object': o, 'kind': 'job', 'holds_in': holds,
         'witness_ref': f'repo:example/{i}'}
    d.update(kw)
    return d


ALL = ['p0', 'p1', 'p2', 'p3']
CTX = {'format': 'aiaeao.cube.binding-context/6', 'reference_version': 'v9.4', 'context_id': 'fixture-vp072', 'source_kind': 'illustrative_fixture',
       'scope_ref': SCOPE, 'predicate_profile_refs': ['P1.10/migration-predicates-v1'],
       'referents': [ref('support', ACT), ref('crm-sync', INT), ref('shop', INT), ref('admin-mailbox', RES), ref('legacy-mail', DEP),
                     ref('new-mail', PRV), ref('dns-zone', DEP), ref('hosting', DEP)],
       'predicate_contracts': [],
       'migration_plans': [{'plan_id': 'mp-layers', 'revision': 'synthetic:v1', 'scope': SCOPE, 'origin': 'illustrative_fixture',
                            'phases': [{'phase_id': 'p0', 'role': 'current'}, {'phase_id': 'p1', 'role': 'intermediate'},
                                       {'phase_id': 'p2', 'role': 'intermediate'}, {'phase_id': 'p3', 'role': 'target'}],
                            'transitions': [{'transition_id': 't-mail', 'at_phase': 'p2', 'retires': ['legacy-mail'], 'introduces': ['new-mail'],
                                             'T': {'role': 'scheduling', 'value': 'TBD'}, 'witness_ref': 'synthetic:contract#scope'}],
                            'dependencies': [dep('d5', 'support', 'depends-on', 'admin-mailbox', ALL),
                                             dep('d4', 'crm-sync', 'depends-on', 'admin-mailbox', ALL),
                                             dep('d2', 'shop', 'sends-via', 'legacy-mail', ['p0', 'p1'], successor_ref='d3'),
                                             dep('d3', 'shop', 'sends-via', 'new-mail', ['p2', 'p3']),
                                             dep('d6', 'shop', 'depends-on', 'dns-zone', ALL),
                                             dep('d1', 'shop', 'depends-on', 'hosting', ALL)]}]}
ORDER = ['platform', 'dns', 'provider', 'account', 'system', 'actor']


def layer_map(**override):
    layers = {'platform': ['hosting'], 'dns': ['dns-zone'], 'provider': ['legacy-mail', 'new-mail'], 'account': ['admin-mailbox'],
              'system': ['shop', 'crm-sync'], 'actor': ['support']}
    layers.update(override)
    return {'format': 'aiaeao.cube.vp07-layer-map/1', 'layer_order': list(ORDER), 'layers': layers}


TRACKS = {'format': 'aiaeao.cube.vp07-track-map/1', 'tracks': {'mail': ['shop', 'support'], 'ops': ['crm-sync']}}


def fp(layers, then=None, tracks=None, **kw):
    d = {'context': copy.deepcopy(CTX), 'plan_id': 'mp-layers', 'layers': layers}
    if tracks:
        d['tracks'] = tracks
    if then:
        d['then'] = then
    d.update(kw)
    return d


PHASES = {'view': 'cube.phases', 'partition': 'subject', 'granularity': 'standard'}


def build():
    v = {}
    v['L-01'] = ('from-plan', fp(layer_map()))
    m = layer_map(); m['layers']['dns'] = ['dns-zone', 'hosting']
    v['L-02'] = ('from-plan', fp(m))
    m = layer_map(); m['layers']['cloud'] = []
    v['L-03'] = ('from-plan', fp(m))
    m = layer_map(); m['layers']['actor'] = ['support', 'ghost']
    v['L-04'] = ('from-plan', fp(m))
    m = layer_map(); m['layers']['actor'] = []
    v['L-05'] = ('from-plan', fp(m, PHASES))
    v['L-06'] = ('from-plan', fp(layer_map(), PHASES))
    v['L-07'] = ('from-plan', fp(layer_map(system=['crm-sync', 'shop']), PHASES))
    v['L-08'] = ('from-plan', fp(None, PHASES))
    v['L-09'] = ('from-plan', fp(layer_map(), {'view': 'cube.flow', 'partition': 'subject', 'granularity': 'standard', 'lens': 'cube.lens.execution'}))
    v['L-10'] = ('from-plan', fp(layer_map(), PHASES))
    v['L-11'] = ('from-plan', fp(layer_map(), {'view': 'cube.phases', 'partition': 'layer', 'granularity': 'standard'}))
    v['L-12'] = ('from-plan', fp(layer_map(), {'view': 'cube.phases', 'partition': 'track,layer', 'granularity': 'standard'}, TRACKS))
    w = {c['id']: c for c in json.loads((HERE/'fixtures/w01_w17_materialized.json').read_text('utf-8'))['cases']}
    v['L-13'] = ('panels', {'source': w['W-01']['input']['source'], 'view': 'cube.phases', 'partition': 'layer', 'granularity': 'standard'})
    return v


def main():
    vecs = build()
    exp = {c['id']: c for c in ORACLE['cases']}
    assert set(vecs) == set(exp), 'oracle/vector id mismatch'
    cases = [{'id': k, 'op': vecs[k][0], 'input': vecs[k][1], 'expected_status': exp[k]['expected_status'],
              'required_codes': exp[k]['required_codes'], 'forbidden_codes': exp[k]['forbidden_codes'], 'expect': exp[k]['expect']}
             for k in sorted(vecs)]
    out = {'format': 'aiaeao.cube.vp07.2-vectors/1', 'reference_version': 'v9.4',
           'source': 'VP07_2_ACCEPTANCE_SPEC.md §5 + oracles/independent_l01_l13.json', 'cases': cases}
    (HERE/'fixtures/l01_l13_materialized.json').write_text(json.dumps(out, ensure_ascii=False, sort_keys=True, indent=1)+'\n', 'utf-8')
    print('wrote', len(cases), 'vectors')


if __name__ == '__main__':
    main()
