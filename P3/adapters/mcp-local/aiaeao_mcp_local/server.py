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
from . import plan_views

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
    except (bridge.BridgeFailure, p1_adapter.P1AdapterFailure, plan_views.PlanFailure) as exc:
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
    """Run descriptive P1 validation with explicit binding-context/1 through /8.
    Use local cube_discover_surface for entry profiles and module-presence limits.
    Higher-context validators are loaded lazily; discovery is not a runtime test.
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
    return _result(surface.discover_surface_local)


# CP-001 / G6: VP-07, VP-08, VP-09 and VP-10 plan views in memory; the view selects the printer (local stdio only).
@mcp.tool()
def cube_plan_source(
    context: dict[str, Any], plan_id: str | None, printer: Literal['vpmigration','vpaxes','vpcells','vpinstances','vpsequence'],
    track_map: dict[str, Any] | None=None, track: str | None=None, labels: dict[str, Any] | None=None,
    layers: dict[str, Any] | None=None, witness_prefixes: dict[str, Any] | None=None,
    edge_styles: list[dict[str, Any]] | None=None, steps: str | None=None, subjects: list[str] | None=None,
    profile: str | None=None, predicate: str | None=None,
    statements: dict[str, Any] | None=None, projection: dict[str, Any] | None=None,
    records: list[dict[str, Any]] | None=None,
) -> CallToolResult:
    """Derive a VP-07 migration source, VP-09 axes input or VP-10 cells input from a binding context, exactly as CLI from-plan.
    vpcells needs predicate (one per view) and reads coverage from binding-context/8.
    vpcells 0.11.0: plan_id null plus statements (aiaeao.cube.statement-set/1), optionally a projection record of
    lunados.lib project.aggregate-relations/v1; the aggregation is read, never recomputed.
    vpinstances (VP-11): a binding-context/9, plan_id null, statements = the trace, optional records
    (aiaeao.cube.conformance-record/1 of lunados.lib analyze.trace-conformance/v1); verdicts are read, never recomputed.
    vpsequence is not supported (VP-08 sources are declared directly). No files; declared_unverified.
    """
    return _result(plan_views.plan_source, context, plan_id, printer, tracks=track_map, track=track, labels=labels,
                   layers=layers, witness_prefixes=witness_prefixes, edge_styles=edge_styles, steps=steps,
                   subjects=subjects, profile=profile, predicate=predicate, statements=statements, projection=projection, records=records)


@mcp.tool()
def cube_plan_views(
    source: dict[str, Any], view: Literal['cube.phases','cube.flow','cube.sequence','cube.axes','cube.cells','cube.instances'],
    granularity: Literal['overview','standard','detail'], partition: str | None=None,
    rows: str | None=None, cols: str | None=None, lens: str | None=None,
    overflow: Literal['summarize','reject'] | None=None, locale: str | None=None,
    hide_ledger: bool | None=None, hide_empty: Literal['rows','cols','both'] | None=None,
    axis_order: list[str] | None=None,
) -> CallToolResult:
    """Print plan panels in memory: SVGs, panel inputs, index and report, byte-identical to CLI print-panels.
    Limits: 512 KiB per SVG, 2 MiB per response; over a limit isError, never truncated. Display only.
    C-12 options (only for 0.7.5 / 0.9.2 sources): locale (de, en) and hide_ledger for cube.phases / cube.flow,
    partition 'method-sets' (VP-07.5); locale and hide_empty for cube.axes, rows/cols Y × Y (VP-09.2).
    cube.cells (VP-10): Y × Y cell states (marked, checked, unknown, hidden) from declared coverage; locale, hide_empty.
    axis_order (cube.cells only, VP-10.1): declared order of the Y display IDs; marks entries above the diagonal as feedback.
    cube.instances (VP-11): a declared trace per instance, taken paths and join inputs; verdicts from lunados.lib records; locale.
    """
    return _result(plan_views.plan_views, source, view, granularity, partition=partition, rows=rows, cols=cols,
                   lens=lens, overflow=overflow, locale=locale, hide_ledger=hide_ledger or None, hide_empty=hide_empty,
                   axis_order=axis_order)


@mcp.tool()
def cube_plan_check(result: dict[str, Any]) -> CallToolResult:
    """Re-verify a cube_plan_views result like CLI check-panels (re-render, digests, coverage); no files."""
    return _result(plan_views.plan_check, result)

# CP-001 / G1: P0 resources remain primary; four legacy tools remain unchanged.
register_resources(mcp)

def main() -> None:
    mcp.run(transport='stdio')
