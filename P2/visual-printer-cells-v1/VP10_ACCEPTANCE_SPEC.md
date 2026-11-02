# VP-10 — Cell states from declared coverage · Acceptance specification

**Status:** DRAFT — decisions D-1…D-9 open, each with a proposal (§6). Not implemented.
**Profile:** `P2-VP-CELLS/0.10.0` (working name), new package `vpcells` in `P2/visual-printer-cells-v1/` (D-1). VP-09 (`vpaxes`, 0.9.0…0.9.2) and VP-07 stay byte-identical.
**Requirement:** VR-05 (MILE-003 handover, rank 2) and PO-6; MILE-005 US-020 / TASK-035. Builds on P1.12 (`binding-context/8`, coverage declarations CV-1…CV-5).
**Basis:**
- `VP09_ACCEPTANCE_SPEC.md` (AX-1…AX-3, CM table) and `VP09_2_ACCEPTANCE_SPEC.md` (Y × Y directed, `--hide-empty`, wrapping, locale).
- `VP07_ACCEPTANCE_SPEC.md` PV-5 (hatches as explicit `line` elements, no `<pattern>`).
- `P1/coverage-instance-profile-v1/P1_12_ACCEPTANCE_SPEC.md` (CV-2: a referent/direction declaration covers every pair at that referent in that direction; a pair declaration covers one ordered pair; CV-5: a declaration is a survey scope, not proof).
- Mockup M-05C and its pre-check (`docs/09-Research/visual-check/`).
- Morphology v9.4 §3.3 (a blank cell imposes no relationship).

**Motivation:**

| Finding (MILE-003 R-1, V-05) | Effect today in `cube.axes` |
|---|---|
| Marked ≠ blank, but "checked empty" and "unknown" look the same (R-1a) | A reader takes "no dependency" for "not surveyed" |
| `--hide-empty` names only the number of hidden rows and columns (R-1b, PO-6) | The hidden elements are visible only in the report |
| Mockups M-05A/B claimed completeness for a whole row that also had an unknown cell | The candidate rule must bind "checked" to the declared scope only (M-05C) |

All examples are synthetic; no client data.

## 0. Scope

| In scope | Out of scope |
|---|---|
| Four cell states in the directed Y × Y matrix: marked, checked empty, unknown, hidden | Y × Z, Z × T and other pairs (Y × Z is undirected in VP-09; D-3) |
| Coverage from `coverage_declarations` of a `/8` context, one predicate per view (D-3) | Evaluating population rules (that is lunados.lib `analyze.population/v1`) |
| Hidden rows and columns named in the legend (PO-6) | Instance-restricted declarations (`instance_ref`, CV-4): ignored and reported (D-7) |
| Colour-free distinction: text plus line hatch | New VG anchors, morphology changes, colour coding |
| Comparison with mockup M-05C | Human readability test (script exists, not run) |

## 1. Design summary

`vpcells` wraps the unchanged `vpaxes` 0.9.2 path, in the same way P1.12 wraps P1.11:

1. `from-plan` reads a `/8` context.
2. It projects the context to `/7` and builds the 0.9.2 axes input with the unchanged VP-07 adapter.
3. It adds a `coverage` block: the declarations for the chosen predicate, translated to display IDs, plus the full-plan pairs of that predicate (D-4).
4. `print-cells` draws Y × Y and assigns every off-diagonal cell exactly one state:

| State | When | Cell content (en / de) |
|---|---|---|
| **marked** | at least one declared dependency of the view in the cell | the entries as in 0.9.2 (`d-pv · references`) |
| **checked empty** | no entry, and a declaration of the chosen predicate covers the cell (CV-2) | `none · checked` / `keine · geprüft`, plus the scope: `pair`, `row` (outgoing) or `column` (incoming) |
| **unknown** | no entry and no covering declaration | hatch of explicit horizontal lines (hatch C, D-5); no text |
| **hidden** | the row or column is left out by `--hide-empty` (D-6) | not drawn; named in a legend strip |

5. Diagonal cells (`r`, `r`) are drawn as `element` and take no state (D-8).
6. The report counts the cells per state and lists every hidden value and every ignored declaration.

### 1.1 Shape (illustrative, synthetic; the DSM-03 / M-05C situation)

```
                 m:parser            m:resolver          m:validator         ┆ hidden: m:printer
m:parser         element             ░░░░░░░░            d-fb · references   ┆
m:resolver       d-rp · references   element             ░░░░░░░░            ┆
m:validator      ░░░░░░░░            d-vr · references   element             ┆
m:printer        none · checked      ░░░░░░░░            d-pv · references   ┆
                 (pair)
```

`░` stands for hatch C. With a declaration "outgoing `references` of m:printer" instead of the pair, the m:resolver cell of that row would also read `none · checked (row)`.

## 2. Status and diagnostic rules

| Situation | Result | Code |
|---|---|---|
| Context is not `/8`, or has no `coverage_declarations` | view drawn; every empty cell is unknown; legend says so (D-9) | `VP10_COVERAGE_NONE` (warning) |
| Declaration names a referent that is not an item of the source | declaration ignored, report lists it | `VP10_COVERAGE_REF_UNKNOWN` (warning) |
| Declaration with `instance_ref` | ignored in Y × Y, report lists it | `VP10_COVERAGE_INSTANCE_IGNORED` (warning) |
| `--predicate` names no predicate of the plan's dependencies | error | `VP10_PREDICATE_INVALID` |
| Pair other than Y × Y | error | `VP10_PAIR_INVALID` |
| Covered cell whose only dependencies lie outside the slice (D-4) | marked, entry with `*` (`d9* · references`) | — |
| All VP-09 0.9.2 rows | unchanged; codes keep their `VP09_` names | — |

## 3. Rules in detail

- **CS-1** Exactly one state per drawn off-diagonal cell. `marked` takes precedence over checked empty: a declared survey scope with an entry is simply marked.
- **CS-2** Checked empty covers only the declared scope (M-05C). A pair declaration covers one cell; an outgoing declaration at r covers row r; an incoming declaration at c covers column c. Nothing else: no view-level declaration (P1.12 D-2), no inference from neighbouring cells.
- **CS-3** Only declarations of the chosen predicate count. Entries of other predicates stay visible; the checked text then names the predicate (`none references · checked`).
- **CS-4** Unknown is drawn, not left blank: hatch C, explicit `line` elements clipped to the cell (PV-5 technique, no `<pattern>`, no `use`/`href`).
- **CS-5** Hidden: under `--hide-empty`, a value is hideable only if its row (or column) has no marked and no checked-empty cell. The legend names every hidden value (PO-6) and says that the hidden cells, unknown ones included, are not shown.
- **CS-6** Colour-free: the four states differ in text, in line elements, or in both. Fill and stroke colour carry no state (checked by attribute audit, as in MILE-003 `attrs.py`).
- **CS-7** Non-implication: "checked" means "no declared dependency within the declared survey scope", not "does not exist" (CV-5). The legend says so; warrant, authority and admission stay `NOT_EVALUATED`.

## 4. Acceptance criteria

| AC | Requirement | Evidence |
|---|---|---|
| VP10-01 | VP-07, VP-09 and P1 files unchanged; `VP07_SHA256SUMS`, `VP09_SHA256SUMS` diff empty; pinned 0.9.0 / 0.9.1 digests hold | file diff, `pin_09x_digests.py` |
| VP10-02 | A 0.10.0 view of a `/8` context without declarations draws the same entries as the 0.9.2 Y × Y view of its `/7` twin | regression test |
| VP10-03 | CS-1…CS-7 | vectors J-01…J-14 (§5) |
| VP10-04 | Every row of §2 yields the stated result and code | one test per row |
| VP10-05 | Independent oracle for J-01…J-14 (cell → state), hand-derived before code | `oracles/independent_j01_j14.json` |
| VP10-06 | Colour-free distinction: the attribute audit finds a non-colour difference between every two states | audit test |
| VP10-07 | Comparison with M-05C documented (same cells, same states, differences named) | `M05C_COMPARISON.md` |
| VP10-08 | Synthetic golden: DSM-03-shaped plan with pair and row declarations, one hidden column, `de` and `en` | `fixtures/golden_cells.json` |

## 5. Vectors (planned)

The base is a synthetic plan with modules m:parser, m:resolver, m:validator and m:printer (`Y:resource-object:resource`). Dependencies use `references` and follow the DSM-03 shape: fb, rp, vr and pv. Expected states are given per cell in the oracle.

| ID | Situation | Expectation |
|---|---|---|
| J-01 | no declarations (`/8`) | all empty cells unknown; `VP10_COVERAGE_NONE` |
| J-02 | pair (printer, parser) | that cell checked (pair); the rest of row printer unknown |
| J-03 | outgoing at printer | every empty cell of row printer checked (row) |
| J-04 | incoming at parser | every empty cell of column parser checked (column) |
| J-05 | pair declared on a marked cell | marked (CS-1) |
| J-06 | declaration of another predicate | ignored for `references` cells; unknown |
| J-07 | entries of two predicates, coverage for one | checked text names the predicate (CS-3) |
| J-08 | `--hide-empty cols`, column printer without marked or checked cells | hidden and named |
| J-09 | `--hide-empty`, column with a checked cell | not hidden (CS-5) |
| J-10 | declaration on an unknown referent | ignored; `VP10_COVERAGE_REF_UNKNOWN` |
| J-11 | declaration with `instance_ref` | ignored; `VP10_COVERAGE_INSTANCE_IGNORED` |
| J-12 | slice without dependency pv; row printer declared | cell (printer, validator) marked `d-pv* · references`, not checked (D-4) |
| J-13 | pair other than Y × Y | `VP10_PAIR_INVALID` |
| J-14 | `--locale de` | `keine · geprüft (Paar/Zeile/Spalte)`; legend in German |

## 6. Decisions (open; proposal in bold)

| Decision | Options | Proposal | Reason |
|---|---|---|---|
| D-1 Place | (a) new package `vpcells` that imports `vpaxes` unchanged · (b) profile 0.9.3 inside `vpaxes` | **(a)** | TASK-035 requires VP-09 byte-identical. `VP09_SHA256SUMS` pins the `vpaxes` code, so (b) would change pinned files. (a) follows the P1.12-over-P1.11 pattern. |
| D-2 Source | (a) migration plan via the unchanged VP-07 adapter (`from-plan`, as R-1 did for DSM) · (b) a direct statement set plus a `/8` context | **(a)** | The pipeline exists and R-1 already showed DSM as a plan. (b) is the general projection PO-7 / G-03 and would add about 0.5 PT; it fits as a follow-up. |
| D-3 Pairs | (a) Y × Y only · (b) also Y × Z | **(a)** | Coverage has a direction. Y × Y is directed, while VP-09 Y × Z shows both directions in one cell. |
| D-4 Slice | (a) checked empty is decided on the full plan; a covered cell with dependencies only outside the slice shows them with `*` · (b) decided on the slice | **(a)** | (b) would print "checked empty" for a cell whose dependency was only cut away by the slice. `*` is the existing VP-09.2 marker for "outside the slice". |
| D-5 Unknown | (a) hatch C, horizontal lines, legend "not surveyed, not empty" · (b) text "open (not surveyed)" without a hatch (M-05A) | **(a)** | M-05C and the pre-check favour the area mark. Horizontal lines do not collide with VP-07 hatches A (`/`) and B (`\`). |
| D-6 Hidden | (a) hide only values without marked or checked cells, and name them in a legend strip · (b) as 0.9.2: hide values without entries, legend shows only the count | **(a)** | A checked cell carries information. PO-6 asks for names. |
| D-7 `instance_ref` | (a) ignore and report · (b) treat as unrestricted | **(a)** | A plan dependency carries no instance. Treating the declaration as unrestricted would claim more than was declared. |
| D-8 Diagonal | (a) `element`, no state · (b) like any other cell | **(a)** | DSM convention (M-05C). A self-dependency has no DSM meaning here. |
| D-9 No declarations | (a) hatch every empty cell and warn `VP10_COVERAGE_NONE` · (b) behave like 0.9.2 (blank) | **(a)** | Under VP-10 a blank cell would be ambiguous again. The warning says why everything is hatched. |

**Locale:** new strings in a VP-10 locale file inside `vpcells`. The VP-07.5 locale files stay byte-identical, because they are pinned in `VP07_SHA256SUMS`.

**Effort:** 1–1.5 PT, as in the MILE-005 plan.

## 7. Not part of VP-10

- Further pairs (Y × Z, Z × Z), statement sets without a plan (PO-7, G-03).
- Population rules in the picture (count, join): they belong to `analyze.population/v1`.
- Instance views (VR-12), cycle components (VR-09).
- G5 delivery: MILE-005 D-5 keeps it local.
