# VP-12 — Landscape view (`cube.landscape`) · Acceptance specification

**Status:** DRAFT for MILE-016 (B6, B10), 2026-11-05. Decisions D-1…D-8 proposed; vectors L-01…L-14 after confirmation, oracle before code.
**Profile:** `P2-VP-LANDSCAPE/0.12.0`, new package `P2/visual-printer-landscape-v1/` (`vplandscape`). Reuses the VP-07 migration source (`from-plan`, VP-07.8) and drawing helpers; changes no existing profile.
**Basis:** Morphology 01.3 (Y × Z: identity and resources against materialization and boundary, derived; T as declared steps); VP-09 CM-3 (introduced/retired markers from transitions) and CM-6 (dependencies between Y and Z referents with predicate); VP-10.1 declared axis order; MILE-011 origin lines; the "current and target" overview of an earlier project run (layers platform → dns → provider → account → system, current and target stacked, retired and introduced, found in repository vs planned).
**Motivation:** The plan views are complete but fine-grained (many panels per plan). A landscape shows on one page which resources, accounts and modules exist at a declared step, how they hang together, and what a migration retires and introduces.

## 0. Scope

| In scope | Out of scope |
|---|---|
| Y and Z referents of a plan as nodes in declared layer columns | X endpoints as nodes (they stay in `cube.flow` and X × Y) |
| Two or more declared steps stacked (default first and last) | A time scale; animation |
| Dependencies holding at each step as edges with predicate; placement predicates drawn heavier | Inferred placement; transitive edges |
| Introduced / retired markers at a step (from transitions) | Judging the migration |
| Edge style by declared origin (MILE-011 origin lines) | Colour as a verdict |
| Status line of the crossing (B10): `Y × Z über T · derived · Morphology 01.3` | — |

## 1. Design

1. **Input.** A VP-07 migration source from `from-plan` (profile `P2-VP-MIGRATION/0.7.8`, `binding-context/10`) plus landscape options: `layers` (ordered list of `{id, label}`), `layer_of` (referent → layer), `steps` (declared step IDs to show), `placement_predicates` (default `runs-on`, `hosted-by`).
2. **Columns** follow `layers` in declared order. Referents without a layer go into a final column "not assigned" (warning `VP12_LAYER_PARTIAL`). Without `layers` the columns are the home groups in Morphology reading order: Z module bodies, Y identity anchors, Y resource chain.
3. **Rows** within a column follow the declared order of the plan (first appearance), never a ranking.
4. **Snapshots.** One band per shown step, top to bottom in declared order. A node appears in a band when a dependency naming it holds at that step. A node introduced at the step (first band in which it appears after an earlier shown step) is marked "introduced", a node present in the previous shown band but absent here is drawn dashed with "retired" in the band where it was last present.
5. **Edges** are the plan dependencies holding at the step, subject → object, labelled by predicate in `<title>`; placement predicates heavier; origin `declared` solid, `derived` dashed, `unknown` dotted (as MILE-011). An edge never encodes a quantity.
6. **Budget.** Per column and band at most 12 nodes (detail), 8 (standard), 5 (overview); overflow is `VP12_BUDGET_EXCEEDED` with the column named (D-6). No silent truncation.
7. **Coverage.** Report and embedded ledger list every node and edge of the shown steps exactly once; `check-panels` re-renders and compares digests.
8. **Status line (B10)** and the general display disclaimer on every panel.

## 2. Decisions (proposed)

| ID | Question | Proposal |
|---|---|---|
| D-1 | Package | New VP-12 package; VP-07 and VP-09 stay untouched |
| D-2 | Layers | Caller declares `layers` and `layer_of`; default by home group (no domain guess) |
| D-3 | Steps | Default first and last declared step; at most 4 bands per panel |
| D-4 | X endpoints | Not drawn as nodes; edges to them counted in the report as "outside the landscape" |
| D-5 | Retired nodes | Dashed in the band of their last presence, label "retired at <next shown step>" |
| D-6 | Overflow | Reject with the column named; the caller narrows `layers`/`steps` or partitions |
| D-7 | Partition | One panel per plan by default; `--partition layer-group` optional later |
| D-8 | Locale | `de` and `en` locale files from the start |

## 3. Acceptance

| ID | Criterion |
|---|---|
| VP12-01 | L-01…L-14 against an oracle committed before code (layers, default groups, partial layer warning, steps, markers, retired dashing, placement weight, origin styles, budget reject, ledger, status line, locale, X endpoints outside, determinism) |
| VP12-02 | No change to any existing P2 output (VP-07…VP-11 regression digests) |
| VP12-03 | lunados.explorer F02 and F05 landscapes (Current and BETA) print; `check-panels` PASS; cockpit shows them |
| VP12-04 | G6 `cube_plan_views` lists `cube.landscape`; G5 as an own step |
