# VP-09 — Declared axes view (`P2-VP-AXES/0.9.0`)

Requirement C-8. A categorical matrix over two declared axes of the seven-coordinate frame: each cell lists the
declared statements (dependencies, transition markers, facets, method bindings) that belong to both its row and its
column. No distance, position, shade, rank or numeric vector encodes anything (`core.json` `never_infer`); a blank
cell asserts nothing; steps are a declared order, not a time scale. Everything shown stays `declared_unverified`.
See `VP09_ACCEPTANCE_SPEC.md` (D-1…D-11 resolved, all as proposed; §3.4 input and entry details).

## Axes and pairs

Axes: `X` (Ψ Γ Σ Ξ Π as perspectives, filled only by declared facets), `Y:kind`, `Y:referent`, `Z:kind`, `Z:referent`,
`T` (declared steps), `F` (P1.11 method bindings). `M` and `O` are reserved. Pairs, in either orientation:
Z × T, F × Z, Y × T, F × T, X × X, Y × Z, X × Z.

## Layout

| Path | Purpose |
|---|---|
| `vpaxes/source.py` | input (VP-07 source 0.7.1/0.7.2 or axes input), `from-plan` over the unchanged VP-07 adapter with P1.11 bindings |
| `vpaxes/axes.py` | values (AX-3), membership per pair (CM), SVG, report, audit |
| `vpaxes/panels.py` | `print-panels` (rows, then columns), coverage of (row, column, entry) units, text index, `check-panels` |
| `vpaxes/__main__.py` | CLI `python3 -m vpaxes` |
| `DIAGNOSTICS.json`, `RULE_COVERAGE.json` | 11 VP-09 codes, 8 rules |
| `oracles/independent_a01_a20.json` | expectations from spec §5 before code (commit `b93df32`) |
| `fixtures/a01_a20_materialized.json` | 20 synthetic vectors (`scripts/materialize_a01_a20.py`) |
| `fixtures/golden_axes.json` | P1.11 golden plan (3 workstreams, 33 dependencies, 23 bindings) and the three priority views (`scripts/build_golden.py`) |
| `scripts/run_vectors.py` | A-01…A-20 against the oracle |
| `tests/test_vp09.py` | 19 tests: oracle, one per §2 row, orientation, kinds, F by step, slicing, golden, VP-07 regression, CLI |

## Run

```bash
cd P2/visual-printer-axes-v1
python3 tests/test_vp09.py
python3 scripts/run_vectors.py                          # 20/20
python3 -m vpaxes from-plan --context ctx7.json --plan mp-acme --out in.json
python3 -m vpaxes print-axes --input in.json --rows Z:referent --cols T --out z-by-step/
python3 -m vpaxes print-panels --input in.json --rows F --cols Z:referent --out methods/
python3 -m vpaxes check-panels --dir methods/
```

## Local results (2026-10-27)

- A-01…A-20: 20/20 match the independent oracle; the five FAIL vectors fail for the stated reason.
- 19/19 unit tests. VP-07 `SHA256SUMS` and the pinned 0.7.0/0.7.1 digests unchanged; VP-01…VP-08 untouched.
- Golden: Z × T (2 panels), Y × T (1) and F × Z (4) at standard each cover all units; kinds read Integration →
  Provider → Third-party Dependency; methods read import → rebuild → retire → rewrite.

## Not part of this stage

M × T and O × X (no declared source yet); interactive pivoting; MCP tool.
