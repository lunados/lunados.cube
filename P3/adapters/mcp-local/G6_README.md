# AIAEAO Cube — G6 plan views as local MCP tools

**Version:** `P3-MCP-LOCAL/0.3.0-rc1` · **Requirement:** C-13 · **Spec:** `G6_PLAN_VIEWS_ACCEPTANCE_SPEC.md` (D-1…D-10 resolved)
**Status:** locally verified release candidate; SDK v2 stdio smoke PASS in the build environment; Claude Desktop host acceptance on the target Mac pending (`G6_CLAUDE_ACCEPTANCE.md`).

## What changes

Three tools join the seven G4 tools of the local stdio server; the view decides the printer:

| Tool | Does | Returns |
|---|---|---|
| `cube_plan_source(context, plan_id, printer, track_map?, track?, labels?, layers?, witness_prefixes?, edge_styles?, steps?, subjects?, profile?)` | `from-plan` of VP-07 (`vpmigration`) or VP-09 (`vpaxes`); `vpsequence` → `P3_PLAN_SOURCE_UNSUPPORTED` (VP-08 sources are declared directly) | `{format, printer, profile, source, mapping}` |
| `cube_plan_views(source, view, granularity, partition?, rows?, cols?, lens?, overflow?, locale?, hide_ledger?, hide_empty?)` | `print-panels` in memory; `view` ∈ `cube.phases`, `cube.flow` (VP-07), `cube.sequence` (VP-08), `cube.axes` (VP-09) | `{panels: [{name, svg, sha256, input, input_sha256}], index, report}` |
| `cube_plan_check(result)` | `check-panels` on a `cube_plan_views` result | the `check-panels` object plus `printer` |

- **Byte-identical to the CLIs:** 201/201 from-plan and print-panels steps over the vectors V, W, L, M, N, O (VP-07), S (VP-08), A, B, H (VP-09) — file by file (SHA-256) for PASS, the same code for FAIL (`scripts/parity_g6.py`).
- **Limits:** arguments ≤ 2 MiB, each SVG ≤ 512 KiB, each response ≤ 2 MiB (canonical JSON, measured once). Over a limit: `isError` with `P3_PLAN_INPUT_INVALID`, `P3_PLAN_SVG_TOO_LARGE` or `P3_PLAN_RESPONSE_TOO_LARGE`, the measured size, the limit and a hint (partition, granularity, slice). Nothing is truncated.
- **Errors:** printer diagnostics (`VP07_*`, `VP08_*`, `VP09_*`) pass through unchanged, plus `printer` and `input_profile`; P3 adds `P3_PLAN_VIEW_UNKNOWN`, `P3_PLAN_ARGUMENT_INVALID` (option the view does not take, or a source of another printer), `P3_PLAN_SOURCE_UNSUPPORTED`.
- **No side effects:** no paths, no files, no network; P2 renderers unchanged (`api.py` per printer; `check_panels(directory)` delegates to `check_files(files)`, outputs pinned).
- **Discovery:** `cube_discover_surface` (local) reports `P3-MCP-LOCAL/0.3.0-rc1`, ten tools and `domains.P2.plan_views` (views, printer profiles, limits). `cube_get_capabilities` and the G4 card `surface.discover_surface()` are byte-identical; the G5 remote surface is derived from that card and therefore lists **no** plan tools (C-13 §5). G5 needs no redeploy.

## C-12 options (VP-07.5, VP-09.2)

`cube_plan_source` with `profile: P2-VP-MIGRATION/0.7.5` or `P2-VP-AXES/0.9.2` yields the new sources. Only for those,
`cube_plan_views` accepts:

| View | Option | Effect |
|---|---|---|
| `cube.phases`, `cube.flow` | `locale: de` | German display text (pinned locale file; `en` = identity); IDs, method IDs, `decl:` references unchanged |
| `cube.phases`, `cube.flow` | `hide_ledger: true` | drawn declaration ledger left out; report and embedded ledger unchanged |
| `cube.phases`, `cube.flow` | `partition: method-sets` | one set of panels per method with every bar named by its bindings; `method_sets`, `memberships` |
| `cube.axes` | `locale: de` | German header, legend, rules, step roles, predicate names |
| `cube.axes` | `hide_empty: rows/cols/both` | values without entries left out before the budget check |
| `cube.axes` | `rows: Y:referent, cols: Y:referent` | new pair Y × Y; F × T entries carry their arguments |

On older sources the printer answers with its own code (`VP07_LOCALE_INVALID`, `VP07_PANEL_PARTITION`,
`VP09_LOCALE_INVALID`, `VP09_SOURCE_INVALID`); an option the view does not take is `P3_PLAN_ARGUMENT_INVALID`.
0.7.5 / 0.9.2 diagnostics name their input profile. Local discovery lists the new profiles under
`domains.P2.plan_views.printers` and the options under `display_options`. The G4 card and therefore G5 are unchanged:
G5 gets plan tools only after its own decision (migration contexts can hold client data).

## Local test (target Mac)

```bash
cd ~/SitesHeroku/lunados.cube/P3/adapters/mcp-local
source .venv/bin/activate          # as for G4; mcp==2.0.0 from requirements-mcp.txt
python scripts/verify_g6.py        # unit tests, K-01…K-18, CLI parity, pinned baseline, G4/G3 regression
python scripts/sdk_g6_stdio_smoke.py
```

Then restart Claude Desktop (the configured server is the same `run_server.py`) and run `G6_CLAUDE_ACCEPTANCE.md`.

## Notes

- The G4 SDK smoke (`scripts/sdk_g4_stdio_smoke.py`) expects the seven-tool 0.2.0-rc1 server; `sdk_g6_stdio_smoke.py` supersedes it.
- `tests/test_g4_surface.py::test_registrations_match` now expects the seven G4 tools first and the three plan tools after them.
- The build environment ran the smoke with `mcp` 2.3.0; the pin stays `mcp==2.0.0`.
- Migration contexts may contain client data: the tools stay local (stdio). A remote variant needs its own decision.
