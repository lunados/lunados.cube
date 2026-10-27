# VP-07 — Migration Plan Views (`P2-VP-MIGRATION/0.7.0`, `0.7.1`, `0.7.2`, `0.7.3`)

Additive to the frozen `P2-VP/1.0.0-rc1` facade (VP-06). Shows declared P1.10 migration plans:
the view `cube.phases` (subjects × declared steps), declared edge styles for `cube.flow` / `cube.tree`,
materialised multi-panel export, and the adapter `from-plan`. Everything shown stays
`declared_unverified`; nothing is inferred. See `VP07_ACCEPTANCE_SPEC.md` (D-1…D-11 resolved).

VP-07.1 (`0.7.1`, `VP07_1_ACCEPTANCE_SPEC.md`, D-1…D-8 resolved) adds, by profile dispatch in the same package:
nested partition `--partition outer,inner` with an outer ledger, coded transition markers (`T1…Tn`) with a
transition legend, the corrected hatch wording (Hatch A / Hatch B) and the declared gap mark mirroring P1.10.1
`P1_MIGRATION_DEPENDENCY_GAP` (`VP07_DECLARED_GAP`, warning only). `0.7.0` plans, sources and panel directories
render byte-identically; `from-plan` emits `0.7.1` unless `--profile P2-VP-MIGRATION/0.7.0` is given and also
accepts P1.10.1 `binding-context/6`.

VP-07.2 (`0.7.2`, `VP07_2_ACCEPTANCE_SPEC.md`, D-1…D-8 resolved) adds a declared layer map
(`aiaeao.cube.vp07-layer-map/1`, `from-plan --layers`): rows of `cube.phases` and nodes of `cube.flow` follow the
declared layers (e.g. platform → dns → provider → account → system → actor), `cube.phases` draws a layer band per
run of rows, `cube.flow` panels get a layer caption, and `--partition layer` (also nested) never mixes layers.
Layers are never derived from concept IDs or the graph. Without `--layers`, `from-plan` emits 0.7.1 exactly as before.

VP-07.3 (`0.7.3`, `VP07_3_ACCEPTANCE_SPEC.md`, D-1…D-8 resolved, requirement C-11) reads a P1.11
`binding-context/7`: `from-plan` selects 0.7.3 by itself and transcribes the declared method bindings, each with its
`declaration_ref`, onto the shown transitions and bars. `cube.phases` names them in the transition legend
(`T2 · t-mail-cut · at p2 · … · import, retire`, catalog order, D-4) and as a bar suffix (`legacy-mail · sends-via ·
rewrite`) that is never cut; markers keep their shape, codes and stacking (`data-vp07-methods` only). Methods get no
colour, hatch or glyph. Unknown method IDs FAIL `VP07_METHOD_UNKNOWN` (same rule as VP-09.1; the catalog constant
lives here and VP-09 imports it, D-6); arguments outside a slice keep their declared ref and warn
`VP07_METHOD_ARGUMENT_HIDDEN`. Layers work as in 0.7.2. `/5` and `/6` contexts behave exactly as before. Display only:
whether a method fits its transition is P1.11's job.

## Layout

| Path | Purpose |
|---|---|
| `vpmigration/phases.py` | Path P: `cube.phases` validation, budgets with lanes, summarize ledger, SVG, report, audit |
| `vpmigration/styles.py` | Path F: unchanged VP-06 `render_job`, then dash geometry + legend (D-9) |
| `vpmigration/source.py` | migration source format `aiaeao.cube.vp07-migration-source/1` (D-10) |
| `vpmigration/adapter.py` | `from-plan`: P1.10 `binding-context/5` (0.7.1 also `/6`) → migration source + `mapping.json`; 0.7.1 transcribes `declared_end` on the full plan (GM-3) |
| `vpmigration/panels.py` | `print-panels` (deterministic packing, coverage ledger, text index) and `check-panels` |
| `vpmigration/__main__.py` | CLI `python3 -m vpmigration` (`vpprint` unchanged) |
| `DIAGNOSTICS.json`, `RULE_COVERAGE.json` | 23 VP-07 codes (VP-07.1 adds `VP07_DECLARED_GAP`, VP-07.2 `VP07_LAYER_UNASSIGNED`, VP-07.3 `VP07_METHOD_UNKNOWN`, `VP07_METHOD_ARGUMENT_HIDDEN`), 15 rules |
| `oracles/independent_v01_v28.json` | expectations transcribed from spec §5 before code (commit `7a069f2`) |
| `fixtures/v01_v28_materialized.json` | 28 synthetic vectors (`scripts/materialize_v01_v28.py`) |
| `fixtures/golden_migration_views.json` | synthetic golden: 31 dependencies, 4 steps, 2 tracks, 1 declared conflict (`scripts/build_golden.py`) |
| `scripts/run_vectors.py` | V-01…V-28 against the oracle |
| `tests/test_vp07.py` | 19 tests: oracle, VP-01…VP-06 regression, §2 rules, determinism, golden, P1.10 agreement, CLI |
| `fixtures/regression_070_digests.json` | VP-07.1 PD-4: SHA-256 of 14 0.7.0 outputs, pinned before any 0.7.1 code (`scripts/pin_070_digests.py`) |
| `oracles/independent_w01_w17.json` | VP-07.1 expectations transcribed from spec §5 before code (commit `ca56800`) |
| `fixtures/w01_w17_materialized.json` | 17 synthetic VP-07.1 vectors (`scripts/materialize_w01_w17.py`) |
| `fixtures/golden_v071.json` | VP-07.1 golden: 3 workstreams (one with 9 subjects), 3 transitions at p2, 1 declared gap (`scripts/build_golden_v071.py`) |
| `scripts/run_vectors_w.py` | W-01…W-17 against the oracle |
| `fixtures/regression_071_digests.json` | VP-07.2 VP072-01: SHA-256 of 16 0.7.1 outputs, pinned before any 0.7.2 code (`scripts/pin_071_digests.py`) |
| `oracles/independent_l01_l13.json` | VP-07.2 expectations transcribed from spec §5 before code (commit `6b06b14`) |
| `fixtures/l01_l13_materialized.json` | 13 synthetic VP-07.2 vectors (`scripts/materialize_l01_l13.py`) |
| `fixtures/golden_v072.json` | VP-07.2 golden: 6 layers × 3 tracks, inventory listed against the layer order (`scripts/build_golden_v072.py`) |
| `scripts/run_vectors_l.py` | L-01…L-13 against the oracle |
| `tests/test_vp072.py` | 17 tests: oracle, pinned 0.7.0/0.7.1 digests, §2 rows, layer partition, lanes, golden, CLI |
| `fixtures/regression_072_digests.json` | VP-07.3 VP073-01: SHA-256 of 13 0.7.2 outputs, pinned before any 0.7.3 code (`scripts/pin_072_digests.py`) |
| `oracles/independent_m01_m12.json` | VP-07.3 expectations transcribed from spec §5 before code (commit `7e5918f`) |
| `fixtures/m01_m12_materialized.json` | 12 synthetic VP-07.3 vectors (`scripts/materialize_m01_m12.py`) |
| `fixtures/golden_v073.json` | VP-07.3 golden: P1.11 GM-pos (4 transitions with methods, 16 `rewrite` bars; `scripts/build_golden_v073.py`) |
| `scripts/run_vectors_m.py` | M-01…M-12 against the oracle |
| `tests/test_vp073.py` | 16 tests: oracle, pinned 0.7.0/0.7.1/0.7.2 digests, catalog pin, §2 rows, unchanged markers, ledger, flow, golden, CLI |
| `tests/test_vp071.py` | 24 tests: oracle, pinned 0.7.0 digests, §2 rows, gap rules, markers, nested flow/phases, golden, P1.10.1 agreement, CLI |

## Run

```bash
cd P2/visual-printer-migration-v1
python3 tests/test_vp07.py
python3 scripts/run_vectors.py                         # 28/28
python3 tests/test_vp071.py
python3 scripts/run_vectors_w.py                       # 17/17 (VP-07.1)
python3 scripts/pin_070_digests.py --check             # 14/14 0.7.0 outputs byte-identical
python3 tests/test_vp072.py
python3 scripts/run_vectors_l.py                       # 13/13 (VP-07.2)
python3 scripts/pin_071_digests.py --check             # 16/16 0.7.1 outputs byte-identical
python3 scripts/run_vectors_m.py                       # 12/12 (VP-07.3)
python3 scripts/pin_072_digests.py --check             # 13/13 0.7.2 outputs byte-identical
python3 -m vpmigration from-plan --context ctx.json --plan mp-acme --tracks tracks.json --out src.json
python3 -m vpmigration print-panels --source src.json --view cube.phases --partition subject --granularity standard --out panels/
python3 -m vpmigration check-panels --dir panels/
python3 -m vpmigration print-panels --source src.json --view cube.phases --partition track,subject --granularity standard --out by-track/
```

## Local results (2026-10-26)

- V-01…V-28: 28/28 match the independent oracle on first run; failures fail for the stated reason.
- 19/19 unit tests. VP-02…VP-06 `SHA256SUMS` unchanged; all four VP-06 examples re-render byte-identically,
  also through Path F without `edge_styles` (ES-5).
- Golden: `cube.phases` by subject at standard → 3 panels, 63/63 (cell, step) units; the one declared conflict
  (`x01`) is hatched in exactly one panel and listed. `cube.flow` by subject with `cube.lens.execution` →
  complete coverage, every panel carries the nested unmodified VP-05 audit (PASS). P1.10 reports the same
  dependency as `P1_MIGRATION_DANGLING_DEPENDENCY`.

## Local results VP-07.1 (2026-10-26)

- W-01…W-17: 17/17 match the independent oracle; the five FAIL vectors fail for the stated reason.
- 0.7.0 regression: 14/14 pinned output digests byte-identical; V-01…V-28 28/28; `test_vp07.py` 19/19.
- 24/24 VP-07.1 unit tests. VP-01…VP-06 untouched.
- Golden: `cube.phases` by `track,subject` at standard → mail 2 panels, files 1, identity 1; 66/66 units, every
  outer group COMPLETE. The one declared gap (`g01`) carries the end cap in exactly one panel; P1.10.1 reports the
  same dependency as `P1_MIGRATION_DEPENDENCY_GAP`. A three-subject slice shows the three p2 transitions stacked
  as `T2…T4` without overlap.

## Local results VP-07.2 (2026-10-27)

- L-01…L-13: 13/13 match the independent oracle; the four FAIL vectors fail for the stated reason.
- Regression: 0.7.0 14/14 and 0.7.1 16/16 pinned digests byte-identical; V 28/28, W 17/17; `test_vp07` 19/19, `test_vp071` 24/24.
- 17/17 VP-07.2 unit tests.
- Golden: rows read shop → invoice-job → crm-sync → report-job → backup-job → finance-team → support-team although the
  inventory lists actors first; `track,layer` at standard covers everything with one layer per panel; the shop flow
  panel at p0 reads hosting → dns-zone → legacy-mail → shop (platform · dns · provider · system).

## Local results VP-07.3 (2026-10-27)

- M-01…M-12: 12/12 match the independent oracle; the two FAIL vectors fail for the stated reason. Every synthetic
  context passes P1.11 itself (M-03 is UNRESOLVED there, as intended).
- Regression: 0.7.0 14/14, 0.7.1 16/16 and 0.7.2 13/13 pinned digests byte-identical; V 28/28, W 17/17, L 13/13;
  all 76 VP-07 unit tests. VP-09: 22/22 pinned 0.9.0 outputs, A 20/20, B 20/20, 38/38 tests.
- Golden (GM-pos): 33 dependencies, 3 panels by subject, coverage COMPLETE; legend reads T1 rebuild, T2/T3 import,
  retire, T4 rebuild, retire; 16 bars end in `rewrite`; markers identical to the same plan without methods.

## Not part of this stage

MCP tool `cube_render_plan` (D-6, follow-up with paging); G4/G5 are unchanged by VP-07. Methods in `cube.flow` and
VP-08 views, partition by method (VP-07.3 §7). Visual acceptance
across fonts and browsers is a separate user decision (VP-06 `VISUAL_REVIEW_CHECKLIST.md`).
