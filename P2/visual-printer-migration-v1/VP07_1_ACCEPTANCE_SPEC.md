# VP-07.1 — Migration Plan Views, nested panels and marker legibility · Acceptance specification

**Status:** DRAFT 2026-10-26 — decisions D-1…D-8 open (§6). Not ready for implementation until they are resolved.
**Profile (proposed):** `P2-VP-MIGRATION/0.7.1`, follow-up to `P2-VP-MIGRATION/0.7.0` (VP-07, PR #12).
**Basis:** `VP07_ACCEPTANCE_SPEC.md` (PV-1…PV-7, PE-1…PE-6, MS-1…MS-3, D-1…D-11), `vpmigration/phases.py` (transition markers, legend), `vpmigration/panels.py` (`_groups`, `_pack`, coverage ledger), `vpmigration/source.py`; P1.10.1 draft (`P1/migration-profile-v2/P1_10_1_ACCEPTANCE_SPEC.md`, requirement C-7) for item (d).
**Motivation:** A field test of P1.10 + VP-07 with a real migration inventory (2026-10-26; about 33 referents, 47 dependencies, 4 steps p0–p3, 3 workstreams; client details withheld) produced requirement C-6:

| Finding | Effect in 0.7.0 |
|---|---|
| `print-panels` partitions by one key only | `--partition track` fails with `VP07_PANEL_PARTITION` as soon as one workstream has more than 6 rows (standard); `--partition subject` mixes workstreams in one picture. Workaround: `from-plan --track <name>` per workstream, then `print-panels` per source — coverage is then proven per source only, never for the whole plan. |
| Transition labels | Drawn at 9 px above the step header and cut to 10 characters (`excerpt(t['id'], 10)`, e.g. "t1-team-m…"). |
| Several markers at one boundary | A retirement marker and an introduction marker of different transitions at the same boundary overlap; the label of the second sits on the first marker (offset 30 px, label anchored left of its marker). |
| Legend text | The hatch rows read "hatch / · declared to hold after its object is retired" and "hatch \ · …"; the "/ ·" is a text defect. |

VP-07.1 fixes these three items and, if D-7 is accepted, draws the P1.10.1 "dependency gap" (C-7) in `cube.phases`. It never infers a dependency, an order or a verdict; everything shown stays `declared_unverified`.

## 0. Scope

| In scope | Out of scope |
|---|---|
| Two-level partition `--partition <outer>,<inner>` with coverage proven per outer group and for the whole source | More than two levels; automatic choice of keys; optimal packing |
| Legible transition markers: readable size, short codes with a marker legend, deterministic offset for several markers at one boundary | Dates, durations or any time axis |
| Corrected legend wording for hatches (and the new gap mark, D-7) | New colours; status or risk colouring |
| Optional gap mark (D-7) computed from declared cells, transitions and target step | Running P1 inside P2 |
| `0.7.0` inputs keep rendering byte-identically (D-1) | Changes to VP-01…VP-06; MCP tool (still deferred, VP-07 D-6) |

## 1. Design summary

1. **Profile dispatch.** Plans, panel inputs and migration sources carry their profile. `0.7.0` documents render exactly as today, so `check-panels` on directories produced with 0.7.0 keeps passing; `0.7.1` documents get the new partition, markers, legend and (D-7) gap mark (D-1).
2. **Nested partition.** `print-panels --partition track,subject` first groups cells by the outer key (declared order), then packs each outer group by the inner key exactly as 0.7.0 packs a single key. Panels never mix outer groups. The report adds an outer-group ledger: per outer value its panels, its units and its own coverage result; the global union check stays.
3. **Markers.** Each transition gets a short code `T1, T2, …` in declared order. Above the column boundary only the code is drawn (≥ 11 px); the full transition ID, the retired and introduced object labels and the declared step appear in a **transition legend** below the grid. Several transitions at one boundary are stacked vertically in declared order with a fixed step, never overlapping.
4. **Legend wording.** Hatch rows read "Hatch A (diagonal lines rising) — declared to hold after its object is retired" and "Hatch B (diagonal lines falling) — declared to hold before its object is introduced"; the sample swatch stays left of the text.

### 1.1 Shape (illustrative, synthetic)

```text
vpmigration print-panels --source acme-src.json --view cube.phases --partition track,subject --granularity standard --out panels/
```

```json
{
  "partition": ["track", "subject"],
  "outer_ledger": [
    {"outer_value": "mail", "panels": ["panel-01", "panel-02"], "units_total": 34, "units_covered": 34, "status": "COMPLETE"},
    {"outer_value": "files", "panels": ["panel-03"], "units_total": 28, "units_covered": 28, "status": "COMPLETE"}
  ],
  "coverage": {"status": "COMPLETE", "units_total": 62, "units_covered": 62}
}
```

Marker legend (synthetic):

```text
T1  t-intro   at p1 · introduces new mail service, new file store
T2  t-mail    at p2 · retires legacy mail service
T3  t-files   at p3 · retires legacy file store
```

## 2. Status and diagnostic rules

| Situation | Result | Diagnostic |
|---|---|---|
| `--partition` with more than two keys, a repeated key, or `step` as outer key with `cube.flow` (flow panels are per step already) | FAIL | `VP07_PANEL_PARTITION` (existing) |
| Outer key `track` but a row has no declared track | FAIL | `VP07_PANEL_PARTITION` (existing) |
| One inner group alone exceeds the panel budget | FAIL | `VP07_PANEL_PARTITION` (existing), message names outer and inner value |
| An outer group's panels do not cover all its units, or the outer ledger disagrees with the panels | FAIL | `VP07_PANEL_COVERAGE` (existing) |
| More transitions at one boundary than the marker stack allows (D-4) | FAIL | `VP07_PHASES_BUDGET` (existing) |
| A cell ends before the target step without retirement of its object, without successor and without drop (D-7) | Rendered with the gap mark; report lists it | `VP07_DECLARED_GAP` (warning, not a verdict) |
| A 0.7.1-only feature requested on a 0.7.0 document (nested partition on a 0.7.0 source, gap fields in a 0.7.0 source) | FAIL | `VP07_SOURCE_INVALID` / `VP07_PANEL_PARTITION` (existing) |

## 3. Rules in detail

### 3.1 Nested partition (NP)

- NP-1: `--partition` takes one key (0.7.0 behaviour) or `outer,inner` with distinct keys from `{subject, object, step, track}`.
- NP-2: Outer groups follow declared order (first appearance in the cell list); each outer group is packed by the inner key with the 0.7.0 packing rule (PE-2). Panels are numbered globally in outer, then inner order.
- NP-3: Coverage unit stays `(cell_id, step)`. The report holds `outer_ledger` (per outer value: panels, units total/covered, status) and the global `coverage`. Both must be COMPLETE.
- NP-4: `check-panels` recomputes the outer ledger from the panel inputs and the embedded source.
- NP-5: The index lists panels grouped under their outer value.

### 3.2 Transition markers (TM)

- TM-1: Codes `T1…Tn` in declared transition order of the plan (panel plans keep the source numbering, so the same transition has the same code in every panel).
- TM-2: Marker glyphs keep their meaning: outlined circle = declares a retirement, filled circle = declares an introduction; a transition doing both shows both, side by side.
- TM-3: Code text ≥ 11 px; never truncated (codes are ≤ 4 characters).
- TM-4: Several transitions at one boundary stack upwards in declared order, fixed pitch (D-4); the header reserves space for the deepest stack in the plan.
- TM-5: The transition legend lists, per code, the full transition ID, the declared step and the labels of retired/introduced objects; long labels wrap (two lines) rather than truncate; the full text is also in the SVG `<title>`.

### 3.3 Legend wording (LW)

- LW-1: Hatch rows: "Hatch A (diagonal lines rising) — declared to hold after its object is retired", "Hatch B (diagonal lines falling) — declared to hold before its object is introduced".
- LW-2: Text and swatch are separate elements; no glyph is used as a separator.

### 3.4 Gap mark (GM, only if D-7 = a)

- GM-1: A cell has a declared gap if its last step is before the plan's target step, its object is not retired at the next step, its subject is not retired at the next step (if P1.10.1 D-3 adopts that exemption), and it carries neither successor nor drop.
- GM-2: The migration source 0.7.1 carries the fields needed: `target_step` (the plan's `target` phase, even when `--steps` slices it away) and per cell `successor` (dependency ID or absent) and `dropped` (bool). `from-plan` fills them from the context.
- GM-3: Drawn as an end cap at the bar's right edge (short vertical bar plus open bracket) and listed in the legend as "Gap — declared to end before the target step without retirement, successor or drop". No colour.
- GM-4: The mark mirrors P1.10.1 `P1_MIGRATION_DEPENDENCY_GAP`; it never replaces the P1 report.

## 4. Acceptance criteria

| AC | Requirement | Evidence |
|---|---|---|
| VP071-01 | VP-01…VP-06 unchanged; VP-07 0.7.0 vectors V-01…V-28 and 0.7.0 golden outputs byte-identical (SVG SHA-256 pinned before code) | regression run against pinned digests |
| VP071-02 | Nested partition NP-1…NP-5 | W-01…W-06 |
| VP071-03 | Transition markers TM-1…TM-5 | W-07…W-11 |
| VP071-04 | Legend wording LW-1, LW-2 | W-12 |
| VP071-05 | Gap mark GM-1…GM-4 (if D-7 = a) | W-13…W-16 |
| VP071-06 | Every row in §2 yields exactly the stated result and code | one test per row |
| VP071-07 | Synthetic golden: 3 workstreams, one with 9 rows, partition `track,subject` covers everything; one boundary with 3 transitions; one declared gap | `fixtures/golden_v071.json` |
| VP071-08 | No client data in fixtures, examples or previews | review |

## 5. Alignment vectors (exit check)

| ID | Case | Expected |
|---|---|---|
| W-01 | Source with 2 tracks, `--partition track,subject`, standard | PASS, no panel mixes tracks, outer ledger COMPLETE for both |
| W-02 | Track with 9 rows, `--partition track,subject`, standard | PASS, that track spans 2 panels |
| W-03 | `--partition track,subject,object` | FAIL · `VP07_PANEL_PARTITION` |
| W-04 | `--partition subject,subject` | FAIL · `VP07_PANEL_PARTITION` |
| W-05 | `--partition track,subject` with a row lacking a track | FAIL · `VP07_PANEL_PARTITION` |
| W-06 | `check-panels` after removing one panel ID from an outer ledger entry | FAIL · `VP07_PANEL_COVERAGE` |
| W-07 | Transition ID of 24 characters | PASS, code `T1` above the grid, full ID in legend and `<title>` |
| W-08 | Two transitions at one boundary (one retires, one introduces) | PASS, markers stacked, no overlapping bounding boxes |
| W-09 | One transition retiring and introducing | PASS, both glyphs side by side under one code |
| W-10 | Same transition in two panels | PASS, same code in both |
| W-11 | More transitions at one boundary than D-4 allows | FAIL · `VP07_PHASES_BUDGET` |
| W-12 | Plan with a declared conflict and a premature cell | PASS, legend rows exactly as LW-1 |
| W-13 | Cell ends at p1, target p3, object never retired, no successor, no drop | PASS + `VP07_DECLARED_GAP` (if D-7 = a) |
| W-14 | W-13 with `dropped: true` | PASS, no gap mark |
| W-15 | W-13 with the object retired at p2 | PASS, no gap mark (P1.10 DP-4 case) |
| W-16 | W-13 sliced with `--steps p0:p1` | PASS + `VP07_DECLARED_GAP` (target step taken from the plan, GM-2) |
| W-17 | 0.7.0 source through 0.7.1 code | PASS, SVG byte-identical to 0.7.0 |

## 6. Decisions (open)

| Decision | Options | Proposal | Consequence of the proposal |
|---|---|---|---|
| D-1 Relation to 0.7.0 | (a) profile dispatch in the same package; 0.7.0 documents render byte-identically · (b) separate package `visual-printer-migration-v1.1` · (c) change 0.7.0 in place | **(a)** | `check-panels` stays valid for existing 0.7.0 directories; one CLI; digests of all 0.7.0 outputs pinned before code. |
| D-2 Nesting depth | (a) exactly two levels · (b) arbitrary depth | **(a)** | Covers workstream × subject; deeper nesting is not motivated by the field test. |
| D-3 Allowed outer keys | (a) `track`, `object`, `subject` for both views, `step` only for `cube.phases` · (b) `track` only | **(a)** | Keeps the 0.7.0 key set; flow panels are per step already, so `step` as outer key adds nothing there. |
| D-4 Marker stack | (a) up to 4 transitions per boundary, pitch 16 px · (b) unlimited, header grows | **(a)** | Header height stays bounded; a fifth transition at one boundary FAILs with a clear message instead of an unreadable stack. |
| D-5 Transition codes | (a) `T1…Tn` in plan order, stable across panels · (b) per-panel numbering · (c) full IDs, wrapped | **(a)** | Same code in every panel and in the legend; no truncation. |
| D-6 Legend placement | (a) transition legend below the grid, after the style legend · (b) right margin | **(a)** | Uses the existing canvas extension; the grid width (0.7.0) stays unchanged. |
| D-7 Gap mark (C-7) | (a) draw and list `VP07_DECLARED_GAP` in 0.7.1, source 0.7.1 carries `target_step`, `successor`, `dropped` · (b) list only · (c) not in VP-07.1 | **(a)**, dependent on P1.10.1 D-1…D-3 | The inventory error of the field test (bar ends at p1, nothing explains it) becomes visible in the picture, consistent with the P1 diagnostic. |
| D-8 Golden fixture | (a) synthetic, three workstreams modelled on the field test · (b) real inventory | **(a)** | Client data stays out of the Cube repository. |

## 7. Not part of VP-07.1

- MCP tool `cube_render_plan` (VP-07 D-6) — separate step.
- Rights, shares and inheritance on resources; transitive dependency propagation.
- Start gaps (a dependency that begins after the current step without introduction or predecessor) — see P1.10.1 §7.
