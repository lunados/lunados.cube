#!/usr/bin/env python3
"""Materialise H-01..H-16 (VP-09.2) from VP09_2_ACCEPTANCE_SPEC.md §5 into explicit vectors.

Expected values are copied from oracles/independent_h01_h16.json (transcribed before code). All names are
synthetic; the base plan is the VP-09.1 plan of materialize_b01_b20.py, read with profile 0.9.2.
"""
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE/'scripts')); sys.dont_write_bytecode = True
import materialize_b01_b20 as B  # noqa: E402

ORACLE = json.loads((HERE/'oracles/independent_h01_h16.json').read_text('utf-8'))
P091, P092 = 'P2-VP-AXES/0.9.1', 'P2-VP-AXES/0.9.2'
LONG = 'tLongtransitionidwithoutanyseparators'+'x'*43


def plan(c):
    return c['migration_plans'][0]


def with_yy():
    c = B.context()
    c['referents'].append(B.ref('archive-box', B.RES))
    plan(c)['dependencies'] += [B.dep('d9', 'support', 'depends-on', 'admin-mailbox', B.ALL),
                                B.dep('d10', 'admin-mailbox', 'recovers-via', 'archive-box', B.ALL)]
    return c


def renamed(new_id):
    c = B.context()
    t = plan(c)['transitions'][0]
    t['transition_id'] = new_id
    return c


def with_hidden_source():
    c = B.context()
    plan(c)['transitions'][0]['methods'].append(B.b('migrate.import/v1', source='old-store', target='new-mail'))
    return c


def with_local():
    c = B.local(B.context())
    plan(c)['transitions'][2]['methods'].append(B.b('acme.archive/v1', arg1='hosting'))
    return c


def out_of_slice_41(n=41):
    c = B.context()
    c['referents'].append(B.ref('archive-job', B.INT))
    for i in range(1, n+1):
        o = f'obj-{i:02d}'
        c['referents'].append(B.ref(o, B.RES))
        plan(c)['dependencies'].append(B.dep(f'ob{i:02d}', 'archive-job', 'depends-on', o, ['p0', 'p1'], dropped=True))
        t = B.tr(f't-obj-{i:02d}', 'p2', [o], [])
        t['methods'] = [B.b('migrate.retire/v1', retired=o)]
        plan(c)['transitions'].append(t)
    return c


def v(op, rows, cols, ctx=None, profile=P092, granularity='standard', **kw):
    d = {'context': ctx or B.context(), 'plan_id': 'mp-axes', 'rows': rows, 'cols': cols, 'granularity': granularity, 'profile': profile}
    d.update(kw)
    return (op, d)


def build():
    x = {}
    x['H-01'] = v('render', 'Y:referent', 'Y:referent', ctx=with_yy())
    x['H-02'] = v('render', 'Y:kind', 'Y:kind', ctx=with_yy())
    x['H-03'] = v('render', 'Y:referent', 'Y:referent', ctx=with_yy(), profile=P091)
    # slice shop, crm-sync: the base plan itself declares Y → Y (support depends-on old-store / new-store), so the case
    # "without any Y → Y dependency" needs a slice without support (corrected before the VP-09.2 code commit; oracle unchanged)
    x['H-04'] = v('render', 'Y:referent', 'Y:referent', hide_empty='both', subjects=['shop', 'crm-sync'])
    x['H-05'] = v('render', 'F', 'T')
    x['H-06'] = v('render', 'F', 'T')
    x['H-07'] = v('render', 'F', 'T', ctx=with_local())
    x['H-08'] = v('render', 'F', 'T', ctx=with_hidden_source(), subjects=['shop', 'crm-sync'])
    x['H-09'] = v('render', 'F', 'Z:referent', hide_empty='cols')
    x['H-10'] = v('panels', 'F', 'Z:referent', ctx=B.context(jobs=17), hide_empty='both')
    x['H-11'] = v('render', 'F', 'Z:referent', ctx=B.context(jobs=17), hide_empty='cols')
    x['H-12'] = v('render', 'F', 'Z:referent', ctx=renamed('transition-legacy-calendar-cutover'))
    x['H-13'] = v('render', 'F', 'Z:referent', ctx=renamed(LONG))
    x['H-14'] = v('render', 'F', 'T', locale='de')
    x['H-15'] = v('render', 'F', 'Z:referent', ctx=out_of_slice_41(), subjects=['shop', 'crm-sync', 'support'])
    x['H-16'] = v('render', 'Q', 'T')
    return x


def main():
    vecs = build()
    exp = {c['id']: c for c in ORACLE['cases']}
    assert set(vecs) == set(exp), 'oracle/vector id mismatch'
    cases = [{'id': k, 'op': vecs[k][0], 'input': vecs[k][1], 'expected_status': exp[k]['expected_status'],
              'required_codes': exp[k]['required_codes'], 'forbidden_codes': exp[k]['forbidden_codes'], 'expect': exp[k]['expect']}
             for k in sorted(vecs)]
    out = {'format': 'aiaeao.cube.vp09-vectors/1', 'reference_version': 'v9.4',
           'source': 'VP09_2_ACCEPTANCE_SPEC.md §5 + oracles/independent_h01_h16.json', 'cases': cases}
    (HERE/'fixtures/h01_h16_materialized.json').write_text(json.dumps(out, ensure_ascii=False, sort_keys=True, indent=1)+'\n', 'utf-8')
    print('wrote', len(cases), 'vectors')


if __name__ == '__main__':
    main()
