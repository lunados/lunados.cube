#!/usr/bin/env python3
"""Check KF-01..KF-09 against the independent oracle."""
import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parents[1]
for path in ('semantic-validator-v1', 'instantiation-profile-v1', 'simulation-profile-v1',
             'comparison-profile-v1', 'migration-profile-v1', 'migration-profile-v2',
             'migration-methods-v1', 'coverage-instance-profile-v1', 'control-flow-profile-v1'):
    sys.path.insert(0, str(REPO / 'P1' / path))
sys.dont_write_bytecode = True
from cube_p113.validator import P113Validator  # noqa: E402

VEC = json.loads((HERE / 'fixtures/kf01_kf09_materialized.json').read_text('utf-8'))['cases']
ORACLE = {c['id']: c for c in json.loads((HERE / 'oracles/independent_kf01_kf09.json').read_text('utf-8'))['cases']}
NOPROMO = ('epistemic_warrant', 'current_authority', 'canonical_admission')


def run(case):
    try:
        return P113Validator().validate_bytes(case['input_text'].encode(), input_format=case['input_format'],
                                              context=case['context'])
    except (ValueError, KeyError, TypeError) as exc:
        return {'overall_status': 'MCP_ERROR', 'diagnostics': [{'code': 'P1_MCP_CONFIG_INVALID'}], '_err': str(exc)}


def main():
    assert {c['id'] for c in VEC} == set(ORACLE), 'vector/oracle ID mismatch'
    failed = 0
    for case in VEC:
        expected = ORACLE[case['id']]
        assert (case['expected_overall'], case['required_codes'], case['forbidden_codes']) == (
            expected['expected_overall'], expected['required_codes'], expected['forbidden_codes'])
        report = run(copy.deepcopy(case))
        codes = [d['code'] for d in report.get('diagnostics', [])]
        ok = (report['overall_status'] == expected['expected_overall'] and
              all(code in codes for code in expected['required_codes']) and
              not any(code in codes for code in expected['forbidden_codes']))
        if report['overall_status'] != 'MCP_ERROR':
            ok = ok and all(report[key] == 'NOT_EVALUATED' for key in NOPROMO)
        failed += not ok
        print('PASS' if ok else 'FAIL', case['id'], 'expected', expected['expected_overall'],
              expected['required_codes'], '| got', report['overall_status'], codes, report.get('_err', ''))
    print(f'{len(VEC) - failed}/{len(VEC)} match')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
