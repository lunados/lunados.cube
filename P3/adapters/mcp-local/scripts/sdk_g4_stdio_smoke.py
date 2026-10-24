"""G4 actual MCP-SDK v2 stdio smoke. Run on macOS after requirements install.

Tests real protocol introspection, 14 Resources, P0 fallback, P1 semantics,
P2 golden SVG, and G4 whole-surface metadata; no writes or web requests.
"""
from __future__ import annotations
import asyncio
import hashlib
import json
import sys
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parents[2]
sys.path.insert(0,str(BASE))
from aiaeao_mcp_local import surface, p0_resources

async def main() -> int:
    try:
        from mcp import Client, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError as err:
        print('MCP_SDK_NOT_INSTALLED: mcp==2.0.0 required: '+str(err),file=sys.stderr)
        return 3
    args=StdioServerParameters(command=sys.executable,args=['-u',str(BASE/'run_server.py')])
    async with Client(stdio_client(args), mode='2026-07-28') as client:
        names=[x.name for x in (await client.list_tools()).tools]
        assert names==list(surface.TOOLS),(names,list(surface.TOOLS))
        refs=[str(x.uri) for x in (await client.list_resources()).resources]
        assert len(refs)==14 and set(refs)==set(surface.discover_surface()['mcp']['resource_uris'])
        discovery=await client.call_tool('cube_discover_surface',{})
        assert not discovery.is_error,discovery.content
        assert discovery.structured_content==surface.discover_surface()
        legacy=await client.call_tool('cube_get_capabilities',{})
        assert not legacy.is_error
        assert legacy.structured_content['adapter']['tools']==names[:4]
        index=await client.call_tool('cube_read_reference',{'uri':p0_resources.INDEX_URI})
        assert not index.is_error and index.structured_content['complete']
        index_bytes=index.structured_content['content'].encode('utf-8')
        assert index_bytes==p0_resources.read_bytes(p0_resources.INDEX_URI)
        acg=(ROOT/'P1/semantic-validator-v1/fixtures/migration.acg').read_text(encoding='utf-8')
        result=await client.call_tool('cube_validate',{'input_text':acg})
        assert not result.is_error and result.structured_content['report']['overall_status']=='UNRESOLVED'
        result=await client.call_tool('cube_validate',{'input_text':'this is not valid ACG'})
        assert not result.is_error and result.structured_content['report']['overall_status']=='FAIL'
        examples=ROOT/'P2/visual-printer-release-v1/examples'
        job=json.loads((examples/'flow_provenance_standard.job.json').read_text(encoding='utf-8'))
        svg=await client.call_tool('cube_render_svg',{'job':job})
        assert not svg.is_error
        returned=svg.structured_content['artifact']['svg_text'].encode('utf-8')
        assert returned==(examples/'flow_provenance_standard.svg').read_bytes()
        assert hashlib.sha256(returned).hexdigest()==svg.structured_content['artifact']['sha256']
        for _ in range(2):
            again=await client.call_tool('cube_discover_surface',{})
            assert again.structured_content==discovery.structured_content
    print('PASS G4 MCP SDK v2 stdio: 7 tools, 14 resources, P0 fallback, P1 semantics, '
          'P2 golden SVG, stable cross-domain surface and backward-compatible legacy card')
    return 0

if __name__=='__main__': raise SystemExit(asyncio.run(main()))
