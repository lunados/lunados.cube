# VP-10 — Cell states from declared coverage (`vpcells`, `P2-VP-CELLS/0.10.0`, opt-in `0.10.1` and `0.11.0`)

**Status:** IMPLEMENTED locally 2026-11-02. Decisions D-1…D-9 are resolved, all as proposed; see [VP10_ACCEPTANCE_SPEC.md](VP10_ACCEPTANCE_SPEC.md).

This is gap VR-05 from MILE-003 and PO-6. `vpcells` wraps the unchanged VP-09.2 path (`vpaxes`) and draws the directed Y:referent × Y:referent matrix. Every cell gets exactly one state:

| State | Shown as |
|---|---|
| **marked** | declared entries, as in VP-09.2; `d-x*` means declared in the plan but outside the slice (D-4) |
| **checked empty** | bold border with `none · checked (pair / row / column)`, only within the declared survey scope (CV-2) |
| **unknown** | horizontal line hatch, explicit `line` elements, no `<pattern>` |
| **hidden** | `--hide-empty` removes only values without marked or checked cells, and names them in the legend |

The diagonal reads `element` and has no state. Coverage comes from the `coverage_declarations` of a `binding-context/8` (P1.12), for one predicate per view. A declaration with `instance_ref`, or one naming a referent outside this input, is ignored and reported. VP-07, VP-09 and their locale files are unchanged.

## VP-10.1 — declared axis order (`P2-VP-CELLS/0.10.1`)

Opt-in display option `axis_order` (CLI `--axis-order a,b,c`, G6 `cube_plan_views` option `axis_order`), specified in [VP10_1_ACCEPTANCE_SPEC.md](VP10_1_ACCEPTANCE_SPEC.md). Without it the output is `0.10.0`, byte for byte.

- Rows and columns follow the declared order within each kind group; values not listed follow at the end of their group and carry the header line `unordered` / `nicht geordnet` (warning `VP10_ORDER_PARTIAL`).
- A marked cell of the chosen predicate above the diagonal gets the italic text line `feedback` / `Rückkopplung`: the row depends on an element declared later. This follows from the declared order only; it is not a finding about the system, and no colour or line style changes.
- A value twice, an empty list or a non-string entry is `VP10_ORDER_INVALID`; a value outside the view is ignored with `VP10_ORDER_NOT_IN_VIEW`.
- The report and ledger add `axis_order`, `unordered_values`, `order_not_in_view`, `feedback_cells` and `order_locale`. The German texts are in their own pinned file `locales/de-0101.json` (`LOCALE_PINNED_0101`), so `de.json` and its digest stay unchanged.

## VP-10 0.11.0 — statement sets without a plan (`P2-VP-CELLS/0.11.0`)

Specified in [VP110_ACCEPTANCE_SPEC.md](VP110_ACCEPTANCE_SPEC.md) (MILE-007, PO-7 and G-03). `from-statements` reads a declared statement set (`aiaeao.cube.statement-set/1`) for a `binding-context/8` instead of a migration plan; an own matrix drawer (Q-3) shows it with the 0.10.x states.

- Axes are the set's `referents`, one home on both axes (Y × Y or Z × Z, Q-2); row = subject, column = object, no transposed reading (D-6).
- Only resolution is checked: referents and predicates must be in the context, concepts allowed by the predicate contract, endpoints listed in `referents` (SS-1…SS-4). The statements stay `declared_unverified`.
- With `--projection`, a record (`aiaeao.cube.projection-record/1`: `library_ref`, call, result) of lunados.lib `project.aggregate-relations/v1` is read, never recomputed (Q-10, PR-6). Derived entries read `derived · n sources` / `abgeleitet · n Quellen`; the legend carries the exact loss line (DR-8); the ledger lists every source, label, internal and suppressed source.
- Coverage applies to plain sets only; with an aggregation it is ignored with `VP10_COVERAGE_NOT_PROJECTED` (Q-9). `axis_order` and `--hide-empty` work as in 0.10.x.
- German texts are in their own pinned file `locales/de-0110.json` (`LOCALE_PINNED_0110`). 0.10.0 and 0.10.1 outputs stay byte-identical (pins 16/16 and 9/9).

## Layout

| Path | Purpose |
|---|---|
| `vpcells/source.py` | `from-plan`: `/8` → projection → unchanged VP-09.2 adapter, plus a `coverage` block (declarations in display IDs, full-plan pairs, ignored declarations) |
| `vpcells/cells.py` | states (CS-1…CS-5), drawing over the VP-09.2 SVG, legend, ledger, audit (CS-6), report |
| `vpcells/locales/de.json` | VP-10 texts in German, pinned (`LOCALE_PINNED`) |
| `oracles/independent_j01_j14.json` | cell states per vector, hand-derived before code (`2316f45`) |
| `fixtures/j01_j14_materialized.json` | 14 synthetic vectors on the MILE-003 R-1 DSM plan (`scripts/materialize_j01_j14.py`) |
| `fixtures/golden_cells.json` | pair and row declaration, column printer hidden, `en` and `de`; the context passes P1.12 (`scripts/build_golden.py`) |
| `scripts/run_vectors.py` | J-01…J-14 against the oracle |
| `tests/test_vp10.py` | 24 tests: oracle, frozen VP-07/VP-09 (SHA256SUMS, pinned 0.9.0/0.9.1 digests), 0.9.2 regression, one per §2 row, states, colour-free audit, locale, golden, CLI |
| `M05C_COMPARISON.md` | VP-10 against mockup M-05C: same cells and states; differences named |
| `vpcells/locales/de-0101.json` | VP-10.1 texts in German, pinned (`LOCALE_PINNED_0101`) |
| `oracles/independent_o01_o10.json` | VP-10.1 expectations, hand-derived before code (`507f8a6`) |
| `fixtures/regression_0100_digests.json` | SVG and report digests of 16 `0.10.0` outputs (`scripts/pin_0100_digests.py`) |
| `fixtures/o01_o10_materialized.json` | 10 synthetic vectors on the J-02 context (`scripts/materialize_o01_o10.py`) |
| `scripts/run_vectors_o.py` | O-01…O-10 against the oracle, O-10 through the G6 API |
| `tests/test_vp101.py` | 14 tests: oracle, byte identity without order, locale pins, kind groups, invalid orders, text-not-colour mark, ledger, G6, CLI |
| `vpcells/statements.py`, `vpcells/matrix.py` | 0.11.0: `from-statements` (resolution, projection record) and the own matrix drawer |
| `vpcells/locales/de-0110.json` | 0.11.0 texts in German, pinned (`LOCALE_PINNED_0110`) |
| `oracles/independent_s01_s16.json` | 0.11.0 expectations, hand-derived before code (`91e1c57`); inputs in `docs/09-Research/statement-sets` |
| `fixtures/regression_0101_digests.json` | SVG and report digests of 9 `0.10.1` outputs (`scripts/pin_0101_digests.py`) |
| `fixtures/s01_s16_materialized.json` | 16 vectors with projection records from the pinned lunados.lib evaluator (`scripts/materialize_s01_s16.py`) |
| `scripts/run_vectors_s.py` | S-01…S-16 against the oracle, S-16 through the G6 API |
| `tests/test_vp110.py` | 17 tests: oracle, pins, locale files, input checks, projection record checks, read-not-recompute, audit, hiding, labels, order, G6, CLI |

## Run

```bash
cd P2/visual-printer-cells-v1
python3 scripts/run_vectors.py          # 14/14
python3 tests/test_vp10.py              # 24 tests
python3 scripts/run_vectors_o.py        # 10/10 (VP-10.1)
python3 scripts/pin_0100_digests.py     # 16/16 byte-identical
python3 tests/test_vp101.py             # 14 tests
python3 scripts/run_vectors_s.py        # 16/16 (0.11.0)
python3 scripts/pin_0101_digests.py     # 9/9 byte-identical
python3 tests/test_vp110.py             # 17 tests
python3 -m vpcells from-plan --context ctx8.json --plan mp-dsm --predicate references --out in.json
python3 -m vpcells print-cells --input in.json --hide-empty cols --locale de --out cells/
python3 -m vpcells print-cells --input in.json --axis-order m:parser,m:resolver,m:validator,m:printer --out ordered/
python3 -m vpcells from-statements --context ctx8.json --statements set.json [--projection record.json] [--predicate P] --out in.json
```

## Local results (2026-11-02)

- **Vectors:** J-01…J-14 14/14 against the independent oracle.
- **Unit tests:** 24/24 pass.
- **Frozen layers:** `VP07_SHA256SUMS` and `VP09_SHA256SUMS` hold, and the pinned 0.9.0 and 0.9.1 outputs are byte-identical. The `vpaxes` suite passes, and so do the P1 suites including P1.12.
- **Golden:** 4 marked, 3 checked, 2 unknown, 3 element and 4 hidden cells; column `m:printer` is hidden by name.
- **Renders and reports:** `docs/10-Evidence/MILE-005/task035/`.
- **VP-10 0.11.0 (MILE-007 TASK-046):** S-01…S-16 16/16; 0.10.0 16/16 and 0.10.1 9/9 byte-identical; 17 tests; renders in `docs/10-Evidence/MILE-007/task046/`.
- **VP-10.1 (MILE-006 TASK-040):** O-01…O-10 10/10; the 16 pinned `0.10.0` outputs stay byte-identical; 14 tests; renders in `docs/10-Evidence/MILE-006/task040/`.

## Not part of VP-10

- Other pairs, and statement sets without a plan (PO-7, G-03).
- MCP adapter (TASK-036) and G5 delivery.
