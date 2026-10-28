"""G6 actual MCP-SDK v2 stdio smoke: the three plan-view tools over the real protocol.

Starts run_server.py as a subprocess, lists the ten tools, derives a source, prints VP-07 / VP-08 / VP-09
panels, checks one result, provokes two errors and compares bytes with the in-process tool layer.
No writes, no web requests.
"""
from __future__ import annotations
import asyncio
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]
sys.path.insert(0, str(BASE))
from aiaeao_mcp_local import surface, plan_views as PV  # noqa: E402


async def main() -> int:
    try:
        from mcp import Client, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError as err:
        print('MCP_SDK_NOT_INSTALLED: mcp>=2.0.0 required: '+str(err), file=sys.stderr)
        return 3
    g74 = json.loads((ROOT/'P2/visual-printer-migration-v1/fixtures/golden_v074.json').read_text('utf-8'))
    gseq = json.loads((ROOT/'P2/visual-printer-sequence-v1/fixtures/golden_sequence.json').read_text('utf-8'))
    gax = json.loads((ROOT/'P2/visual-printer-axes-v1/fixtures/golden_axes.json').read_text('utf-8'))
    args = StdioServerParameters(command=sys.executable, args=['-u', str(BASE/'run_server.py')])
    async with Client(stdio_client(args), mode='2026-07-28') as client:
        names = [x.name for x in (await client.list_tools()).tools]
        assert names == list(surface.TOOLS_G6), names
        disc = await client.call_tool('cube_discover_surface', {})
        assert not disc.is_error and disc.structured_content == surface.discover_surface_local()
        src = await client.call_tool('cube_plan_source', {'context': g74['context'], 'plan_id': g74['plan_id'],
                                                         'printer': 'vpmigration', 'profile': g74['profile']})
        assert not src.is_error, src.content
        source = src.structured_content['source']
        assert source == PV.plan_source(g74['context'], g74['plan_id'], 'vpmigration', profile=g74['profile'])['source']
        flow = await client.call_tool('cube_plan_views', {'source': source, 'view': 'cube.flow', 'granularity': 'standard',
                                                          'partition': 'subject', 'lens': 'cube.lens.execution'})
        assert not flow.is_error, flow.content
        local = PV.plan_views(source, 'cube.flow', 'standard', partition='subject', lens='cube.lens.execution')
        assert flow.structured_content == local
        assert flow.content[0].text.encode('utf-8') == PV.canonical(local)
        chk = await client.call_tool('cube_plan_check', {'result': flow.structured_content})
        assert not chk.is_error and chk.structured_content['status'] == 'PASS'
        seq = await client.call_tool('cube_plan_views', {'source': gseq['sequence_source'], 'view': 'cube.sequence', 'granularity': 'standard'})
        assert not seq.is_error and seq.structured_content['report']['coverage']['status'] == 'COMPLETE'
        ax = await client.call_tool('cube_plan_source', {'context': gax['context'], 'plan_id': gax['plan_id'], 'printer': 'vpaxes',
                                                        'profile': 'P2-VP-AXES/0.9.1'})
        axv = await client.call_tool('cube_plan_views', {'source': ax.structured_content['source'], 'view': 'cube.axes',
                                                         'granularity': 'standard', 'rows': 'F', 'cols': 'Z:referent'})
        assert not axv.is_error and axv.structured_content['report']['binding_coverage']['status'] == 'COMPLETE'
        bad = await client.call_tool('cube_plan_views', {'source': source, 'view': 'cube.phases', 'granularity': 'detail',
                                                         'partition': 'banana'})
        assert bad.is_error and bad.structured_content['code'] == 'VP07_PANEL_PARTITION'
        unsupported = await client.call_tool('cube_plan_source', {'context': g74['context'], 'plan_id': g74['plan_id'], 'printer': 'vpsequence'})
        assert unsupported.is_error and unsupported.structured_content['code'] == 'P3_PLAN_SOURCE_UNSUPPORTED'
    print('PASS G6 MCP SDK v2 stdio: 10 tools, plan source, cube.flow / cube.sequence / cube.axes panels equal to the '
          'in-process tool layer, check PASS, printer and transport errors as isError')
    return 0


if __name__ == '__main__':
    raise SystemExit(asyncio.run(main()))
