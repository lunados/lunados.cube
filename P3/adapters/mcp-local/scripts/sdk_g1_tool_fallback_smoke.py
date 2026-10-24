"""G1.1 real MCP SDK v2 stdio tool-only bridge fallback smoke test.

Requires installed mcp==2.0.0; no mocks, no network, no Claude needed.
"""
from __future__ import annotations
import asyncio
import hashlib
import json
import sys
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE))
from aiaeao_mcp_local import p0_resources as p0

async def main():
    try:
        from mcp import Client, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError as exc:
        print('UNVERIFIED_SDK: install mcp==2.0.0: '+str(exc),file=sys.stderr)
        return 3
    params=StdioServerParameters(command=sys.executable,args=['-u',str(BASE/'run_server.py')])
    async with Client(stdio_client(params),mode='2026-07-28') as client:
        listed=[x.name for x in (await client.list_tools()).tools]
        expected=['cube_get_capabilities','cube_prepare_print','cube_check_print','cube_render_svg','cube_read_reference','cube_validate','cube_discover_surface']
        assert listed==expected,(listed,expected)
        idx_result=await client.call_tool('cube_read_reference',{'uri':p0.INDEX_URI})
        assert not idx_result.is_error,idx_result.content
        idx=idx_result.structured_content
        assert idx['complete'] and idx['content'].encode('utf-8')==p0.read_bytes(p0.INDEX_URI)
        catalog=json.loads(idx['content'])
        lookup={entry['uri']:entry for entry in catalog['resources']}
        for uri in ('https://cube.lunados.net/v9.4/morphology.md',
                    'https://cube.lunados.net/v9.4/grammar/concepts.json'):
            offset=0
            chunks=[]
            while True:
                r=await client.call_tool('cube_read_reference',{'uri':uri,'offset':offset,'max_bytes':32768})
                assert not r.is_error,r.content
                p=r.structured_content
                assert p['sha256']==lookup[uri]['sha256']
                assert p['offset']==offset
                chunks.append(p['content'].encode('utf-8'))
                if p['complete']:
                    assert p['next_offset'] is None
                    break
                assert p['next_offset']>offset
                offset=p['next_offset']
            rebuilt=b''.join(chunks)
            assert rebuilt==p0.read_bytes(uri)
            assert hashlib.sha256(rebuilt).hexdigest()==lookup[uri]['sha256']
        denied=await client.call_tool('cube_read_reference',{'uri':'file:///etc/passwd'})
        assert denied.is_error and denied.structured_content['code']=='P0_URI_NOT_FOUND'
        denied=await client.call_tool('cube_read_reference',{'uri':'https://cube.lunados.net/v9.4/morphology.md','offset':-1})
        assert denied.is_error and denied.structured_content['code']=='P0_OFFSET_INVALID'
        print('PASS G1.1 official MCP SDK v2 stdio: 5 tools, pinned index, P0 morphology + concepts byte parity, denied URIs/offsets')
    return 0
if __name__=='__main__':raise SystemExit(asyncio.run(main()))
