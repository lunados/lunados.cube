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


---

# C-12 runs (VP-07.5, VP-09.2) — same rules as above

Run after steps 1–9, with the same server. Only synthetic repository fixtures; no file edits; genuine tool calls only.

10. **Discovery:** `cube_discover_surface` lists `P2-VP-MIGRATION/0.7.5` and `P2-VP-AXES/0.9.2` under `domains.P2.plan_views.printers` and `display_options` with `locale: [de, en]`, `hide_ledger`, `method-sets` and `hide_empty: [rows, cols, both]`.
11. **Locale de:** `cube_plan_source` on `P2/visual-printer-migration-v1/fixtures/golden_v075.json` (`context`, `plan_id`, `profile` 0.7.5, `printer: vpmigration`), then `cube_plan_views` with `view: cube.phases`, `partition: subject`, `granularity: standard`, `locale: de`. Report the header line (`CUBE.PHASES · DEKLARIERTE SCHRITTE …`), one step header (`p2 · Zwischenstand`), one bar label with a German predicate, and `report.locale`. Confirm the IDs are unchanged.
12. **Ledger hidden:** the same source with `view: cube.flow`, `partition: subject`, `lens: cube.lens.execution`, `hide_ledger: true` (and `locale: de`). Confirm no `DECLARATION LEDGER` / `DEKLARATIONSREGISTER` text in the panels, `report.ledger_hidden: true`, and `cube_plan_check` PASS on the unchanged result.
13. **Method sets (not only `none`):** the same source with `view: cube.phases`, `partition: method-sets`, `granularity: standard`. Report `report.method_sets` (per set: panels, cell count, status). Expect import 26, rebuild 12, retire 16, rewrite 16, none 1 (only `g01`), all `COMPLETE`; the import / retire bars are in their sets, not in `none`. `cube_plan_check` PASS.
14. **Y × Y:** `cube_plan_source` with `printer: vpaxes`, `profile: P2-VP-AXES/0.9.2` on `P2/visual-printer-axes-v1/fixtures/golden_v092.json`, then `cube_plan_views` with `view: cube.axes`, `rows: Y:referent`, `cols: Y:referent`, `granularity: standard`, `hide_empty: both`. Expect cells `acme:ops-desk|acme:archive-store` = `y01 · depends-on` and `acme:archive-store|acme:backup-vault` = `y02 · recovers-via`, `hidden_rows: [acme:backup-vault]`, `hidden_cols: [acme:ops-desk]`.
15. **F × T with arguments:** the same 0.9.2 source with `rows: F`, `cols: T`, `locale: de`. Report the p2 entries, e.g. `t-mail-cut · import: acme:legacy-mail → acme:new-mail` and `a01a · rewrite: acme:account-01 → acme:new-directory`, and the German header.
16. **Old profiles stay as they were:** `locale: de` on the 0.7.4 source of step 2 → `isError` `VP07_LOCALE_INVALID`; `rows: Q` on the 0.9.2 source → `isError` `VP09_AXIS_INVALID` whose diagnostic says `profile: P2-VP-AXES/0.9.2`.
17. Report PASS/FAIL per step 10–16 and host limitations (response size, SVG display).
