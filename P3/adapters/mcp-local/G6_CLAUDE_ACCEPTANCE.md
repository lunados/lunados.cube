# Copyable prompt for Claude Desktop — G6 only

Run a real MCP tool and host acceptance test for the local **AIAEAO Cube G6** server (plan views). Do not edit any files, do not use web search and use only synthetic fixtures from the repository (no client data).

1. Call **`cube_discover_surface`**: report the release version (`P3-MCP-LOCAL/0.3.0-rc1`), all ten tools and the section `domains.P2.plan_views` (views, printers, profiles, limits). Confirm `remote_available: false` and that `cube_get_capabilities` still reports the legacy P2-only card.
2. Read `P2/visual-printer-migration-v1/fixtures/golden_v074.json` yourself and pass its `context`, `plan_id` and `profile` to **`cube_plan_source`** with `printer: vpmigration`. Report the source profile and the number of cells and transitions.
3. Call **`cube_plan_views`** with that source, `view: cube.flow`, `granularity: standard`, `partition: subject`, `lens: cube.lens.execution`. Report the panel count, the coverage status and, for one panel of step p2, the methods line (`TRANSITIONS AT p2 (declared) …`). Show one SVG if the host can render it.
4. Call **`cube_plan_check`** with the unchanged result: expect `PASS`. Change one character in one panel's `svg` and call it again: expect `isError` with `VP07_PANEL_COVERAGE`.
5. `cube.sequence`: pass the `sequence_source` of `P2/visual-printer-sequence-v1/fixtures/golden_sequence.json` to `cube_plan_views` (`granularity: standard`); report panels and coverage.
6. `cube.axes`: `cube_plan_source` with `printer: vpaxes`, `profile: P2-VP-AXES/0.9.1` on `P2/visual-printer-axes-v1/fixtures/golden_axes.json`, then `cube_plan_views` with `rows: F`, `cols: Z:referent`; report `binding_coverage`.
7. Errors as tool results: `view: cube.matrix` → `P3_PLAN_VIEW_UNKNOWN`; `cube_plan_source` with `printer: vpsequence` → `P3_PLAN_SOURCE_UNSUPPORTED`; `granularity: detail` for `cube.axes` `Z:referent × T` on the 30-job context of vector A-18 → `VP09_AXES_BUDGET`. Each must arrive as `isError` with a full diagnostic, not as a host failure.
8. Confirm no file was written and nothing claims truth, authority or admission (`NOT_EVALUATED`).
9. Report PASS/FAIL per step, host limitations (e.g. large tool results, SVG display) and whether G6 can be accepted.

Only genuine tool calls count, no simulated replies or implementation changes.
