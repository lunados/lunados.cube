# AIAEAO Pure Cube — Local MCP Proof / PoC-A

**Status:** Local MCP release candidate. Adapter and VP-06 parity tested; official MCP SDK in-process and stdio smoke PASS **as reported by the user on macOS 2026-10-24**. A real Claude/Grok host connection remains **not yet accepted**. Gate A remains PENDING until the actual host test.

**Decision:** ADR-001 ACCEPTED on 2026-10-24. Version `P3-MCP-LOCAL/0.1.1`. No online endpoint, HTTP API, WebMCP, P1 execution or modification to P0/P1/P2.

## Scope

Four tools, in order:

1. `cube_get_capabilities()` — frozen core capability card under `core`, local-only adapter metadata under `adapter`.
2. `cube_prepare_print(bundle, lens, granularity, overflow, focus, max_items, max_edges)` — SHA-bound VP-04 job, directly via frozen `make_job()`.
3. `cube_check_print(job)` — unmodified VP-06 `render_job()` report, no SVG.
4. `cube_render_svg(job)` — full, unchanged SVG **as UTF-8 text** and unmodified VP-06 audit report. The SDK returns both `structuredContent` and text fallback.

**Errors:** Exact `VP06_*` diagnostic appears as `structuredContent` and text fallback; MCP `isError=true`. The wrapper is not a P1 verification or admission guarantee. Input max 2 MiB per tool; inline SVG max 512 KiB; no incoming URLs, paths or filesystem outputs.

The adapter uses the **official MCP Python SDK v2**, not a handwritten JSON-RPC implementation. Python **3.11+** recommended for SDK v2, even though frozen VP-06 itself supports Python 3.10+. Exact direct dependency is pinned in `requirements-mcp.txt`. This PoC does not ship a complete transitive lockfile; generate it on the target machine before a controlled release.

## Mac quickstart

Use this **P3-only release overlay** within an up-to-date checkout of `lunados/lunados.cube` (it requires the existing sibling `P2/` tree). In Terminal (from the repository root):

```bash
cd P3/adapters/mcp-local
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-mcp.txt
python scripts/verify_local.py
python scripts/sdk_smoke.py
python scripts/sdk_stdio_smoke.py
python scripts/generate_claude_config.py
```

`verify_local.py`: bridge unit/parity/security tests and no SDK requirement. `sdk_smoke.py`: **real** SDK in-process. `sdk_stdio_smoke.py`: **real** SDK transport starting a child process over stdin/stdout, checking discovery and actual SVG contents against the golden file. **Do not mark host gate PASS just because unit tests pass.**

### Claude Desktop

Copy the output of `python scripts/generate_claude_config.py` into the MCP servers section of your Claude Desktop configuration (merge the `aiaeao-cube` entry with any existing entries; do not replace existing unrelated servers). On macOS the usual configuration file location is:

`~/Library/Application Support/Claude/claude_desktop_config.json`

The paths must be **absolute** and use the Python interpreter from the virtual environment. Restart Claude Desktop, inspect the available tools and invoke `cube_get_capabilities` before printing.

Try this agent task:

> Identify your connected AIAEAO Cube tools. From the explicit VP-03 `flow_provenance_standard` example bundle, select the declared Provenance lens and Standard granularity; prepare, check and render the SVG. Return the actual SVG source or save it if your host supports artifacts. Quote the SVG SHA-256 and explain whether P1 validity was assessed.

The example bundle must be provided through host-accessible project context, pasted into the tool call, or copied into the agent context. MCP tools intentionally **do not read arbitrary files or GitHub URLs**. The tool list is self-describing, but the server does not automatically import the bundled example into an agent workspace.

### Capture the host acceptance

1. Client and version; official SDK and protocol revisions; configuration method.
2. `tools/list` shows all four names; source and form IDs unchanged.
3. Tool call produces **real** SVG source and report (not a textual claim), equals golden SHA-256.
4. Negative case produces `isError=true` + complete `VP06_*` diagnostic.
5. Note if host can display, attach or export SVG. **Not all clients render SVG inline.**
6. Record `PASS`, `FAIL` or `UNSUPPORTED_HOST` explicitly in `evidence/HOST_ACCEPTANCE_TEMPLATE.md`.

## Safety and boundaries

Never pass arbitrary file paths or URIs; neither feature exists. Do not offer `cube_validate`: P1 has not been wrapped or invoked. Do not infer view structure, Lens facets, measurement values or Authority/Admission. The adapter returns declared, **unverified** visual projections. The output XML is checked for active elements, external attributes, event handlers and resource URLs before transport. The generated source is still untrusted display content in a client.

Reference: original `P2/visual-printer-release-v1/agent/AGENT_QUICKSTART.md` and `ADR-001_APPROVAL.md` at the ZIP root.


## A1.1 release note

See [RELEASE_0.1.1.md](RELEASE_0.1.1.md): patched official SDK stdio smoke transport, preserved virtualenv interpreter path in Claude config generation, updated adapter version, and captured user-reported macOS test evidence. No semantic, rendering or safety policy changes.

---

## G4 consolidated capability surface

**Current G4 release candidate: `P3-MCP-LOCAL/0.2.0-rc1`.** See [G4_README.md](G4_README.md) and [G4_INSTALL.md](G4_INSTALL.md). Whole-Cube discovery uses new `cube_discover_surface` (seven MCP tools); the legacy `cube_get_capabilities` remains intentionally **P2-only**, including its historic adapter version/tool list. For host-specific acceptance see [G4_CLAUDE_ACCEPTANCE.md](G4_CLAUDE_ACCEPTANCE.md).
