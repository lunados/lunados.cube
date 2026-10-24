"""G2 real official MCP v2 SDK stdio smoke; execute on macOS after SDK install.

This is NOT a mock; it starts a separate P3 server process.
"""
from __future__ import annotations
import asyncio
import hashlib
import json
import sys
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parents[2]
FIX=ROOT/'P1'/'semantic-validator-v1'/'fixtures'
sys.path.insert(0,str(BASE))


async def main():
    try:
        from mcp import Client, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError as exc:
        print('SDK_NOT_INSTALLED: install mcp==2.0.0 ('+str(exc)+')',file=sys.stderr)
        return 3
    source=(FIX/'migration.acg').read_text(encoding='utf-8')
    ctx=json.loads((FIX/'migration.binding-context.json').read_text(encoding='utf-8'))
    params=StdioServerParameters(command=sys.executable,args=['-u',str(BASE/'run_server.py')])
    async with Client(stdio_client(params),mode='2026-07-28') as client:
        tools=[x.name for x in (await client.list_tools()).tools]
        expected=['cube_get_capabilities','cube_prepare_print','cube_check_print','cube_render_svg','cube_read_reference','cube_validate','cube_discover_surface']
        assert tools==expected,(tools,expected)
        legacy=await client.call_tool('cube_get_capabilities',{})
        assert not legacy.is_error
        assert legacy.structured_content['adapter']['tools']==expected[:4]
        refs=await client.call_tool('cube_read_reference',{'uri':'aiaeao://p0/resources/v1'})
        assert not refs.is_error and refs.structured_content['complete']
        for title,params,expected_status in [
            ('PASS',{'input_text':source,'context':ctx},'PASS'),
            ('UNRESOLVED',{'input_text':source},'UNRESOLVED'),
            ('FAIL',{'input_text':'this is not valid ACG'},'FAIL'),
        ]:
            resp=await client.call_tool('cube_validate',params)
            assert not resp.is_error,(title,resp.content)
            result=resp.structured_content
            assert result['report']['overall_status']==expected_status,(title,result)
            assert result['report']['input_sha256']==hashlib.sha256(params['input_text'].encode()).hexdigest()
            assert len(result['report']['checks'])==8
            assert all(result['report'][k]=='NOT_EVALUATED' for k in
                       ('epistemic_warrant','current_authority','canonical_admission'))
            assert result['p1_validation_performed'] and not result['p2_printing_performed']
        bad=dict(ctx,source_kind='trusted_source')
        rejected=await client.call_tool('cube_validate',{'input_text':source,'context':bad})
        assert rejected.is_error,rejected.content
        assert rejected.structured_content['code']=='P1_MCP_CONFIG_INVALID'
        assert rejected.structured_content['semantic_status']=='NOT_EVALUATED'
        print('PASS G2 official MCP SDK v2 stdio: 6 tools, P0 fallback, P1 PASS/FAIL/UNRESOLVED, 8 checks, input digests, invalid context rejected')
    return 0

if __name__=='__main__':raise SystemExit(asyncio.run(main()))
