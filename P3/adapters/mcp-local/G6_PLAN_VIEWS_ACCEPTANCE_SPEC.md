# G6 — Plan views as local MCP tools · Acceptance specification

**Status:** DRAFT 2026-10-28 — decisions D-1…D-10 open, no code.
**Release (proposed):** `P3-MCP-LOCAL/0.3.0-rc1`, successor of `0.2.0-rc1` (G4) in `P3/adapters/mcp-local`; stdio only.
**Requirement:** C-13 from the running migration field test (2026-10-28; an inventory of 38 referents, 60 dependencies, 4 steps, 3 transitions, 36 method bindings rendered in 24 runs with VP-07.3/.4 and VP-09.1; client details withheld).
**Basis:** `G4_README.md`, `G4_ACCEPTANCE.md`, `G4_CLAUDE_ACCEPTANCE.md` (surface, host acceptance pattern), `aiaeao_mcp_local/bridge.py` (in-memory VP-06 bridge: 2 MiB argument limit, 512 KiB SVG limit, diagnostics as `isError`), `surface.py` and `spec/G4_CAPABILITY_SURFACE.schema.json`; P2 VP-07 (`P2-VP-MIGRATION/0.7.0…0.7.4`), VP-08 (`P2-VP-SEQUENCE/0.8.0`), VP-09 (`P2-VP-AXES/0.9.0…0.9.1`) with their `print_panels` / `check_panels` / `from_plan` APIs; ADR-001 (local first; no remote hosting without a decision).
**Motivation:** The local MCP server offers only VP-06 (`cube.flow`, `cube.diagramm`, `cube.tree`). VP-07, VP-08 and VP-09 run only through their CLIs with `--out` folders, so an agent must write inputs to disk, run the CLI and read files back.

| Finding | Effect |
|---|---|
| `print_panels` of all three printers already returns `(report, files)` in memory | The renderers need no change; only a transport is missing |
| `check_panels(directory)` reads a folder | An in-memory check needs a files mapping instead of a path |
| VP-08 has no `from-plan`; its sources are declared directly | `cube_plan_source` cannot derive a VP-08 source (D-7) |
| A VP-07 report embeds its source; VP-09 panel inputs embed the whole axes input | Responses grow with plan size; a hard limit is needed (C-13 §3) |

## 0. Scope

| In scope | Out of scope |
|---|---|
| In-memory API per printer (`vpmigration`, `vpsequence`, `vpaxes`): JSON in, `{panels, index, report}` out, no paths, no side effects | Changes to any existing P2 output, profile or CLI behaviour |
| Three tools `cube_plan_source`, `cube_plan_views`, `cube_plan_check` in the local stdio server | Remote (G5) exposure — needs its own decision because contexts may hold client data (C-13 §5) |
| Hard limits 512 KiB per SVG, 2 MiB per response; FAIL with own code and a hint | Silent truncation, paging (D-6) |
| `cube_discover_surface` lists tools, views, profiles and limits | Changes to `cube_get_capabilities` (legacy card stays byte-identical) |
| Parity with the CLI over all existing vectors; SDK v2 stdio smoke; Claude Desktop host acceptance | P0, P1 changes |

## 1. Design summary

1. **In-memory API (P2, additive).** Each printer package gets a module `api.py` (D-2):
   - `source(context, plan_id, **options)` → the printer's input document (VP-07 migration source or VP-09 axes input) and the mapping, exactly as `from-plan` writes them;
   - `views(source, view, **options)` → `{format, printer, profile, view, panels: [{name, svg, sha256, input, input_sha256}], index: {svg, sha256}, report}` (D-3);
   - `check(views_result)` → the same object `check-panels` prints.
   `check_panels(directory)` becomes "read the directory, then `check_files(files)`"; the CLI output stays byte-identical.
2. **Tools.** The view decides the printer, not the tool name:

   | `view` | Printer | Source format |
   |---|---|---|
   | `cube.phases`, `cube.flow` | `vpmigration` | `aiaeao.cube.vp07-migration-source/1` |
   | `cube.sequence` | `vpsequence` | VP-08 sequence source |
   | `cube.axes` | `vpaxes` | `aiaeao.cube.vp09-axes-input/1` (or a VP-07 source) |

   - `cube_plan_source(context, plan_id, printer, track_map?, track?, labels?, layers?, witness_prefixes?, edge_styles?, steps?, subjects?, profile?)` → `{source, mapping}`.
   - `cube_plan_views(source, view, granularity, partition?, rows?, cols?, lens?, overflow?)` → the `views` result.
   - `cube_plan_check(result)` → the `check` result (D-4).
3. **Limits.** Arguments ≤ 2 MiB (as `bridge.py`); every SVG ≤ 512 KiB; the whole response ≤ 2 MiB, measured on the canonical JSON payload (D-5). Over a limit: FAIL with a P3 code, the measured size, the limit and a hint ("choose a partition, a smaller granularity or a step/subject slice"); nothing partial is returned (D-6).
4. **Errors.** Printer errors pass through unchanged as the diagnostic (`VP07_*`, `VP08_*`, `VP09_*`, with code, stage, message) and `isError: true`; P3 adds only transport codes (§2).
5. **Surface.** `cube_discover_surface` gets the three tools in its tool list and a section `domains.P2.plan_views` with views, printers, profiles (from each printer's capabilities), limits, `files_returned_inline: true`, `filesystem_side_effects: false`, `remote_available: false`. `spec/G4_CAPABILITY_SURFACE.schema.json` is extended additively (or a G6 schema, D-1).
6. **Data handling.** Tools never write files, never log arguments, never fetch anything; a response contains only what follows from its arguments. G5 does not list the tools (C-13 §5).

### 1.1 Shape (illustrative, synthetic)

```json
{
  "format": "aiaeao.cube.plan-views/1",
  "printer": "vpmigration", "profile": "P2-VP-MIGRATION/0.7.4", "view": "cube.flow",
  "panels": [{"name": "panel-07", "svg": "<?xml …", "sha256": "…", "input": {"format": "aiaeao.cube.vp07-panel-input/1", "…": "…"}, "input_sha256": "…"}],
  "index": {"svg": "<?xml …", "sha256": "…"},
  "report": {"format": "aiaeao.cube.vp07-panel-report/1", "coverage": {"status": "COMPLETE"}, "…": "…"}
}
```

## 2. Status and diagnostic rules (proposed)

| Situation | Result | Code |
|---|---|---|
| Printer error (invalid context, budget exceeded, partition impossible, …) | `isError`, full printer diagnostic | `VP07_*` / `VP08_*` / `VP09_*` (unchanged) |
| Arguments over 2 MiB or not finite JSON | `isError` | `P3_PLAN_INPUT_INVALID` (new) |
| `view` not one of the four | `isError` | `P3_PLAN_VIEW_UNKNOWN` (new) |
| `view` does not fit the source format, or an option the printer does not take (e.g. `rows` for `cube.phases`) | `isError` | `P3_PLAN_ARGUMENT_INVALID` (new) |
| `cube_plan_source` with `printer: vpsequence` | per D-7 | `P3_PLAN_SOURCE_UNSUPPORTED` (new) |
| One SVG over 512 KiB | `isError`, panel name and size, hint | `P3_PLAN_SVG_TOO_LARGE` (new) |
| Response over 2 MiB | `isError`, size, hint | `P3_PLAN_RESPONSE_TOO_LARGE` (new) |
| `cube_plan_check` on a modified result | `isError`, printer diagnostic | `VP07_PANEL_COVERAGE` / `VP08_…` / `VP09_PANEL_COVERAGE` |

Every diagnostic carries `printer`, `profile` (of the input where known), `stage`, `message`; `epistemic_warrant`, `current_authority`, `canonical_admission` stay `NOT_EVALUATED`.

## 3. Rules in detail

### 3.1 In-memory API (MA)

- MA-1: `views` returns exactly the files `print-panels` writes: for each panel its SVG (UTF-8 text) and its input (parsed JSON whose canonical encoding equals the `.input.json` bytes), the index SVG and the report. Digests are SHA-256 of those bytes.
- MA-2: `check` rebuilds the files mapping from a `views` result and applies the unchanged checks of `check-panels`; the directory form only reads files and delegates.
- MA-3: No module-level state, no temp files, no environment reads; equal inputs give equal bytes.

### 3.2 Parity (MP)

- MP-1: For every PASS vector of VP-07 (V, W, L, M, N), VP-08 (S) and VP-09 (A, B) that prints panels, the CLI output directory and the `views` result have identical SHA-256 per file; `from-plan` outputs equal `source` (D-10).
- MP-2: For every FAIL vector, MCP returns `isError` with the same code as the CLI.

### 3.3 Tools (MT)

- MT-1: Tool arguments are JSON objects only — no paths, URLs or file names.
- MT-2: `profile` passes through to the printer's `from-plan` unchanged; without it the printer's own default applies (D-8).
- MT-3: Text content and `structuredContent` carry the same canonical JSON (as `bridge.py`).

## 4. Acceptance criteria (draft)

| AC | Requirement | Evidence |
|---|---|---|
| G6-01 | P0, P1 and all P2 profiles byte-identical; pinned digests 0.7.0…0.7.4, 0.9.0…0.9.1 and VP-08 golden unchanged | regression run |
| G6-02 | In-memory API MA-1…MA-3; `check-panels` CLI output unchanged | K-01…K-04 |
| G6-03 | Tools MT-1…MT-3 and the view dispatch | K-05…K-10 |
| G6-04 | Every §2 row yields exactly the stated code | K-11…K-16 |
| G6-05 | Parity MP-1, MP-2 over all vectors | K-17 |
| G6-06 | `cube_discover_surface` lists tools, profiles, limits; `cube_get_capabilities` byte-identical; surface schema valid | K-18 |
| G6-07 | SDK v2 stdio smoke (`scripts/sdk_g6_stdio_smoke.py`) | smoke |
| G6-08 | Host acceptance in Claude Desktop after the G4 pattern (`G6_CLAUDE_ACCEPTANCE.md`) | user, on the target Mac |
| G6-09 | No client data in fixtures, examples or evidence | review |

## 5. Alignment vectors (draft)

| ID | Case | Expected |
|---|---|---|
| K-01 | `api.views` on the VP-07.3 golden, `cube.phases` by subject | PASS, bytes equal to the CLI directory |
| K-02 | `api.check` on that result | PASS, equal to `check-panels` output |
| K-03 | `check-panels` CLI after the refactor on all pinned directories | outputs unchanged |
| K-04 | Two calls with equal arguments | equal bytes |
| K-05 | `cube_plan_source` vpmigration on a /7 context | `source` equal to CLI `from-plan` |
| K-06 | `cube_plan_source` vpaxes with `profile: P2-VP-AXES/0.9.1` | equal to CLI |
| K-07 | `cube_plan_views` `cube.flow`, lens execution, 0.7.4 source | PASS, methods lines present |
| K-08 | `cube_plan_views` `cube.sequence` on the VP-08 golden | PASS |
| K-09 | `cube_plan_views` `cube.axes` F × Z panels (0.9.1) | PASS, binding coverage COMPLETE |
| K-10 | `cube_plan_check` on an unmodified result | PASS |
| K-11 | Invalid context (`binding-context/9`) | `isError` · `VP07_ADAPTER_INPUT` |
| K-12 | `view: cube.matrix` | `isError` · `P3_PLAN_VIEW_UNKNOWN` |
| K-13 | `cube.axes` detail over budget | `isError` · `VP09_AXES_BUDGET` |
| K-14 | Response over 2 MiB (synthetic plan with many panels) | `isError` · `P3_PLAN_RESPONSE_TOO_LARGE`, size and hint |
| K-15 | `cube_plan_check` with one SVG byte changed | `isError` · `VP07_PANEL_COVERAGE` |
| K-16 | `cube_plan_source` printer vpsequence | per D-7 |
| K-17 | Parity sweep MP-1/MP-2 over V, W, L, M, N, S, A, B | all equal |
| K-18 | `cube_discover_surface` | ten tools; plan views section; legacy card unchanged |

## 6. Decisions (open)

| Decision | Options | Proposal | Consequence |
|---|---|---|---|
| D-1 Release | (a) `P3-MCP-LOCAL/0.3.0-rc1`, surface schema extended additively · (b) `0.2.1-rc1` · (c) separate G6 schema | **(a)** | New tools are a feature release; the G4 surface stays readable by old clients (additive fields). |
| D-2 Where the in-memory API lives | (a) additive `api.py` in each P2 package + `check_files` refactor (directory form delegates, outputs identical) · (b) in the P3 adapter only (temp folders for the check) · (c) a new P2 umbrella package | **(a)** | The API is usable without MCP (tests, other hosts); (b) would need temp files — a side effect C-13 rules out. The refactor touches frozen code paths, so K-03 pins the CLI outputs. |
| D-3 Content of a views result | (a) panels with SVG and input plus digests, index, report · (b) SVGs only | **(a)** | `cube_plan_check` can verify a result without a second render; the client keeps everything in memory. |
| D-4 Input of `cube_plan_check` | (a) the views result as returned · (b) separate `panels`, `index`, `report` arguments | **(a)** | One object round-trips; nothing to assemble by hand. |
| D-5 Measuring the 2 MiB | (a) canonical JSON of the payload once (text and `structuredContent` carry the same JSON) · (b) both copies | **(a)** | Matches the limit a client sees in either channel; (b) would halve the usable size. |
| D-6 Over the limit | (a) FAIL with code, measured size and hint; nothing partial · (b) paging with a continuation token | **(a)** | Same rule as the printers (no silent omission); paging can follow as its own step. |
| D-7 VP-08 in `cube_plan_source` | (a) not supported — VP-08 sources are declared directly; `P3_PLAN_SOURCE_UNSUPPORTED`; views and check accept them · (b) identity: validate and return the source | **(a)** | VP-08 has no adapter from binding contexts; (b) would suggest one exists. |
| D-8 Default profile | (a) the printer's own default (as the CLI; /7 → 0.7.3, VP-09 → 0.9.0) · (b) latest profile | **(a)** | Same call, same bytes as the CLI (VP-07.4 D-1, VP-09.1 D-1). |
| D-9 Single image without panels (`print-axes`, `print-phases`) | (a) not in this stage; always panels (one panel when it fits) · (b) a fourth tool `cube_plan_render` | **(a)** | Panels cover every case with proven coverage; one more tool can follow. |
| D-10 Parity reference | (a) the CLI output directories via subprocess for every vector · (b) the Python `print_panels` only | **(a)** | C-13 asks for CLI equality; (b) would not catch a CLI-side difference. |

## 7. Not part of G6

- G5 / remote exposure of plan tools (separate decision on client data).
- Paging of large results; a single-image tool (D-9).
- C-12 display options (locale, hidden ledger, Y × Y, …); they reach MCP automatically as new profiles once implemented.
