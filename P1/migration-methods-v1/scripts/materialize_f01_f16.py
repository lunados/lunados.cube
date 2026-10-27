#!/usr/bin/env python3
"""Materialise F-01..F-16 from P1_11_ACCEPTANCE_SPEC.md §5 into explicit vectors.

Expected values are copied from oracles/independent_f01_f16.json (transcribed before code).
All names are synthetic.
"""
import copy, json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ORACLE = json.loads((HERE/'oracles/independent_f01_f16.json').read_text('utf-8'))
A, SCOPE, W = 'α', 'acme:migration', 'synthetic:contract#scope'
INT, RES, ACT = 'Z:module-body:integration', 'Y:resource-object:resource', 'Y:identity-anchor:actor'
PRV, DEP = 'Z:module-body:provider', 'Z:module-body:third-party-dependency'
HOME = {INT: 'Z', RES: 'Y', ACT: 'Y', PRV: 'Z', DEP: 'Z'}
TEXT = f'rel("sends-via",Z:{A}:Integration["shop"],Z:{A}:Provider["new-mail"])'
SUPERSEDES = (f'rel("supersedes",Z:{A}:Provider["new-mail"],Z:{A}:ThirdPartyDependency["legacy-mail"]) '
              f'@T(role="scheduling",witness_ref="{W}") @F(method="migrate.import/v1")')
QP = {'format': 'aiaeao.cube.qualifier-profiles/1', 'origin': 'illustrative_fixture', 'profile_id': 'acme:qualifiers', 'reference_version': 'v9.4',
      'scope': SCOPE, 'witness_refs': [W],
      'qualifiers': [{'coordinate': 'T', 'profile_ref': 'acme:T-scheduling/v1', 'allowed_parameters': ['role', 'witness_ref'],
                      'required_parameters': ['role', 'witness_ref'], 'allowed_values': {'role': ['scheduling']}, 'requires_witness': True},
                     {'coordinate': 'F', 'profile_ref': 'acme:F-method/v1', 'allowed_parameters': ['method'], 'required_parameters': ['method'],
                      'allowed_values': {}, 'requires_witness': False}]}


def ref(r, cid):
    return {'ref': r, 'concept_id': cid, 'home': HOME[cid], 'layers': [A], 'provenance_status': 'declared_unverified', 'scope_ref': SCOPE}


def tr(i, at, ret, intro, **kw):
    t = {'transition_id': i, 'at_phase': at, 'retires': ret, 'introduces': intro, 'T': {'role': 'scheduling', 'value': 'TBD'}, 'witness_ref': W}
    t.update(kw)
    return t


def dep(i, s, pred, o, holds, **kw):
    d = {'dependency_id': i, 'subject': s, 'predicate_id': pred, 'object': o, 'kind': 'job', 'holds_in': holds, 'witness_ref': f'repo:example/{i}'}
    d.update(kw)
    return d


def bind(mid, **args):
    return {'method_id': mid, 'arguments': args}


def base(fmt='aiaeao.cube.binding-context/7', methods=True):
    c = {'format': fmt, 'reference_version': 'v9.4', 'context_id': 'p111-methods', 'source_kind': 'illustrative_fixture', 'scope_ref': SCOPE,
         'predicate_profile_refs': ['P1.10/migration-predicates-v1'],
         'referents': [ref('shop', INT), ref('support', ACT), ref('legacy-mail', DEP), ref('new-mail', PRV), ref('mailbox-x', RES)],
         'predicate_contracts': [],
         'migration_plans': [{'plan_id': 'mp-acme', 'revision': 'v1', 'scope': SCOPE, 'origin': 'illustrative_fixture',
                              'phases': [{'phase_id': 'p0', 'role': 'current'}, {'phase_id': 'p1', 'role': 'intermediate'},
                                         {'phase_id': 'p2', 'role': 'intermediate'}, {'phase_id': 'p3', 'role': 'target'}],
                              'transitions': [tr('t-mail', 'p2', ['legacy-mail'], ['new-mail'])],
                              'dependencies': [dep('d-a', 'shop', 'sends-via', 'legacy-mail', ['p0', 'p1'], successor_ref='d-b'),
                                               dep('d-b', 'shop', 'sends-via', 'new-mail', ['p2', 'p3'])]}]}
    if methods:
        c['method_profile_refs'] = ['P1.11/migration-methods-v1']
    return c


def plan(c):
    return c['migration_plans'][0]


def t0(c):
    return plan(c)['transitions'][0]


def case(ctx, text=TEXT, qp=None):
    d = {'input_text': text, 'input_format': 'acg_text', 'context': ctx}
    if qp:
        d['qualification_profiles'] = copy.deepcopy(qp)
    return d


def build():
    v = {}
    v['F-01'] = case(base())
    c = base(); c['method_profile_refs'] = ['P1.11/migration-methods-v9']; v['F-02'] = case(c)
    v['F-03'] = dict(case(base()), tamper_catalog=True)
    c = base(); c['method_contracts'] = [{'method_id': 'migrate.import/v1', 'revision': 'local', 'scope': SCOPE, 'origin': 'illustrative_fixture',
                                          'argument_min': 2, 'argument_max': 2, 'effect_class': 'pure_declarative'}]
    v['F-04'] = case(c)
    c = base(); t0(c)['methods'] = [bind('migrate.import/v1', source='legacy-mail', target='new-mail'), bind('migrate.retire/v1', retired='legacy-mail')]
    plan(c)['dependencies'][0]['method'] = bind('migrate.rewrite/v1', dependant='shop', new_object='new-mail')
    v['F-05'] = case(c)
    c = base(); t0(c)['methods'] = [bind('migrate.unknown/v1', target='new-mail')]; v['F-06'] = case(c)
    c = base(); t0(c)['methods'] = [bind('migrate.import/v1', source='legacy-mail')]; v['F-07'] = case(c)
    c = base(); t0(c)['methods'] = [bind('migrate.import/v1', source='legacy-mail', target='support')]; v['F-08'] = case(c)
    c = base(); t0(c)['methods'] = [bind('migrate.import/v1', source='legacy-mail', target='ghost-mail')]; v['F-09'] = case(c)
    c = base(); t0(c)['methods'] = [bind('migrate.retire/v1', retired='mailbox-x')]; v['F-10'] = case(c)
    c = base(); plan(c)['transitions'].insert(0, tr('t-prep', 'p1', [], ['mailbox-x'],
                                                    methods=[bind('migrate.import/v1', source='legacy-mail', target='new-mail')]))
    v['F-11'] = case(c)
    c = base(); plan(c)['dependencies'][1]['method'] = bind('migrate.rewrite/v1', dependant='shop', new_object='new-mail')
    v['F-12'] = case(c)
    c = base(); plan(c)['dependencies'][0]['method'] = bind('migrate.rewrite/v1', dependant='shop', new_object='mailbox-x')
    v['F-13'] = case(c)
    v['F-14'] = case(base(), SUPERSEDES, QP)
    v['F-15'] = case(base(methods=False), SUPERSEDES, QP)
    c = base('aiaeao.cube.binding-context/6', methods=False)
    t0(c)['methods'] = [bind('migrate.retire/v1', retired='legacy-mail')]
    v['F-16'] = case(c)
    return v


def main():
    vecs = build()
    exp = {c['id']: c for c in ORACLE['cases']}
    assert set(vecs) == set(exp), 'oracle/vector id mismatch'
    cases = []
    for k in sorted(vecs):
        cases.append({'id': k, **vecs[k], 'expected_overall': exp[k]['expected_overall'], 'required_codes': exp[k]['required_codes'],
                      'forbidden_codes': exp[k]['forbidden_codes']})
    out = {'format': 'aiaeao.cube.p1.11-vectors/1', 'reference_version': 'v9.4',
           'source': 'P1_11_ACCEPTANCE_SPEC.md §5 + oracles/independent_f01_f16.json', 'cases': cases}
    (HERE/'fixtures/f01_f16_materialized.json').write_text(json.dumps(out, ensure_ascii=False, indent=1)+'\n', 'utf-8')
    print('wrote', len(cases), 'vectors')


if __name__ == '__main__':
    main()
