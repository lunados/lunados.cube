# P1.9 — Declared Comparison Profile (`binding-context/4`)

Additive to P1.8. Declares **paired comparisons** in the Cube domain — protocol,
arms, pairing, parity, outcomes — and **replay against a record**, without
computing any statistic or running anything. See `P1_9_ACCEPTANCE_SPEC.md`
(decisions D-1…D-6 resolved in §6, all as proposed).

## Layout

| Path | Purpose |
|---|---|
| `cube_p19/comparison.py` | /4 config validation (CP, AR, OC shapes, replay fields), lossless /3 projection |
| `cube_p19/validator.py` | `P19Validator`: wraps P1.8; comparison and replay checks |
| `context-v4.schema.json` | strict superset of `context-v3.schema.json` (`scripts/build_schema.py`) |
| `DIAGNOSTIC_EXTENSION.json`, `RULE_COVERAGE.json` | 13 new codes, 9 rules with Morphology references |
| `oracles/independent_c01_c20.json` | expectations transcribed from spec §5 before code |
| `fixtures/c01_c20_materialized.json` | 20 explicit vectors (`scripts/materialize_c01_c20.py`) |
| `fixtures/golden_*.json` | four golden comparisons (P1.9-15, `scripts/build_goldens.py`) |
| `scripts/run_vectors.py` | vectors directly or `--adapter` through G4; `--with-s`, `--with-r` add S and R vectors |
| `tests/test_p19.py` | 30 unit tests incl. regression, config, rules, schema, goldens with negative controls |

## Run

```bash
python3 P1/comparison-profile-v1/tests/test_p19.py
python3 P1/comparison-profile-v1/scripts/run_vectors.py --adapter --with-s --with-r   # 50/50
python3 P1/comparison-profile-v1/scripts/build_goldens.py --space ~/SitesHeroku/lunados.space --verify
python3 P3/remote-mcp-g5/scripts/assemble_core.py                                     # incl. P1.9 smoke
```

## Local results (2026-10-25)

- 30/30 unit tests, incl. byte-identical reports against P1.8 for R-01…R-13, S-01…S-17 and both P1.8 goldens.
- C-01…C-20, S-01…S-17, R-01…R-13: 50/50 directly and through the G4 adapter.
- All C vectors valid against `context-v4.schema.json`; all reports valid against the frozen `report.schema.json`.
- G4 suite 193/193, G5 contract 18/18, P1.8 suite unchanged.
- G5 assembly: PASS, 87 staged files incl. `cube_p19`; discover shows `p19_comparison`, version `P3-MCP-REMOTE/0.3.0-proof`; all four goldens PASS through the staged core.

## Golden comparisons (P1.9-15)

| File | Arms | Outcomes | What it shows |
|---|---|---|---|
| `golden_exp002b.json` | ADM (control) vs MPC | 36 (18 cases × cost, errors), bootstrap intervals | MPC has fewer errors everywhere; cost ranking flips to MPC only in `cost_first` and `loss_x6`, undetermined in `loss_x3_hazard_under` |
| `golden_exp003.json` | STATIC (control), RULE, ADAPTIVE | 4, per metric, `aggregation: none` | ADAPTIVE beats RULE, STATIC beats ADAPTIVE on Brier and net loss — no overall score |
| `golden_exp007.json` | direct (control) + 4 strategies | 4 intervals, `result_equivalence` parity | all four faster than direct at exact result parity |
| `golden_exp009d.json` | certified Fixed (control) + 5 full-coverage strategies × 3 rates | 30 deltas, calibration and holdout split | certified Fixed cheapest on holdout at every rate; 009 baseline reproduced via `replay_of` |

Every source file is pinned by SHA-256 to `lunados.space` (`web/docs/experiment/…`).
The build script **transcribes** archived numbers; outcome labels follow the archived
sign or interval under the declared direction. The Cube computes nothing. EXP-009-D
excludes `morph_reactive_native` (coverage 0.80) instead of hiding a missing parity.
The 002B and 003 source packages are on `lunados.space` branch `docs/exp-sources-002-003`
until merged.

## Supersession notes

As with P1.8, Charge 3 `test_08_never_accept_unknown_context_format` assumes
`/4` is unknown; with P1.9 it is a known, explicitly activated format. Charge 3
source pins (`p1_adapter.py`, `core_runtime.py`, `assemble_core.py`) were already
superseded by P1.8. `gateway/src/index.mjs` stays unchanged, so the MCP
`serverInfo.version` still reads the Charge 3 value; `cube_discover_surface`
reports `P3-MCP-REMOTE/0.3.0-proof`.
