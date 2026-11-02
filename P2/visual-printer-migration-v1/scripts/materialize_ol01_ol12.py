#!/usr/bin/env python3
"""VP-07.6 TASK-064: materialize OL-01..OL-12 before any 0.7.6 runtime code.

Inputs in G6 wire form (cube_plan_source arguments, then cube_plan_views arguments), built from fixed sources: the
MILE-007 C4 context and statement set, the VP-10 S-04 projection record, the P1.14 contexts (HO vectors) and the
P1.11 golden plan. Expected values come only from oracles/independent_ol01_ol12.json.
"""
import copy, hashlib, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]; REPO = HERE.parents[1]
sys.path.insert(0, str(REPO/'P1/relation-origin-profile-v1/scripts'))
import materialize_ho01_ho12 as HO  # noqa: E402

ORACLE = json.loads((HERE/'oracles/independent_ol01_ol12.json').read_text('utf-8'))
SET = json.loads((HO.SS/'set-c4.json').read_text('utf-8'))
S04 = next(c for c in json.loads((REPO/'P2/visual-printer-cells-v1/fixtures/s01_s16_materialized.json').read_text('utf-8'))['cases']
           if c['id'] == 'S-04')
P076 = 'P2-VP-MIGRATION/0.7.6'
FLOW = {'view': 'cube.flow', 'granularity': 'standard', 'partition': 'subject'}
API, DB = 'c4:shop/api', 'c4:shop/db'


def ctx():
    c = HO.c4_context(); c['context_id'] = SET['context_id']        # the set and the S-04 record refer to mile007-c4
    return c


def set2(origins):
    s = copy.deepcopy(SET); s['format'] = 'aiaeao.cube.statement-set/2'
    for st in s['statements']:
        st.update(origins.get(st['statement_id'], {}))
    return s


def pair(**kw):
    return {'format': 'aiaeao.cube.statement-set/2', 'set_id': 'c4-containers', 'context_id': SET['context_id'],
            'referents': [API, DB], 'statements': [{'statement_id': 'x-1', 'subject': API, 'predicate_id': 'uses', 'object': DB, **kw}],
            'witness_ref': 'synthetic:mile011#c4-containers'}


def src(statements=None, records=None, context=None, plan_id=None, **opt):
    a = {'context': context or ctx(), 'plan_id': plan_id, 'printer': 'vpmigration', 'profile': P076, 'origin_lines': True}
    if statements is not None: a['statements'] = statements
    if records is not None: a['records'] = records
    a.update(opt); return a


DECL = {'s-1': {'origin': 'declared'}, 's-2': {'origin': 'declared'}, 's-3': {'origin': 'declared'}}


def plan_ctx():
    c = HO.plan_context()
    for d in c['migration_plans'][0]['dependencies']:
        d.pop('origin', None)
        if d['dependency_id'] == 'm01a': d['origin'] = 'declared'
        if d['dependency_id'] == 'm01b': d['origin'] = 'unknown'
    return c


def inputs():
    rec = copy.deepcopy(S04['projection']); bad = copy.deepcopy(rec); bad['result']['input_set_sha256'] = '0'*64
    plan = plan_ctx(); pid = plan['migration_plans'][0]['plan_id']
    return {
        'OL-01': ('statements', src(set2(DECL)), FLOW),
        'OL-02': ('statements', src(copy.deepcopy(S04['statements']), [rec]), FLOW),
        'OL-03a': ('statements', src(pair(origin='declared')), FLOW),
        'OL-03b': ('statements', src(pair(origin='derived', basis='b-api-db')), FLOW),
        'OL-04': ('statements', src(copy.deepcopy(SET)), FLOW),
        'OL-05': ('statements', src(set2(DECL | {'s-1': {'origin': 'unknown'}})), FLOW),
        'OL-06': ('statements', src(pair(origin='derived')), FLOW),
        'OL-07': ('from-plan', src(context=plan, plan_id=pid), FLOW | {'partition': 'subject'}),
        'OL-08': ('statements', src(set2(DECL), edge_styles=[{'predicate_id': 'uses', 'style': 'dashed', 'legend': 'uses'}]), FLOW),
        'OL-09': ('from-plan', src(context=plan, plan_id=pid), {'view': 'cube.phases', 'granularity': 'standard', 'partition': 'subject'}),
        'OL-10': ('statements', src(copy.deepcopy(S04['statements']), [bad]), FLOW),
        'OL-11': ('statements', src(pair(origin='derived', basis='b-api-db')), FLOW | {'locale': 'de'}),
        'OL-12': ('g6', src(copy.deepcopy(S04['statements']), [rec]), FLOW),
    }


def build():
    ins = inputs(); cases = []
    for o in ORACLE['cases']:
        op, source_args, view_args = ins[o['id']]
        cases.append({'id': o['id'], 'case': o['case'], 'op': op, 'plan_source': source_args, 'plan_views': view_args,
                      'expected_status': o['expected_status'], 'required_codes': o['required_codes'], 'edges': o['edges'], 'also': o['also']})
    return {'format': 'aiaeao.cube.vp07-vectors/1', 'profile': P076, 'reference_version': 'v9.4',
            'source': 'synthetic; MILE-007 C4 set, VP-10 S-04 projection record, P1.14 HO contexts, P1.11 GM-pos; no client data',
            'oracle_sha256': hashlib.sha256((HERE/'oracles/independent_ol01_ol12.json').read_bytes()).hexdigest(), 'cases': cases}


if __name__ == '__main__':
    v = build()
    (HERE/'fixtures/ol01_ol12_materialized.json').write_text(json.dumps(v, ensure_ascii=False, indent=1)+'\n', 'utf-8')
    print('materialized', len(v['cases']))
