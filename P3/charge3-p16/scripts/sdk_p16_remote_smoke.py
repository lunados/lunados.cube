#!/usr/bin/env python3
"""Actual G5 authenticated remote MCP SDK v2 P1.6 conformance (no side effects).

Run after explicit controlled G5 proof deployment, never as part of offline gate.
Authenticates using env variables, writes only sanitized evidence when requested.
"""
from __future__ import annotations
import argparse,asyncio,datetime,hashlib,json,os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/'fixtures/r01_r13_materialized.json'

async def run(evidence_path=None):
    url=os.environ.get('AIAEAO_G5_URL','')
    token=os.environ.get('AIAEAO_G5_TOKEN','')
    if not (url.startswith('https://') or url.startswith('http://127.0.0.1:')):
        raise SystemExit('AIAEAO_G5_URL must use HTTPS (or loopback HTTP)')
    if len(token)<32:raise SystemExit('AIAEAO_G5_TOKEN must be set securely (32+ characters)')
    try:
        import httpx2
        from mcp import Client
        from mcp.client.streamable_http import streamable_http_client
    except ImportError:
        raise SystemExit('MCP SDK v2 + httpx2 required in dedicated local venv')
    raw=INPUT.read_bytes()
    source_sha=hashlib.sha256(raw).hexdigest()
    vectors=json.loads(raw)['cases']
    assert [v['id'] for v in vectors]==[f'R-{i:02}' for i in range(1,14)]
    findings=[]
    async with httpx2.AsyncClient(headers={'Authorization':f'Bearer {token}'},
                                  timeout=httpx2.Timeout(30.0,read=300.0)) as h:
        async with Client(streamable_http_client(url,http_client=h),mode='2026-07-28') as client:
            names=[v.name for v in (await client.list_tools()).tools]
            assert names==['cube_get_capabilities','cube_prepare_print','cube_check_print',
                           'cube_render_svg','cube_read_reference','cube_validate','cube_discover_surface']
            resources=(await client.list_resources()).resources
            assert len(resources)==14
            surface=await client.call_tool('cube_discover_surface',{})
            assert not surface.is_error
            m=surface.structured_content
            p=m['p16_instantiation']
            assert p['activation']=='explicit_context_format_2_only'
            assert p['binding_context_formats']==['aiaeao.cube.binding-context/1',
                                                   'aiaeao.cube.binding-context/2']
            assert m['deployment']['remote_status']=='G5_PROOF_NOT_PRODUCTION_AUTHORIZED'
            for v in vectors:
                req={'input_text':v['input_text'],'input_format':v['input_format'],'context':v['context']}
                answer=await client.call_tool('cube_validate',req)
                assert not answer.is_error, v['id']
                body=answer.structured_content
                r=body['report']
                assert r['overall_status']==v['expected_overall'],(v['id'],r['overall_status'])
                codes={d['code'] for d in r['diagnostics']}
                assert set(v['required_codes']).issubset(codes),v['id']
                assert body['source_warrant']=='declared_unverified'
                assert not body['p2_printing_performed']
                for field in ('epistemic_warrant','current_authority','canonical_admission'):
                    assert r[field]=='NOT_EVALUATED',(v['id'],field)
                if v['context']['format'].endswith('/2'):
                    assert body['binding_context_profile']=='P1.6/instantiation-profile-v1'
                else:
                    assert 'binding_context_profile' not in body
                findings.append({'id':v['id'],'status':r['overall_status'],'codes_present':sorted(codes)})
            # No caller-provided context format is silently normalized to /2.
            bad=dict(vectors[0]['context']);bad['format']='aiaeao.cube.binding-context/3'
            reply=await client.call_tool('cube_validate',{'input_text':vectors[0]['input_text'],'context':bad})
            assert reply.is_error and reply.structured_content['code']=='P1_MCP_CONFIG_INVALID'
    evidence={'format':'aiaeao.cube.p16.charge3-remote-acceptance/1',
              'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'status':'PASS', 'security_scope':'existing_protected_G5_proof_endpoint',
              'fixtures_sha256':source_sha, 'p16_vectors':findings,
              'tools_count':7,'resource_count':14,
              'config_error_is_mcp_error':True,
              'epistemic_warrant_evaluated':False,
              'current_authority_evaluated':False,
              'canonical_admission_evaluated':False,
              'production_authorized':False}
    if evidence_path:
        dest=Path(evidence_path);dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(evidence,sort_keys=True,indent=2)+'\n','utf8')
    print('PASS CHARGE 3 ACTUAL REMOTE MCP: R-01..R-13, 7 tools, 14 resources, protected G5 proof only')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--evidence',help='Optional sanitized output JSON; no token or source payloads')
    args=parser.parse_args()
    asyncio.run(run(args.evidence))
