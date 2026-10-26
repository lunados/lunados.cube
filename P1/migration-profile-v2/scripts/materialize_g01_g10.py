#!/usr/bin/env python3
"""Materialise G-01..G-10 from P1_10_1_ACCEPTANCE_SPEC.md §5 into explicit vectors.

Expected values are copied from oracles/independent_g01_g10.json (transcribed before code).
All names are synthetic.
"""
import copy, json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ORACLE = json.loads((HERE/'oracles/independent_g01_g10.json').read_text('utf-8'))
A, SCOPE = 'α', 'acme:migration'
INT, RES = 'Z:module-body:integration', 'Y:resource-object:resource'
TEXT = f'rel("depends-on",Z:{A}:Integration["import-job"],Y:{A}:Resource["mailbox-x"])'


def ref(r, cid, home):
    return {'ref': r, 'concept_id': cid, 'home': home, 'layers': [A], 'provenance_status': 'declared_unverified', 'scope_ref': SCOPE}


def dep(i, obj, holds, **kw):
    d = {'dependency_id': i, 'subject': 'import-job', 'predicate_id': 'depends-on', 'object': obj, 'kind': 'job',
         'holds_in': holds, 'witness_ref': f'repo:example/jobs/{i}'}
    d.update(kw)
    return d


def tr(i, at, retires):
    return {'transition_id': i, 'at_phase': at, 'retires': retires, 'introduces': [],
            'T': {'role': 'scheduling', 'value': 'TBD'}, 'witness_ref': 'synthetic:contract#scope'}


def base(fmt='aiaeao.cube.binding-context/6'):
    return {'format': fmt, 'reference_version': 'v9.4', 'context_id': 'p1101-gap', 'source_kind': 'illustrative_fixture',
            'scope_ref': SCOPE, 'predicate_profile_refs': ['P1.10/migration-predicates-v1'],
            'referents': [ref('import-job', INT, 'Z'), ref('mailbox-x', RES, 'Y'), ref('mailbox-y', RES, 'Y')],
            'predicate_contracts': [],
            'migration_plans': [{'plan_id': 'mp-acme', 'revision': 'v1', 'scope': SCOPE, 'origin': 'illustrative_fixture',
                                 'phases': [{'phase_id': 'p0', 'role': 'current'}, {'phase_id': 'p1', 'role': 'intermediate'},
                                            {'phase_id': 'p2', 'role': 'intermediate'}, {'phase_id': 'p3', 'role': 'target'}],
                                 'transitions': [], 'dependencies': [dep('d-import', 'mailbox-x', ['p0', 'p1'])]}]}


def plan(c):
    return c['migration_plans'][0]


def build():
    v = {}
    v['G-01'] = base()
    v['G-02'] = base('aiaeao.cube.binding-context/5')
    c = base(); plan(c)['dependencies'][0]['holds_in'] = ['p0', 'p1', 'p2', 'p3']; v['G-03'] = c
    c = base(); plan(c)['dependencies'][0]['dropped'] = True; v['G-04'] = c
    c = base(); plan(c)['transitions'] = [tr('t-x', 'p2', ['mailbox-x'])]; v['G-05'] = c
    c = base(); plan(c)['transitions'] = [tr('t-x', 'p3', ['mailbox-x'])]; v['G-06'] = c
    c = base(); plan(c)['transitions'] = [tr('t-job', 'p2', ['import-job'])]; v['G-07'] = c
    c = base(); plan(c)['dependencies'][0]['successor_ref'] = 'd-next'
    plan(c)['dependencies'].append(dep('d-next', 'mailbox-y', ['p2', 'p3'])); v['G-08'] = c
    c = copy.deepcopy(v['G-08']); plan(c)['dependencies'][1]['holds_in'] = ['p3']; v['G-09'] = c
    c = base(); plan(c)['dependencies'][0]['ends_reason'] = 'scope_end'; v['G-10'] = c
    return v


def main():
    vecs = build()
    exp = {c['id']: c for c in ORACLE['cases']}
    assert set(vecs) == set(exp), 'oracle/vector id mismatch'
    cases = [{'id': k, 'input_text': TEXT, 'input_format': 'acg_text', 'context': vecs[k],
              'expected_overall': exp[k]['expected_overall'], 'required_codes': exp[k]['required_codes'],
              'forbidden_codes': exp[k]['forbidden_codes']} for k in sorted(vecs)]
    out = {'format': 'aiaeao.cube.p1.10.1-vectors/1', 'reference_version': 'v9.4',
           'source': 'P1_10_1_ACCEPTANCE_SPEC.md §5 + oracles/independent_g01_g10.json', 'cases': cases}
    (HERE/'fixtures/g01_g10_materialized.json').write_text(json.dumps(out, ensure_ascii=False, sort_keys=True, indent=2)+'\n', 'utf-8')
    print('wrote', len(cases), 'vectors')


if __name__ == '__main__':
    main()
