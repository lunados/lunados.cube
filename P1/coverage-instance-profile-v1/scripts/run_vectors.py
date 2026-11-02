#!/usr/bin/env python3
"""Run K-01..K-21 against the P1.12 validator. Exit 0 only if every case matches the independent oracle."""
import copy, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]; REPO = HERE.parents[1]
for p in ('P1/semantic-validator-v1', 'P1/instantiation-profile-v1', 'P1/simulation-profile-v1', 'P1/comparison-profile-v1',
          'P1/migration-profile-v1', 'P1/migration-profile-v2', 'P1/migration-methods-v1', 'P1/coverage-instance-profile-v1'):
    sys.path.insert(0, str(REPO/p))
sys.dont_write_bytecode = True
from cube_p112.validator import P112Validator  # noqa: E402

VEC = json.loads((HERE/'fixtures/k01_k21_materialized.json').read_text('utf-8'))['cases']
ORACLE = {c['id']: c for c in json.loads((HERE/'oracles/independent_k01_k21.json').read_text('utf-8'))['cases']}
NOPROMO = ('epistemic_warrant', 'current_authority', 'canonical_admission')


def run(c):
    try:
        return P112Validator().validate_bytes(c['input_text'].encode(), input_format=c['input_format'], context=c['context'],
                                              qualification_profiles=c.get('qualification_profiles'))
    except (ValueError, KeyError, TypeError) as e:
        return {'overall_status': 'MCP_ERROR', 'diagnostics': [{'code': 'P1_MCP_CONFIG_INVALID'}], '_err': str(e)}


def main():
    assert {c['id'] for c in VEC} == set(ORACLE), 'vector/oracle id mismatch'
    bad = 0
    for c in VEC:
        o = ORACLE[c['id']]
        assert (c['expected_overall'], c['required_codes'], c['forbidden_codes']) == \
            (o['expected_overall'], o['required_codes'], o['forbidden_codes']), c['id']+': vector differs from oracle'
        rep = run(copy.deepcopy(c))
        codes = [d['code'] for d in rep.get('diagnostics', [])]
        ok = rep['overall_status'] == c['expected_overall'] and all(x in codes for x in c['required_codes']) \
            and not any(x in codes for x in c['forbidden_codes'])
        if rep['overall_status'] != 'MCP_ERROR':
            ok = ok and all(rep[k] == 'NOT_EVALUATED' for k in NOPROMO)
        bad += not ok
        print('PASS' if ok else 'FAIL', c['id'], 'expected', c['expected_overall'], c['required_codes'], '| got', rep['overall_status'], codes,
              rep.get('_err', ''))
    print(f'{len(VEC)-bad}/{len(VEC)} match')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
