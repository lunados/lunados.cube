#!/usr/bin/env python3
"""Materialise N-01..N-14 (VP-07.4) from VP07_4_ACCEPTANCE_SPEC.md §5 into explicit vectors.

Expected values are copied from oracles/independent_n01_n14.json (transcribed before code).
All names are synthetic; the base plan is the VP-07.3 plan of materialize_m01_m12.py. N-06 builds
its 0.7.2 source with the unchanged 0.7.2 code path.
"""
import copy, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE/'scripts')); sys.dont_write_bytecode = True
import materialize_m01_m12 as M  # noqa: E402

ORACLE = json.loads((HERE/'oracles/independent_n01_n14.json').read_text('utf-8'))
P074 = 'P2-VP-MIGRATION/0.7.4'
LOCAL = {'method_id': 'acme.archive/v1', 'revision': 'local', 'scope': M.SCOPE, 'origin': 'illustrative_fixture',
         'argument_min': 1, 'argument_max': 1, 'effect_class': 'pure_declarative'}
PH = lambda part: {'view': 'cube.phases', 'partition': part, 'granularity': 'standard'}  # noqa: E731
FL = lambda part: {'view': 'cube.flow', 'partition': part, 'granularity': 'standard', 'lens': 'cube.lens.execution'}  # noqa: E731


def base():
    c = M.context()
    c['method_contracts'] = [dict(LOCAL)]
    M.plan(c)['dependencies'][3]['method'] = M.b('acme.archive/v1', arg1='admin-mailbox')
    return c


def many_rewrites(n=30):
    c = base()
    p = M.plan(c)
    for i in range(1, n+1):
        j = f'job-{i:02d}'
        c['referents'].append(M.ref(j, M.INT))
        p['dependencies'] += [M.dep(f'jo{i:02d}', j, 'sends-via', 'legacy-mail', ['p0', 'p1'], successor_ref=f'jn{i:02d}',
                                    method=M.b('migrate.rewrite/v1', dependant=j, new_object='new-mail')),
                              M.dep(f'jn{i:02d}', j, 'sends-via', 'new-mail', ['p2', 'p3'])]
    return c


def many_boxes(n=12):
    c = base()
    p = M.plan(c)
    for i in range(1, n+1):
        box = f'box-{i:02d}'
        c['referents'].append(M.ref(box, M.RES))
        p['dependencies'].append(M.dep(f'bx{i:02d}', 'crm-sync', 'depends-on', box, ['p0', 'p1'], dropped=True))
        t = M.tr(f't-box-{i:02d}', 'p2', [box], [])
        t['methods'] = [M.b('migrate.retire/v1', retired=box)]
        p['transitions'].append(t)
    return c


def v(then, ctx=None, profile=None, **kw):
    d = {'context': ctx or base(), 'plan_id': 'mp-methods', 'then': then}
    if profile:
        d['profile'] = profile
    d.update(kw)
    return ('from-plan', d)


def n06_source():
    from vpmigration import from_plan                       # unchanged 0.7.2 code path
    src, _ = from_plan(M.context('/6'), 'mp-methods', layers=M.LAYERS)
    assert src['profile'] == 'P2-VP-MIGRATION/0.7.2'
    return src


def build():
    x = {}
    x['N-01'] = v(PH('method'))
    x['N-02'] = v(PH('method'))
    x['N-03'] = v(PH('method'), ctx=many_rewrites())
    x['N-04'] = v(PH('track,method'), tracks=M.TRACKS)
    x['N-05'] = v(FL('method,subject'))
    x['N-06'] = ('panels', {'source': n06_source(), **PH('method')})
    x['N-07'] = v(FL('subject'), profile=P074)
    x['N-08'] = v(FL('subject'), profile=P074)
    x['N-09'] = v(FL('subject'), profile=P074)
    c = base(); del M.plan(c)['transitions'][2]['methods']
    x['N-10'] = v(FL('subject'), ctx=c, profile=P074)
    x['N-11'] = v(FL('object,subject'), ctx=many_boxes(), profile=P074)  # oracle n11_correction
    x['N-12'] = v(FL('subject'), profile=P074)
    x['N-13'] = v(FL('subject'), profile=P074, tamper='edit_methods_line')
    x['N-14'] = v(FL('subject'), profile=P074, layers=M.LAYERS)
    return x


def main():
    vecs = build()
    exp = {c['id']: c for c in ORACLE['cases']}
    assert set(vecs) == set(exp), 'oracle/vector id mismatch'
    cases = [{'id': k, 'op': vecs[k][0], 'input': vecs[k][1], 'expected_status': exp[k]['expected_status'],
              'required_codes': exp[k]['required_codes'], 'forbidden_codes': exp[k]['forbidden_codes'], 'expect': exp[k]['expect']}
             for k in sorted(vecs)]
    out = {'format': 'aiaeao.cube.vp07-vectors/1', 'reference_version': 'v9.4',
           'source': 'VP07_4_ACCEPTANCE_SPEC.md §5 + oracles/independent_n01_n14.json', 'cases': cases}
    (HERE/'fixtures/n01_n14_materialized.json').write_text(json.dumps(out, ensure_ascii=False, sort_keys=True, indent=1)+'\n', 'utf-8')
    print('wrote', len(cases), 'vectors')


if __name__ == '__main__':
    main()
