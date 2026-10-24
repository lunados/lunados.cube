"""Real in-process MCP SDK v2 test. Requires pip install -r requirements-mcp.txt.
No home-directory writes, no fake server, no HTTP, no network.
"""
from __future__ import annotations
import asyncio
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from aiaeao_mcp_local.bridge import PRINTER, TOOL_NAMES

async def main():
    try:
        from mcp import Client
        from aiaeao_mcp_local.server import mcp
    except ImportError as error:
        print('UNVERIFIED_SDK: install MCP v2 first (' + str(error) + ')')
        return 3
    job=json.loads((PRINTER/'examples/flow_provenance_standard.job.json').read_text())
    async with Client(mcp, mode='2026-07-28') as client:
        listed=await client.list_tools()
        names=[tool.name for tool in listed.tools]
        assert names==list(TOOL_NAMES),(names,TOOL_NAMES)
        card=await client.call_tool('cube_get_capabilities',{})
        assert not card.is_error
        assert card.structured_content['adapter']['remote_available'] is False
        result=await client.call_tool('cube_render_svg',{'job':job})
        assert not result.is_error, result.content
        payload=result.structured_content
        svg=payload['artifact']['svg_text'].encode('utf-8')
        assert hashlib.sha256(svg).hexdigest()==payload['report']['svg_sha256']
        assert svg==(PRINTER/'examples/flow_provenance_standard.svg').read_bytes()
        print('PASS MCP SDK in-process: tools/list + capabilities + render SVG byte parity')
    return 0

if __name__=='__main__':raise SystemExit(asyncio.run(main()))
