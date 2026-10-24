#!/usr/bin/env python3
"""G5 REAL remote MCP SDK v2 test: run only after deploying both Workers.

Examples:
  export AIAEAO_G5_URL='https://aiaeao-cube-g5-gateway.<account>.workers.dev/mcp'
  export AIAEAO_G5_TOKEN='<secret created for test>'
  python scripts/sdk_remote_smoke.py

No tokens are printed, no files written, no local stdio server started.
"""
import asyncio, hashlib, json, os, sys, argparse, datetime
from pathlib import Path

REPO=Path(__file__).resolve().parents[3]
async def main():
    url=os.environ.get('AIAEAO_G5_URL','')
    token=os.environ.get('AIAEAO_G5_TOKEN','')
    if not url.startswith('https://') and not url.startswith('http://127.0.0.1:'):
        raise SystemExit('Set AIAEAO_G5_URL to an HTTPS endpoint (or local 127.0.0.1)')
    if len(token)<32:raise SystemExit('Set AIAEAO_G5_TOKEN (32+ characters)')
    try:
        import httpx2
        from mcp import Client
        from mcp.client.streamable_http import streamable_http_client
    except ImportError:raise SystemExit('Install official mcp SDK v2 and httpx2 in isolated venv')
    evidence={'format':'aiaeao.cube.g5-r3-remote-check/1', 'date':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'profile':'P3-MCP-REMOTE/0.1.0-proof','test':'actual_remote_mcp','status':'PENDING'}
    async with httpx2.AsyncClient(headers={'Authorization':f'Bearer {token}'},
                                  timeout=httpx2.Timeout(30.0,read=300.0)) as client_http:
        # Unauthorized requests must be rejected, independently of tool semantics.
        denied=await client_http.post(url,content='{}',headers={'Authorization':'Bearer wrong'})
        assert denied.status_code==401, ('unauthorized request was not rejected',denied.status_code)
        denied_origin=await client_http.post(url,content='{}',headers={'Origin':'https://bad.invalid'})
        assert denied_origin.status_code==403, ('bad Origin not denied',denied_origin.status_code)
        transport=streamable_http_client(url,http_client=client_http)
        async with Client(transport,mode='2026-07-28') as client:
            names=[v.name for v in (await client.list_tools()).tools]
            assert names==['cube_get_capabilities','cube_prepare_print','cube_check_print','cube_render_svg',
                           'cube_read_reference','cube_validate','cube_discover_surface'],names
            refs=await client.list_resources()
            assert len(refs.resources)==14
            expected={x['uri']:x['mime_type'] for x in json.loads((REPO/'P3/remote-mcp-g5/gateway/src/p0-registry.json').read_text())['resources']}
            assert {str(x.uri):x.mime_type for x in refs.resources}==expected, 'remote resource MIME differs from frozen P0 lock'
            assert sum(m=='text/markdown' for m in expected.values())>=2
            evidence['resources_count']=len(refs.resources)
            evidence['resource_mime_matches_p0_lock']=True
            surf=await client.call_tool('cube_discover_surface',{})
            assert not surf.is_error and surf.structured_content['deployment']['remote_mcp_available']
            evidence['remote_discovery']=True
            evidence['tools_count']=len(names)
            index=await client.call_tool('cube_read_reference',{'uri':'aiaeao://p0/resources/v1'})
            assert not index.is_error
            content=index.structured_content['content'].encode('utf-8')
            assert hashlib.sha256(content).hexdigest()==index.structured_content['sha256']
            evidence['p0_index_sha256']=hashlib.sha256(content).hexdigest()
            fixture_input=(REPO/'P1/semantic-validator-v1/fixtures/migration.acg').read_text('utf-8')
            p1_unresolved=await client.call_tool('cube_validate',{'input_text':fixture_input})
            assert not p1_unresolved.is_error and p1_unresolved.structured_content['report']['overall_status']=='UNRESOLVED'
            context=json.loads((REPO/'P1/semantic-validator-v1/fixtures/migration.binding-context.json').read_text('utf-8'))
            p1_pass=await client.call_tool('cube_validate',{'input_text':fixture_input,'context':context})
            assert not p1_pass.is_error and p1_pass.structured_content['report']['overall_status']=='PASS'
            p1=await client.call_tool('cube_validate',{'input_text':'this is not valid ACG'})
            assert not p1.is_error and p1.structured_content['report']['overall_status']=='FAIL'
            invalid=await client.call_tool('cube_validate',{
                'input_text':'x','context':{'source_kind':'trusted_source'}})
            assert invalid.is_error
            fixtures=REPO/'P2/visual-printer-release-v1/examples'
            job=json.loads((fixtures/'flow_provenance_standard.job.json').read_text('utf8'))
            actual=await client.call_tool('cube_render_svg',{'job':job})
            assert not actual.is_error
            svg=actual.structured_content['artifact']['svg_text'].encode('utf-8')
            assert svg==(fixtures/'flow_provenance_standard.svg').read_bytes(), 'remote SVG differs from VP-06 bytes'
            assert hashlib.sha256(svg).hexdigest()==actual.structured_content['artifact']['sha256']
            assert actual.structured_content['report']['epistemic_warrant']=='NOT_EVALUATED'
            repeated=await client.call_tool('cube_render_svg',{'job':job})
            assert not repeated.is_error and repeated.structured_content['artifact']['svg_text'].encode('utf-8')==svg
            evidence['p1_semantic_statuses']=['UNRESOLVED','PASS','FAIL']
            evidence['p1_invalid_config_is_mcp_error']=True
            evidence['svg_bytes']=len(svg)
            evidence['svg_sha256_client_computed']=hashlib.sha256(svg).hexdigest()
            evidence['svg_matches_local_golden_bytes']=True
            evidence['repeated_svg_matches_exact_bytes']=True
            evidence['auth_wrong_token_rejected']=True
            evidence['wrong_origin_rejected']=True
            evidence['status']='PASS'
    print('PASS G5 ACTUAL REMOTE MCP: auth, Origin, 7 tools, 14 resources, P0, P1, VP06 byte parity')
    if args.evidence:
        dest=Path(args.evidence)
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(evidence,sort_keys=True,indent=2)+'\n','utf-8')
        print('PASS G5 sanitized R3 evidence written to:',dest)
if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--evidence',help='Write sanitized JSON after all assertions pass')
    args=parser.parse_args()
    asyncio.run(main())
