#!/usr/bin/env python3
"""Run F-01..F-16 against the P1.11 validator (and --adapter: through the G4 MCP p1_adapter facade).

Usage: run_vectors.py [--adapter]
Exit 0 only if every case matches the independent oracle.
"""
import copy, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]; REPO = HERE.parents[1]
for p in ('P1/semantic-validator-v1', 'P1/instantiation-profile-v1', 'P1/simulation-profile-v1', 'P1/comparison-profile-v1',
          'P1/migration-profile-v1', 'P1/migration-profile-v2', 'P1/migration-methods-v1'):
    sys.path.insert(0, str(REPO/p))
sys.dont_write_bytecode = True
ADAPTER = '--adapter' in sys.argv
if ADAPTER:
    sys.path.insert(0, str(REPO/'P3/adapters/mcp-local'))
    from aiaeao_mcp_local import p1_adapter
from cube_p111 import methods as M  # noqa: E402
from cube_p111.validator import P111Validator  # noqa: E402

VEC = json.loads((HERE/'fixtures/f01_f16_materialized.json').read_text('utf-8'))['cases']
ORACLE = {c['id']: c for c in json.loads((HERE/'oracles/independent_f01_f16.json').read_text('utf-8'))['cases']}
NOPROMO = ('epistemic_warrant', 'current_authority', 'canonical_admission')


class tampered_catalog:
    """F-03: pretend the pinned catalog file changed (digest mismatch) without touching the file."""
    def __enter__(self):
        self.saved = dict(M.PINNED); M._CACHE.clear()
        name, _ = M.PINNED['P1.11/migration-methods-v1']
        M.PINNED['P1.11/migration-methods-v1'] = (name, '0'*64)

    def __exit__(self, *exc):
        M.PINNED.clear(); M.PINNED.update(self.saved); M._CACHE.clear()


def run(c):
    qp = c.get('qualification_profiles')
    if ADAPTER:
        try:
            env = p1_adapter.validate(c['input_text'], c['input_format'], c['context'], qp)
            return env['report'], env
        except p1_adapter.P1AdapterFailure as e:
            return {'overall_status': 'MCP_ERROR', 'diagnostics': [{'code': e.diagnostic['code']}]}, None
    try:
        return P111Validator().validate_bytes(c['input_text'].encode(), input_format=c['input_format'], context=c['context'],
                                              qualification_profiles=qp), None
    except (ValueError, KeyError, TypeError) as e:
        return {'overall_status': 'MCP_ERROR', 'diagnostics': [{'code': 'P1_MCP_CONFIG_INVALID'}], '_err': str(e)}, None


def main():
    assert {c['id'] for c in VEC} == set(ORACLE), 'vector/oracle id mismatch'
    bad = 0
    for c in VEC:
        o = ORACLE[c['id']]
        assert (c['expected_overall'], c['required_codes'], c['forbidden_codes']) == \
            (o['expected_overall'], o['required_codes'], o['forbidden_codes']), c['id']+': vector differs from oracle'
        if c.get('tamper_catalog'):
            with tampered_catalog():
                rep, env = run(copy.deepcopy(c))
        else:
            rep, env = run(copy.deepcopy(c))
        codes = [d['code'] for d in rep.get('diagnostics', [])]
        ok = rep['overall_status'] == c['expected_overall'] and all(x in codes for x in c['required_codes']) \
            and not any(x in codes for x in c['forbidden_codes'])
        if rep['overall_status'] != 'MCP_ERROR':
            ok = ok and all(rep[k] == 'NOT_EVALUATED' for k in NOPROMO)
        if env is not None and c['context']['format'] == 'aiaeao.cube.binding-context/7':
            ok = ok and env.get('migration_profile') == 'P1.11/migration-methods-v1' and env.get('evaluation_performed_by_cube') is False
        bad += not ok
        print('PASS' if ok else 'FAIL', c['id'], 'expected', c['expected_overall'], c['required_codes'], '| got', rep['overall_status'], codes,
              rep.get('_err', ''))
    print(f'{len(VEC)-bad}/{len(VEC)} match')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
