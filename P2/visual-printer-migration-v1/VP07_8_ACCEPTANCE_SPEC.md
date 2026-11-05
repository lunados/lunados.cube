# VP-07.8 — X endpoints, source, cache and revision in the migration printer · Acceptance specification

**Status:** IMPLEMENTED LOCALLY (TASK-075, 2026-11-05). G5 delivery is not part of this step.
**Profile:** `P2-VP-MIGRATION/0.7.8`, opt-in follow-up to `0.7.7` in the same package `vpmigration`. `0.7.0…0.7.7` stay byte-identical.
**Milestone:** [MILE-014](../../docs/02-Milestones/MILE-014-printer-x-endpoints.md) · Task: [TASK-075](../../docs/05-Tasks/TASK-075-vp078-x-endpoints.md)
**Requirement:** lunados.explorer after MILE-013: every remaining unprinted dependency of the five worked cases points at an X endpoint (mostly Admission) or at a source, cache or revision object. All have canonical VG anchors in P0 v9.4. VP-07.7 §1 left the X endpoints out as an open display question; a prototype on case F05 showed that the flow and phases panels draw a `form.contract-anchor` object as a card with its contract glyph and that `check-panels` passes.

## 1. Design

`0.7.8` is `0.7.7` with thirteen more rows in the closed concept table. Nothing else changes.

| Concept | Anchor | Form |
|---|---|---|
| `X:endpoint:perception`, `conclusion`, `authority`, `admission`, `expectation`, `satisfaction`, `delegation`, `completion`, `action`, `result` | `contract-pairs.<endpoint>` | `form.contract-anchor` |
| `Y:resource-object:source`, `cache`, `revision` | `resource-objects.<kind>` | `form.resource-card` |

Each form is the anchor's `form_suggestion` (P0 `validation/v1/visual/anchors.json`). X scopes (`X:scope:*`) have no VG anchor and stay unmapped; so do all other concepts outside the table.

**Display only.** Drawing an X endpoint says nothing about whether it is bound: P1.6 binds an X endpoint only with a scoped instantiation profile and filled slots (`P1_INSTANTIATION_PROFILE_REQUIRED` otherwise). The printer never checks or implies that binding.

## 2. Rules

| ID | Rule | Check |
|---|---|---|
| VP078-01 | 0.7.7 outputs are pinned **before** any 0.7.8 code (`scripts/pin_077_digests.py --write`) and stay byte-identical; 0.7.0…0.7.6 keep their pins | `pin_07x_digests.py --check`, `test_077_and_076_outputs_byte_identical` |
| VP078-02 | The 0.7.8 table is the 0.7.7 table plus exactly the thirteen rows of §1 | `test_table_is_077_plus_the_fixed_rows` |
| VP078-03 | A `/10` plan with all new concepts prints under 0.7.8 (`cube.flow` with origin lines and every endpoint anchor in the SVG, `cube.phases`), `check-panels` PASS | `test_new_rows_print_under_078`, `test_phases_view_under_078` |
| VP078-04 | The same plan under 0.7.7 still FAILs `VP07_ADAPTER_MAPPING` | `test_077_table_stays_closed` |
| VP078-05 | X scopes stay unmapped (`VP07_ADAPTER_MAPPING`) | `test_x_scopes_stay_unmapped` |
| VP078-06 | The statement path uses the same table | `test_statement_path_under_078` |
| VP078-07 | G6 equals the CLI byte for byte; capabilities list 0.7.8 | `test_g6_cli_files_byte_identical`, `test_table_is_077_plus_the_fixed_rows` |

## 3. Status and diagnostics

No new codes. `VP07_ADAPTER_INPUT` for statement path and origin lines now names `0.7.6`, `0.7.7` or `0.7.8`.

## 4. Boundaries

- Display only; everything stays `declared_unverified`.
- No domain accent colours for the contract anchors in `cube.flow` / `cube.phases`; the glyph identifies the endpoint.
- VP-04 budgets unchanged. G5 is not updated here.
