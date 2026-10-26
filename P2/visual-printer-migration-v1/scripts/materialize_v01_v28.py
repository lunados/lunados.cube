#!/usr/bin/env python3
"""Materialise V-01..V-28 from VP07_ACCEPTANCE_SPEC.md §5 into explicit vectors.

Expected values are NOT computed here: they are copied from the independent oracle
(oracles/independent_v01_v28.json), transcribed before code. All names are synthetic.
Frozen VP-03/VP-06 code is used only to build Path F input jobs.
"""
import copy, hashlib, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]; P2 = HERE.parent; REPO = P2.parent
sys.path[:0] = [str(P2/'visual-printer-release-v1'), str(P2/'visual-printer-2d-lab')]
sys.dont_write_bytecode = True
from vpprint.core import make_job
from vplenses.printer import source_digest
ORACLE = json.loads((HERE/'oracles/independent_v01_v28.json').read_text('utf-8'))
PROFILE = 'P2-VP-MIGRATION/0.7.0'
INT = ('module-bodies.integration', 'form.module-block')
PRV = ('module-bodies.provider', 'form.module-block')
DEP = ('module-bodies.third-party-dependency', 'form.module-block')
RES = ('resource-objects.resource', 'form.resource-card')
STEPS = [{'id': f'p{i}', 'label': f'p{i} · {r}'} for i, r in enumerate(['current', 'intermediate', 'intermediate', 'target'])]


def item(i, kind, label):
    return {'id': i, 'anchor_id': kind[0], 'form_id': kind[1], 'label': label}


def cell(i, row, obj, pred, steps):
    return {'id': i, 'row': row, 'object': obj, 'predicate_id': pred, 'steps': steps, 'declaration_ref': f'fixture:vp07/{i}'}


def tr(i, at, ret, intro):
    return {'id': i, 'at': at, 'retires': ret, 'introduces': intro, 'declaration_ref': f'fixture:vp07/{i}'}


def plan():
    return {'printer_profile': PROFILE, 'reference_version': 'v9.4', 'view': 'cube.phases', 'lens': 'neutral',
            'granularity': 'standard', 'title': 'Outbound mail · steps p0 → p3', 'steps': copy.deepcopy(STEPS),
            'rows': [item('outbox', INT, 'contact outbox')],
            'objects': [item('old', DEP, 'legacy mail service'), item('new', PRV, 'new mail service')],
            'cells': [cell('c1', 'outbox', 'old', 'sends-via', ['p0', 'p1']), cell('c2', 'outbox', 'new', 'sends-via', ['p2', 'p3'])],
            'transitions': [tr('t1', 'p2', ['old'], ['new'])],
            'declaration_status': 'declared_unverified'}


def many_rows(n):
    p = plan()
    p['rows'] = [item(f'r{i}', INT, f'job {i}') for i in range(n)]
    p['cells'] = [cell(f'c{i}', f'r{i}', 'old', 'sends-via', ['p0', 'p1']) for i in range(n)]
    return p


def flow_bundle():
    vp = {'printer_profile': 'P2-VP-VIEWS/0.2.0', 'reference_version': 'v9.4', 'view': 'cube.flow', 'lens': 'neutral',
          'granularity': 'standard', 'title': 'Outbox dependencies', 'subtitle': 'synthetic VP-07 Path F fixture',
          'direction': 'left-to-right',
          'nodes': [item('outbox', INT, 'contact outbox'), item('old', DEP, 'legacy mail service'), item('mbox', RES, 'admin mailbox')],
          'order': ['outbox', 'old', 'mbox'],
          'edges': [{'from': 'outbox', 'to': 'old', 'predicate_id': 'sends-via', 'declaration_ref': 'fixture:vp07/f1',
                     'arrow_anchor_id': 'relation-arrows.reference'},
                    {'from': 'outbox', 'to': 'mbox', 'predicate_id': 'recovers-via', 'declaration_ref': 'fixture:vp07/f2',
                     'arrow_anchor_id': 'relation-arrows.reference'}],
          'declaration_status': 'declared_unverified'}
    return {'format': 'aiaeao.cube.vp03-lens-bundle/1', 'lens_profile': 'P2-VP-LENSES/0.3.0', 'reference_version': 'v9.4',
            'source_view_sha256': source_digest(vp), 'view_plan': vp, 'basis': 'declared_unverified',
            'facet_bindings': [{'lens': 'cube.lens.provenance', 'target_kind': 'edge', 'target_id': 'e1',
                                'declaration_ref': 'fixture:vp07/f1', 'note': 'witness fixture', 'basis': 'declared_unverified'}]}


def envelope(job, styles):
    e = {'format': 'aiaeao.cube.vp07-styled-print/1', 'profile': PROFILE, 'reference_version': 'v9.4', 'job': job}
    if styles is not None:
        e['edge_styles'] = styles
    return e


def source(subjects, cells):
    rows = [item(s, INT, s.replace('-', ' ')) for s in subjects]
    objs = [item('old', DEP, 'legacy service'), item('new', PRV, 'new service'), item('arc', RES, 'archive')]
    return {'format': 'aiaeao.cube.vp07-migration-source/1', 'profile': PROFILE, 'reference_version': 'v9.4',
            'context_id': 'fixture-ctx', 'plan_id': 'mp-fixture', 'source_context_sha256': hashlib.sha256(b'fixture').hexdigest(),
            'title': 'Fixture migration', 'steps': copy.deepcopy(STEPS), 'rows': rows, 'objects': objs, 'cells': cells,
            'transitions': [tr('t1', 'p2', ['old'], ['new'])], 'facet_bindings': [], 'declaration_status': 'declared_unverified'}


def src12():
    cs = []
    for s in ('s1', 's2', 's3', 's4'):
        cs += [cell(f'{s}-a', s, 'old', 'sends-via', ['p0', 'p1']), cell(f'{s}-b', s, 'new', 'sends-via', ['p2', 'p3']),
               cell(f'{s}-c', s, 'arc', 'stores-in', ['p0', 'p1', 'p2', 'p3'])]
    return source(['s1', 's2', 's3', 's4'], cs)


def p110():
    m = {c['id']: c for c in json.loads((REPO/'P1/migration-profile-v1/fixtures/m01_m22_materialized.json').read_text())['cases']}
    g = {c['id']: c for c in json.loads((REPO/'P1/migration-profile-v1/fixtures/golden_migration_synthetic.json').read_text())['cases']}
    return m, g


def rename_ref(ctx, old, new):
    return json.loads(json.dumps(ctx, ensure_ascii=False).replace(f'"{old}"', f'"{new}"'))


def build():
    v = {}
    m, g = p110()
    m01 = m['M-01']['context']
    v['V-01'] = ('phases', {'plan': plan(), 'overflow': 'summarize'})
    p = plan(); p['cells'][0]['steps'] = ['p1', 'p0']; v['V-02'] = ('phases', {'plan': p, 'overflow': 'summarize'})
    p = plan(); p['cells'][0]['steps'] = ['p0', 'p2']; v['V-03'] = ('phases', {'plan': p, 'overflow': 'summarize'})
    p = plan(); p['cells'][1]['object'] = 'ghost'; v['V-04'] = ('phases', {'plan': p, 'overflow': 'summarize'})
    p = plan(); p['cells'][0]['steps'] = ['p0', 'p1', 'p2']; v['V-05'] = ('phases', {'plan': p, 'overflow': 'summarize'})
    v['V-06'] = ('phases', {'plan': many_rows(7), 'overflow': 'reject'})
    v['V-07'] = ('phases', {'plan': many_rows(7), 'overflow': 'summarize'})
    p = plan(); p['steps'] = p['steps'][:1]; p['cells'] = [cell('c1', 'outbox', 'old', 'sends-via', ['p0'])]; p['transitions'] = []
    v['V-08'] = ('phases', {'plan': p, 'overflow': 'summarize'})
    job = make_job(flow_bundle(), 'cube.lens.provenance', 'standard')
    v['V-09'] = ('styled', {'envelope': envelope(job, [{'predicate_id': 'sends-via', 'style': 'solid', 'legend': 'sends via'},
                                                       {'predicate_id': 'recovers-via', 'style': 'dashed', 'legend': 'recovers via'}])})
    v['V-10'] = ('styled', {'envelope': envelope(job, [{'predicate_id': 'sends-via', 'style': 'red', 'legend': 'sends via'}])})
    v['V-11'] = ('styled', {'envelope': envelope(job, [{'predicate_id': 'sends-via', 'style': 'solid', 'legend': 'a'},
                                                       {'predicate_id': 'sends-via', 'style': 'dashed', 'legend': 'b'}])})
    ex = json.loads((P2/'visual-printer-release-v1/examples/flow_provenance_standard.job.json').read_text())
    v['V-12'] = ('styled', {'envelope': envelope(ex, None), 'vp06_svg': 'visual-printer-release-v1/examples/flow_provenance_standard.svg'})
    panels = {'view': 'cube.phases', 'partition': 'subject', 'granularity': 'overview'}
    v['V-13'] = ('panels', {'source': src12(), **panels})
    v['V-14'] = ('panels', {'source': src12(), **panels, 'partition': 'colour'})
    s = src12(); s['cells'][2]['steps'] = ['p0', 'p1']
    s['cells'].insert(1, cell('s1-d', 's1', 'arc', 'references', ['p0', 'p1']))
    v['V-15'] = ('panels', {'source': s, **panels})
    v['V-16'] = ('panels', {'source': src12(), **panels, 'tamper': 'ledger'})
    v['V-17'] = ('from-plan', {'context': m01, 'plan_id': 'mp-1',
                               'then': {'view': 'cube.flow', 'partition': 'step', 'granularity': 'standard', 'lens': 'cube.lens.provenance'}})
    v['V-18'] = ('from-plan', {'context': m['M-20']['context'], 'plan_id': 'mp-1'})
    c = copy.deepcopy(m01); c['referents'][0]['concept_id'] = 'Y:identified-object:annotation'
    v['V-19'] = ('from-plan', {'context': c, 'plan_id': 'mp-1'})
    v['V-20'] = ('from-plan', {'context': g['G-pos']['context'], 'plan_id': 'mp-acme',
                               'then': {'view': 'cube.phases', 'partition': 'subject', 'granularity': 'standard'}})
    p = plan(); p['cells'][1]['steps'] = ['p1', 'p2', 'p3']; v['V-21'] = ('phases', {'plan': p, 'overflow': 'summarize'})
    p = plan(); p['objects'] += [item(f'o{i}', RES, f'object {i}') for i in (3, 4, 5)]
    p['cells'] += [cell(f'c{i}', 'outbox', f'o{i}', 'stores-in', ['p0', 'p1']) for i in (3, 4, 5)]
    v['V-22'] = ('phases', {'plan': p, 'overflow': 'reject'})
    p = plan(); p['lens'] = 'cube.lens.execution'; v['V-23'] = ('phases', {'plan': p, 'overflow': 'summarize'})
    v['V-24'] = ('panels', {'source': ex, **panels})
    v['V-25'] = ('panels', {'source': src12(), **panels, 'tamper': 'svg'})
    v['V-26'] = ('styled', {'envelope': envelope(ex, [{'predicate_id': 'references', 'style': 'dashed', 'legend': 'references'}]),
                            'vp06_svg': 'visual-printer-release-v1/examples/flow_provenance_standard.svg'})
    v['V-27'] = ('from-plan', {'context': rename_ref(m01, 'job', 'contact job'), 'plan_id': 'mp-1'})
    v['V-28'] = ('from-plan', {'context': m01, 'plan_id': 'mp-1', 'track': 'a',
                               'tracks': {'format': 'aiaeao.cube.vp07-track-map/1', 'tracks': {'a': ['job'], 'b': ['job']}}})
    return v


def main():
    vecs = build()
    exp = {c['id']: c for c in ORACLE['cases']}
    assert set(vecs) == set(exp), 'oracle/vector id mismatch'
    cases = [{'id': k, 'op': vecs[k][0], 'input': vecs[k][1], 'expected_status': exp[k]['expected_status'],
              'required_codes': exp[k]['required_codes'], 'expect': exp[k]['expect']} for k in sorted(vecs)]
    out = {'format': 'aiaeao.cube.vp07-vectors/1', 'reference_version': 'v9.4',
           'source': 'VP07_ACCEPTANCE_SPEC.md §5 + oracles/independent_v01_v28.json', 'cases': cases}
    (HERE/'fixtures/v01_v28_materialized.json').write_text(json.dumps(out, ensure_ascii=False, sort_keys=True, indent=1)+'\n', 'utf-8')
    print('wrote', len(cases), 'vectors')


if __name__ == '__main__':
    main()
