# VP-09 — Declared axes view (`P2-VP-AXES/0.9.0`, `0.9.1`)

Requirement C-8. A categorical matrix over two declared axes of the seven-coordinate frame: each cell lists the
declared statements (dependencies, transition markers, facets, method bindings) that belong to both its row and its
column. No distance, position, shade, rank or numeric vector encodes anything (`core.json` `never_infer`); a blank
cell asserts nothing; steps are a declared order, not a time scale. Everything shown stays `declared_unverified`.
See `VP09_ACCEPTANCE_SPEC.md` (D-1…D-11 resolved, all as proposed; §3.4 input and entry details).

## VP-09.1 — F axes from P1.11 bindings (`0.9.1`, opt-in)

Requirement C-11. `from-plan --profile P2-VP-AXES/0.9.1` writes an axes input that carries, per binding, the
`declaration_ref` into the context, the `witness_ref`, for dependencies the declared step (`successor_first` /
`own_last`), the context's local method contracts, and every binding or argument outside the plan slice. Profile
0.9.0 stays the default and byte-identical (D-1). See `VP09_1_ACCEPTANCE_SPEC.md` (D-1…D-9 resolved, all as proposed).

- New pair **F × Y** (accounts, mailboxes, actors); entries read `owner · role`.
- **Binding ledger:** every `(binding, role)` — `(binding, *)` in F × T — is `drawn`, `off_axis` (home of the
  referent named, e.g. Y in F × Z) or `out_of_slice`, exactly once; report, embedded ledger and `check-panels` prove it.
  The legend states how many arguments are off the axis, so a partial view never looks complete.
- **Methods** must be P1.11 catalog IDs or local method contracts; anything else FAILs `VP09_METHOD_UNKNOWN` with
  its path. Rows follow the catalog order, then local methods; nothing is ranked or derived (MP-5).
- **F × T** places a `rewrite` on a dependency at the first step of its successor, i.e. in the column of the cut.
- An F axis without bindings (/5, /6) gives an empty table and `VP09_METHODS_NONE` instead of FAIL.
- Display only: whether a binding fits its plan is P1.11's job (MP-1…MP-4).
- Since VP-07.3 the catalog IDs come from `vpmigration.common.METHOD_CATALOG` (one copy on P2, VP-07.3 D-6); outputs unchanged.

## Axes and pairs

Axes: `X` (Ψ Γ Σ Ξ Π as perspectives, filled only by declared facets), `Y:kind`, `Y:referent`, `Z:kind`, `Z:referent`,
`T` (declared steps), `F` (P1.11 method bindings). `M` and `O` are reserved. Pairs, in either orientation:
Z × T, F × Z, Y × T, F × T, X × X, Y × Z, X × Z; in 0.9.1 also F × Y.

## Layout

| Path | Purpose |
|---|---|
| `vpaxes/source.py` | input (VP-07 source 0.7.1/0.7.2 or axes input), `from-plan` over the unchanged VP-07 adapter with P1.11 bindings; 0.9.1 transcription and method check |
| `vpaxes/axes.py` | values (AX-3), membership per pair (CM), SVG, report, audit; 0.9.1 binding ledger (FL) |
| `vpaxes/panels.py` | `print-panels` (rows, then columns), coverage of (row, column, entry) units, text index, `check-panels` |
| `vpaxes/__main__.py` | CLI `python3 -m vpaxes` |
| `DIAGNOSTICS.json`, `RULE_COVERAGE.json` | 15 VP-09 codes (4 since 0.9.1), 13 rules (5 since 0.9.1) |
| `oracles/independent_a01_a20.json` | expectations from spec §5 before code (commit `b93df32`) |
| `fixtures/a01_a20_materialized.json` | 20 synthetic vectors (`scripts/materialize_a01_a20.py`) |
| `fixtures/golden_axes.json` | P1.11 golden plan (3 workstreams, 33 dependencies, 23 bindings) and the three priority views (`scripts/build_golden.py`) |
| `scripts/run_vectors.py` | A-01…A-20 against the oracle |
| `tests/test_vp09.py` | 19 tests: oracle, one per §2 row, orientation, kinds, F by step, slicing, golden, VP-07 regression, CLI |
| `oracles/independent_b01_b20.json` | VP-09.1 expectations from spec §5, hand-counted, before code (commit `4223904`) |
| `fixtures/b01_b20_materialized.json` | 20 synthetic vectors incl. the P1.11 golden GM-pos (sha recorded, D-8) (`scripts/materialize_b01_b20.py`) |
| `fixtures/regression_090_digests.json` | 22 pinned 0.9.0 outputs (`scripts/pin_090_digests.py --check`) |
| `scripts/run_vectors_b.py` | B-01…B-20 against the oracle |
| `tests/test_vp091.py` | 19 tests: vectors, 0.9.0 digests, catalog pin, one per §2 row, 0.9.0 vs 0.9.1 (same VP-07 source), ledger states, panels, CLI |

## Run

```bash
cd P2/visual-printer-axes-v1
python3 -m unittest discover -s tests                   # 38 tests
python3 scripts/run_vectors.py                          # 20/20
python3 scripts/run_vectors_b.py                        # 20/20 (VP-09.1)
python3 scripts/pin_090_digests.py                      # 22/22 0.9.0 outputs byte-identical
python3 -m vpaxes from-plan --context ctx7.json --plan mp-acme --out in.json
python3 -m vpaxes print-axes --input in.json --rows Z:referent --cols T --out z-by-step/
python3 -m vpaxes print-panels --input in.json --rows F --cols Z:referent --out methods/
python3 -m vpaxes check-panels --dir methods/
python3 -m vpaxes from-plan --context ctx7.json --plan mp-acme --out in91.json --profile P2-VP-AXES/0.9.1
python3 -m vpaxes print-panels --input in91.json --rows F --cols Y:referent --out methods-y/
```

## Local results (2026-10-27)

- A-01…A-20: 20/20 match the independent oracle; the five FAIL vectors fail for the stated reason.
- 19/19 unit tests. VP-07 `SHA256SUMS` and the pinned 0.7.0/0.7.1 digests unchanged; VP-01…VP-08 untouched.
- Golden: Z × T (2 panels), Y × T (1) and F × Z (4) at standard each cover all units; kinds read Integration →
  Provider → Third-party Dependency; methods read import → rebuild → retire → rewrite.

VP-09.1 (2026-10-27): B-01…B-20 20/20; 38/38 unit tests; 22/22 pinned 0.9.0 outputs and the default
`capabilities` output byte-identical; VP-07 and P1.11 untouched. GM-pos: F × Z 41/41 arguments drawn (4 panels),
F × T 23 bindings with all 16 `rewrite` entries at p2. Every synthetic plan of the vectors passes P1.11 itself
(B-02 is UNRESOLVED there, as intended).

## In-memory API (G6, P3 C-13)

`vpaxes/api.py`: `source(context, plan_id, …, profile)` → axes input as `from-plan`; `views(source, view, granularity, rows,
cols)` → panels, index and report in memory; `check(result)` → the output of `check-panels`, which now delegates to
`check_files(files)` (CLI outputs unchanged). Used by the local MCP tools `cube_plan_*`; no profile change.

## Not part of this stage

M × T and O × X (no declared source yet); interactive pivoting; MCP tool. Methods in VP-07 views are VP-07.3.
