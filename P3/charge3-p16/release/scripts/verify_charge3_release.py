#!/usr/bin/env python3
"""Charge 3 evidence integrity and local-source consistency. Read-only; no remote calls."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
RELEASE = REPO / 'P3/charge3-p16/release'
MANIFEST = RELEASE / 'CHARGE3_EVIDENCE_MANIFEST.json'


def fail(message):
    raise SystemExit('FAIL: CHARGE 3 RELEASE EVIDENCE: ' + message)


def get_bytes(rel):
    # All paths come from this package's manifest, but reject traversal nevertheless.
    if not isinstance(rel, str) or rel.startswith('/') or '..' in Path(rel).parts:
        fail('unsafe manifest path')
    p = (REPO / rel).resolve()
    if not p.is_relative_to(REPO.resolve()) or not p.is_file():
        fail('missing/disallowed file: ' + rel)
    return p.read_bytes()


def get_json(rel):
    try:
        return json.loads(get_bytes(rel))
    except (UnicodeDecodeError, ValueError) as exc:
        fail('invalid JSON: ' + rel + ' (' + type(exc).__name__ + ')')


def sha(value):
    return hashlib.sha256(value).hexdigest()


def canonical_json_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode('utf-8')


def main():
    manifest = get_json('P3/charge3-p16/release/CHARGE3_EVIDENCE_MANIFEST.json')
    if manifest.get('format') != 'aiaeao.cube.p16.charge3-release-evidence/1':
        fail('unexpected evidence format')
    if manifest.get('production_authorized') is not False:
        fail('production boundary not preserved')
    for record in manifest['artifacts']:
        raw = get_bytes(record['path'])
        if sha(raw) != record['sha256'] or len(raw) != record['bytes']:
            fail('sha256/size mismatch: ' + record['path'])
    refs = {a['role']: a['path'] for a in manifest['artifacts']}
    fixture = get_json(refs['p16_fixture'])
    remote = get_json(refs['p16_remote_sdk'])
    r3 = get_json(refs['g5_r3_remote_sdk'])
    report = get_bytes(refs['g5_r4_host_report']).decode('utf-8')
    assert fixture['format'] == 'aiaeao.cube.p16.charge3.materialized-vectors/1', 'fixture format'
    if remote.get('format') != 'aiaeao.cube.p16.charge3-remote-acceptance/1' or remote.get('status') != 'PASS':
        fail('P1.6 remote acceptance invalid')
    if remote.get('fixtures_sha256') != sha(get_bytes(refs['p16_fixture'])):
        fail('SDK P1.6 reference fixture digest mismatch')
    cases = {v['id']: v for v in fixture['cases']}
    results = {v['id']: v for v in remote['p16_vectors']}
    expected_ids = {'R-%02d' % i for i in range(1, 14)}
    if set(cases) != expected_ids or set(results) != expected_ids or len(remote['p16_vectors']) != 13:
        fail('R-01..R-13 coverage mismatch')
    for label, case in cases.items():
        observed = results[label]
        if observed['status'] != case['expected_overall']:
            fail('status mismatch at ' + label)
        if not set(case['required_codes']).issubset(set(observed['codes_present'])):
            fail('required diagnostics missing at ' + label)
    if remote.get('tools_count') != 7 or remote.get('resource_count') != 14:
        fail('remote P1.6 surface counts')
    if any(remote.get(k) is not False for k in ('production_authorized',
            'epistemic_warrant_evaluated', 'current_authority_evaluated',
            'canonical_admission_evaluated')):
        fail('P1.6 scope and non-promotion')
    if not remote.get('config_error_is_mcp_error'):
        fail('config error boundary')
    if r3.get('format') != 'aiaeao.cube.g5-r3-remote-check/1' or r3.get('status') != 'PASS':
        fail('G5 R3 evidence invalid')
    for k in ('auth_wrong_token_rejected', 'wrong_origin_rejected',
              'remote_discovery', 'repeated_svg_matches_exact_bytes',
              'resource_mime_matches_p0_lock', 'p1_invalid_config_is_mcp_error',
              'svg_matches_local_golden_bytes'):
        if r3.get(k) is not True:
            fail('G5 R3 flag: ' + k)
    if (r3.get('tools_count'), r3.get('resources_count')) != (7,14) or \
            set(r3.get('p1_semantic_statuses',[])) != {'PASS','FAIL','UNRESOLVED'}:
        fail('G5 R3 surface or semantic statuses')
    if r3.get('profile') != 'P3-MCP-REMOTE/0.1.0-proof':
        fail('G5 R3 remote profile')
    if '**Gesamtstatus: PASS**' not in report or 'G5_PROOF_NOT_PRODUCTION_AUTHORIZED' not in report:
        fail('R4 attestation/status not present')
    if '## 7. Abweichungen und Hinweise' not in report or 'Aufrufe 12–14' not in report:
        fail('R4 report lacks independent-host scope constraints')
    for label in ('R-01','R-04','R-12'):
        row = next((s for s in report.splitlines() if s.startswith('| '+label+' |')), None)
        if row is None:
            fail('R4 case missing: ' + label)
        case = cases[label]
        digest = sha(canonical_json_bytes(case['context']))
        if (case['expected_overall'] not in row or digest not in row or
                any(code not in row for code in case['required_codes'])):
            fail('R4 reported fixture row discrepancy: ' + label)
    if sha(get_bytes(refs['p0_lock'])) != manifest['cross_checks']['p0_snapshot_lock_sha256']:
        fail('P0 reference lock')
    svg = get_bytes(refs['p2_golden_svg'])
    if sha(svg) != manifest['cross_checks']['r4_svg_golden_sha256'] or \
            not any(t in report for t in (str(len(svg)), f'{len(svg):,}'.replace(',', '.'))) or sha(svg) not in report:
        fail('R4 SVG local golden cross-check')
    if (manifest['cross_checks']['r3_svg_sha256'] != r3['svg_sha256_client_computed'] or
            manifest['cross_checks']['r4_svg_golden_sha256'] == r3['svg_sha256_client_computed']):
        fail('R3/R4 distinct fixture distinction')
    print('PASS: CHARGE 3 RELEASE EVIDENCE: SHA-256, R3, R01–R13, R4, source cross-checks '
          '(NO live MCP, NO production approval)')


if __name__ == '__main__':
    main()
