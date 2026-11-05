# VP-12 — Landscape view (`cube.landscape`) · Acceptance specification

**Status:** SPECIFIED for TASK-079 (2026-11-05). Decisions D-1…D-8 confirmed by the user as proposed; vectors L-01…L-14 below, oracle `oracles/independent_l01_l14.json` before code.
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

1. **Input.** `vplandscape from-plan` calls the VP-07.8 source path unchanged (`vpmigration.api.source`, profile `P2-VP-MIGRATION/0.7.8`, `binding-context/10`, `origin_lines` on, optional VP-07.2 layer map `aiaeao.cube.vp07-layer-map/1`) and wraps the result in `aiaeao.cube.vp12-landscape-input/1`: `profile`, `source` (the VP-07.8 source with origin ledger), `concepts` (display ID → concept ID, from the from-plan mapping), `steps` (shown bands), `placement_predicates` (default `runs-on`, `hosted-by`), `locale`, `granularity`. Errors of the source path keep their VP-07 codes (no new wrapper code).
2. **Nodes** are the Y and Z display items of the source. X items (anchor family `contract-pairs`) are never nodes (D-4).
3. **Columns.** With a layer map: the declared `layer_order`, all of it, empty layers included. Y/Z nodes without a layer go into a final column `unassigned` (warning `VP12_LAYER_PARTIAL`, nodes listed). Without a layer map: the anchor families present, in Morphology reading order `module-bodies`, `governance-boundary`, `identity-anchors`, `resource-objects`. At most 6 columns, else `VP12_BUDGET_EXCEEDED` (D-6).
4. **Order within a column.** With a layer map the VP-07.2 `layer_sequence` (declared listing order); without one, first appearance in the plan's dependency order (subject before object). Never a ranking.
5. **Bands.** `steps` lists declared step IDs; default first and last declared step (D-3). Bands are drawn top to bottom in declared order whatever the given order; at most 4 bands (`VP12_BUDGET_EXCEEDED`). An undeclared step is `VP12_STEP_UNKNOWN`; a duplicate or empty list is `VP12_INPUT`.
6. **Presence.** A Y/Z node is in a band when any plan dependency naming it holds at that step, including a dependency whose other endpoint is X (that dependency is not drawn, §1.9).
7. **Markers** (between consecutive shown bands): a node present in a band but not in the previous shown band is `introduced`; a node present in a band but not in the next shown band is `retired`, drawn dashed in that band with `retired_at` the next shown step (D-5). Each marker lists `declared_by`: the codes of declared transitions with `at` after the earlier and up to the later band step that introduce or retire that node (may be empty; the marker itself is derived from presence).
8. **Edges** are the shown dependencies holding at the band step between two nodes, subject → object, predicate in the label and `<title>`; predicates in `placement_predicates` drawn heavier (`placement: true`). Style from the VP-07.6 origin ledger: `declared` solid, `derived` dashed, `unknown` and `unbound` dotted. An edge never encodes a quantity.
9. **Outside.** A dependency with an X endpoint is not drawn; the report lists it under `x_outside` with each shown step where it holds.
10. **Budget.** Per column and band at most 12 nodes (detail), 8 (standard), 5 (overview); overflow is `VP12_BUDGET_EXCEEDED` naming band and column. No silent truncation.
11. **Coverage.** Report and embedded ledger list every node and edge of every band exactly once; `check-panels` re-renders and compares digests and ledgers.
12. **Status line (B10)** `Y × Z over T · derived · Morphology 01.3` (de: `Y × Z über T · abgeleitet · Morphologie 01.3`) and the general display disclaimer on every panel.

## 2. Decisions (confirmed 2026-11-05)

| ID | Question | Proposal |
|---|---|---|
| D-1 | Package | New VP-12 package; VP-07 and VP-09 stay untouched |
| D-2 | Layers | Caller declares layers (VP-07.2 layer map, reused); default by anchor family (no domain guess) |
| D-3 | Steps | Default first and last declared step; at most 4 bands per panel |
| D-4 | X endpoints | Not drawn as nodes; edges to them counted in the report as "outside the landscape" |
| D-5 | Retired nodes | Dashed in the band of their last presence, label "retired at <next shown step>" |
| D-6 | Overflow | Reject with the column named; the caller narrows `layers`/`steps` or partitions |
| D-7 | Partition | One panel per plan by default; `--partition layer-group` optional later |
| D-8 | Locale | `de` and `en` locale files from the start |

## 2a. Vectors (L-01…L-14, synthetic)

One synthetic `binding-context/10` (`vp12-ls`, scope `ctx:ls`), no client data. Referents: `act:op`, `acc:admin` (Y Actor); `mod.conn` (Z Connector), `mod.core` (Z Core); `res:mail-old`, `res:mail-new`, `res:dns` (Y Resource); `adm` (X Admission). Plan `pm-ls`, steps `current`, `mvp`, `beta`; transition `t-mvp` (code T1) at `mvp` retires `res:mail-old`, introduces `res:mail-new`.

| Dependency | Subject → object | Predicate | Holds in | Origin |
|---|---|---|---|---|
| d1 | act:op → mod.conn | invoked-by | current, mvp, beta | declared |
| d2 | mod.conn → res:mail-old | reads | current | declared |
| d3 | mod.conn → res:mail-new | reads | mvp, beta | derived (basis from d2) |
| d4 | res:mail-new → res:dns | hosted-by | mvp, beta | unknown |
| d5 | mod.core → adm | gated-by | beta | declared |
| d6 | acc:admin → res:mail-new | configured-by | beta | unbound (predicate without origin binding) |

Layer map: `layer_order` actor, module, data, platform; actor [act:op, acc:admin], module [mod.conn, mod.core], data [res:mail-old, res:mail-new], platform [res:dns]. Default steps: `current`, `beta`.

| ID | Case | Expected |
|---|---|---|
| L-01 | layer map, default steps | PASS; columns actor, module, data, platform; band current: actor [act:op], module [mod.conn], data [res:mail-old], platform [], edges [d1, d2]; band beta: actor [act:op, acc:admin], module [mod.conn, mod.core], data [res:mail-new], platform [res:dns], edges [d1, d3, d4, d6] |
| L-02 | no layer map | PASS; columns module-bodies [mod.conn, mod.core], identity-anchors [act:op, acc:admin], resource-objects [res:mail-old, res:mail-new, res:dns] (order over all bands) |
| L-03 | layer map without res:dns | PASS; columns actor, module, data, platform, unassigned; unassigned [res:dns] in band beta; warning `VP12_LAYER_PARTIAL` [res:dns] |
| L-04 | steps current, mvp, beta | PASS; band mvp: act:op, mod.conn, res:mail-new, res:dns, edges [d1, d3, d4]; markers current: res:mail-old retired at mvp (T1); mvp: res:mail-new introduced (T1), res:dns introduced; beta: acc:admin, mod.core introduced |
| L-05 | steps include `gamma` | `VP12_STEP_UNKNOWN` |
| L-06 | layer map with seven layers | `VP12_BUDGET_EXCEEDED` |
| L-07 | placement weight | d4 `placement: true`; d1, d2, d3, d6 `false` |
| L-08 | origin styles | d1 solid, d2 solid, d3 dashed, d4 dotted, d6 dotted |
| L-09 | markers, default steps | band current: res:mail-old retired, retired_at beta, declared_by [T1]; band beta introduced: acc:admin [], mod.core [], res:mail-new [T1], res:dns [] |
| L-10 | X endpoints | no node `adm`; `x_outside` [{cell d5, steps [beta]}] |
| L-11 | locale | en status `Y × Z over T · derived · Morphology 01.3`; de status `Y × Z über T · abgeleitet · Morphologie 01.3` |
| L-12 | determinism and ledger | two renders byte-identical; embedded ledger equals report ledger; every node and edge of every band once |
| L-13 | `placement_predicates` [] | no edge with `placement: true` |
| L-14 | steps beta, current (reversed) | PASS; bands in declared order current, beta (same panel as L-01) |

## 3. Acceptance

| ID | Criterion |
|---|---|
| VP12-01 | L-01…L-14 against `oracles/independent_l01_l14.json`, transcribed by hand from §2a before code |
| VP12-02 | No change to any existing P2 output (VP-07…VP-11 regression digests) |
| VP12-03 | lunados.explorer F02 and F05 landscapes (Current and BETA) print; `check-panels` PASS; cockpit shows them |
| VP12-04 | G6 `cube_plan_views` lists `cube.landscape`; G5 as an own step |
