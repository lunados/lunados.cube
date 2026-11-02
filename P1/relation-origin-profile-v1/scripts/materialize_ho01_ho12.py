#!/usr/bin/env python3
"""P1.14 TASK-064: materialize HO-01..HO-12 before any P1.14 runtime code.

Inputs are built from fixed, committed sources (MILE-007 C4 context and statement set, the S-04 projection record of
VP-10 0.11.0, P1.13 KF-01, P1.11 golden GM-pos). Expected values come only from oracles/independent_ho01_ho12.json.
With --baseline the script also validates every case projected to /9 (P1.14 fields removed) with the current
validator and writes fixtures/baseline_p113.json: the state before P1.14.
"""
import copy, hashlib, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]; REPO = HERE.parents[1]
canon = lambda o: json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
ORACLE = json.loads((HERE/'oracles/independent_ho01_ho12.json').read_text('utf-8'))
SS = REPO/'docs/09-Research/statement-sets/inputs'
C4 = json.loads((SS/'ctx-c4.json').read_text('utf-8'))
S04 = next(c for c in json.loads((REPO/'P2/visual-printer-cells-v1/fixtures/s01_s16_materialized.json').read_text('utf-8'))['cases']
           if c['id'] == 'S-04')['projection']
KF01 = next(c for c in json.loads((REPO/'P1/control-flow-profile-v1/fixtures/kf01_kf09_materialized.json').read_text('utf-8'))['cases']
            if c['id'] == 'KF-01')
GM = next(c for c in json.loads((REPO/'P1/migration-methods-v1/fixtures/golden_methods_synthetic.json').read_text('utf-8'))['cases']
          if c['id'] == 'GM-pos')
RECORD_SHA = hashlib.sha256(canon(S04)).hexdigest()


def c4_context():
    ctx = copy.deepcopy(C4)
    ctx['format'] = 'aiaeao.cube.binding-context/10'; ctx['context_id'] = 'p114-c4'
    for p in ctx['predicate_contracts']:
        if p['predicate_id'] == 'uses':
            p['origin_binding'] = 'required'
    ctx['origin_bases'] = [
        {'basis_id': 'b-api-db', 'kind': 'statements', 'set_id': 'c4-components', 'statement_ids': ['s-1', 's-2'],
         'witness_ref': 'synthetic:mile007#c4-components'},
        {'basis_id': 'b-agg', 'kind': 'projection_record', 'record_sha256': RECORD_SHA, 'statement_id': 'd-1',
         'library_ref': copy.deepcopy(S04['library_ref'])}]
    return ctx


def plan_context():
    ctx = copy.deepcopy(GM['context'])
    ctx['format'] = 'aiaeao.cube.binding-context/10'; ctx['context_id'] = 'p114-gm'
    for p in ctx['predicate_contracts']:
        if p['predicate_id'] == 'sends-via':
            p['origin_binding'] = 'required'
    for d in ctx['migration_plans'][0]['dependencies']:
        if d['dependency_id'] != 'm01b':
            d['origin'] = 'declared'
    return ctx


def build():
    cases = []
    for o in ORACLE['cases']:
        if o['id'] == 'HO-11':
            text, fmt, ctx = KF01['input_text'], KF01.get('input_format', 'acg_text'), copy.deepcopy(KF01['context'])
        elif o['id'] == 'HO-12':
            text, fmt, ctx = GM['input_text'][:-1]+';origin="declared")', 'acg_text', plan_context()
        else:
            text, fmt, ctx = o['input_text'], 'acg_text', c4_context()
        cases.append({'id': o['id'], 'case': o['case'], 'input_text': text, 'input_format': fmt, 'context': ctx,
                      'expected_overall': o['expected_overall'], 'required_codes': o['required_codes'],
                      'forbidden_codes': o['forbidden_codes'], **({'required_pointer_prefix': o['required_pointer_prefix']}
                                                                    if 'required_pointer_prefix' in o else {})})
    return {'format': 'aiaeao.cube.p1.14-vectors/1', 'reference_version': 'v9.4',
            'source': 'synthetic; MILE-007 C4 context and set, VP-10 S-04 projection record, P1.13 KF-01, P1.11 GM-pos; no client data',
            'oracle_sha256': hashlib.sha256((HERE/'oracles/independent_ho01_ho12.json').read_bytes()).hexdigest(),
            'projection_record_sha256': RECORD_SHA, 'cases': cases}


def to_v9(ctx):
    ctx = copy.deepcopy(ctx)
    if ctx['format'] != 'aiaeao.cube.binding-context/10':
        return ctx
    ctx['format'] = 'aiaeao.cube.binding-context/9'; ctx.pop('origin_bases', None)
    for p in ctx['predicate_contracts']:
        p.pop('origin_binding', None)
    for plan in ctx.get('migration_plans', []):
        for d in plan['dependencies']:
            d.pop('origin', None); d.pop('basis', None)
    return ctx


def baseline(vec):
    sys.path.insert(0, str(REPO/'P3/adapters/mcp-local'))
    from aiaeao_mcp_local import p1_adapter
    rows = []
    for c in vec['cases']:
        r = p1_adapter.validate(c['input_text'], c['input_format'], to_v9(c['context']))['report']
        rows.append({'id': c['id'], 'status_p113': r['overall_status'], 'codes_p113': sorted({d['code'] for d in r['diagnostics']}),
                     'expected_p114': c['expected_overall']})
    return {'format': 'aiaeao.cube.p1.14-baseline/1', 'note': 'P1.13 on the same inputs with P1.14 fields removed (context /9); before any P1.14 code',
            'rows': rows}


if __name__ == '__main__':
    vec = build()
    (HERE/'fixtures/ho01_ho12_materialized.json').write_text(json.dumps(vec, ensure_ascii=False, indent=1)+'\n', 'utf-8')
    print('materialized', len(vec['cases']))
    if '--baseline' in sys.argv:
        b = baseline(vec)
        (HERE/'fixtures/baseline_p113.json').write_text(json.dumps(b, ensure_ascii=False, indent=1)+'\n', 'utf-8')
        for r in b['rows']:
            print(r['id'], r['status_p113'], r['codes_p113'], '→ P1.14:', r['expected_p114'])
