# VP-08 — Sequence Views (`P2-VP-SEQUENCE/0.8.0`)

Additive to the frozen `P2-VP/1.0.0-rc1` facade (VP-06) and independent of VP-07/VP-07.1. Shows, per declared
trigger (UI button, schedule, webhook, CLI, event, manual), the declared messages between modules as a sequence
view `cube.sequence`: lifelines, numbered arrows (call, return, async, self), activation bars and `alt` / `opt` /
`loop` frames. Message numbers give the declared order only — never a time axis — and an arrow never asserts
causation, success or authority. Everything shown stays `declared_unverified`; returns are drawn only when
declared. See `VP08_ACCEPTANCE_SPEC.md` (D-1…D-10 resolved).

## Layout

| Path | Purpose |
|---|---|
| `vpsequence/source.py` | source format `aiaeao.cube.vp08-sequence-source/1` (SS-1…SS-5) |
| `vpsequence/sequence.py` | `cube.sequence`: analysis (numbering, return warnings), windows (SS-6), SVG, report, audit |
| `vpsequence/panels.py` | `print-panels` (one panel per trigger window, coverage ledger, text trigger index) and `check-panels` |
| `vpsequence/__main__.py` | CLI `python3 -m vpsequence` |
| `vpsequence/common.py` | helpers; VP-01…VP-06 primitives imported through the VP-07 path setup, never edited |
| `DIAGNOSTICS.json`, `RULE_COVERAGE.json` | 14 VP-08 codes, 8 rules |
| `oracles/independent_s01_s20.json` | expectations transcribed from spec §5 before code (commit `0381470`) |
| `fixtures/s01_s20_materialized.json` | 20 synthetic vectors (`scripts/materialize_s01_s20.py`) |
| `fixtures/golden_sequence.json` | synthetic shop: 5 participants, 4 triggers (3 buttons, 1 schedule), `alt` with nested `loop`, one continued sequence (`scripts/build_golden.py`) |
| `scripts/run_vectors.py` | S-01…S-20 against the oracle |
| `tests/test_vp08.py` | 18 tests: oracle, one per §2 row, golden, use-case partition, determinism, VP-07 regression, CLI |

## Run

```bash
cd P2/visual-printer-sequence-v1
python3 tests/test_vp08.py
python3 scripts/run_vectors.py                          # 20/20
python3 -m vpsequence check-sequence --source src.json --trigger btn-checkout
python3 -m vpsequence print-panels --source src.json --partition trigger --granularity standard --out panels/
python3 -m vpsequence check-panels --dir panels/
```

## Local results (2026-10-26)

- S-01…S-20: 20/20 match the independent oracle; the ten FAIL vectors fail for the stated reason.
- 18/18 unit tests. VP-07 0.7.0 pinned digests 14/14 and `VP07_SHA256SUMS.txt` unchanged; VP-01…VP-06 untouched.
- Golden: `--partition trigger` at standard → 5 panels (Daily reminders continues in 2 windows), 34/34
  (trigger, message) units; Checkout shows `alt` [payment accepted / declined] with a nested `loop`.

## Not part of this stage

MCP tool (D-10); flowchart view; clickable HTML index; link to migration steps; time or duration views.

## In-memory API (G6, P3 C-13)

`vpsequence/api.py`: `views(source, view='cube.sequence', granularity, partition, overflow)` → panels, index and report in
memory, exactly the files of `print-panels`; `check(result)` → the output of `check-panels`, which now delegates to
`check_files(files)` (CLI outputs unchanged). VP-08 has no `from-plan`; its sources are declared directly (G6 D-7).
