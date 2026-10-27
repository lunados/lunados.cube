#!/usr/bin/env python3
"""Build fixtures/golden_v072.json (VP072-06, D-8): synthetic, no client data.

A binding-context/6 plan with 6 declared layers (platform → dns → provider → account → system
→ actor) and 3 declared tracks (shop, crm, files). The dependency inventory is listed against
the layer order (actors first) so that layer ordering is observable. Expected values are
declared by design, not computed here.
"""
import json
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
SCOPE = 'acme:migration'
INT, RES, ACT = 'Z:module-body:integration', 'Y:resource-object:resource', 'Y:identity-anchor:actor'
PRV, DEP = 'Z:module-body:provider', 'Z:module-body:third-party-dependency'
HOME = {INT: 'Z', RES: 'Y', ACT: 'Y', PRV: 'Z', DEP: 'Z'}
ALL = ['p0', 'p1', 'p2', 'p3']


def ref(r, cid):
    return {'ref': r, 'concept_id': cid, 'home': HOME[cid], 'layers': ['α'], 'provenance_status': 'declared_unverified', 'scope_ref': SCOPE}


deps = []


def dep(i, s, pred, o, holds, **kw):
    d = {'dependency_id': i, 'subject': s, 'predicate_id': pred, 'object': o, 'kind': 'job', 'holds_in': holds, 'witness_ref': f'repo:example/{i}'}
    d.update(kw)
    deps.append(d)


REFS = [ref('support-team', ACT), ref('finance-team', ACT), ref('shop', INT), ref('crm-sync', INT), ref('backup-job', INT),
        ref('report-job', INT), ref('invoice-job', INT), ref('admin-mailbox', RES), ref('billing-mailbox', RES), ref('file-share', RES),
        ref('legacy-mail', DEP), ref('new-mail', PRV), ref('legacy-files', DEP), ref('new-files', PRV), ref('dns-zone', DEP),
        ref('mail-dns', DEP), ref('hosting', DEP), ref('cdn', DEP)]
dep('a1', 'support-team', 'depends-on', 'admin-mailbox', ALL)
dep('a2', 'finance-team', 'depends-on', 'billing-mailbox', ALL)
dep('c1', 'crm-sync', 'depends-on', 'admin-mailbox', ALL)
dep('c2', 'crm-sync', 'depends-on', 'mail-dns', ALL)
dep('r1', 'report-job', 'sends-via', 'legacy-mail', ['p0', 'p1'], successor_ref='r2')
dep('r2', 'report-job', 'sends-via', 'new-mail', ['p2', 'p3'])
dep('b1', 'backup-job', 'syncs-with', 'legacy-files', ['p0', 'p1', 'p2'], successor_ref='b2')
dep('b2', 'backup-job', 'syncs-with', 'new-files', ['p3'])
dep('b3', 'backup-job', 'depends-on', 'file-share', ALL)
dep('b4', 'backup-job', 'depends-on', 'cdn', ALL)
dep('i1', 'invoice-job', 'sends-via', 'legacy-mail', ['p0', 'p1'], successor_ref='i2')
dep('i2', 'invoice-job', 'sends-via', 'new-mail', ['p2', 'p3'])
dep('i3', 'invoice-job', 'depends-on', 'billing-mailbox', ALL)
dep('s1', 'shop', 'sends-via', 'legacy-mail', ['p0', 'p1'], successor_ref='s2')
dep('s2', 'shop', 'sends-via', 'new-mail', ['p2', 'p3'])
dep('s3', 'shop', 'depends-on', 'dns-zone', ALL)
dep('s4', 'shop', 'depends-on', 'hosting', ALL)


def tr(i, at, ret, intro):
    return {'transition_id': i, 'at_phase': at, 'retires': ret, 'introduces': intro, 'T': {'role': 'scheduling', 'value': 'TBD'},
            'witness_ref': 'synthetic:contract#scope'}


CTX = {'format': 'aiaeao.cube.binding-context/6', 'reference_version': 'v9.4', 'context_id': 'golden-vp072', 'source_kind': 'illustrative_fixture',
       'scope_ref': SCOPE, 'predicate_profile_refs': ['P1.10/migration-predicates-v1'], 'referents': REFS, 'predicate_contracts': [],
       'migration_plans': [{'plan_id': 'mp-acme', 'revision': 'synthetic:v1', 'scope': SCOPE, 'origin': 'illustrative_fixture',
                            'phases': [{'phase_id': 'p0', 'role': 'current'}, {'phase_id': 'p1', 'role': 'intermediate'},
                                       {'phase_id': 'p2', 'role': 'intermediate'}, {'phase_id': 'p3', 'role': 'target'}],
                            'transitions': [tr('t-intro', 'p1', [], ['new-mail', 'new-files']), tr('t-mail', 'p2', ['legacy-mail'], []),
                                            tr('t-files', 'p3', ['legacy-files'], [])],
                            'dependencies': deps}]}
LAYERS = {'format': 'aiaeao.cube.vp07-layer-map/1', 'layer_order': ['platform', 'dns', 'provider', 'account', 'system', 'actor'],
          'layers': {'platform': ['hosting', 'cdn'], 'dns': ['dns-zone', 'mail-dns'],
                     'provider': ['legacy-mail', 'new-mail', 'legacy-files', 'new-files'],
                     'account': ['admin-mailbox', 'billing-mailbox', 'file-share'],
                     'system': ['shop', 'invoice-job', 'crm-sync', 'report-job', 'backup-job'],
                     'actor': ['finance-team', 'support-team']}}
TRACKS = {'format': 'aiaeao.cube.vp07-track-map/1',
          'tracks': {'shop': ['shop', 'invoice-job', 'finance-team'], 'crm': ['crm-sync', 'report-job', 'support-team'], 'files': ['backup-job']}}
EXPECTED = {
    'dependencies': 17, 'layers': 6, 'tracks': 3,
    'row_order': ['shop', 'invoice-job', 'crm-sync', 'report-job', 'backup-job', 'finance-team', 'support-team'],
    'track_layer_standard': {'outer_values': ['shop', 'crm', 'files'], 'coverage': 'COMPLETE', 'one_layer_per_panel': True},
    'flow_shop_p0': {'order': ['hosting', 'dns-zone', 'legacy-mail', 'shop'], 'caption': ['platform', 'dns', 'provider', 'system']},
    'unassigned': [],
}


def main():
    out = {'format': 'aiaeao.cube.vp072-golden/1', 'reference_version': 'v9.4', 'source': 'synthetic (D-8); no client data',
           'context': CTX, 'tracks': TRACKS, 'layers': LAYERS, 'expected': EXPECTED}
    (HERE/'fixtures/golden_v072.json').write_text(json.dumps(out, ensure_ascii=False, sort_keys=True, indent=1)+'\n', 'utf-8')
    print('wrote golden;', len(deps), 'dependencies')


if __name__ == '__main__':
    main()
