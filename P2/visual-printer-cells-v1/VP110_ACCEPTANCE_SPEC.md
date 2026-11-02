# VP-10 0.11.0 — Statement sets and aggregated relations · Acceptance specification

**Status:** SPECIFIED. MILE-007 decisions D-1…D-8 apply; detail questions Q-1…Q-10 resolved 2026-11-02 (all as proposed). IMPLEMENTED locally 2026-11-02 (TASK-046): S-01…S-16 16/16, 0.10.0 16/16 and 0.10.1 9/9 byte-identical.
**Profile:** `P2-VP-CELLS/0.11.0` in `vpcells`, a new input path next to `from-plan`. `0.10.0`, `0.10.1`, VP-09 and VP-07 stay byte-identical.
**Requirement:** PO-7 (MILE-003 handover), G-03 (MILE-002 gap ledger); MILE-007 US-024, US-025, TASK-043…047.
**Basis:**
- [RENDER-RESULTS](../../docs/09-Research/visual-check/RENDER-RESULTS.md): DSM and C4 material had to be bent into a P1.10 migration plan; the VP-07 adapter maps only six concepts (AD-2).
- [C4-02](../../docs/09-Research/grammar-sampling/reports/C4-02.md): two component relations aggregated into one container relation; one source invisible; strategy not bound.
- [DSM-01](../../docs/09-Research/grammar-sampling/reports/DSM-01.md): modules with `dependsOn`; row/column convention must be bound.
- `VP10_ACCEPTANCE_SPEC.md` (CS-1…CS-7) and `VP10_1_ACCEPTANCE_SPEC.md` (AO-1…AO-4).

All examples are synthetic.

## 0. Scope

| In scope | Out of scope |
|---|---|
| A declared statement set for a `binding-context/8`, drawn as a cell matrix without a migration plan | Statement sets in `cube.flow`, `cube.axes`, `cube.sequence`; provenance lines (VR-01) |
| Reading a typed aggregation result computed by lunados.lib (`project.aggregate-relations/v1`) | Computing or re-checking the aggregation in the Cube |
| Cell states (marked, checked, unknown, hidden) and `axis_order` as in 0.10.x | `project.dsm`, `project.mdm`, domain blocks (DSM-02), predicate traits (G-09) |
| CLI and G6 (local) | G5; P1 verdicts on the statements |

## 1. Statement set (`aiaeao.cube.statement-set/1`)

```json
{
  "format": "aiaeao.cube.statement-set/1",
  "set_id": "dsm-modules",
  "context_id": "<context_id of the binding-context/8>",
  "referents": ["m:parser", "m:resolver", "m:validator", "m:printer"],
  "statements": [
    {"statement_id": "s-rp", "subject": "m:resolver", "predicate_id": "dependsOn", "object": "m:parser", "label": "optional text"}
  ],
  "witness_ref": "synthetic:dsm#modules"
}
```

- **SS-1:** Every referent and every statement endpoint resolves to a referent `ref` of the context; every `predicate_id` resolves to a predicate contract of the context. Subject and object concepts must be allowed by that contract. Otherwise the input is rejected (§5). This is resolution, not a P1 verdict (D-3).
- **SS-2:** `statement_id` is unique in the set. `label` is optional display text.
- **SS-3:** The statements stay `declared_unverified`; the set claims nothing about completeness. Completeness comes only from `coverage_declarations` of the context (P1.12).

## 2. Aggregation result (`aiaeao.projection-result/v1`, computed in lunados.lib)

Input: a statement set, the method parameters and the context. Output (shape; the exact schema is part of the LIB entry, TASK-045):

```json
{
  "schema": "aiaeao.projection-result/v1",
  "method_id": "project.aggregate-relations/v1",
  "library_ref": {"library_id": "lunados.lib", "entry_id": "project.aggregate-relations", "revision": 1, "sha256": "<INDEX value>"},
  "parameters": {"strategy": "all", "source_predicate": "uses", "derived_predicate": "uses.derived", "membership_predicate": "contains"},
  "input_set_sha256": "<sha256 of the canonical statement set>",
  "referents": ["c4:shop/api", "c4:shop/db"],
  "statements": [
    {"statement_id": "d-1", "subject": "c4:shop/api", "predicate_id": "uses.derived", "object": "c4:shop/db", "origin": "derived",
     "derived_from": ["s-1", "s-2"], "label": "Writes orders to", "labels_dropped": 1}
  ],
  "internal": ["s-3"],
  "suppressed": [],
  "loss": {"sources": 3, "derived": 1, "merged": 2, "internal": 1, "suppressed": 0, "labels_dropped": 1},
  "status": "declared_unverified", "runtime_authority": "not-evaluated"
}
```

- **PR-1:** The strategy is a required parameter and is echoed in the result (D-4).
- **PR-2:** Each derived statement lists **all** its sources; nothing is dropped from the trace. Loss means only what the aggregated view cannot show: merged sources, internal relations, suppressed sources, dropped labels.
- **PR-3:** The Cube checks the result's format, `method_id`, `library_ref` shape and `input_set_sha256` against the statement set it is given. It never recomputes the aggregation.

## 3. Drawing (0.11.0)

- **DR-1 Axes:** rows and columns are the set's `referents` (aggregation: the result's `referents`), in declared order, grouped by concept in order of first appearance. `axis_order` works as in 0.10.1.
- **DR-2 Convention:** row = subject, column = object (D-6). The legend says so; there is no transposed mode.
- **DR-3 Cells:** a cell lists the statements of the chosen predicate as `<statement_id> · <predicate>`; `label` is not drawn in the cell (ledger only). Derived statements read `<statement_id> · <predicate> · abgeleitet · n Quellen` / `derived · n sources`.
- **DR-4 States:** marked, checked, unknown, hidden and the diagonal `element` as in 0.10.x (CS-1…CS-7). Coverage from the context applies to plain statement sets only (Q-9).
- **DR-5 Legend and ledger:** title is `<set_id> · <predicate>`; no migration vocabulary (plan, phase, step). With an aggregation result, the legend states the strategy and the loss line, e.g. "Verdichtung all: 3 Quellen → 1 abgeleitete Aussage; 1 intern; 0 unterdrückt; 1 Beschreibung verworfen". The ledger lists every derived statement with its sources, labels and the internal and suppressed sources.
- **DR-6 No colour:** derived and declared differ by text only; the colour-free audit applies.

## 4. Interfaces

| Surface | Call |
|---|---|
| CLI | `python3 -m vpcells from-statements --context ctx8.json --statements set.json [--projection result.json] --predicate P --out in.json`, then `print-cells` / `check-cells` as today |
| G6 | `cube_plan_source` with `printer: vpcells` and a `statements` argument (plus optional `projection`) instead of `plan_id`; `cube_plan_views` view `cube.cells`; `cube_plan_check` |

`from-plan` and all 0.10.x behaviour stay unchanged.

## 5. Status and diagnostic rules

| Situation | Result | Code |
|---|---|---|
| Referent or endpoint not in the context | error | `VP10_STATEMENT_REF_UNKNOWN` |
| Predicate not in the context, or concepts not allowed by its contract | error | `VP10_STATEMENT_PREDICATE_INVALID` |
| Duplicate `statement_id` | error | `VP10_STATEMENT_SET_INVALID` |
| Mixed homes on the axes (Q-2) | error | `VP10_PAIR_INVALID` |
| Projection result whose `input_set_sha256` does not match the given set, or wrong `method_id` / format | error | `VP10_PROJECTION_INVALID` |
| Coverage declarations present with an aggregation result | ignored, empty cells unknown | `VP10_COVERAGE_NOT_PROJECTED` (warning) |
| No statement of the chosen predicate | drawn; all off-diagonal cells unknown or checked | `VP10_PREDICATE_EMPTY` (warning) |

## 6. Acceptance criteria and vectors (planned, fixed in TASK-044)

| AC | Requirement | Evidence |
|---|---|---|
| VP110-01 | 0.10.0 and 0.10.1 outputs pinned before code and byte-identical afterwards; VP-07, VP-09 unchanged | pins, SHA256SUMS |
| VP110-02 | DSM-01 as a statement set: four `dependsOn` entries at subject × object, own concept and predicate, no plan vocabulary | vector |
| VP110-03 | C4-02 aggregated with each strategy: derived entries, sources, internal and suppressed sources, loss line as in the oracle | vectors per strategy, LIB cases |
| VP110-04 | every §5 row | vectors |
| VP110-05 | G6 round trip and `cube_plan_check` | adapter test |

Planned vectors: S-01 DSM-01 set (Y × Y); S-02 S-01 with coverage (checked and unknown cells); S-03 S-01 with `axis_order`; S-04…S-06 C4-02 aggregated with `all`, `unless_same`, `unless_any` (with a declared container relation for the latter two); S-07…S-11 §5 errors and warnings; S-12 G6 equals CLI.

## 7. Detail questions (resolved 2026-11-02, all as proposed)

| ID | Question | Decision | Reason |
|---|---|---|---|
| **Q-1** | Which referents form the axes? | The set lists them in `referents` (required); order = declared order | DSM needs isolated modules too; no hidden universe from the context |
| **Q-2** | Which pairs? | **Y × Y and Z × Z** (one home on both axes); mixed homes rejected | C4 boundaries and tools are Z (MILE-002 context), DSM modules are Y |
| **Q-3** | How is it drawn? | **Own matrix drawer in `vpcells`** with the 0.10.x conventions (grid, states, legend sections, ledger), not through VP-07/VP-09 | the VP-07 adapter maps only six concepts and brings plan titles; that is exactly PO-7. Cost: about +0.25–0.5 PT in charge C |
| **Q-4** | How is membership declared for aggregation? | As statements in the set with a predicate named by the required parameter `membership_predicate` (C4: `contains`, parent → child); a child with two parents is an error | stays inside Cube statements; no second structure |
| **Q-5** | Which level? | One level per call: an element maps to its parent, or to itself if it has none. Both ends map to themselves → the statement passes through as declared. Both ends map to the same parent → internal | simple and checkable; deeper levels by calling again |
| **Q-6** | What do the strategies mean? | All sources of one parent pair merge into one derived statement in every strategy. `all`: always derive, even next to a declared parent-level statement. `unless_same`: no derived statement if a declared statement with `derived_predicate` or `source_predicate` already links the pair; its sources count as suppressed. `unless_any`: the same for a declared statement of any predicate | mirrors the Structurizr strategies without losing the trace |
| **Q-7** | Which predicate do derived statements carry? | Required parameter `derived_predicate`; it must exist in the context and allow the parents' concepts (C4-02: `uses.derived`) | derived and declared stay distinguishable in P1 terms |
| **Q-8** | What happens to labels? | The derived statement keeps the label of its first source in set order; the others count as `labels_dropped` | reproduces C4-02 "first defined" and makes the loss visible |
| **Q-9** | Coverage with aggregation? | Not transferred: child coverage says nothing about the parent pair. Coverage is ignored with a warning; empty cells read unknown | avoids a false "checked empty" |
| **Q-10** | How much does the Cube check of the LIB result? | Format, `method_id`, `library_ref` shape, `input_set_sha256`; no recomputation | same boundary as `analyze.population/v1` |

## 8. Precisions fixed with the vectors (TASK-044, before any code)

These close gaps in §1–§5 without changing a decision.

- **SS-4:** Every statement endpoint must be listed in the set's `referents`; otherwise `VP10_STATEMENT_SET_INVALID`. Check order: set shape and duplicate IDs → resolution in the context (`VP10_STATEMENT_REF_UNKNOWN`) → predicate and concepts (`VP10_STATEMENT_PREDICATE_INVALID`) → endpoints in `referents` → one home on the axes (`VP10_PAIR_INVALID`).
- **PR-4:** A statement whose ends both map to themselves passes through unchanged (`origin: declared`) and counts as `passed_through`. Statements of other predicates and the membership statements are not part of the result. `loss` has the keys `sources`, `passed_through`, `derived`, `merged`, `internal`, `suppressed`, `labels_dropped`. Suppressed sources are listed as `{statement_id, suppressed_by}`.
- **PR-5:** Derived statements are numbered `d-1`, `d-2`, … in the order of their first source in the set. The result's `referents` are the images of the set's referents, in order of first appearance.
- **DR-7:** With an aggregation result the view shows all statements of the result (passed-through `source_predicate` and `derived_predicate`), passed-through first; the title names the `derived_predicate`. `--predicate` may be omitted or must equal the `derived_predicate`.
- **DR-8:** The loss line is exact and has no plural forms: `aggregation <strategy>: sources <n> → derived <n>; passed through <n>; internal <n>; suppressed <n>; labels dropped <n>` (de: `Verdichtung <strategy>: Quellen <n> → abgeleitet <n>; durchgereicht <n>; intern <n>; unterdrückt <n>; Beschreibungen verworfen <n>`).
- **PR-6 (TASK-045):** The evaluator cannot know the INDEX hash of its own `entry.json`, so the result it writes has no `library_ref`. The Cube reads a projection record `{format: aiaeao.cube.projection-record/1, library_ref, call, result}`; the Q-10 checks apply to that record (`library_ref` shape, `call.method_id` = `result.method_id`, result format, `input_set_sha256`).
- **Vectors:** the planned list in §6 is fixed as S-01…S-16 in `oracles/independent_s01_s16.json`; the aggregation cases A-01…A-10 are in `docs/09-Research/statement-sets/CHECK-CASES.json`. The 0.10.1 outputs are pinned in `fixtures/regression_0101_digests.json` (9), the 0.10.0 outputs stay pinned (16).
