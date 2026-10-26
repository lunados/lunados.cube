#!/usr/bin/env python3
"""Run G-01..G-10 (and --with-m: M-01..M-22 re-run as /6) against the P1.10.1 validator.

Usage: run_vectors.py [--adapter] [--with-m]   (--adapter: through the G4 MCP p1_adapter facade)
Exit 0 only if every case matches the independent oracle.
"""
import copy, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]; REPO = HERE.parents[1]
for p in ('P1/semantic-validator-v1', 'P1/instantiation-profile-v1', 'P1/simulation-profile-v1', 'P1/comparison-profile-v1',
          'P1/migration-profile-v1', 'P1/migration-profile-v2'):
    sys.path.insert(0, str(REPO/p))
sys.dont_write_bytecode = True
ADAPTER = '--adapter' in sys.argv
if ADAPTER:
    sys.path.insert(0, str(REPO/'P3/adapters/mcp-local'))
    from aiaeao_mcp_local import p1_adapter
else:
    from cube_p1101.validator import P1101Validator
    V = P1101Validator()


def run(c):
    qp = c.get('qualification_profiles')
    if ADAPTER:
        try:
            env = p1_adapter.validate(c['input_text'], c['input_format'], c['context'], qp)
            return env['report'], env
        except p1_adapter.P1AdapterFailure as e:
            return {'overall_status': 'MCP_ERROR', 'diagnostics': [{'code': e.diagnostic['code']}]}, None
    try:
        return V.validate_bytes(c['input_text'].encode(), input_format=c['input_format'], context=c['context'],
                                qualification_profiles=qp), None
    except (ValueError, KeyError, TypeError) as e:
        return {'overall_status': 'MCP_ERROR', 'diagnostics': [{'code': 'P1_MCP_CONFIG_INVALID'}], '_err': str(e)}, None


def m_as_v6():
    oracle = {c['id']: c for c in json.loads((REPO/'P1/migration-profile-v1/oracles/independent_m01_m22.json').read_text())['cases']}
    out = []
    for c in json.loads((REPO/'P1/migration-profile-v1/fixtures/m01_m22_materialized.json').read_text('utf-8'))['cases']:
        c = copy.deepcopy(c)
        if c['context']['format'] == 'aiaeao.cube.binding-context/5':
            c['context']['format'] = 'aiaeao.cube.binding-context/6'
        c['id'] = c['id']+'/6'
        o = oracle[c['id'][:-2]]
        c['expected_overall'], c['required_codes'] = o['expected_overall'], o['required_codes']
        c['forbidden_codes'] = ['P1_MIGRATION_DEPENDENCY_GAP']
        out.append(c)
    return out


def main():
    cases = json.loads((HERE/'fixtures/g01_g10_materialized.json').read_text('utf-8'))['cases']
    if '--with-m' in sys.argv:
        cases += m_as_v6()
    bad = 0
    for c in cases:
        rep, env = run(c)
        codes = [d['code'] for d in rep.get('diagnostics', [])]
        ok = rep['overall_status'] == c['expected_overall'] and all(x in codes for x in c['required_codes']) \
            and not any(x in codes for x in c.get('forbidden_codes', []))
        if rep['overall_status'] != 'MCP_ERROR':
            ok = ok and all(rep[k] == 'NOT_EVALUATED' for k in ('epistemic_warrant', 'current_authority', 'canonical_admission'))
        if env is not None and c['context']['format'] == 'aiaeao.cube.binding-context/6':
            ok = ok and env.get('migration_profile') == 'P1.10.1/migration-profile-v2' and env.get('evaluation_performed_by_cube') is False
        bad += not ok
        print('PASS' if ok else 'FAIL', c['id'], 'expected', c['expected_overall'], c['required_codes'], '| got', rep['overall_status'], codes,
              rep.get('_err', ''))
    print(f'{len(cases)-bad}/{len(cases)} match')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
