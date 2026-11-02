#!/usr/bin/env python3
"""Materialise J-01..J-14 (VP10_ACCEPTANCE_SPEC.md §5) as explicit binding-context/8 contexts plus call parameters.

Base: the MILE-003 R-1 DSM plan (synthetic), lifted to /8. Expectations stay in oracles/independent_j01_j14.json.
"""
import copy, json
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]; REPO = HERE.parents[1]
R1 = json.loads((REPO/'docs/09-Research/visual-check/renders/R-1.json').read_text('utf-8'))
ORACLE = json.loads((HERE/'oracles/independent_j01_j14.json').read_text('utf-8'))['cases']
P, R, V, PR = 'm:parser', 'm:resolver', 'm:validator', 'm:printer'


def base(jid, decls=None):
    c = copy.deepcopy(R1['context'])
    c['format'] = 'aiaeao.cube.binding-context/8'
    c['context_id'] = 'vp10-'+jid.lower()
    if decls is not None:
        c['coverage_declarations'] = decls
    return c


def pair(i, s, o, pred='references'):
    return {'declaration_id': i, 'scope': 'pair', 'subject': s, 'predicate_id': pred, 'object': o, 'witness_ref': 'synthetic:survey#'+i}


def rrd(i, ref, direction, **kw):
    return {'declaration_id': i, 'scope': 'referent_relation_direction', 'referent': ref, 'predicate_id': 'references', 'direction': direction,
            'witness_ref': 'synthetic:survey#'+i, **kw}


def dep(did, s, o, pred, holds=('p0', 'p1')):
    return {'dependency_id': did, 'subject': s, 'object': o, 'predicate_id': pred, 'kind': 'other', 'holds_in': list(holds),
            'witness_ref': 'synthetic:dsm#'+did}


def plan(c):
    return c['migration_plans'][0]


J = {}
J['J-01'] = (base('J-01'), {})
J['J-02'] = (base('J-02', [pair('cv-pp', PR, P)]), {})
J['J-03'] = (base('J-03', [rrd('cv-pr-out', PR, 'outgoing')]), {})
J['J-04'] = (base('J-04', [rrd('cv-p-in', P, 'incoming')]), {})
J['J-05'] = (base('J-05', [pair('cv-rp', R, P)]), {})
J['J-06'] = (base('J-06', [pair('cv-pp-rv', PR, P, 'recovers-via')]), {})
c = base('J-07', [pair('cv-pp', PR, P)])
plan(c)['dependencies'] += [dep('d-pp', PR, P, 'recovers-via'), dep('d-vp', V, PR, 'recovers-via')]
J['J-07'] = (c, {})
J['J-08'] = (base('J-08', [pair('cv-pp', PR, P)]), {'hide_empty': 'cols'})
J['J-09'] = (base('J-09', [rrd('cv-pr-in', PR, 'incoming')]), {'hide_empty': 'cols'})
J['J-10'] = (base('J-10', [pair('cv-lexer', PR, 'm:lexer')]), {})
J['J-11'] = (base('J-11', [rrd('cv-pr-i1', PR, 'outgoing', instance_ref='vp10:i1')]), {})
c = base('J-12', [rrd('cv-pr-out', PR, 'outgoing')])
plan(c)['phases'] = [{'phase_id': 'p0', 'role': 'current'}, {'phase_id': 'p1', 'role': 'intermediate'}, {'phase_id': 'p2', 'role': 'target'}]
for d in plan(c)['dependencies']:
    d['holds_in'] = ['p0'] if d['dependency_id'] == 'd-pv' else ['p0', 'p1', 'p2']
plan(c)['dependencies'].append(dep('d-pr', PR, R, 'recovers-via', ('p0', 'p1', 'p2')))
J['J-12'] = (c, {'steps': 'p1:p2'})   # corrected before the code commit: cube.phases needs at least two steps
J['J-13'] = (base('J-13', [pair('cv-pp', PR, P)]), {'rows': 'Y:referent', 'cols': 'T'})
J['J-14'] = (base('J-14', [rrd('cv-pr-out', PR, 'outgoing')]), {'locale': 'de'})

out = []
for o in ORACLE:
    ctx, call = J[o['id']]
    out.append({'id': o['id'], 'variant': o['variant'], 'context': ctx, 'plan_id': R1['plan_id'], 'predicate': o['predicate'],
                'steps': call.get('steps'), 'rows': call.get('rows', 'Y:referent'), 'cols': call.get('cols', 'Y:referent'),
                'hide_empty': call.get('hide_empty'), 'locale': call.get('locale'), 'expected': o['expected']})
(HERE/'fixtures').mkdir(exist_ok=True)
(HERE/'fixtures/j01_j14_materialized.json').write_text(json.dumps(
    {'format': 'aiaeao.p2.vp10-vectors/1', 'source': 'VP10_ACCEPTANCE_SPEC.md §5; base MILE-003 R-1 plan; synthetic, no client data', 'cases': out},
    ensure_ascii=False, indent=1)+'\n', 'utf-8')
print('wrote', len(out), 'vectors')
