# VP-07.7 — Module bodies, grant, evidence and content in the migration printer · Acceptance specification

**Status:** IMPLEMENTED LOCALLY (TASK-073, 2026-11-05). G5 delivery is not part of this step.
**Profile:** `P2-VP-MIGRATION/0.7.7`, opt-in follow-up to `0.7.6` in the same package `vpmigration`. `0.7.0…0.7.6` stay byte-identical.
**Milestone:** [MILE-013](../../docs/02-Milestones/MILE-013-printer-module-bodies.md) · Task: [TASK-073](../../docs/05-Tasks/TASK-073-vp077-module-bodies.md)
**Requirement:** lunados.explorer pilot F02 (2026-11-05): a P1.14-valid `/10` plan of a real migration could print only 5 of 42 dependencies with 0.7.6, because the adapter's closed table (AD-2 plus VP-07.6 Q-2) lacks the module bodies Core, Connector and Toolbox, Grant and the resource objects Evidence and Content. All of them have canonical VG anchors and forms in P0 v9.4.

## 1. Design

`0.7.7` is `0.7.6` with a larger closed concept table. Nothing else changes: origin lines, statement path, panels, budgets, header, legend and audit behave as in 0.7.6.

| Concept | Anchor | Form | Concept key |
|---|---|---|---|
| `Z:module-body:core` | `module-bodies.core` | `form.module-block` | `Core` |
| `Z:module-body:connector` | `module-bodies.connector` | `form.module-block` | `Connector` |
| `Z:module-body:toolbox` | `module-bodies.toolbox` | `form.module-block` | `Toolbox` |
| `Z:module-body:adapter` | `module-bodies.adapter` | `form.module-block` | `Adapter` |
| `Z:boundary:grant` | `governance-boundary.grant` | `form.boundary-frame` | `Grant` |
| `Y:resource-object:evidence` | `resource-objects.evidence` | `form.resource-card` | `Evidence` |
| `Y:resource-object:content` | `resource-objects.content` | `form.resource-card` | `Content` |

Every form is the anchor's `form_suggestion` (P0 `validation/v1/visual/anchors.json`), the same form as for the already mapped members of each family. The table stays closed: any other concept FAILs `VP07_ADAPTER_MAPPING` as before.

**Not in 0.7.7:** X endpoints (`X:endpoint:admission`, `X:endpoint:result`). Their anchors use `form.contract-anchor`, a marker, not a card; how an X endpoint appears as a node of a migration view is a separate display question.

## 2. Rules

| ID | Rule | Check |
|---|---|---|
| VP077-01 | 0.7.6 outputs are pinned **before** any 0.7.7 code (`scripts/pin_076_digests.py --write` on the unchanged code) and stay byte-identical; 0.7.0…0.7.5 keep their pins | `pin_07x_digests.py --check`, `test_076_outputs_byte_identical` |
| VP077-02 | The 0.7.7 table is the 0.7.6 table plus exactly the seven rows of §1 | `test_table_is_076_plus_the_fixed_rows` |
| VP077-03 | A `/10` plan with the new concepts prints under 0.7.7 (`cube.flow` with origin lines, `cube.phases`), `check-panels` PASS | `test_new_rows_print_under_077`, `test_phases_view_under_077` |
| VP077-04 | The same plan under 0.7.6 still FAILs `VP07_ADAPTER_MAPPING` | `test_076_table_stays_closed` |
| VP077-05 | X endpoints stay unmapped under 0.7.7 (`VP07_ADAPTER_MAPPING`) | `test_x_endpoints_stay_unmapped` |
| VP077-06 | The statement path (`statement-set/2`) uses the same table | `test_statement_path_under_077` |
| VP077-07 | G6 (`cube_plan_source`, `cube_plan_views`, `cube_plan_check`) equals the CLI byte for byte; capabilities list 0.7.7, `latest_profile` is 0.7.7 | `test_g6_cli_files_byte_identical`, `test_table_is_076_plus_the_fixed_rows` |

## 3. Status and diagnostics

No new codes. `VP07_ADAPTER_MAPPING`, `VP07_ADAPTER_INPUT` (statement path and origin lines need `0.7.6` or `0.7.7`) and every 0.7.6 code keep their meaning.

## 4. Boundaries

- Display only; everything stays `declared_unverified`. A drawn Core or Connector is no claim that the module exists, admits or acts.
- The VP-04 budgets are unchanged. A subject with more than three objects in one step does not fit one `cube.flow` panel at `detail`; slicing such a plan is the caller's job (lunados.explorer packs its print plans).
- G5 (`.g5-runtime`, remote surface) is not updated here.
