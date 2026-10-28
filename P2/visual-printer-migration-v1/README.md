# VP-07 — Migration Plan Views (`P2-VP-MIGRATION/0.7.0`, `0.7.1`, `0.7.2`, `0.7.3`, `0.7.4`, `0.7.5`)

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

VP-07.4 (`0.7.4`, `VP07_4_ACCEPTANCE_SPEC.md`) adds `--partition method` (single or nested, also on 0.7.3 sources):
every bar goes to the group of its own declared method, bars without one to `none`; groups follow catalog order,
`none` last, are never merged and split by subject when large. With `from-plan --profile P2-VP-MIGRATION/0.7.4`
(a /7 context still yields 0.7.3 by default) `cube.flow` panels get a methods line in the strip above the layer
caption — `TRANSITIONS AT p2 (declared) · T1 t-mail · import, retire · T3 t-box · retire` — listing the transitions
of the panel's step whose items are panel nodes or objects of a panel row at any step; two lines, then `+n more`,
full list in title and ledger. Edges of bars with a method carry `data-vp07-method`. Nothing is moved; the audit
fails if the line would overlap the panel. D-5 and D-7 were reopened at implementation and decided by the user.

VP-07.5 (`0.7.5`, `VP07_5_ACCEPTANCE_SPEC.md`, C-12) is opt-in with `from-plan --profile P2-VP-MIGRATION/0.7.5`; the
source then carries the declared role of each step. Only for 0.7.5 sources, `print-panels` takes:

- `--locale de` — display text in German from the pinned locale file `vpmigration/locales/de.json` (`en` is the identity,
  so `--locale en` equals no locale). Step roles (`Ist`, `Zwischenstand`, `Ziel`) and P1.10 predicate names
  (`sendet über`) are translated; IDs, method IDs and short names (`import`), `decl:` references and report keys never.
  Frozen VP-04/05/06 texts in `cube.flow` are replaced by exact full-text matches; a required text that does not match
  is an audit failure. A predicate without a German name shows its ID (`VP07_LOCALE_FALLBACK`).
- `--hide-ledger` — the drawn declaration ledger is left out (in `cube.flow` the frozen edge-ledger block); the embedded
  ledger, `report.json` and `check-panels` are unchanged; `ledger_hidden: true` is recorded.
- `--partition method-sets` — per method one set of panels with every bar named by a binding of that method (the bar
  carries it, or its subject or object is an argument of a transition binding); a bar can be in several sets, bars
  named by none form `none`; each set is COMPLETE on its own; the report adds `method_sets` and `memberships`, which
  `check-panels` recomputes. Deviation from the spec's flag `--method-sets`: the selection is passed as the partition
  value, so the CLI and the G6 tools need no extra argument. `--partition method` (0.7.4) is unchanged.

0.7.5 reports add `warning_summary` (per code: count and items; `warnings` stays); 0.7.5 diagnostics name the input
profile (`profile`) and the base (`printer_profile`). Error output for 0.7.0…0.7.4 is unchanged (D-8).

## Layout

| Path | Purpose |
|---|---|
| `vpmigration/phases.py` | Path P: `cube.phases` validation, budgets with lanes, summarize ledger, SVG, report, audit |
| `vpmigration/styles.py` | Path F: unchanged VP-06 `render_job`, then dash geometry + legend (D-9) |
| `vpmigration/source.py` | migration source format `aiaeao.cube.vp07-migration-source/1` (D-10) |
| `vpmigration/adapter.py` | `from-plan`: P1.10 `binding-context/5` (0.7.1 also `/6`) → migration source + `mapping.json`; 0.7.1 transcribes `declared_end` on the full plan (GM-3) |
| `vpmigration/panels.py` | `print-panels` (deterministic packing, coverage ledger, text index) and `check-panels` |
| `vpmigration/__main__.py` | CLI `python3 -m vpmigration` (`vpprint` unchanged) |
| `vpmigration/locale.py`, `vpmigration/locales/{en,de}.json` | VP-07.5 locale profile `aiaeao.cube.p2-locale/1`, pinned by SHA-256; shared with VP-09.2 |
| `DIAGNOSTICS.json`, `RULE_COVERAGE.json` | 25 VP-07 codes (VP-07.1 adds `VP07_DECLARED_GAP`, VP-07.2 `VP07_LAYER_UNASSIGNED`, VP-07.3 `VP07_METHOD_UNKNOWN`, `VP07_METHOD_ARGUMENT_HIDDEN`; VP-07.4 none; VP-07.5 `VP07_LOCALE_INVALID`, `VP07_LOCALE_FALLBACK`), 22 rules |
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
| `fixtures/regression_073_digests.json` | VP-07.4 VP074-01: SHA-256 of 14 0.7.3 scenarios (phases and flow), pinned before any 0.7.4 code (`scripts/pin_073_digests.py`) |
| `oracles/independent_n01_n14.json` | VP-07.4 expectations transcribed before code (commit `fc5f3ff`); N-11 panel selection corrected (`7bcca0a`) and count amended with D-5 (`c9dccd0`), both documented in the file |
| `fixtures/n01_n14_materialized.json` | 14 synthetic VP-07.4 vectors (`scripts/materialize_n01_n14.py`) |
| `fixtures/golden_v074.json` | VP-07.4 golden: GM-pos, method groups rewrite/none, flow lines T1 at p1, T2…T4 at p2 (`scripts/build_golden_v074.py`) |
| `scripts/run_vectors_n.py` | N-01…N-14 against the oracle |
| `tests/test_vp074.py` | 12 tests: oracle, pinned 0.7.0…0.7.3 digests, profile selection, partition on 0.7.3/0.7.4, PM-5, consistent forgery caught by check-panels, overlap audit, line bounds, inner result, golden, CLI |
| `fixtures/regression_074_digests.json` | VP-07.5 VP075-01: SHA-256 of 16 0.7.4 scenarios, pinned before any 0.7.5 code (`scripts/pin_074_digests.py`) |
| `oracles/independent_o01_o15.json` | VP-07.5 expectations and German anchor texts transcribed before code (commit `e52d337`) |
| `fixtures/o01_o15_materialized.json` | 15 synthetic VP-07.5 vectors (`scripts/materialize_o01_o15.py`); O-14 slice corrected before the code commit (documented in the script) |
| `fixtures/golden_v075.json` | VP-07.5 golden: GM-pos, method sets import 26 / rebuild 12 / retire 16 / rewrite 16 / none 1, `de`, hidden ledger (`scripts/build_golden_v075.py`) |
| `scripts/run_vectors_o.py` | O-01…O-15 against the oracle |
| `tests/test_vp075.py` | 16 tests: oracle, pinned 0.7.0…0.7.4 digests, every §2 row, identity locale, flow `de` with hidden ledger, D-3 audit, IDs, forged memberships caught, `--partition method` unchanged, summary, golden, CLI |
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
python3 scripts/run_vectors_n.py                       # 14/14 (VP-07.4)
python3 scripts/pin_073_digests.py --check             # 14/14 0.7.3 scenarios byte-identical
python3 tests/test_vp075.py
python3 scripts/run_vectors_o.py                       # 15/15 (VP-07.5)
python3 scripts/pin_074_digests.py --check             # 16/16 0.7.4 scenarios byte-identical
python3 -m vpmigration from-plan --context ctx.json --plan mp-acme --tracks tracks.json --out src.json
python3 -m vpmigration print-panels --source src.json --view cube.phases --partition subject --granularity standard --out panels/
python3 -m vpmigration check-panels --dir panels/
python3 -m vpmigration print-panels --source src.json --view cube.phases --partition track,subject --granularity standard --out by-track/
python3 -m vpmigration from-plan --context ctx.json --plan mp-acme --profile P2-VP-MIGRATION/0.7.5 --out src75.json
python3 -m vpmigration print-panels --source src75.json --view cube.phases --partition method-sets --granularity standard \
    --locale de --hide-ledger --out runbook/
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

## Local results VP-07.4 (2026-10-27)

- N-01…N-14: 14/14 match the oracle; N-06 and N-13 fail for the stated reason. Every synthetic context passes P1.11.
- Regression: pinned 0.7.0 14/14, 0.7.1 16/16, 0.7.2 13/13, 0.7.3 14/14; V 28/28, W 17/17, L 13/13, M 12/12; 88/88 VP-07 tests
  (the VP-07.3 capability test now accepts a later latest profile, as VP-07.2 did for VP-07.1).
- Golden (GM-pos): method groups rewrite (16 bars) and none; flow lines list T1 at p1 and T2…T4 at p2, which needed the
  amended D-5 (T1 introduces new-mail, used from p2).

## Local results VP-07.5 (2026-10-28)

- O-01…O-15: 15/15 match the oracle; O-05, O-08 and O-15 fail for the stated reason (O-15 names profile 0.7.5).
- Regression: pinned 0.7.0 14/14, 0.7.1 16/16, 0.7.2 13/13, 0.7.3 14/14, 0.7.4 16/16; V 28/28, W 17/17, L 13/13,
  M 12/12, N 14/14; 104/104 VP-07 tests.
- Golden (GM-pos, `de`, hidden ledger): sets import, rebuild, retire, rewrite, none with 26/12/16/16/1 bars, each COMPLETE;
  `check-panels` PASS.
- Vector correction before the code commit: O-14 needs the slice `crm-sync, shop` (with `crm-sync` alone the base
  plan's own `t-mail` adds two hidden arguments; the oracle's hand note counts only the 41 boxes). Oracle unchanged.
- With `--hide-ledger`, `cube.flow` keeps the frozen VP-06 page height (the block is removed, nothing is moved).

## In-memory API (G6, P3 C-13)

`vpmigration/api.py`: `source(context, plan_id, …)` → `{source, mapping}` as `from-plan`; `views(source, view, granularity,
partition, lens)` → `{panels: [{name, svg, sha256, input, input_sha256}], index, report}`, exactly the files of
`print-panels`; `check(result)` → the output of `check-panels`. `check_panels(directory)` now reads the folder and
delegates to `check_files(files)`; CLI outputs are unchanged (G6 pins). Used by the local MCP tools `cube_plan_*`
(`P3/adapters/mcp-local/G6_README.md`); no profile change. C-12: `views(…, locale=None, hide_ledger=False)` passes
the VP-07.5 options only when set.

## Not part of this stage

MCP tool `cube_render_plan` (D-6, follow-up with paging); G4/G5 are unchanged by VP-07 (G5 gets the plan tools only
after its own decision, because migration contexts can hold client data). VP-08 views and VP-08 locale; colours or
hatches per method; showing P1.11 fit results; user-supplied locale files and translated method names (VP-07.5 D-2 c,
D-4 b). Visual acceptance
across fonts and browsers is a separate user decision (VP-06 `VISUAL_REVIEW_CHECKLIST.md`).
