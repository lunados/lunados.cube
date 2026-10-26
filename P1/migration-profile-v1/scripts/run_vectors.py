#!/usr/bin/env python3
"""Run M-01..M-22 (optional --with-c C-01..C-20, --with-s S-01..S-17, --with-r R-01..R-13) against the local P1.10 validator.

Usage: run_vectors.py [--adapter]   (--adapter: through the G4 MCP p1_adapter facade)
Exit 0 only if every case matches the independent oracle.
"""
import json, sys
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]; REPO=HERE.parents[1]
for p in ('P1/semantic-validator-v1','P1/instantiation-profile-v1','P1/simulation-profile-v1','P1/comparison-profile-v1','P1/migration-profile-v1'):
    sys.path.insert(0,str(REPO/p))
sys.dont_write_bytecode=True
ADAPTER='--adapter' in sys.argv
if ADAPTER:
    sys.path.insert(0,str(REPO/'P3/adapters/mcp-local'))
    from aiaeao_mcp_local import p1_adapter
else:
    from cube_p110.validator import P110Validator
    V=P110Validator()

def run(c):
    qp=c.get('qualification_profiles')
    if ADAPTER:
        try:
            env=p1_adapter.validate(c['input_text'],c['input_format'],c['context'],qp)
            return env['report'],env
        except p1_adapter.P1AdapterFailure as e:
            return {'overall_status':'MCP_ERROR','diagnostics':[{'code':e.diagnostic['code']}]},None
    try:
        return V.validate_bytes(c['input_text'].encode(),input_format=c['input_format'],context=c['context'],
                                qualification_profiles=qp),None
    except (ValueError,KeyError,TypeError) as e:
        return {'overall_status':'MCP_ERROR','diagnostics':[{'code':'P1_MCP_CONFIG_INVALID'}],'_err':str(e)},None

def main():
    files=[HERE/'fixtures/m01_m22_materialized.json']
    if '--with-c' in sys.argv: files.append(REPO/'P1/comparison-profile-v1/fixtures/c01_c20_materialized.json')
    if '--with-s' in sys.argv: files.append(REPO/'P1/simulation-profile-v1/fixtures/s01_s17_materialized.json')
    if '--with-r' in sys.argv: files.append(REPO/'P3/charge3-p16/fixtures/r01_r13_materialized.json')
    bad=0;n=0
    for f in files:
        for c in json.loads(f.read_text('utf-8'))['cases']:
            n+=1
            rep,env=run(c); codes=[d['code'] for d in rep.get('diagnostics',[])]
            ok=rep['overall_status']==c['expected_overall'] and all(x in codes for x in c['required_codes'])
            if rep['overall_status']!='MCP_ERROR':
                ok=ok and all(rep[k]=='NOT_EVALUATED' for k in ('epistemic_warrant','current_authority','canonical_admission'))
            fmt=(c['context'] or {}).get('format')
            if env is not None and fmt=='aiaeao.cube.binding-context/5':
                ok=ok and env.get('evaluation_performed_by_cube') is False and env.get('migration_profile')=='P1.10/migration-profile-v1'
            bad+=not ok
            print(('PASS' if ok else 'FAIL'), c['id'], 'expected', c['expected_overall'], c['required_codes'],
                  '| got', rep['overall_status'], codes, rep.get('_err',''))
    print(f'{n-bad}/{n} match'); sys.exit(1 if bad else 0)
if __name__=='__main__': main()
