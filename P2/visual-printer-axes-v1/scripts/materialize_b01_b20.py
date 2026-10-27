#!/usr/bin/env python3
"""Materialise B-01..B-20 (VP-09.1) from VP09_1_ACCEPTANCE_SPEC.md §5 into explicit vectors.

Expected values are copied from oracles/independent_b01_b20.json (transcribed before code).
All names are synthetic. B-19/B-20 copy the P1.11 golden GM-pos context (D-8) and record the
SHA-256 of the P1.11 golden file, so a change there shows up as a mismatch.
"""
import copy, hashlib, json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]; REPO = HERE.parents[1]
ORACLE = json.loads((HERE/'oracles/independent_b01_b20.json').read_text('utf-8'))
GM_FILE = REPO/'P1/migration-methods-v1/fixtures/golden_methods_synthetic.json'
P091, P090 = 'P2-VP-AXES/0.9.1', 'P2-VP-AXES/0.9.0'
SCOPE, W = 'acme:migration', 'synthetic:contract#scope'
INT, RES, ACT = 'Z:module-body:integration', 'Y:resource-object:resource', 'Y:identity-anchor:actor'
PRV, DEP = 'Z:module-body:provider', 'Z:module-body:third-party-dependency'
HOME = {INT: 'Z', RES: 'Y', ACT: 'Y', PRV: 'Z', DEP: 'Z'}
ALL = ['p0', 'p1', 'p2', 'p3']


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


def context(fmt='/7', jobs=0):
    deps = [dep('d1', 'shop', 'sends-via', 'legacy-mail', ['p0', 'p1'], successor_ref='d2'),
            dep('d2', 'shop', 'sends-via', 'new-mail', ['p2', 'p3']),
            dep('d3', 'shop', 'depends-on', 'hosting', ALL),
            dep('d4', 'crm-sync', 'depends-on', 'admin-mailbox', ALL),
            dep('d5', 'support', 'depends-on', 'old-store', ['p0', 'p1'], successor_ref='d6'),
            dep('d6', 'support', 'depends-on', 'new-store', ['p2', 'p3']),
            dep('d7', 'crm-sync', 'depends-on', 'mailbox-x', ['p0', 'p1'], dropped=True),
            dep('d8', 'crm-sync', 'sends-via', 'new-mail', ['p2', 'p3'])]
    names = [f'job-{i:02d}' for i in range(1, jobs+1)]
    deps += [dep(f'j{k+1}', j, 'depends-on', 'hosting', ALL) for k, j in enumerate(names)]
    trs = [tr('t-mail', 'p2', ['legacy-mail'], ['new-mail']), tr('t-store', 'p2', ['old-store'], ['new-store']),
           tr('t-box', 'p2', ['mailbox-x'], [])]
    c = {'format': 'aiaeao.cube.binding-context'+fmt, 'reference_version': 'v9.4', 'context_id': 'vp091-axes',
         'source_kind': 'illustrative_fixture', 'scope_ref': SCOPE, 'predicate_profile_refs': ['P1.10/migration-predicates-v1'],
         'referents': [ref('shop', INT), ref('crm-sync', INT), ref('support', ACT), ref('admin-mailbox', RES), ref('mailbox-x', RES),
                       ref('old-store', RES), ref('new-store', RES), ref('legacy-mail', DEP), ref('new-mail', PRV), ref('hosting', DEP)]
         + [ref(j, INT) for j in names],
         'predicate_contracts': [],
         'migration_plans': [{'plan_id': 'mp-axes', 'revision': 'v1', 'scope': SCOPE, 'origin': 'illustrative_fixture',
                              'phases': [{'phase_id': 'p0', 'role': 'current'}, {'phase_id': 'p1', 'role': 'intermediate'},
                                         {'phase_id': 'p2', 'role': 'intermediate'}, {'phase_id': 'p3', 'role': 'target'}],
                              'transitions': trs, 'dependencies': deps}]}
    if fmt == '/7':
        c['method_profile_refs'] = ['P1.11/migration-methods-v1']
        trs[0]['methods'] = [b('migrate.import/v1', source='legacy-mail', target='new-mail'), b('migrate.retire/v1', retired='legacy-mail')]
        trs[1]['methods'] = [b('migrate.import/v1', source='old-store', target='new-store'), b('migrate.retire/v1', retired='old-store')]
        trs[2]['methods'] = [b('migrate.retire/v1', retired='mailbox-x')]
        deps[0]['method'] = b('migrate.rewrite/v1', dependant='shop', new_object='new-mail')
        deps[4]['method'] = b('migrate.rewrite/v1', dependant='support', new_object='new-store')
    return c


def plan(c):
    return c['migration_plans'][0]


def local(c):
    c['method_contracts'] = [{'method_id': 'acme.archive/v1', 'revision': 'local', 'scope': SCOPE, 'origin': 'illustrative_fixture',
                              'argument_min': 1, 'argument_max': 1, 'effect_class': 'pure_declarative'}]
    return c


def v(op, rows, cols, granularity='standard', ctx=None, profile=P091, plan_id='mp-axes', **kw):
    d = {'context': ctx or context(), 'plan_id': plan_id, 'rows': rows, 'cols': cols, 'granularity': granularity, 'profile': profile}
    d.update(kw)
    return (op, d)


def build():
    gm_raw = GM_FILE.read_bytes()
    gm = next(c for c in json.loads(gm_raw)['cases'] if c['id'] == 'GM-pos')['context']
    gm_pid = gm['migration_plans'][0]['plan_id']
    x = {}
    x['B-01'] = v('render', 'F', 'Z:referent')
    c = context(); plan(c)['transitions'][0]['methods'][0]['method_id'] = 'migrate.imprt/v1'
    x['B-02'] = v('render', 'F', 'Z:referent', ctx=c)
    c = local(context()); plan(c)['transitions'][2]['methods'].append(b('acme.archive/v1', arg1='hosting'))
    x['B-03'] = v('render', 'F', 'Z:referent', ctx=c)
    c = context(); plan(c)['transitions'][0]['methods'].reverse()
    x['B-04'] = v('render', 'F', 'Z:referent', ctx=c)
    x['B-05'] = v('render', 'F', 'Z:referent')
    x['B-06'] = v('render', 'F', 'Y:referent')
    x['B-07'] = v('render', 'F', 'Z:referent')
    x['B-08'] = v('render', 'F', 'Y:kind')
    x['B-09'] = v('render', 'F', 'Z:referent', ctx=context('/5'))
    x['B-10'] = v('render', 'F', 'Z:referent')
    x['B-11'] = v('render', 'F', 'T')
    c = local(context()); plan(c)['dependencies'][3]['method'] = b('acme.archive/v1', arg1='admin-mailbox')
    x['B-12'] = v('render', 'F', 'T', ctx=c)
    x['B-13'] = v('render', 'F', 'T')
    x['B-14'] = v('render', 'F', 'Z:referent', subjects=['shop', 'crm-sync'])
    x['B-15'] = v('render', 'F', 'Z:referent')
    x['B-16'] = v('panels', 'F', 'Z:referent', ctx=context(jobs=17))
    x['B-17'] = v('panels', 'F', 'Z:referent', ctx=context(jobs=17), tamper='drop_binding_unit')
    x['B-18'] = v('render', 'F', 'Z:referent', profile=P090)
    x['B-19'] = v('panels', 'F', 'Z:referent', ctx=copy.deepcopy(gm), plan_id=gm_pid)
    x['B-20'] = v('render', 'F', 'T', ctx=copy.deepcopy(gm), plan_id=gm_pid)
    return x, hashlib.sha256(gm_raw).hexdigest()


def main():
    vecs, gm_sha = build()
    exp = {c['id']: c for c in ORACLE['cases']}
    assert set(vecs) == set(exp), 'oracle/vector id mismatch'
    cases = [{'id': k, 'op': vecs[k][0], 'input': vecs[k][1], 'expected_status': exp[k]['expected_status'],
              'required_codes': exp[k]['required_codes'], 'forbidden_codes': exp[k]['forbidden_codes'], 'expect': exp[k]['expect']}
             for k in sorted(vecs)]
    out = {'format': 'aiaeao.cube.vp09-vectors/1', 'reference_version': 'v9.4',
           'source': 'VP09_1_ACCEPTANCE_SPEC.md §5 + oracles/independent_b01_b20.json',
           'gm_pos_source': {'path': 'P1/migration-methods-v1/fixtures/golden_methods_synthetic.json', 'sha256': gm_sha}, 'cases': cases}
    (HERE/'fixtures/b01_b20_materialized.json').write_text(json.dumps(out, ensure_ascii=False, sort_keys=True, indent=1)+'\n', 'utf-8')
    print('wrote', len(cases), 'vectors')


if __name__ == '__main__':
    main()
