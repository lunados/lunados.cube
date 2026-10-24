"""Official Python MCP SDK v2 adapter: stdio only, no HTTP/server hosting.

Transport framing and negotiated protocol revisions are owned by the MCP SDK.
We do not implement JSON-RPC or MCP framing ourselves.
"""
from __future__ import annotations
import json
from typing import Any, Literal
from mcp.server.mcpserver import MCPServer
from mcp.types import CallToolResult, TextContent
from . import bridge

mcp = MCPServer('aiaeao-cube-local',
                instructions='Deterministic, local-only AIAEAO VP-06 SVG printer. '
                             'Sources remain declared_unverified; P1 is not invoked. '
                             'Use capabilities first; prepare from declared VP-03 bundles, '
                             'then check and render. Missing facets are errors.')


def _result(fn, *args, **kwargs) -> CallToolResult:
    try:
        payload = fn(*args, **kwargs)
        error = False
    except bridge.BridgeFailure as exc:
        payload = exc.diagnostic
        error = True
    # Stable structuredContent + textual fallback for clients without structure support.
    return CallToolResult(content=[TextContent(type='text', text=json.dumps(
        payload,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False))],
        structured_content=payload, is_error=error)


@mcp.tool()
def cube_get_capabilities() -> CallToolResult:
    """Discover supported Cube views, lenses and budgets; no remote server or P1 validator."""
    return _result(bridge.get_capabilities)


@mcp.tool()
def cube_prepare_print(
    bundle: dict[str, Any], lens: str, granularity: Literal['overview','standard','detail'],
    overflow: Literal['summarize','reject']='summarize',
    focus: dict[str, str] | None=None,
    max_items: int | None=None, max_edges: int | None=None,
) -> CallToolResult:
    """Prepare a SHA-bound VP-04 job from an explicitly declared VP-03 lens bundle. Never infer facets."""
    return _result(bridge.prepare_print,bundle,lens,granularity,overflow,focus,max_items,max_edges)


@mcp.tool()
def cube_check_print(job: dict[str, Any]) -> CallToolResult:
    """Validate VP-04 job and return VP-06 report in memory; does not produce a file."""
    return _result(bridge.check_print,job)


@mcp.tool()
def cube_render_svg(job: dict[str, Any]) -> CallToolResult:
    """Return actual UTF-8 SVG XML and unmodified VP-06 audit report; source remains unverified."""
    return _result(bridge.render_svg,job)


def main() -> None:
    mcp.run(transport='stdio')
