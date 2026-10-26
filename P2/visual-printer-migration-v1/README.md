# VP-07 — Migration Plan Views (`P2-VP-MIGRATION/0.7.0`)

Additive to the frozen `P2-VP/1.0.0-rc1` facade (VP-06). Shows declared P1.10 migration plans:
the view `cube.phases` (subjects × declared steps), declared edge styles for `cube.flow` / `cube.tree`,
materialised multi-panel export, and the adapter `from-plan`. Everything shown stays
`declared_unverified`; nothing is inferred. See `VP07_ACCEPTANCE_SPEC.md` (D-1…D-11 resolved).

## Layout

| Path | Purpose |
|---|---|
| `vpmigration/phases.py` | Path P: `cube.phases` validation, budgets with lanes, summarize ledger, SVG, report, audit |
| `vpmigration/styles.py` | Path F: unchanged VP-06 `render_job`, then dash geometry + legend (D-9) |
| `vpmigration/source.py` | migration source format `aiaeao.cube.vp07-migration-source/1` (D-10) |
| `vpmigration/adapter.py` | `from-plan`: P1.10 `binding-context/5` → migration source + `mapping.json` |
| `vpmigration/panels.py` | `print-panels` (deterministic packing, coverage ledger, text index) and `check-panels` |
| `vpmigration/__main__.py` | CLI `python3 -m vpmigration` (`vpprint` unchanged) |
| `DIAGNOSTICS.json`, `RULE_COVERAGE.json` | 19 VP-07 codes, 8 rules |
| `oracles/independent_v01_v28.json` | expectations transcribed from spec §5 before code (commit `7a069f2`) |
| `fixtures/v01_v28_materialized.json` | 28 synthetic vectors (`scripts/materialize_v01_v28.py`) |
| `fixtures/golden_migration_views.json` | synthetic golden: 31 dependencies, 4 steps, 2 tracks, 1 declared conflict (`scripts/build_golden.py`) |
| `scripts/run_vectors.py` | V-01…V-28 against the oracle |
| `tests/test_vp07.py` | 19 tests: oracle, VP-01…VP-06 regression, §2 rules, determinism, golden, P1.10 agreement, CLI |

## Run

```bash
cd P2/visual-printer-migration-v1
python3 tests/test_vp07.py
python3 scripts/run_vectors.py                         # 28/28
python3 -m vpmigration from-plan --context ctx.json --plan mp-acme --tracks tracks.json --out src.json
python3 -m vpmigration print-panels --source src.json --view cube.phases --partition subject --granularity standard --out panels/
python3 -m vpmigration check-panels --dir panels/
```

## Local results (2026-10-26)

- V-01…V-28: 28/28 match the independent oracle on first run; failures fail for the stated reason.
- 19/19 unit tests. VP-02…VP-06 `SHA256SUMS` unchanged; all four VP-06 examples re-render byte-identically,
  also through Path F without `edge_styles` (ES-5).
- Golden: `cube.phases` by subject at standard → 3 panels, 63/63 (cell, step) units; the one declared conflict
  (`x01`) is hatched in exactly one panel and listed. `cube.flow` by subject with `cube.lens.execution` →
  complete coverage, every panel carries the nested unmodified VP-05 audit (PASS). P1.10 reports the same
  dependency as `P1_MIGRATION_DANGLING_DEPENDENCY`.

## Not part of this stage

MCP tool `cube_render_plan` (D-6, follow-up with paging); G4/G5 are unchanged by VP-07. Visual acceptance
across fonts and browsers is a separate user decision (VP-06 `VISUAL_REVIEW_CHECKLIST.md`).
