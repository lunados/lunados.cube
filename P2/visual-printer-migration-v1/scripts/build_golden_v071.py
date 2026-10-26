#!/usr/bin/env python3
"""Build fixtures/golden_v071.json (VP071-07, D-8): synthetic, no client data.

A binding-context/6 plan with three declared workstreams modelled on the field test:
mail (9 subjects), files (4 subjects), identity (3 subjects); 4 steps p0..p3; one step
boundary (p2) with three transitions; exactly one dependency (g01: mail-job-09 archives-to
archive-store, ends at p1, never retired, no successor, no drop, no end reason) is a
declared gap. Expected values are declared by design, not computed here.
"""
import json
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
A, SCOPE = 'α', 'acme:migration'
INT, RES = 'Z:module-body:integration', 'Y:resource-object:resource'
PRV, DEP = 'Z:module-body:provider', 'Z:module-body:third-party-dependency'
HOME = {INT: 'Z', RES: 'Y', PRV: 'Z', DEP: 'Z'}
W = 'synthetic:contract#scope'


def ref(r, cid):
    return {'ref': 'acme:'+r, 'concept_id': cid, 'home': HOME[cid], 'layers': [A], 'provenance_status': 'declared_unverified', 'scope_ref': SCOPE}


MAIL = [f'mail-job-{i:02d}' for i in range(1, 10)]
FILES = [f'file-job-{i:02d}' for i in range(1, 5)]
IDENT = [f'account-{i:02d}' for i in range(1, 4)]
refs = [ref('legacy-mail', DEP), ref('new-mail', PRV), ref('legacy-files', DEP), ref('new-files', PRV),
        ref('legacy-directory', DEP), ref('new-directory', PRV), ref('archive-store', RES)]
refs += [ref(s, INT) for s in MAIL+FILES+IDENT]
deps = []


def dep(i, s, pred, o, holds, kind, witness, **kw):
    d = {'dependency_id': i, 'subject': 'acme:'+s, 'predicate_id': pred, 'object': 'acme:'+o, 'kind': kind, 'holds_in': holds, 'witness_ref': witness}
    d.update(kw)
    deps.append(d)


for prefix, subjects, pred, old, new in (('m', MAIL, 'sends-via', 'legacy-mail', 'new-mail'),
                                         ('f', FILES, 'syncs-with', 'legacy-files', 'new-files'),
                                         ('a', IDENT, 'signs-in-via', 'legacy-directory', 'new-directory')):
    for n, s in enumerate(subjects, 1):
        dep(f'{prefix}{n:02d}a', s, pred, old, ['p0', 'p1'], 'job', f'repo:example/{s}', successor_ref=f'{prefix}{n:02d}b')
        dep(f'{prefix}{n:02d}b', s, pred, new, ['p2', 'p3'], 'job', f'plan:mp-acme#{prefix}{n:02d}b')
dep('g01', 'mail-job-09', 'archives-to', 'archive-store', ['p0', 'p1'], 'job', 'repo:example/mail-job-09/archive')


def tr(i, at, ret, intro):
    return {'transition_id': i, 'at_phase': at, 'retires': ['acme:'+x for x in ret], 'introduces': ['acme:'+x for x in intro],
            'T': {'role': 'scheduling', 'value': 'TBD'}, 'witness_ref': W}


CTX = {'format': 'aiaeao.cube.binding-context/6', 'reference_version': 'v9.4', 'context_id': 'golden-vp071', 'source_kind': 'illustrative_fixture',
       'scope_ref': SCOPE, 'predicate_profile_refs': ['P1.10/migration-predicates-v1'], 'referents': refs, 'predicate_contracts': [],
       'migration_plans': [{'plan_id': 'mp-acme', 'revision': 'synthetic:v1', 'scope': SCOPE, 'origin': 'illustrative_fixture',
                            'phases': [{'phase_id': 'p0', 'role': 'current'}, {'phase_id': 'p1', 'role': 'intermediate'},
                                       {'phase_id': 'p2', 'role': 'intermediate'}, {'phase_id': 'p3', 'role': 'target'}],
                            'transitions': [tr('t-intro-mail', 'p1', [], ['new-mail']),
                                            tr('t-mail-cut', 'p2', ['legacy-mail'], []),
                                            tr('t-files-switch', 'p2', ['legacy-files'], ['new-files']),
                                            tr('t-directory-switch', 'p2', ['legacy-directory'], ['new-directory'])],
                            'dependencies': deps}]}
TRACKS = {'format': 'aiaeao.cube.vp07-track-map/1',
          'tracks': {'mail': ['acme:'+s for s in MAIL], 'files': ['acme:'+s for s in FILES], 'identity': ['acme:'+s for s in IDENT]}}
P1_INPUT = 'rel("supersedes",Z:α:Provider["acme:new-mail"],Z:α:ThirdPartyDependency["acme:legacy-mail"]) @T(role="scheduling",witness_ref="'+W+'")'
EXPECTED = {
    'dependencies': 33, 'steps': 4, 'tracks': 3, 'units': 66,
    'phases_track_subject_standard': {'outer_panels': {'mail': 2, 'files': 1, 'identity': 1}, 'coverage': 'COMPLETE'},
    'boundary_p2_transitions': ['t-mail-cut', 't-files-switch', 't-directory-switch'],
    'transition_codes': {'t-intro-mail': 'T1', 't-mail-cut': 'T2', 't-files-switch': 'T3', 't-directory-switch': 'T4'},
    'declared_gaps': ['g01'],
    'p1_10_1_code': 'P1_MIGRATION_DEPENDENCY_GAP', 'p1_10_1_gap_pointer': '/migration_plans/0/dependencies/32',
}


def main():
    out = {'format': 'aiaeao.cube.vp071-golden/1', 'reference_version': 'v9.4', 'source': 'synthetic (D-8); no client data',
           'context': CTX, 'tracks': TRACKS, 'p1_input_text': P1_INPUT, 'expected': EXPECTED}
    (HERE/'fixtures/golden_v071.json').write_text(json.dumps(out, ensure_ascii=False, sort_keys=True, indent=1)+'\n', 'utf-8')
    print('wrote golden;', len(deps), 'dependencies')


if __name__ == '__main__':
    main()
