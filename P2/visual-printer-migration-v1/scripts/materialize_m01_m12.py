#!/usr/bin/env python3
"""Materialise M-01..M-12 (VP-07.3) from VP07_3_ACCEPTANCE_SPEC.md §5 into explicit vectors.

Expected values are copied from oracles/independent_m01_m12.json (transcribed before code).
All names are synthetic. M-05 builds its 0.7.2 source with the unchanged 0.7.2 code and then
adds method fields by hand (a source that 0.7.2 must refuse).
"""
import copy, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE)); sys.dont_write_bytecode = True
ORACLE = json.loads((HERE/'oracles/independent_m01_m12.json').read_text('utf-8'))
SCOPE, W = 'acme:migration', 'synthetic:contract#scope'
INT, RES, ACT = 'Z:module-body:integration', 'Y:resource-object:resource', 'Y:identity-anchor:actor'
PRV, DEP = 'Z:module-body:provider', 'Z:module-body:third-party-dependency'
HOME = {INT: 'Z', RES: 'Y', ACT: 'Y', PRV: 'Z', DEP: 'Z'}
ALL = ['p0', 'p1', 'p2', 'p3']
PHASES = {'view': 'cube.phases', 'partition': 'subject', 'granularity': 'standard'}


def ref(r, cid):
    return {'ref': r, 'concept_id': cid, 'home': HOME[cid], 'layers': ['α'], 'provenance_status': 'declared_unverified', 'scope_ref': SCOPE}


def dep(i, s, pred, o, holds, **kw):
    d = {'dependency_id': i, 'subject': s, 'predicate_id': pred, 'object': o, 'kind': 'job', 'holds_in': holds, 'witness_ref': f'repo:example/{i}'}
    d.update(kw)
    return d


def tr(i, at, ret, intro):
    return {'transition_id': i, 'at_phase': at, 'retires': ret, 'introduces': intro, 'T': {'role': 'scheduling', 'value': 'TBD'}, 'witness_ref': W}


def b(mid, **args):
    return {'method_id': mid, 'arguments': args}


def context(fmt='/7'):
    deps = [dep('d1', 'shop', 'sends-via', 'legacy-mail', ['p0', 'p1'], successor_ref='d2'),
            dep('d2', 'shop', 'sends-via', 'new-mail', ['p2', 'p3']),
            dep('d3', 'shop', 'depends-on', 'hosting', ALL),
            dep('d4', 'crm-sync', 'depends-on', 'admin-mailbox', ALL),
            dep('d5', 'support', 'depends-on', 'old-store', ['p0', 'p1'], successor_ref='d6'),
            dep('d6', 'support', 'depends-on', 'new-store', ['p2', 'p3']),
            dep('d7', 'crm-sync', 'depends-on', 'mailbox-x', ['p0', 'p1'], dropped=True),
            dep('d8', 'crm-sync', 'sends-via', 'new-mail', ['p2', 'p3'])]
    trs = [tr('t-mail', 'p2', ['legacy-mail'], ['new-mail']), tr('t-store', 'p2', ['old-store'], ['new-store']),
           tr('t-box', 'p2', ['mailbox-x'], [])]
    c = {'format': 'aiaeao.cube.binding-context'+fmt, 'reference_version': 'v9.4', 'context_id': 'vp073-methods',
         'source_kind': 'illustrative_fixture', 'scope_ref': SCOPE, 'predicate_profile_refs': ['P1.10/migration-predicates-v1'],
         'referents': [ref('shop', INT), ref('crm-sync', INT), ref('support', ACT), ref('admin-mailbox', RES), ref('mailbox-x', RES),
                       ref('old-store', RES), ref('new-store', RES), ref('legacy-mail', DEP), ref('new-mail', PRV), ref('hosting', DEP)],
         'predicate_contracts': [],
         'migration_plans': [{'plan_id': 'mp-methods', 'revision': 'v1', 'scope': SCOPE, 'origin': 'illustrative_fixture',
                              'phases': [{'phase_id': 'p0', 'role': 'current'}, {'phase_id': 'p1', 'role': 'intermediate'},
                                         {'phase_id': 'p2', 'role': 'intermediate'}, {'phase_id': 'p3', 'role': 'target'}],
                              'transitions': trs, 'dependencies': deps}]}
    if fmt == '/7':
        c['method_profile_refs'] = ['P1.11/migration-methods-v1']
        trs[0]['methods'] = [b('migrate.retire/v1', retired='legacy-mail'), b('migrate.import/v1', source='legacy-mail', target='new-mail')]
        trs[1]['methods'] = [b('migrate.import/v1', source='old-store', target='new-store'), b('migrate.retire/v1', retired='old-store')]
        trs[2]['methods'] = [b('migrate.retire/v1', retired='mailbox-x')]
        deps[0]['method'] = b('migrate.rewrite/v1', dependant='shop', new_object='new-mail')
        deps[4]['method'] = b('migrate.rewrite/v1', dependant='support', new_object='new-store')
    return c


def plan(c):
    return c['migration_plans'][0]


LAYERS = {'format': 'aiaeao.cube.vp07-layer-map/1', 'layer_order': ['provider', 'account', 'system', 'actor'],
          'layers': {'provider': ['hosting', 'legacy-mail', 'new-mail'], 'account': ['admin-mailbox', 'mailbox-x', 'old-store', 'new-store'],
                     'system': ['shop', 'crm-sync'], 'actor': ['support']}}
TRACKS = {'format': 'aiaeao.cube.vp07-track-map/1', 'tracks': {'mail': ['shop', 'crm-sync'], 'store': ['support']}}
LABELS = {'format': 'aiaeao.cube.vp07-label-map/1',
          'labels': {'legacy-mail': {'id': 'legacy-mail', 'label': 'legacy mail relay of the synthetic shop platform'}}}


def v(op, ctx=None, then=PHASES, **kw):
    d = {'context': ctx or context(), 'plan_id': 'mp-methods'}
    if then:
        d['then'] = dict(then)
    d.update(kw)
    return (op, d)


def m05_source():
    from vpmigration import from_plan                       # unchanged 0.7.2 code (this script runs before any 0.7.3 code)
    src, _ = from_plan(context('/6'), 'mp-methods', layers=LAYERS)
    assert src['profile'] == 'P2-VP-MIGRATION/0.7.2'
    src = copy.deepcopy(src)
    src['transitions'][0]['methods'] = [b('migrate.import/v1', source='legacy-mail', target='new-mail')]
    return src


def build():
    x = {}
    x['M-01'] = v('from-plan', then=None)
    x['M-02'] = v('from-plan', ctx=context('/6'), then=None)
    c = context(); plan(c)['transitions'][0]['methods'][1]['method_id'] = 'migrate.imprt/v1'
    x['M-03'] = v('from-plan', ctx=c, then=None)
    c = context()
    c['method_contracts'] = [{'method_id': 'acme.archive/v1', 'revision': 'local', 'scope': SCOPE, 'origin': 'illustrative_fixture',
                              'argument_min': 1, 'argument_max': 1, 'effect_class': 'pure_declarative'}]
    plan(c)['transitions'][2]['methods'].append(b('acme.archive/v1', arg1='hosting'))
    x['M-04'] = v('from-plan', ctx=c)
    x['M-05'] = ('panels', {'source': m05_source(), **PHASES})
    x['M-06'] = v('from-plan')
    x['M-07'] = v('from-plan')
    x['M-08'] = v('from-plan', labels=LABELS)
    x['M-09'] = v('from-plan')
    x['M-10'] = v('from-plan', layers=LAYERS, then={'view': 'cube.phases', 'partition': 'layer', 'granularity': 'standard'})
    x['M-11'] = v('from-plan', tracks=TRACKS, then={'view': 'cube.phases', 'partition': 'track', 'granularity': 'standard'})
    x['M-12'] = v('from-plan', subjects=['crm-sync'])
    return x


def main():
    vecs = build()
    exp = {c['id']: c for c in ORACLE['cases']}
    assert set(vecs) == set(exp), 'oracle/vector id mismatch'
    cases = [{'id': k, 'op': vecs[k][0], 'input': vecs[k][1], 'expected_status': exp[k]['expected_status'],
              'required_codes': exp[k]['required_codes'], 'forbidden_codes': exp[k]['forbidden_codes'], 'expect': exp[k]['expect']}
             for k in sorted(vecs)]
    out = {'format': 'aiaeao.cube.vp07-vectors/1', 'reference_version': 'v9.4',
           'source': 'VP07_3_ACCEPTANCE_SPEC.md §5 + oracles/independent_m01_m12.json', 'cases': cases}
    (HERE/'fixtures/m01_m12_materialized.json').write_text(json.dumps(out, ensure_ascii=False, sort_keys=True, indent=1)+'\n', 'utf-8')
    print('wrote', len(cases), 'vectors')


if __name__ == '__main__':
    main()
