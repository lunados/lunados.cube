#!/usr/bin/env python3
"""Build fixtures/golden_methods_synthetic.json (P1.11-08): synthetic, no client data.

Reuses the synthetic three-workstream plan of the VP-07.1 golden (mail, files, identity; 33
dependencies; four transitions, three of them at p2), maps its display-only predicates to the P1.10
profile predicate depends-on, lifts it to binding-context/7, binds every
transition and every successor-bearing dependency to a catalog method, and declares the one
gap-ending dependency as dropped. GM-pos binds everything consistently; GM-misfit adds one
retire binding on a referent the transition does not retire. Expected values are declared by design.
"""
import copy, json
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]; REPO = HERE.parents[1]
SRC = json.loads((REPO/'P2/visual-printer-migration-v1/fixtures/golden_v071.json').read_text('utf-8'))
TEXT = 'rel("sends-via",Z:α:Integration["acme:mail-job-01"],Z:α:Provider["acme:new-mail"])'


def b(mid, **args):
    return {'method_id': mid, 'arguments': args}


def pos():
    ctx = copy.deepcopy(SRC['context'])
    ctx['format'] = 'aiaeao.cube.binding-context/7'
    ctx['context_id'] = 'golden-p111'
    ctx['method_profile_refs'] = ['P1.11/migration-methods-v1']
    mp = ctx['migration_plans'][0]
    for d in mp['dependencies']:  # the P2 golden uses display-only predicates; P1 needs profile predicates
        if d['predicate_id'] not in ('depends-on', 'sends-via', 'syncs-with'):
            d['predicate_id'] = 'depends-on'
    methods = {
        't-intro-mail': [b('migrate.rebuild/v1', target='acme:new-mail')],
        't-mail-cut': [b('migrate.import/v1', source='acme:legacy-mail', target='acme:new-mail'), b('migrate.retire/v1', retired='acme:legacy-mail')],
        't-files-switch': [b('migrate.import/v1', source='acme:legacy-files', target='acme:new-files'), b('migrate.retire/v1', retired='acme:legacy-files')],
        't-directory-switch': [b('migrate.rebuild/v1', target='acme:new-directory'), b('migrate.retire/v1', retired='acme:legacy-directory')],
    }
    for t in mp['transitions']:
        t['methods'] = methods[t['transition_id']]
    deps = {d['dependency_id']: d for d in mp['dependencies']}
    for d in mp['dependencies']:
        if 'successor_ref' in d:
            d['method'] = b('migrate.rewrite/v1', dependant=d['subject'], new_object=deps[d['successor_ref']]['object'])
        if d['dependency_id'] == 'g01':
            d['dropped'] = True
    return ctx


def misfit():
    ctx = pos()
    t = next(t for t in ctx['migration_plans'][0]['transitions'] if t['transition_id'] == 't-mail-cut')
    t['methods'].append(b('migrate.retire/v1', retired='acme:archive-store'))
    return ctx


CASES = [
    {'id': 'GM-pos', 'description': 'every transition and successor bound consistently; gap declared as dropped',
     'input_text': TEXT, 'input_format': 'acg_text', 'context': pos(), 'expected_overall': 'PASS', 'required_codes': [],
     'expected_bindings': {'transitions': 7, 'dependencies': 16}},
    {'id': 'GM-misfit', 'description': 'GM-pos plus a retire binding on a referent the transition does not retire',
     'input_text': TEXT, 'input_format': 'acg_text', 'context': misfit(), 'expected_overall': 'FAIL',
     'required_codes': ['P1_MIGRATION_METHOD_PLAN'], 'expected_code_count': {'P1_MIGRATION_METHOD_PLAN': 1}},
]


def main():
    out = {'format': 'aiaeao.cube.p1.11-golden/1', 'reference_version': 'v9.4', 'source': 'synthetic (VP-07.1 golden plan); no client data',
           'cases': CASES}
    (HERE/'fixtures/golden_methods_synthetic.json').write_text(json.dumps(out, ensure_ascii=False, indent=1)+'\n', 'utf-8')
    print('wrote', len(CASES), 'golden cases')


if __name__ == '__main__':
    main()
