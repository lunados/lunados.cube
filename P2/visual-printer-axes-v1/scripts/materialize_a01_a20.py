#!/usr/bin/env python3
"""Materialise A-01..A-20 from VP09_ACCEPTANCE_SPEC.md §5 into explicit vectors.

Expected values are copied from oracles/independent_a01_a20.json (transcribed before code).
All names are synthetic. Vectors start from a binding-context (/6 or /7) and go through
`vpaxes from-plan` (AQ-1), so F data comes from declared P1.11 bindings.
"""
import copy, json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ORACLE = json.loads((HERE/'oracles/independent_a01_a20.json').read_text('utf-8'))
A, SCOPE, W = 'α', 'acme:migration', 'synthetic:contract#scope'
INT, RES, ACT = 'Z:module-body:integration', 'Y:resource-object:resource', 'Y:identity-anchor:actor'
PRV, DEP = 'Z:module-body:provider', 'Z:module-body:third-party-dependency'
HOME = {INT: 'Z', RES: 'Y', ACT: 'Y', PRV: 'Z', DEP: 'Z'}
ALL = ['p0', 'p1', 'p2', 'p3']
JOBS = [f'job-{i:02d}' for i in range(1, 7)]


def ref(r, cid):
    return {'ref': r, 'concept_id': cid, 'home': HOME[cid], 'layers': [A], 'provenance_status': 'declared_unverified', 'scope_ref': SCOPE}


def dep(i, s, pred, o, holds, **kw):
    d = {'dependency_id': i, 'subject': s, 'predicate_id': pred, 'object': o, 'kind': 'job', 'holds_in': holds, 'witness_ref': f'repo:example/{i}'}
    d.update(kw)
    return d


def tr(i, at, ret, intro, methods=None):
    t = {'transition_id': i, 'at_phase': at, 'retires': ret, 'introduces': intro, 'T': {'role': 'scheduling', 'value': 'TBD'}, 'witness_ref': W}
    if methods:
        t['methods'] = methods
    return t


def b(mid, **args):
    return {'method_id': mid, 'arguments': args}


def context(fmt='aiaeao.cube.binding-context/7', jobs=JOBS):
    deps = [dep('d1', 'shop', 'sends-via', 'legacy-mail', ['p0', 'p1'], successor_ref='d2'),
            dep('d2', 'shop', 'sends-via', 'new-mail', ['p2', 'p3']),
            dep('d3', 'shop', 'depends-on', 'hosting', ALL),
            dep('d4', 'crm-sync', 'depends-on', 'admin-mailbox', ALL),
            dep('d5', 'support', 'depends-on', 'admin-mailbox', ALL),
            dep('d6', 'crm-sync', 'depends-on', 'mailbox-x', ['p0', 'p1'], dropped=True),
            dep('d7', 'shop', 'depends-on', 'dns-zone', ALL)]
    deps += [dep(f'j{k+1}', j, 'depends-on', 'hosting', ALL) for k, j in enumerate(jobs)]
    trs = [tr('t-mail', 'p2', ['legacy-mail'], ['new-mail']), tr('t-box', 'p2', ['mailbox-x'], [])]
    c = {'format': fmt, 'reference_version': 'v9.4', 'context_id': 'vp09-axes', 'source_kind': 'illustrative_fixture', 'scope_ref': SCOPE,
         'predicate_profile_refs': ['P1.10/migration-predicates-v1'],
         'referents': [ref('shop', INT), ref('crm-sync', INT), ref('support', ACT), ref('admin-mailbox', RES), ref('mailbox-x', RES),
                       ref('legacy-mail', DEP), ref('new-mail', PRV), ref('hosting', DEP), ref('dns-zone', DEP)] + [ref(j, INT) for j in jobs],
         'predicate_contracts': [],
         'migration_plans': [{'plan_id': 'mp-axes', 'revision': 'v1', 'scope': SCOPE, 'origin': 'illustrative_fixture',
                              'phases': [{'phase_id': 'p0', 'role': 'current'}, {'phase_id': 'p1', 'role': 'intermediate'},
                                         {'phase_id': 'p2', 'role': 'intermediate'}, {'phase_id': 'p3', 'role': 'target'}],
                              'transitions': trs, 'dependencies': deps}]}
    if fmt.endswith('/7'):
        c['method_profile_refs'] = ['P1.11/migration-methods-v1']
        trs[0]['methods'] = [b('migrate.import/v1', source='legacy-mail', target='new-mail'), b('migrate.retire/v1', retired='legacy-mail')]
        trs[1]['methods'] = [b('migrate.retire/v1', retired='mailbox-x')]
        deps[0]['method'] = b('migrate.rewrite/v1', dependant='shop', new_object='new-mail')
    return c


LAYERS = {'format': 'aiaeao.cube.vp07-layer-map/1', 'layer_order': ['provider', 'account', 'system', 'actor'],
          'layers': {'provider': ['hosting', 'dns-zone', 'legacy-mail', 'new-mail'], 'account': ['admin-mailbox', 'mailbox-x'],
                     'system': ['crm-sync', 'shop'] + JOBS, 'actor': ['support']}}


def v(op, rows, cols, granularity='standard', ctx=None, **kw):
    d = {'context': ctx or context(), 'plan_id': 'mp-axes', 'rows': rows, 'cols': cols, 'granularity': granularity}
    d.update(kw)
    return (op, d)


def build():
    x = {}
    x['A-01'] = v('render', 'Z:referent', 'T')
    x['A-02'] = v('render', 'M', 'T')
    x['A-03'] = v('render', 'T', 'T')
    x['A-04'] = v('render', 'F', 'Z:referent', ctx=context('aiaeao.cube.binding-context/6'))
    x['A-05'] = v('render', 'Z:kind', 'T')
    x['A-06'] = v('render', 'Z:referent', 'T', 'detail', layers=LAYERS)
    x['A-07'] = v('render', 'Z:referent', 'T', 'detail')
    x['A-08'] = v('render', 'Y:referent', 'T')
    x['A-09'] = v('render', 'F', 'Z:referent', 'detail', ctx=context(jobs=[]))  # Z columns within the detail budget
    x['A-10'] = v('render', 'X', 'X')
    x['A-11'] = v('render', 'Y:referent', 'Z:referent', 'detail', ctx=context(jobs=[]))
    x['A-12'] = v('render', 'Y:referent', 'Z:referent', 'detail', ctx=context(jobs=[]))
    x['A-13'] = v('render', 'Y:referent', 'Z:referent', 'detail', ctx=context(jobs=[]))
    x['A-14'] = v('render', 'Z:referent', 'T', 'detail')
    x['A-15'] = v('render', 'Y:referent', 'T')
    x['A-16'] = v('render', 'Y:referent', 'T')
    x['A-17'] = v('render', 'Z:referent', 'T', 'standard')
    many = [f'job-{i:02d}' for i in range(1, 31)]
    x['A-18'] = v('render', 'Z:referent', 'T', 'standard', ctx=context(jobs=many))
    x['A-19'] = v('panels', 'Z:referent', 'T', 'standard', ctx=context(jobs=many))
    x['A-20'] = v('panels', 'Z:referent', 'T', 'standard', ctx=context(jobs=many), tamper='drop_entry')
    return x


def main():
    vecs = build()
    exp = {c['id']: c for c in ORACLE['cases']}
    assert set(vecs) == set(exp), 'oracle/vector id mismatch'
    cases = [{'id': k, 'op': vecs[k][0], 'input': vecs[k][1], 'expected_status': exp[k]['expected_status'],
              'required_codes': exp[k]['required_codes'], 'forbidden_codes': exp[k]['forbidden_codes'], 'expect': exp[k]['expect']}
             for k in sorted(vecs)]
    out = {'format': 'aiaeao.cube.vp09-vectors/1', 'reference_version': 'v9.4',
           'source': 'VP09_ACCEPTANCE_SPEC.md §5 + oracles/independent_a01_a20.json', 'cases': cases}
    (HERE/'fixtures/a01_a20_materialized.json').write_text(json.dumps(out, ensure_ascii=False, sort_keys=True, indent=1)+'\n', 'utf-8')
    print('wrote', len(cases), 'vectors')


if __name__ == '__main__':
    main()
