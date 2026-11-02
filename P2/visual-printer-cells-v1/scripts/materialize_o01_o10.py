#!/usr/bin/env python3
"""Materialise O-01..O-10 (VP10_1_ACCEPTANCE_SPEC.md) as explicit binding-context/8 contexts plus call parameters.

Base: the J-02 context (MILE-003 R-1 DSM plan as /8 with the pair declaration m:printer -> m:parser, predicate references).
Expectations stay in oracles/independent_o01_o10.json; this script copies them unchanged.
"""
import copy, json
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
ORACLE = json.loads((HERE/'oracles/independent_o01_o10.json').read_text('utf-8'))['cases']
J = {c['id']: c for c in json.loads((HERE/'fixtures/j01_j14_materialized.json').read_text('utf-8'))['cases']}
J02 = J['J-02']

out = []
for o in ORACLE:
    ctx = copy.deepcopy(J02['context'])
    ctx['context_id'] = 'vp101-'+o['id'].lower()
    if o['id'] == 'O-03':
        ctx = copy.deepcopy(J02['context'])                  # O-03 is J-02 unchanged: the 0.10.0 bytes must not move
    if o['id'] == 'O-08':
        ctx['migration_plans'][0]['dependencies'].append(
            {'dependency_id': 'd-rv', 'subject': 'm:resolver', 'object': 'm:validator', 'predicate_id': 'recovers-via', 'kind': 'other',
             'holds_in': ['p0', 'p1'], 'witness_ref': 'synthetic:dsm#d-rv'})
    out.append({'id': o['id'], 'context': ctx, 'plan_id': J02['plan_id'], 'predicate': 'references', 'steps': None,
                'rows': 'Y:referent', 'cols': 'Y:referent', 'hide_empty': o.get('hide_empty'), 'locale': o.get('locale'),
                'axis_order': o.get('axis_order'), 'via': o.get('via', 'cli'), 'expected': o['expected']})
(HERE/'fixtures/o01_o10_materialized.json').write_text(json.dumps(
    {'format': 'aiaeao.p2.vp101-vectors/1', 'source': 'VP10_1_ACCEPTANCE_SPEC.md §4; base J-02; synthetic, no client data', 'cases': out},
    ensure_ascii=False, indent=1)+'\n', 'utf-8')
print('wrote', len(out), 'vectors')
