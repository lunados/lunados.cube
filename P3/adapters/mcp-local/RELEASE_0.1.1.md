# AIAEAO Cube Local MCP — P3-MCP-LOCAL/0.1.1

**Status:** local candidate, source-publication ready; host acceptance PENDING.
**Basis:** ADR-001 ACCEPTED; VP-06 frozen on `main`; pure local MCP/stdio.

## Changes from A1/0.1.0

- Fix SDK stdio smoke: wrap `StdioServerParameters` with `stdio_client(params)` explicitly.
- Fix Claude Desktop configuration generator: retain the `.venv/bin/python` path; never resolve its symlink to a system interpreter.
- Update local adapter capability version to `P3-MCP-LOCAL/0.1.1`.
- Clarify GitHub packaging: **publish P3 only**. No copy of frozen P2 or P0 assets.
- Include user-reported successful official SDK in-process and stdio smoke results; real Claude Desktop host still pending.

## Unchanged

Four tool names/signatures, all VP-06 renderer semantics and output bytes, safety limits, diagnostics, and absence of network/API endpoints. No P1 semantic validation.

## Evidence and gates

- Original offline bridge: 36/36; frozen VP-06: 237/237; VP-05 matrix: 90/90 (previous release evidence).
- On 2026-10-24 the user reported PASS for `sdk_smoke.py` and `sdk_stdio_smoke.py` on macOS with official MCP SDK v2. **Not independently reproduced here** due to SDK unavailable in build environment.
- Gate A requires a Claude Desktop connected-host session: list four tools, prepare/check/render identical SVG and report, and one negative `isError` diagnostic.

## Deploy boundary

GitHub contains **source code**. Claude Desktop launches a **local** server via stdio. No Cloudflare/Remote MCP endpoint is created in this release.
