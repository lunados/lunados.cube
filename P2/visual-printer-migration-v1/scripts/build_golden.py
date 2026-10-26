#!/usr/bin/env python3
"""Build fixtures/golden_migration_views.json (VP07-08, D-8): synthetic, no client data.

A binding-context/5 plan with 31 dependencies, 4 steps and 2 declared tracks. Exactly one
dependency (acme:admin-mailbox recovers-via acme:legacy-mail in p2) is declared to hold
after its object is retired. Expected values are declared by design, not computed here.
"""
import json
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
A, SCOPE = 'α', 'acme:migration'
INT, RES = 'Z:module-body:integration', 'Y:resource-object:resource'
PRV, DEP = 'Z:module-body:provider', 'Z:module-body:third-party-dependency'
HOME = {INT: 'Z', RES: 'Y', PRV: 'Z', DEP: 'Z'}


def ref(r, cid):
    return {'ref': 'acme:'+r, 'concept_id': cid, 'home': HOME[cid], 'layers': [A], 'provenance_status': 'declared_unverified', 'scope_ref': SCOPE}


MAIL = [f'mail-job-{i:02d}' for i in range(1, 9)]
FILES = [f'file-job-{i:02d}' for i in range(1, 8)]
refs = [ref('legacy-mail', DEP), ref('legacy-files', DEP), ref('new-mail', PRV), ref('new-files', PRV), ref('admin-mailbox', RES)]
refs += [ref(s, INT) for s in MAIL+FILES]
deps = []


def dep(i, s, pred, o, holds, kind, witness, **kw):
    d = {'dependency_id': i, 'subject': 'acme:'+s, 'predicate_id': pred, 'object': 'acme:'+o, 'kind': kind, 'holds_in': holds, 'witness_ref': witness}
    d.update(kw)
    deps.append(d)


for n, s in enumerate(MAIL, 1):
    dep(f'm{n:02d}a', s, 'sends-via', 'legacy-mail', ['p0', 'p1'], 'job', f'repo:example/jobs/{s}', successor_ref=f'm{n:02d}b', schedule='every 5m')
    dep(f'm{n:02d}b', s, 'sends-via', 'new-mail', ['p2', 'p3'], 'job', f'plan:mp-acme#m{n:02d}b', schedule='every 5m')
for n, s in enumerate(FILES, 1):
    dep(f'f{n:02d}a', s, 'syncs-with', 'legacy-files', ['p0', 'p1', 'p2'], 'sync', f'repo:example/sync/{s}', successor_ref=f'f{n:02d}b')
    dep(f'f{n:02d}b', s, 'syncs-with', 'new-files', ['p3'], 'sync', f'plan:mp-acme#f{n:02d}b')
dep('x01', 'admin-mailbox', 'recovers-via', 'legacy-mail', ['p0', 'p1', 'p2'], 'account', 'repo:example/accounts/admin')
CTX = {'format': 'aiaeao.cube.binding-context/5', 'reference_version': 'v9.4', 'context_id': 'golden-vp07', 'source_kind': 'illustrative_fixture',
       'scope_ref': SCOPE, 'predicate_profile_refs': ['P1.10/migration-predicates-v1'], 'referents': refs, 'predicate_contracts': [],
       'migration_plans': [{'plan_id': 'mp-acme', 'revision': 'synthetic:v1', 'scope': SCOPE, 'origin': 'illustrative_fixture',
                            'phases': [{'phase_id': 'p0', 'role': 'current'}, {'phase_id': 'p1', 'role': 'intermediate'},
                                       {'phase_id': 'p2', 'role': 'intermediate'}, {'phase_id': 'p3', 'role': 'target'}],
                            'transitions': [
                                {'transition_id': 't-intro', 'at_phase': 'p1', 'retires': [], 'introduces': ['acme:new-mail', 'acme:new-files'],
                                 'T': {'role': 'scheduling', 'value': 'TBD'}, 'witness_ref': 'synthetic:contract#scope'},
                                {'transition_id': 't-mail', 'at_phase': 'p2', 'retires': ['acme:legacy-mail'], 'introduces': [],
                                 'T': {'role': 'scheduling', 'value': 'TBD'}, 'witness_ref': 'synthetic:contract#scope'},
                                {'transition_id': 't-files', 'at_phase': 'p3', 'retires': ['acme:legacy-files'], 'introduces': [],
                                 'T': {'role': 'scheduling', 'value': 'TBD'}, 'witness_ref': 'synthetic:contract#scope'}],
                            'dependencies': deps}]}
TRACKS = {'format': 'aiaeao.cube.vp07-track-map/1',
          'tracks': {'mail': ['acme:'+s for s in MAIL]+['acme:admin-mailbox'], 'files': ['acme:'+s for s in FILES]}}
STYLES = [{'predicate_id': 'sends-via', 'style': 'solid', 'legend': 'sends via'},
          {'predicate_id': 'syncs-with', 'style': 'dashed', 'legend': 'syncs with'},
          {'predicate_id': 'recovers-via', 'style': 'double', 'legend': 'recovers via'}]
PREFIXES = {'format': 'aiaeao.cube.vp07-witness-prefixes/1',
            'prefixes': [{'prefix': 'plan:', 'note': 'planned'}, {'prefix': 'repo:', 'note': 'found in source'}]}
EXPECTED = {
    'dependencies': 31, 'steps': 4, 'tracks': 2,
    'phases_subject_standard': {'panels': 3, 'coverage': 'COMPLETE', 'units': 63},
    'flow_subject_standard_execution': {'coverage': 'COMPLETE', 'units': 63},
    'phases_track_mail_standard_subject': {'panels': 2, 'coverage': 'COMPLETE'},
    'declared_conflicts': [{'cell_id': 'x01', 'kind': 'holds_after_retirement', 'steps': ['p2']}],
    'p1_10_overall': 'FAIL', 'p1_10_code': 'P1_MIGRATION_DANGLING_DEPENDENCY',
}


def main():
    out = {'format': 'aiaeao.cube.vp07-golden/1', 'reference_version': 'v9.4', 'source': 'synthetic (D-8); no client data',
           'context': CTX, 'tracks': TRACKS, 'edge_styles': STYLES, 'witness_prefixes': PREFIXES, 'expected': EXPECTED}
    (HERE/'fixtures/golden_migration_views.json').write_text(json.dumps(out, ensure_ascii=False, sort_keys=True, indent=1)+'\n', 'utf-8')
    print('wrote golden;', len(deps), 'dependencies')


if __name__ == '__main__':
    main()
