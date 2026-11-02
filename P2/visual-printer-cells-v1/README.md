# VP-10 — Cell states from declared coverage (`vpcells`, `P2-VP-CELLS/0.10.0`)

**Status:** IMPLEMENTED locally 2026-11-02. Decisions D-1…D-9 are resolved, all as proposed; see [VP10_ACCEPTANCE_SPEC.md](VP10_ACCEPTANCE_SPEC.md).

This is gap VR-05 from MILE-003 and PO-6. `vpcells` wraps the unchanged VP-09.2 path (`vpaxes`) and draws the directed Y:referent × Y:referent matrix. Every cell gets exactly one state:

| State | Shown as |
|---|---|
| **marked** | declared entries, as in VP-09.2; `d-x*` means declared in the plan but outside the slice (D-4) |
| **checked empty** | bold border with `none · checked (pair / row / column)`, only within the declared survey scope (CV-2) |
| **unknown** | horizontal line hatch, explicit `line` elements, no `<pattern>` |
| **hidden** | `--hide-empty` removes only values without marked or checked cells, and names them in the legend |

The diagonal reads `element` and has no state. Coverage comes from the `coverage_declarations` of a `binding-context/8` (P1.12), for one predicate per view. A declaration with `instance_ref`, or one naming a referent outside this input, is ignored and reported. VP-07, VP-09 and their locale files are unchanged.

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

## Run

```bash
cd P2/visual-printer-cells-v1
python3 scripts/run_vectors.py          # 14/14
python3 tests/test_vp10.py              # 24 tests
python3 -m vpcells from-plan --context ctx8.json --plan mp-dsm --predicate references --out in.json
python3 -m vpcells print-cells --input in.json --hide-empty cols --locale de --out cells/
```

## Local results (2026-11-02)

- **Vectors:** J-01…J-14 14/14 against the independent oracle.
- **Unit tests:** 24/24 pass.
- **Frozen layers:** `VP07_SHA256SUMS` and `VP09_SHA256SUMS` hold, and the pinned 0.9.0 and 0.9.1 outputs are byte-identical. The `vpaxes` suite passes, and so do the P1 suites including P1.12.
- **Golden:** 4 marked, 3 checked, 2 unknown, 3 element and 4 hidden cells; column `m:printer` is hidden by name.
- **Renders and reports:** `docs/10-Evidence/MILE-005/task035/`.

## Not part of VP-10

- Other pairs, and statement sets without a plan (PO-7, G-03).
- Declared axis order (PO-5).
- MCP adapter (TASK-036) and G5 delivery.
