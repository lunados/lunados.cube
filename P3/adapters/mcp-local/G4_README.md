# AIAEAO Cube — G4 Local MCP consolidated release

**Version:** `P3-MCP-LOCAL/0.2.0-rc1` · **Profile:** G4 / CP-001 · **Status:** locally verified release candidate; genuine target macOS and Claude Host reconfirmation pending.

## What is actually shipped

This is one **self-contained P3 overlay** that supersedes the sequence P3 0.1.1 → G1 → G1.1 → G2 → G3. It requires the already-published, unchanged `P1/` and `P2/` directories beside `P3/` in `lunados.cube`. P0 v9.4 is a locked local P3 snapshot used for reference Resources and the tool fallback. No P0/P1/P2 files are patched by G4.

* P0: 13 pinned, offline v9.4 document references + one Resource index (`aiaeao://p0/resources/v1`). The Claude remote-devices bridge may not expose Resources; `cube_read_reference` provides paged tool-only access to identical bytes.
* P1: `cube_validate`, unchanged P1-VC/1.0.0 report, including `PASS`, `FAIL`, `UNRESOLVED`, and separate adapter errors.
* P2: the original four offline SVG Printer tools and their original signatures and responses.
* G4: **`cube_discover_surface`**, the whole-Cube capability inventory, distinguishing the three domains and transport limits.

## All seven tools, in stable discovery order

1. `cube_get_capabilities` — **legacy P2-only** capability card. Its original `adapter.tools` and `adapter.p1_validation: false` are intentionally preserved.
2. `cube_prepare_print` — prepare an explicit VP-04 job, no inferred facets.
3. `cube_check_print` — P2 projection check, **not** P1 validation.
4. `cube_render_svg` — memory-only SVG + P2 report.
5. `cube_read_reference` — allowlisted, paged P0 fallback for hosts that hide Resources.
6. `cube_validate` — P1 descriptive validation.
7. `cube_discover_surface` — **entire P0/P1/P2 interface**, current version and actual availability.

**Discovery priority for agents:** call `cube_discover_surface` for whole-Cube questions. Call `cube_get_capabilities` only for VP-06 Printer dimensions/budgets. The latter continues reporting the legacy P3 0.1.1 printer-adapter card; this is compatibility, not the G4 release version.

## Zero semantic promotion

P0 source integrity is not truth. P1 semantic status is not authority or admission. P2 render success is not P1 status or source evidence. MCP connection success is not a semantic outcome. No automatic ACG → VP-03 conversion, external network access, remote MCP or WebMCP is included.

## Local test

Run from `P3/adapters/mcp-local/` inside the existing repo:

```sh
source .venv/bin/activate
python scripts/verify_g4.py
python scripts/sdk_g4_stdio_smoke.py
python scripts/sdk_g3_stdio_smoke.py
python scripts/generate_claude_config.py
```

`verify_g4.py` needs only Python stdlib for its required tests; `jsonschema>=4` adds a strict independent schema gate. The two `sdk_*_smoke.py` programs require **official MCP SDK v2** installed from `requirements-mcp.txt` and launch the real server as a child process through `stdio`. This release has NOT been executed inside Claude Desktop here; that is the target-host acceptance.

No GitHub or Cloudflare deployment was performed while creating G4. Source files in `P1/` and `P2/` are dependencies, not bundled or altered by this overlay. `G4_INSTALL.md` uses the existing Finder → `~/cube-patches` → `rsync` workflow.
