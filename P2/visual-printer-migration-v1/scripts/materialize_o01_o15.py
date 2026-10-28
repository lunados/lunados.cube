#!/usr/bin/env python3
"""Materialise O-01..O-15 (VP-07.5) from VP07_5_ACCEPTANCE_SPEC.md §5 into explicit vectors.

Expected values are copied from oracles/independent_o01_o15.json (transcribed before code). All names are
synthetic; the base plan is the VP-07.3 plan of materialize_m01_m12.py, printed with profile 0.7.5. O-03 adds a
dependency with a local predicate the locale does not know (not a P1.10 predicate; O-03 is not run through P1).
O-08 builds its 0.7.4 source with the unchanged code path.
"""
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE/'scripts')); sys.dont_write_bytecode = True
import materialize_m01_m12 as M  # noqa: E402

ORACLE = json.loads((HERE/'oracles/independent_o01_o15.json').read_text('utf-8'))
P074, P075 = 'P2-VP-MIGRATION/0.7.4', 'P2-VP-MIGRATION/0.7.5'
PH = lambda part='subject', **k: {'view': 'cube.phases', 'partition': part, 'granularity': 'standard', **k}  # noqa: E731
FL = lambda part='subject', **k: {'view': 'cube.flow', 'partition': part, 'granularity': 'standard', 'lens': 'cube.lens.execution', **k}  # noqa: E731


def many_import_bars(n=30):
    c = M.context()
    p = M.plan(c)
    for i in range(1, n+1):
        j = f'job-{i:02d}'
        c['referents'].append(M.ref(j, M.INT))
        p['dependencies'] += [M.dep(f'jo{i:02d}', j, 'sends-via', 'legacy-mail', ['p0', 'p1'], successor_ref=f'jn{i:02d}'),
                              M.dep(f'jn{i:02d}', j, 'sends-via', 'new-mail', ['p2', 'p3'])]
    return c


def hidden_41(n=41):
    c = M.context()
    p = M.plan(c)
    for i in range(1, n+1):
        box, src = f'box-{i:02d}', f'src-{i:02d}'
        c['referents'] += [M.ref(box, M.RES), M.ref(src, M.RES)]
        p['dependencies'].append(M.dep(f'bx{i:02d}', 'crm-sync', 'depends-on', box, ['p2', 'p3']))
        t = M.tr(f't-new-{i:02d}', 'p2', [], [box])
        t['methods'] = [M.b('migrate.import/v1', source=src, target=box)]
        p['transitions'].append(t)
    return c


def with_unknown_predicate():
    c = M.context()
    M.plan(c)['dependencies'].append(M.dep('d9', 'shop', 'acme-mirrors-to', 'hosting', M.ALL))
    return c


def v(then, ctx=None, profile=P075, **kw):
    d = {'context': ctx or M.context(), 'plan_id': 'mp-methods', 'profile': profile, 'then': then}
    d.update(kw)
    return ('from-plan', d)


def o08_source():
    from vpmigration import from_plan                       # unchanged 0.7.4 code path
    src, _ = from_plan(M.context(), 'mp-methods', profile=P074)
    assert src['profile'] == P074
    return src


def build():
    x = {}
    x['O-01'] = v(PH(locale='de'))
    x['O-02'] = v(PH(locale='de'))
    x['O-03'] = v(PH(locale='de'), ctx=with_unknown_predicate())
    x['O-04'] = v(PH(locale='en'))
    x['O-05'] = v(PH(locale='xx'))
    x['O-06'] = v(PH(hide_ledger=True), flow=FL(hide_ledger=True))
    x['O-07'] = v(PH(hide_ledger=True, locale='de'))
    x['O-08'] = ('panels', {'source': o08_source(), **PH(hide_ledger=True)})
    x['O-09'] = v(PH('method-sets'))
    x['O-10'] = v(PH('method-sets'))
    x['O-11'] = v(PH('method-sets'))
    x['O-12'] = v(PH('method-sets'))
    x['O-13'] = v(PH('method-sets'), ctx=many_import_bars())
    x['O-14'] = v(FL('object'), ctx=hidden_41(), subjects=['crm-sync'])
    x['O-15'] = v(PH('banana'))
    return x


def main():
    vecs = build()
    exp = {c['id']: c for c in ORACLE['cases']}
    assert set(vecs) == set(exp), 'oracle/vector id mismatch'
    cases = [{'id': k, 'op': vecs[k][0], 'input': vecs[k][1], 'expected_status': exp[k]['expected_status'],
              'required_codes': exp[k]['required_codes'], 'forbidden_codes': exp[k]['forbidden_codes'], 'expect': exp[k]['expect']}
             for k in sorted(vecs)]
    out = {'format': 'aiaeao.cube.vp07-vectors/1', 'reference_version': 'v9.4',
           'source': 'VP07_5_ACCEPTANCE_SPEC.md §5 + oracles/independent_o01_o15.json', 'cases': cases}
    (HERE/'fixtures/o01_o15_materialized.json').write_text(json.dumps(out, ensure_ascii=False, sort_keys=True, indent=1)+'\n', 'utf-8')
    print('wrote', len(cases), 'vectors')


if __name__ == '__main__':
    main()
