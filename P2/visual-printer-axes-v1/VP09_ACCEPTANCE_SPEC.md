# VP-09 — Declared axes view · Acceptance specification

**Status:** SPECIFIED, decisions D-1…D-11 resolved 2026-10-27 (all as proposed) — ready for oracle transcription and implementation.
**Profile:** `P2-VP-AXES/0.9.0`, new package `P2/visual-printer-axes-v1` (`vpaxes`), additive to VP-06 and reading VP-07 migration sources.
**Requirement:** C-8 from the running migration field test (2026-10-27; about 37 referents, 56 dependencies, steps p0–p3; client details withheld).
**Basis:** Morphology v9.4 §3.1 (seven coordinates; X/Y/Z primary homes, T/F/M/O cross-cutting qualifiers), §3.2 (declared reading order per axis: X Ψ → Γ → Σ → Ξ → Π; Y identity anchors, then resource chain; Z module bodies Core → … → Third-party Dependency), §3.3 (Dimension × Identity Anchor: a categorical matrix whose "blank cells do not impose an artificial relationship"), §3.8 (presentation order), §3.9 ("no automatic morpho-to-feature-space mapping"), §3.10/§3.13 (M has no frozen enum; Loose/Transitional/Strict are interpretive labels; O ≠ Ψ Observation); `core.json` `never_infer` ("X/Y/Z = independent storage containers", "X/Y/Z/F/M = numeric feature vector"); VP-03 lens profiles (five lenses = five X dimensions); VP-07 migration source; P1.11 (method bindings, C-10).
**Motivation:** The field test needs overviews that a dependency list and `cube.phases` do not give at a glance: which provider or module is involved in which step, which method applies to which component, how accounts and resources live through the steps. These are two-way tables over declared material: a categorical matrix with two chosen axes, each cell listing declared statements. Nothing is measured, ranked or placed at a distance.

## 0. Scope

| In scope | Out of scope |
|---|---|
| View `cube.axes`: categorical matrix, two declared axes, cells list declared statements | Distances, positions, scales, scores, heat shading, any numeric vector over coordinates (`never_infer`) |
| Home axes X, Y, Z (values from declared `concept_id` / anchors) and qualifier axes T, F (values from declared steps and P1.11 method bindings) | M and O axes in 0.9.0 (no declared migration source yet, D-6) |
| A closed list of axis pairs in priority order (D-2) | Arbitrary pairs; three or more axes; pivoting UI |
| Budgets, overflow per cell, panels with coverage, text index | Inferring an axis value from labels, names or graph structure |
| Row/column order = P0 §3.2 reading order or a declared layer map (VP-07.2) | Sorting by counts or by any computed measure |

## 1. Design summary

1. **Input.** A VP-07 migration source (0.7.1+; 0.7.2 for layers; a later revision carrying P1.11 method bindings for F) plus `--rows <axis>` and `--cols <axis>`. No new source format (D-3).
2. **Axis values.**
   - **X:** the five dimensions Ψ Γ Σ Ξ Π as *perspective columns/rows* (§3.3 precedent); entries are declared facet bindings of the matching VP-03 lens (D-5).
   - **Y / Z:** either concept kinds (e.g. `Z:module-body:provider`) or individual referents grouped under their kind (D-4); values only for referents whose declared `concept_id` has that home.
   - **T:** the declared steps of the source in declared order — a declared step sequence (P1.10 transitions carry T role `scheduling`), **not a time scale**; columns have equal width.
   - **F:** declared method IDs from P1.11 bindings, catalog order.
3. **Cells.** For each (row value, column value), the declared statements that belong to both (§3.2 table). Empty cells stay blank; a blank cell asserts nothing.
4. **Entries.** Shown as a list with an overflow line `+n more` (D-7); every entry is in the ledger with its `declaration_ref`.
5. **Panels.** Split along the row axis (and, if needed, the column axis) in declared order; coverage unit `(row value, column value, entry)`; text index; `check-panels` as VP-07 PE-6.

### 1.1 Shape (illustrative, synthetic)

```text
vpaxes print --source src.json --rows Z:referent --cols T --granularity standard --out z-by-step/
```

```text
                      p0 · current      p1            p2            p3 · target
Z · Provider
  legacy mail         d-shop-a, d-crm   d-shop-a      –             –
  new mail            –                 –             d-shop-b      d-shop-b, d-crm-b
Z · Third-party Dep.
  legacy files        f01a … +3 more    f01a … +3     –             –
```

(Rendered as SVG: equal cells, text only, one legend: "cell lists declared dependencies naming the row referent in the column step; blank = nothing declared".)

## 2. Status and diagnostic rules

| Situation | Result | Diagnostic |
|---|---|---|
| Axis name outside the closed set, or a pair not in the D-2 list | FAIL | `VP09_AXIS_INVALID` |
| Same axis twice (except X × X, D-2) | FAIL | `VP09_AXIS_INVALID` |
| Axis needs data the source does not declare (F without method bindings, X without facet bindings, Y/Z axis with no referent of that home) | FAIL | `VP09_AXIS_EMPTY` |
| Source item without a declared home (`semantic_ref` from `from-plan`, AX-2) | FAIL | `VP09_SOURCE_INVALID` |
| Rows or columns over the granularity budget with `reject` (or `detail`) | FAIL | `VP09_AXES_BUDGET` |
| Cell entries over the per-cell budget | Rendered with `+n more`; ledger lists all | `VP09_CELL_OVERFLOW` (warning) |
| Panel directory differs from a deterministic re-render | FAIL | `VP09_PANEL_COVERAGE` |
| Active SVG content, embedded ledger mismatch | FAIL | `VP09_AUDIT` |

## 3. Rules in detail

### 3.1 Axes (AX)

- AX-1: Closed axis set in 0.9.0: `X`, `Y:kind`, `Y:referent`, `Z:kind`, `Z:referent`, `T`, `F`. `M` and `O` are reserved names that FAIL with `VP09_AXIS_INVALID` until D-6 adds a declared source.
- AX-2: Home and kind of a referent come from the context's declared `home` / `concept_id`, which `from-plan` transcribes into each source item's `semantic_ref` (`Z:α:Provider["acme:new-mail"]`). An item without `semantic_ref` FAILs with `VP09_SOURCE_INVALID`; anchor IDs and labels are never used to guess a home.
- AX-3: Value order: X in §3.2 order Ψ Γ Σ Ξ Π; Y/Z kinds in §3.2 order (identity anchors → resource chain; Core → … → Third-party Dependency); referents within a kind in the declared layer-map order if present (VP-07.2), else source order; T in declared step order; F in catalog order.
- AX-4: X values are perspectives, not containers: an entry appears in an X row/column only through a declared facet binding of the matching lens (Ψ epistemology, Γ governance, Σ semantics, Ξ execution, Π provenance).

### 3.2 Cell membership per pair (CM)

| Pair (field-test priority) | Rows × columns | Cell (r, c) lists |
|---|---|---|
| 1 · Z × T | Z referents (by kind) × steps | dependencies whose subject or object is r and that hold in step c |
| 2 · F × Z | methods × Z referents | method bindings with method r that name c as an argument |
| 3 · Y × T | Y referents (by kind) × steps | dependencies naming r that hold in c; plus "introduced"/"retired" markers from transitions at c (text, not colour) |
| 4 · F × T | methods × steps | method bindings with method r on transitions at c or on dependencies ending at c |
| 5 · X × X | dimensions × dimensions | referents/cells with declared facets in both lenses (diagonal: facets of that lens) |
| 6 · Y × Z | Y referents × Z referents | dependencies between r and c (either direction), with predicate |
| 7 · X × Z | dimensions × Z referents | facet notes of lens r on c or on dependencies naming c |

- CM-1: Membership is computed only from declared fields; no transitive closure, no path search.
- CM-2: An entry may appear in several cells; repetitions are listed in the ledger (as VP-07 panels list repeated rows).

### 3.3 Drawing (AD)

- AD-1: Equal column widths and equal row heights per granularity; no size, position or shade encodes a quantity.
- AD-2: Row headers carry the P0 anchor glyph of the kind; column headers for T show the step label, for F the method ID, for X the dimension glyph and name.
- AD-3: Entries are text (ID or short label), ≥ 11 px, never truncated within the visible count; overflow line `+n more` names the count as a cardinality of declared entries, not a score.
- AD-4: Legend states the membership rule of the pair (CM table) and "blank = nothing declared, not 'no relation'".

## 4. Acceptance criteria

| AC | Requirement | Evidence |
|---|---|---|
| VP09-01 | VP-01…VP-08 unchanged | regression (SHA-256 ledgers, pinned digests) |
| VP09-02 | Axes AX-1…AX-4 | A-01…A-06 |
| VP09-03 | Cell membership CM-1, CM-2 for every pair in scope | A-07…A-13 |
| VP09-04 | Drawing AD-1…AD-4; no numeric encoding | A-14…A-16 |
| VP09-05 | Budgets, overflow, panels, coverage | A-17…A-20 |
| VP09-06 | Every row in §2 yields exactly the stated result and code | one test per row |
| VP09-07 | Synthetic golden: field-test-like source, Z × T, Y × T and (with P1.11) F × Z complete over panels | fixture |
| VP09-08 | No client data | review |

## 5. Alignment vectors (exit check)

| ID | Case | Expected |
|---|---|---|
| A-01 | `--rows Z:referent --cols T` | PASS |
| A-02 | `--rows M --cols T` in 0.9.0 | FAIL · `VP09_AXIS_INVALID` |
| A-03 | `--rows T --cols T` | FAIL · `VP09_AXIS_INVALID` |
| A-04 | `--rows F --cols Z:referent` on a source without method bindings | FAIL · `VP09_AXIS_EMPTY` |
| A-05 | Z kinds appear in P0 §3.2 order regardless of source order | PASS |
| A-06 | Layer map present: referents within a kind follow it | PASS |
| A-07 | Z × T: dependency holding p0–p1 appears in exactly the p0 and p1 cells of both its subject (if Z) and object rows | PASS |
| A-08 | Y × T: transition retiring a resource at p2 shows the "retired" marker in the p2 cell | PASS |
| A-09 | F × Z: import binding lists source and target components | PASS |
| A-10 | X × X: Ξ × Π cell lists items with execution and provenance facets | PASS |
| A-11 | Y × Z: dependency listed once in its (subject, object) cell with predicate | PASS |
| A-12 | Blank cell has no glyph and no fill | PASS |
| A-13 | No transitive membership (A depends on B, B on C: A not in C's cell) | PASS |
| A-14 | All cells equal width/height; no `fill` varies with entry count | PASS |
| A-15 | T columns equal width with uneven step labels | PASS |
| A-16 | SVG audit | PASS · `NO_ACTIVE_SVG_CONTENT` |
| A-17 | Cell with 7 entries at standard | PASS + `VP09_CELL_OVERFLOW`, ledger lists 7 |
| A-18 | 30 rows at standard, `reject` | FAIL · `VP09_AXES_BUDGET` |
| A-19 | Same with panels | PASS, coverage COMPLETE |
| A-20 | `check-panels` after removing an entry from a panel input | FAIL · `VP09_PANEL_COVERAGE` |

## 6. Decisions (resolved 2026-10-27, all as proposed)

| Decision | Options | Resolution | Consequence |
|---|---|---|---|
| D-1 Package and profile | (a) new package `vpaxes`, `P2-VP-AXES/0.9.0` · (b) view inside `vpmigration` | **(a)** | The view is not migration-specific (X × X, Y × Z); it reads migration sources first. |
| D-2 Pairs in 0.9.0 | (a) closed list in priority order: Z × T, Y × T, Y × Z, X × X, X × Z now; F × Z, F × T once P1.11 bindings reach the source · (b) any pair of the axis set | **(a)** | Each pair has a written membership rule (CM table); an arbitrary pair would need ad-hoc semantics. |
| D-3 Input | (a) VP-07 migration source (0.7.1+), F data via a later source revision · (b) own axes source format | **(a)** | One adapter path (`from-plan`); no second source to keep in sync. |
| D-4 Y/Z granularity | (a) both `:kind` and `:referent` (referents grouped under kind headers) · (b) referents only · (c) kinds only | **(a)** | Kinds give the compact overview; referents answer "which provider is active in p2". |
| D-5 X as an axis | (a) perspective rows/columns filled only by declared facet bindings of the matching lens · (b) not an axis in 0.9.0 | **(a)** | Matches Morphology §3.3 and the five VP-03 lenses; X never becomes a container of referents (`never_infer`). |
| D-6 M and O | (a) reserved, FAIL in 0.9.0; added when a declared mode/observer source exists (e.g. a P1 profile declaring Loose/Transitional/Strict per step as an interpretive label) · (b) M from free-text labels | **(a)** | No frozen M enum exists (§3.10); O needs witnesses (P1.4). |
| D-7 Many entries per cell | (a) list up to a per-cell budget (overview 2, standard 3, detail 6) + `+n more`, full list in ledger and `<title>` · (b) count only · (c) list only, row grows | **(a)** | Readable at a glance; nothing hidden; the count is a stated cardinality, not a score. |
| D-8 Budgets (rows / columns) | (a) overview 8/4, standard 14/6, detail 24/8 · (b) other | **(a)** | Columns match step counts (p0–p3) with headroom; detail allows a full field-test Z axis on few panels. |
| D-9 Panels | (a) split along rows in declared order (kind headers repeated), columns never split unless over budget · (b) split along both axes always | **(a)** | Steps stay side by side, which is the point of × T views. |
| D-10 Ordering of values | (a) P0 §3.2 reading order for kinds and dimensions, declared layer map or source order for referents · (b) alphabetical · (c) by entry count | **(a)** | Declared orders only; (c) would rank. |
| D-11 Golden | (a) synthetic, field-test-like (3 workstreams, 4 steps, ~35 referents) · (b) field-test data | **(a)** | Client data stays out. |

## 7. Not part of VP-09

- M × T and O × X (D-6), Y × Z with more than direct dependencies, three-way tables.
- Interactive pivoting, filtering or sorting in the viewer.
- Any aggregation into numbers beyond the overflow count (sums, ratios, scores).
- MCP tool (as VP-07 D-6 / VP-08 D-10).
