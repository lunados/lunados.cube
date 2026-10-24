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
from .p0_resources import register_resources
from .p0_tool import read_reference as read_p0_reference
from . import p1_adapter
from . import surface

mcp = MCPServer('aiaeao-cube-local',
                instructions='AIAEAO Cube local MCP: use cube_discover_surface for the full P0/P1/P2 '
                             'inventory; cube_get_capabilities is P2 legacy only. '
                             'P0 read-only Resources may be hidden by host bridges; use '
                             'cube_read_reference as compatible fallback. P1 descriptive '
                             'validation and P2 SVG printing remain independent and do '
                             'not assert source truth, authority or admission.')


def _result(fn, *args, **kwargs) -> CallToolResult:
    try:
        payload = fn(*args, **kwargs)
        error = False
    except (bridge.BridgeFailure, p1_adapter.P1AdapterFailure) as exc:
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


# CP-001 / G1.1: compatibility for hosts that expose Tools but hide Resources.
# The original four VP-06 tool signatures and their capability card are unchanged.
@mcp.tool()
def cube_read_reference(uri: str, offset: int = 0, max_bytes: int = 8192) -> CallToolResult:
    """Read a pinned P0 v9.4 reference via tool-only MCP bridges. Use index URI
    aiaeao://p0/resources/v1 for exact allowlist/digests; page with next_offset.
    max_bytes <= 32768. Never fetch arbitrary URLs/files or infer source truth.
    """
    return _result(read_p0_reference, uri, offset, max_bytes)

# CP-001 / G2: single separately scoped P1 tool; P1 statuses are not MCP errors.
@mcp.tool()
def cube_validate(input_text: str, input_format: Literal['acg_text','json_ast']='acg_text',
                  context: dict[str, Any] | None=None,
                  qualification_profiles: dict[str, Any] | None=None) -> CallToolResult:
    """Run frozen P1-VC/1.0.0 descriptive validation; return exact P1 report.
    PASS, FAIL, UNRESOLVED are normal tool results; invalid config is isError.
    No truth, authorization, P2 printing, or automatic ACG-to-SVG conversion.
    """
    return _result(p1_adapter.validate, input_text, input_format, context, qualification_profiles)

# CP-001 / G4: whole-surface introspection; no new semantic operation.
@mcp.tool()
def cube_discover_surface() -> CallToolResult:
    """Discover the complete local P0 Reference, P1 Validation and P2 SVG surface.
    Unlike cube_get_capabilities, this is whole-Cube, not printer-only.
    Resources depend on host support; cube_read_reference is the tool fallback.
    """
    return _result(surface.discover_surface)

# CP-001 / G1: P0 resources remain primary; four legacy tools remain unchanged.
register_resources(mcp)

def main() -> None:
    mcp.run(transport='stdio')
