# VP-10.1 — Declared axis order and feedback reading · Acceptance specification

**Status:** SPECIFIED. MILE-006 decisions D-4 and D-5 apply; detail questions Q-1…Q-6 resolved 2026-11-02 (all as proposed). IMPLEMENTED locally 2026-11-02 (TASK-040): O-01…O-10 10/10, 0.10.0 pins 16/16 byte-identical.
**Profile:** `P2-VP-CELLS/0.10.1`, follow-up to `0.10.0` in `vpcells`; opt-in (Q-2). `0.10.0`, VP-09 and VP-07 stay byte-identical.
**Requirement:** PO-5 (MILE-003 handover); MILE-006 US-022, TASK-039/040.
**Basis:**
- `VP10_ACCEPTANCE_SPEC.md`: CS-1…CS-7, D-1…D-9.
- Mockup M-05C: „Rückkopplung“ on the entry above the diagonal.
- `M05C_COMPARISON.md`: order by first appearance; no feedback reading.

**Motivation:**

| Finding | Effect in 0.10.0 |
|---|---|
| VP-09 orders referents by first appearance in the plan | The DSM reading "above the diagonal = feedback" depends on an accidental order and cannot be used |
| No feedback mark | The M-05C note on `d-fb` has no printer counterpart |

All examples are synthetic.

## 0. Scope

| In scope | Out of scope |
|---|---|
| A declared order of the Y:referent values, used for rows and columns alike | Automatic ordering such as sequencing or clustering; the printer never computes an order |
| The text mark „Rückkopplung“ / "feedback" on marked cells above the diagonal, only with a declared order | Marks on checked, unknown or element cells; weighting; cycles (VR-09) |
| G6 option `axis_order` for `cube.cells` | Remote plan views (MILE-006 D-2) |

## 1. Design summary

`print-cells` (and G6 `cube_plan_views`, view `cube.cells`) take an optional `axis_order`: a list of display IDs.

- **Without `axis_order`:** the output is byte-identical to 0.10.0, SVG and report alike.
- **With `axis_order`:**
  - Rows and columns follow the declared order within each kind group (Q-5).
  - Values that are not listed follow at the end of their group in the previous order. Their header gets the second line `nicht geordnet` / `unordered` (Q-3).
  - Marked cells above the diagonal (row before column in the drawn order) get the line `Rückkopplung` / `feedback`.
  - The legend says that the mark follows only from the declared order, row depends on a later element, and is not a finding about the system.
  - The report and ledger carry `axis_order`, `unordered_values`, `feedback_cells` and the profile `P2-VP-CELLS/0.10.1`.

## 2. Status and diagnostic rules

| Situation | Result | Code |
|---|---|---|
| `axis_order` absent | 0.10.0 output, byte-identical | — |
| Duplicate entry in `axis_order` | error | `VP10_ORDER_INVALID` |
| Entry that is not a Y:referent value of this view (unknown, outside the slice) | ignored | `VP10_ORDER_NOT_IN_VIEW` (warning) (Q-4) |
| Not every value listed | drawn; unlisted values follow and are marked | `VP10_ORDER_PARTIAL` (warning) |
| A value hidden by `--hide-empty` | order of the remaining values unchanged; hidden ones are named as before | — |

## 3. Rules

- **AO-1:** The order is declared input, never computed. Rows and columns use the same order, so the diagonal stays the diagonal.
- **AO-2:** The feedback mark applies only to cells in state `marked` whose row comes before their column in the drawn order. That includes `d-x*` entries outside the slice. Entries of other predicates in the same cell carry no mark (Q-6).
- **AO-3:** The mark is text in the cell, not colour or line style. The colour-free audit (CS-6) still applies.
- **AO-4:** The legend names the convention: row = subject, column = object, entry above the diagonal = depends on an element that comes later in the declared order.

## 4. Acceptance criteria

| AC | Requirement | Evidence |
|---|---|---|
| VP101-01 | 0.10.0 outputs (J vectors, golden) pinned before any code and byte-identical afterwards; VP-07, VP-09 unchanged | `fixtures/regression_0100_digests.json`, SHA256SUMS |
| VP101-02 | AO-1…AO-4 and §2 rows | vectors O-01…O-10 |
| VP101-03 | Independent oracle (order, unordered values, feedback cells), hand-derived before code | `oracles/independent_o01_o10.json` |
| VP101-04 | G6 `cube.cells` accepts `axis_order`; `cube_plan_check` re-renders it | adapter test |
| VP101-05 | M-05C order (parser, resolver, validator, printer) reproduces the mockup's feedback cell `d-fb` | vector O-01, comparison note |

## 5. Vectors (planned)

The base is the R-1 DSM plan as `/8` (as in VP-10), with the pair declaration (printer, parser) and the predicate `references`.

| ID | Situation | Expectation |
|---|---|---|
| O-01 | order parser, resolver, validator, printer | rows and columns in that order; feedback on parser → validator only |
| O-02 | order printer, validator, resolver, parser (reversed) | feedback on resolver → parser, validator → resolver, printer → validator |
| O-03 | no `axis_order` (the J-02 input) | byte-identical to the pinned 0.10.0 output |
| O-04 | partial order parser, validator | resolver and printer follow in previous order, marked unordered; `VP10_ORDER_PARTIAL` |
| O-05 | duplicate entry | `VP10_ORDER_INVALID` |
| O-06 | unknown entry `m:lexer` | ignored; `VP10_ORDER_NOT_IN_VIEW` |
| O-07 | O-01 with `--hide-empty cols` | printer hidden; order of the rest unchanged |
| O-08 | O-01 plus `d-rv` resolver → validator (recovers-via), above the diagonal | no feedback mark on the other-predicate entry (Q-6) |
| O-09 | O-04, `--locale de` | `Rückkopplung`, `nicht geordnet`, German legend |
| O-10 | O-01 through G6 `cube_plan_views` + `cube_plan_check` | same SVG as the CLI; check PASS |

## 6. Detail questions (resolved 2026-11-02, all as proposed)

| Question | Options | Resolution | Reason |
|---|---|---|---|
| Q-1 Where the order lives | (a) display option of `print-cells` / G6, like `hide_empty` · (b) in the VP-10 input via `from-plan` · (c) new field in the `/8` context | **(a)** | Order is a reading aid, not a statement about the model. (c) would change P1.12, (b) the input format. |
| Q-2 Profile switch | (a) giving `axis_order` switches to 0.10.1; without it 0.10.0, byte-identical · (b) explicit `--profile` | **(a)** | No extra parameter; the pins prove that nothing changes without the option. |
| Q-3 Unlisted values | (a) follow at the end of their group, header line `nicht geordnet` · (b) error | **(a)** | A partial order is still useful for large matrices; the mark keeps "accidental position" visible. |
| Q-4 Entries not in the view | (a) warning and ignore · (b) error | **(a)** | One declared order should work across slices and hidden values; duplicates stay an error (probably a typo). |
| Q-5 Several kinds | (a) order within each kind group, kind groups as before · (b) declared order across kinds, without kind headers | **(a)** | Keeps the VP-09 layout and the kind headers; DSM views are usually one kind. |
| Q-6 Which entries get the mark | (a) only cells marked for the chosen predicate · (b) every entry above the diagonal | **(a)** | Feedback is a reading of the predicate shown in the matrix; other predicates would mix readings. |
