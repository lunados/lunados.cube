"""G1 real MCP SDK v2 stdio smoke: SDK client -> subprocess -> MCP resources.

Run on macOS after pip install -r requirements-mcp.txt. Uses no network.
A real Claude host read remains a separate acceptance step.
"""
from __future__ import annotations
import asyncio
import hashlib
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from aiaeao_mcp_local import p0_resources as p0


def _as_text(result):
    from mcp.types import TextResourceContents
    if len(result.contents) != 1 or not isinstance(result.contents[0], TextResourceContents):
        raise AssertionError('read_resource did not return exactly one text resource')
    return result.contents[0].text


async def main() -> int:
    try:
        from mcp import Client, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError as error:
        print('UNVERIFIED_SDK: install mcp==2.0.0: ' + str(error), file=sys.stderr)
        return 3
    params = StdioServerParameters(command=sys.executable, args=['-u', str(BASE / 'run_server.py')])
    async with Client(stdio_client(params), mode='2026-07-28') as client:
        first = [str(x.uri) for x in (await client.list_resources()).resources]
        second = [str(x.uri) for x in (await client.list_resources()).resources]
        assert first == second, 'resources/list order is unstable'
        expected = {e['uri'] for e in p0.entries()} | {p0.INDEX_URI}
        assert len(first) == len(expected) == 14 and set(first) == expected, (len(first), sorted(set(first)^expected))
        lookup = {e['uri']: e for e in p0.entries()}
        index = json.loads(_as_text(await client.read_resource(p0.INDEX_URI)))
        assert index['format'] == 'aiaeao.cube.mcp-p0-resources/1'
        assert index['snapshot_lock_sha256'] == p0.PINNED_LOCK_SHA256
        checked_uris = [
            'https://cube.lunados.net/v9.4/morphology.md',
            'https://cube.lunados.net/v9.4/grammar/concepts.json',
            'https://cube.lunados.net/v9.4/notation/ast.schema.json',
            'https://cube.lunados.net/v9.4/visual/symbols.json',
        ]
        for uri in checked_uris:
            content = _as_text(await client.read_resource(uri)).encode('utf-8')
            assert hashlib.sha256(content).hexdigest() == lookup[uri]['sha256'], uri
            assert content == p0.read_bytes(uri), uri
        # Important regression: the previous four VP-06 Tools still exist, unchanged.
        tool_names = [x.name for x in (await client.list_tools()).tools]
        assert tool_names == ['cube_get_capabilities','cube_prepare_print',
                              'cube_check_print','cube_render_svg','cube_read_reference','cube_validate','cube_discover_surface'], tool_names
        cap = await client.call_tool('cube_get_capabilities', {})
        assert not cap.is_error and cap.structured_content['adapter']['p1_validation'] is False
        # Unknown resources must not trigger HTTP or become fallback filesystem reads.
        for uri in ['https://evil.invalid/payload', 'https://cube.lunados.net/v9.4/../manifest.json']:
            denied = False
            try:
                await client.read_resource(uri)
            except Exception:
                denied = True
            assert denied, 'Unregistered URI unexpectedly accepted: ' + uri
    print('PASS G1 MCP SDK v2 stdio: 14 resources, 4 byte-parity reads, unknown URI rejection, 4 legacy tools + 1 fallback')
    return 0


if __name__ == '__main__':
    raise SystemExit(asyncio.run(main()))
