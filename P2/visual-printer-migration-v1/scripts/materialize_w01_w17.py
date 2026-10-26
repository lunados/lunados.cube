#!/usr/bin/env python3
"""Materialise W-01..W-17 from VP07_1_ACCEPTANCE_SPEC.md §5 into explicit vectors.

Expected values are copied from oracles/independent_w01_w17.json (transcribed before code).
All names are synthetic.
"""
import copy, hashlib, json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]; REPO = HERE.parents[1]
ORACLE = json.loads((HERE/'oracles/independent_w01_w17.json').read_text('utf-8'))
P071 = 'P2-VP-MIGRATION/0.7.1'
INT = ('module-bodies.integration', 'form.module-block')
PRV = ('module-bodies.provider', 'form.module-block')
DEP = ('module-bodies.third-party-dependency', 'form.module-block')
RES = ('resource-objects.resource', 'form.resource-card')
STEPS = [{'id': f'p{i}', 'label': f'p{i} · {r}'} for i, r in enumerate(['current', 'intermediate', 'intermediate', 'target'])]


def item(i, kind, label, **kw):
    d = {'id': i, 'anchor_id': kind[0], 'form_id': kind[1], 'label': label}
    d.update(kw)
    return d


def cell(i, row, obj, pred, steps, **kw):
    d = {'id': i, 'row': row, 'object': obj, 'predicate_id': pred, 'steps': steps, 'declaration_ref': f'fixture:vp071/{i}'}
    d.update(kw)
    return d


def tr(i, at, ret, intro):
    return {'id': i, 'at': at, 'retires': ret, 'introduces': intro, 'declaration_ref': f'fixture:vp071/{i}'}


def plan(**kw):
    p = {'printer_profile': P071, 'reference_version': 'v9.4', 'view': 'cube.phases', 'lens': 'neutral', 'granularity': 'standard',
         'title': 'Outbound mail · 0.7.1', 'steps': copy.deepcopy(STEPS),
         'rows': [item('outbox', INT, 'contact outbox')],
         'objects': [item('old', DEP, 'legacy mail service'), item('new', PRV, 'new mail service')],
         'cells': [cell('c1', 'outbox', 'old', 'sends-via', ['p0', 'p1']), cell('c2', 'outbox', 'new', 'sends-via', ['p2', 'p3'])],
         'transitions': [tr('t1', 'p2', ['old'], ['new'])], 'declaration_status': 'declared_unverified'}
    p.update(kw)
    return p


def source(tracks, cells_per_row=2, transitions=None):
    rows, cells = [], []
    for track, names in tracks.items():
        for n in names:
            rows.append(item(n, INT, n.replace('-', ' '), **({'track': track} if track else {})))
            cells.append(cell(f'{n}-a', n, 'old', 'sends-via', ['p0', 'p1']))
            if cells_per_row > 1:
                cells.append(cell(f'{n}-b', n, 'new', 'sends-via', ['p2', 'p3']))
    return {'format': 'aiaeao.cube.vp07-migration-source/1', 'profile': P071, 'reference_version': 'v9.4',
            'context_id': 'fixture-ctx', 'plan_id': 'mp-fixture', 'source_context_sha256': hashlib.sha256(b'fixture').hexdigest(),
            'title': 'Fixture migration 0.7.1', 'steps': copy.deepcopy(STEPS), 'target_step': 'p3', 'rows': rows,
            'objects': [item('old', DEP, 'legacy service'), item('new', PRV, 'new service')] if cells_per_row > 1 else [item('old', DEP, 'legacy service')],
            'cells': cells, 'transitions': transitions if transitions is not None else [dict(tr('t1', 'p2', ['old'], ['new']), code='T1')],
            'facet_bindings': [], 'declaration_status': 'declared_unverified'}


def build():
    v = {}
    two = {'mail': ['mail-1', 'mail-2', 'mail-3'], 'files': ['file-1', 'file-2']}
    nested = {'view': 'cube.phases', 'partition': 'track,subject', 'granularity': 'standard'}
    v['W-01'] = ('panels', {'source': source(two), **nested})
    v['W-02'] = ('panels', {'source': source({'mail': [f'mail-{i}' for i in range(1, 10)], 'files': ['file-1', 'file-2']}, 1,
                                             [dict(tr('t1', 'p2', ['old'], []), code='T1')]), **nested})
    v['W-03'] = ('panels', {'source': source(two), **nested, 'partition': 'track,subject,object'})
    v['W-04'] = ('panels', {'source': source(two), **nested, 'partition': 'subject,subject'})
    s = source(two); del s['rows'][0]['track']
    v['W-05'] = ('panels', {'source': s, **nested})
    v['W-06'] = ('panels', {'source': source(two), **nested, 'tamper': 'outer_ledger'})
    v['W-07'] = ('phases', {'plan': plan(transitions=[tr('transition-team-mail-cut', 'p2', ['old'], ['new'])])})
    v['W-08'] = ('phases', {'plan': plan(transitions=[tr('t-ret', 'p2', ['old'], []), tr('t-intro', 'p2', [], ['new'])])})
    v['W-09'] = ('phases', {'plan': plan()})
    s = source({'': ['s1', 's2', 's3']})
    s['objects'].append(item('arc', RES, 'archive'))
    s['cells'].append(cell('s1-c', 's1', 'arc', 'stores-in', ['p1', 'p2', 'p3']))
    s['transitions'] = [dict(tr('t-a', 'p1', [], ['arc']), code='T1'), dict(tr('t-x', 'p2', ['old'], ['new']), code='T2')]
    v['W-10'] = ('panels', {'source': s, 'view': 'cube.phases', 'partition': 'subject', 'granularity': 'overview'})
    p = plan()
    p['objects'] += [item(f'o{i}', RES, f'object {i}') for i in range(1, 6)]
    p['cells'] += [cell(f'k{i}', 'outbox', f'o{i}', 'stores-in', ['p0', 'p1']) for i in range(1, 6)]
    p['granularity'] = 'detail'
    p['rows'] += [item(f'r{i}', INT, f'job {i}') for i in range(1, 6)]
    for i in range(1, 6):
        p['cells'][-6+i]['row'] = f'r{i}'
    p['transitions'] = [tr(f't{i}', 'p2', [f'o{i}'], []) for i in range(1, 6)]
    v['W-11'] = ('phases', {'plan': p})
    p = plan(); p['cells'][0]['steps'] = ['p0', 'p1', 'p2']; p['cells'][1]['steps'] = ['p1', 'p2', 'p3']
    v['W-12'] = ('phases', {'plan': p})
    v['W-13'] = ('phases', {'plan': plan(transitions=[tr('t1', 'p2', [], ['new'])])})
    p = plan(transitions=[tr('t1', 'p2', [], ['new'])]); p['cells'][0]['dropped'] = True
    v['W-14'] = ('phases', {'plan': p})
    v['W-15'] = ('phases', {'plan': plan()})
    g = {c['id']: c for c in json.loads((REPO/'P1/migration-profile-v2/fixtures/g01_g10_materialized.json').read_text('utf-8'))['cases']}
    v['W-16'] = ('from-plan', {'context': g['G-01']['context'], 'plan_id': 'mp-acme', 'steps': 'p0:p1',
                               'then': {'view': 'cube.phases', 'partition': 'subject', 'granularity': 'standard'}})
    vec = {c['id']: c for c in json.loads((HERE/'fixtures/v01_v28_materialized.json').read_text('utf-8'))['cases']}
    v['W-17'] = ('panels', {'source': vec['V-13']['input']['source'], 'view': 'cube.phases', 'partition': 'subject', 'granularity': 'overview'})
    return v


def main():
    vecs = build()
    exp = {c['id']: c for c in ORACLE['cases']}
    assert set(vecs) == set(exp), 'oracle/vector id mismatch'
    cases = [{'id': k, 'op': vecs[k][0], 'input': vecs[k][1], 'expected_status': exp[k]['expected_status'],
              'required_codes': exp[k]['required_codes'], 'forbidden_codes': exp[k]['forbidden_codes'], 'expect': exp[k]['expect']}
             for k in sorted(vecs)]
    out = {'format': 'aiaeao.cube.vp07.1-vectors/1', 'reference_version': 'v9.4',
           'source': 'VP07_1_ACCEPTANCE_SPEC.md §5 + oracles/independent_w01_w17.json', 'cases': cases}
    (HERE/'fixtures/w01_w17_materialized.json').write_text(json.dumps(out, ensure_ascii=False, sort_keys=True, indent=1)+'\n', 'utf-8')
    print('wrote', len(cases), 'vectors')


if __name__ == '__main__':
    main()
