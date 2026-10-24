"""Official SDK subprocess/stdio integration test, run ON A MACHINE WITH SDK v2 installed.

This is not a mock. It launches the exact Python server that a desktop host uses.
"""
from __future__ import annotations
import asyncio
import hashlib
import json
import sys
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parents[2]
PRINTER=ROOT/'P2/visual-printer-release-v1'

async def main():
    try:
        from mcp import Client, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError as e:
        print('UNVERIFIED_SDK: install MCP v2 first: '+str(e),file=sys.stderr)
        return 3
    job=json.loads((PRINTER/'examples/flow_provenance_standard.job.json').read_text())
    bundle=json.loads((PRINTER/'examples/flow_provenance_standard.vp03.bundle.json').read_text())
    params=StdioServerParameters(command=sys.executable,args=['-u',str(BASE/'run_server.py')])
    async with Client(stdio_client(params),mode='2026-07-28') as client:
        listed=await client.list_tools()
        names=[tool.name for tool in listed.tools]
        expected=['cube_get_capabilities','cube_prepare_print','cube_check_print','cube_render_svg','cube_read_reference','cube_validate','cube_discover_surface']
        assert names==expected,(names,expected)
        card=await client.call_tool('cube_get_capabilities',{})
        assert not card.is_error
        assert card.structured_content['adapter']['remote_available'] is False
        prepared=await client.call_tool('cube_prepare_print',{
            'bundle':bundle,'lens':'cube.lens.provenance','granularity':'standard'})
        assert not prepared.is_error,prepared.content
        assert prepared.structured_content==job
        checked=await client.call_tool('cube_check_print',{'job':job})
        assert not checked.is_error,checked.content
        printed=await client.call_tool('cube_render_svg',{'job':job})
        assert not printed.is_error,printed.content
        content=printed.structured_content
        svg=content['artifact']['svg_text'].encode('utf-8')
        assert hashlib.sha256(svg).hexdigest()==content['report']['svg_sha256']
        assert content['report']==checked.structured_content
        assert svg==(PRINTER/'examples/flow_provenance_standard.svg').read_bytes()
        for _ in range(2):
            again=await client.call_tool('cube_render_svg',{'job':job})
            assert not again.is_error and again.structured_content==content
        bad=json.loads(json.dumps(job))
        bad['source_bundle']['view_plan']['title']='digest tamper'
        refused=await client.call_tool('cube_check_print',{'job':bad})
        assert refused.is_error
        assert refused.structured_content['code']=='VP06_SOURCE_DIGEST_MISMATCH'
        missing=json.loads(json.dumps(bundle))
        missing['facet_bindings']=[b for b in missing['facet_bindings'] if b['lens']!='cube.lens.provenance']
        refused=await client.call_tool('cube_prepare_print',{
            'bundle':missing,'lens':'cube.lens.provenance','granularity':'standard'})
        assert refused.is_error
        assert refused.structured_content['code']=='VP06_LENS_NOT_DECLARED'
        print('PASS official MCP SDK v2 / stdio: discover, prepare, check, SVG parity ×3, diagnostics')
    return 0

if __name__=='__main__':raise SystemExit(asyncio.run(main()))
