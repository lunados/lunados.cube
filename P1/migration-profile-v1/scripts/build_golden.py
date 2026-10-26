#!/usr/bin/env python3
"""Build fixtures/golden_migration_synthetic.json (P1.10-14, D-7).

A synthetic migration plan modelled on the shape of the 2026-10-26 test case
(mail, calendar, file storage, chat; system mailboxes with recovery addresses).
No client names, domains, mailboxes or repository paths. Expected values are
declared by design: the negative control re-introduces the ordering risk
(recovery via the provider retired first) and must FAIL; the corrected variant must PASS.
"""
import copy, json
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
A = 'α'; SCOPE = 'acme:migration'
INT, RES = 'Z:module-body:integration', 'Y:resource-object:resource'
PRV, DEP = 'Z:module-body:provider', 'Z:module-body:third-party-dependency'
HOME = {INT: 'Z', RES: 'Y', PRV: 'Z', DEP: 'Z'}
REFS = {
    'legacy-mail': DEP, 'legacy-system-mail': DEP, 'legacy-calendar': DEP, 'legacy-files': DEP, 'legacy-chat': DEP,
    'new-mail': PRV, 'new-calendar': PRV, 'new-files': PRV, 'new-chat': PRV, 'dns': PRV,
    'contact-form': INT, 'newsletter-job': INT, 'calendar-sync': INT, 'file-sync': INT, 'backup-job': INT,
    'chat-bot': INT, 'website': INT, 'crm-sync': INT,
    'system-mailbox': RES, 'admin-mailbox': RES, 'shared-drive': RES, 'doc-archive': RES,
}
def ref(r): return {'ref': 'acme:' + r, 'concept_id': REFS[r], 'home': HOME[REFS[r]], 'layers': [A],
                    'provenance_status': 'declared_unverified', 'scope_ref': SCOPE}
P = ['p0', 'p1', 'p2']
def dep(i, s, pred, o, holds, kind, **kw):
    d = {'dependency_id': i, 'subject': 'acme:' + s, 'predicate_id': pred, 'object': 'acme:' + o,
         'kind': kind, 'holds_in': holds, 'witness_ref': 'synthetic:inventory#' + i}
    d.update(kw); return d
DEPS = [
    dep('d01', 'contact-form', 'sends-via', 'legacy-system-mail', P[:2], 'job', successor_ref='d01b', schedule='every 1m'),
    dep('d01b', 'contact-form', 'sends-via', 'new-mail', P[2:], 'job', schedule='every 1m'),
    dep('d02', 'newsletter-job', 'sends-via', 'legacy-mail', P[:1], 'job', successor_ref='d02b'),
    dep('d02b', 'newsletter-job', 'sends-via', 'new-mail', P[1:], 'job'),
    dep('d03', 'calendar-sync', 'syncs-with', 'legacy-calendar', P[:1], 'sync', successor_ref='d03b'),
    dep('d03b', 'calendar-sync', 'syncs-with', 'new-calendar', P[1:], 'sync'),
    dep('d04', 'file-sync', 'syncs-with', 'legacy-files', P[:2], 'sync', successor_ref='d04b'),
    dep('d04b', 'file-sync', 'syncs-with', 'new-files', P[2:], 'sync'),
    dep('d05', 'backup-job', 'stores-in', 'legacy-files', P[:2], 'data', dropped=True),
    dep('d06', 'chat-bot', 'depends-on', 'legacy-chat', P[:2], 'api', successor_ref='d06b'),
    dep('d06b', 'chat-bot', 'depends-on', 'new-chat', P[2:], 'api'),
    dep('d07', 'website', 'hosted-by', 'dns', P, 'dns'),
    dep('d08', 'crm-sync', 'depends-on', 'legacy-mail', P[:1], 'api', successor_ref='d08b'),
    dep('d08b', 'crm-sync', 'depends-on', 'new-mail', P[1:], 'api'),
    dep('d09', 'system-mailbox', 'recovers-via', 'legacy-mail', P[:1], 'account', successor_ref='d09b'),
    dep('d09b', 'system-mailbox', 'recovers-via', 'admin-mailbox', P[1:], 'account'),
    dep('d10', 'admin-mailbox', 'stores-in', 'legacy-system-mail', P[:2], 'account', successor_ref='d10b'),
    dep('d10b', 'admin-mailbox', 'stores-in', 'new-mail', P[2:], 'account'),
    dep('d11', 'shared-drive', 'stores-in', 'legacy-files', P[:2], 'data', successor_ref='d11b'),
    dep('d11b', 'shared-drive', 'stores-in', 'new-files', P[2:], 'data'),
    dep('d12', 'doc-archive', 'references', 'legacy-files', P[:2], 'docs', successor_ref='d12b'),
    dep('d12b', 'doc-archive', 'references', 'new-files', P[2:], 'docs'),
    dep('d13', 'website', 'sends-via', 'legacy-mail', P[:1], 'job', successor_ref='d13b'),
    dep('d13b', 'website', 'sends-via', 'new-mail', P[1:], 'job'),
]
def tr(i, at, ret, intro):
    return {'transition_id': i, 'at_phase': at, 'retires': ['acme:' + r for r in ret], 'introduces': ['acme:' + r for r in intro],
            'T': {'role': 'scheduling', 'value': 'TBD'}, 'witness_ref': 'synthetic:contract#scope'}
CTX = {
    'format': 'aiaeao.cube.binding-context/5', 'reference_version': 'v9.4', 'context_id': 'golden-migration-synthetic',
    'source_kind': 'illustrative_fixture', 'scope_ref': SCOPE, 'predicate_profile_refs': ['P1.10/migration-predicates-v1'],
    'referents': [ref(r) for r in REFS], 'predicate_contracts': [],
    'migration_plans': [{'plan_id': 'mp-acme', 'revision': 'synthetic:v1', 'scope': SCOPE, 'origin': 'illustrative_fixture',
        'phases': [{'phase_id': 'p0', 'role': 'current'}, {'phase_id': 'p1', 'role': 'intermediate'}, {'phase_id': 'p2', 'role': 'target'}],
        'transitions': [tr('t-mail', 'p1', ['legacy-mail', 'legacy-calendar'], ['new-mail', 'new-calendar', 'new-files']),
                        tr('t-final', 'p2', ['legacy-system-mail', 'legacy-files', 'legacy-chat'], ['new-chat'])],
        'dependencies': DEPS}]}
TEXT = f'rel("supersedes",Z:{A}:Provider["acme:new-mail"],Z:{A}:ThirdPartyDependency["acme:legacy-mail"]) @T(role="scheduling",witness_ref="synthetic:contract#scope")'
QP = {'format': 'aiaeao.cube.qualifier-profiles/1', 'reference_version': 'v9.4', 'profile_id': 'acme:qualifiers',
      'scope': SCOPE, 'origin': 'illustrative_fixture', 'witness_refs': ['synthetic:contract#scope'],
      'qualifiers': [{'profile_ref': 'acme:T-scheduling/v1', 'coordinate': 'T', 'required_parameters': ['role', 'witness_ref'],
                      'allowed_parameters': ['role', 'witness_ref'], 'allowed_values': {'role': ['scheduling']}, 'requires_witness': True}]}
def main():
    neg = copy.deepcopy(CTX)
    d09 = next(d for d in neg['migration_plans'][0]['dependencies'] if d['dependency_id'] == 'd09')
    d09['holds_in'] = ['p0', 'p1']          # recovery still via the provider retired first
    out = {'format': 'aiaeao.cube.p1.10-golden/1', 'reference_version': 'v9.4',
           'source': 'synthetic (D-7); shape modelled on the 2026-10-26 test case without client data',
           'cases': [
             {'id': 'G-neg', 'description': 'negative control: d09 recovers via acme:legacy-mail in p1, where it is retired',
              'input_text': TEXT, 'input_format': 'acg_text', 'qualification_profiles': QP, 'context': neg,
              'expected_overall': 'FAIL', 'required_codes': ['P1_MIGRATION_DANGLING_DEPENDENCY']},
             {'id': 'G-pos', 'description': 'corrected: recovery moves to acme:admin-mailbox at p1 (d09b)',
              'input_text': TEXT, 'input_format': 'acg_text', 'qualification_profiles': QP, 'context': CTX,
              'expected_overall': 'PASS', 'required_codes': []}]}
    (HERE/'fixtures/golden_migration_synthetic.json').write_text(json.dumps(out, ensure_ascii=False, sort_keys=True, indent=2)+'\n', 'utf-8')
    print('wrote golden;', len(DEPS), 'dependencies')
if __name__ == '__main__': main()
