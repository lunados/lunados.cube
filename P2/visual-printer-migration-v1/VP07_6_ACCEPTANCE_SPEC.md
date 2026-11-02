# VP-07.6 — Origin lines and statement sets in `cube.flow` · Acceptance specification

**Status:** SPECIFIED. MILE-011 decisions D-1…D-8 apply (2026-11-02); detail questions Q-1…Q-10 resolved 2026-11-02 (all as proposed). Not implemented.
**Profile:** `P2-VP-MIGRATION/0.7.6`, opt-in follow-up to `0.7.5` in the same package `vpmigration`. `0.7.0…0.7.5` stay byte-identical.
**Requirement:** VR-01 of the MILE-003 handover (`docs/09-Research/visual-check/HANDOVER.md` §2, rank 1), mockup M-01A; PO-1 (two meanings of "declared"); PO-7 for `cube.flow` (statement sets without a migration plan); MILE-011 D-4, D-5.
**Basis:** `VP07_ACCEPTANCE_SPEC.md` (ES-1…ES-6 edge styles, PE-1…PE-5 panels, AD-1…AD-9 adapter, MS-1…MS-3 source), `VP07_1…VP07_5_ACCEPTANCE_SPEC.md`; VP-02 `vpviews` (edges as `g[data-edge-id][data-declaration-ref]`); P1.14 (`binding-context/10`, `origin`, `basis`, `statement-set/2`); VP-10 0.11.0 statement sets and projection records (MILE-007, SS-1…SS-4, PR-1…PR-6, Q-10).
**Motivation:**

| Finding | Effect today |
|---|---|
| `edge_styles` maps a **predicate** to a line style | the same predicate `uses` cannot show "declared" and "condensed" differently; style follows the name the author chose (C4-03) |
| The header says `CUBE.FLOW · DECLARED RELATIONSHIPS`, the legend uses "declared" for "not derived" | two meanings of one word (PO-1, blind check B06/B13) |
| `cube.flow` reads only migration plans; the adapter maps six concepts | the C4 cases (`Z:boundary:boundary`, `Z:module-body:tool`, `Y:resource-object:artifact`) cannot be drawn (PO-7) |

VP-07.6 draws each edge by its **bound origin** and lets `cube.flow` read a statement set. It never computes an origin, never derives an edge and never judges a relation; everything stays `declared_unverified`.

## 0. Scope

| In scope | Out of scope |
|---|---|
| Origin mode for `cube.flow` (plan path and statement path) | Origin in `cube.phases`, `cube.sequence`, `cube.axes`, `cube.cells`, `cube.instances` |
| Statement path: `statement-set/1` or `/2` against a `/10` context, optional projection records (read) | Computing aggregations; comparing with a foreign model |
| Header text after PO-1 in 0.7.6 | Changes to VP-01…VP-06 or to `0.7.0…0.7.5` output |
| CLI and G6 (`cube_plan_source`, `cube_plan_views`, `cube_plan_check`); G5 in TASK-067 | New VG anchors (none needed) |

## 1. Design summary

1. **Origin mode (OL).** With `--origin-lines` (CLI) or `origin_lines: true` (G6), every edge of `cube.flow` takes its line style from its bound origin: `declared` solid, `derived` dashed, `unknown` dotted, **not bound** dotted (M-01A). The predicate stays the edge label. The arrowhead stays `relation-arrows.reference` (ES-2).
2. **Origin text (OT).** Every edge label ends with its origin as text: `· declared`, `· derived from s-1, s-2`, `· origin unknown`, `· origin not bound` (German with `locale de`, Q-6). The origin is readable without colour and without the line style.
3. **Legend (OG).** A fixed legend with the three line styles and the four texts replaces the `edge_styles` legend in origin mode.
4. **Statement path (SP).** `cube_plan_source` with `printer: vpmigration`, `plan_id: null`, `statements` (`statement-set/1` or `/2`) and optional `records` (MILE-007 projection records) produces a `cube.flow` source; `print-panels` partitions by `subject` or `object` (Q-3).
5. **Plan path.** `from-plan` with a `/10` context reads `origin` and `basis` of each dependency (P1.14 OR-6).
6. **Per edge, not per predicate.** Styling targets each `g[data-edge-id]` through its `data-declaration-ref`, after the frozen `render_job` (Path F layering pattern of VP-07, D-9).
7. **PO-1.** In 0.7.6 the header reads `CUBE.FLOW · FIXTURE ASSERTIONS · no inferred chronology or causality` (Q-8).

## 2. Origin resolution (per edge)

| Source of the edge | Origin shown | Text |
|---|---|---|
| Statement or dependency with `origin: declared` | declared (solid) | `· declared` |
| `origin: derived` with a resolvable `basis` of kind `statements` | derived (dashed) | `· derived from <statement IDs>` |
| Derived statement of a projection record (`origin: derived`, `derived_from`) | derived (dashed) | `· derived from <derived_from>` |
| `origin: unknown` | unknown (dotted) | `· origin unknown` |
| No `origin` (`statement-set/1`, plan in `/5…/9`, predicate without `origin_binding`) | not bound (dotted) | `· origin not bound` |

- OL-1: An edge without bound origin is **never solid**.
- OL-2: A `derived` edge whose `basis` does not resolve, or whose `basis` is missing, is drawn as **not bound** and reported (`VP07_ORIGIN_UNRESOLVED`, warning); the printer gives no P1 verdict.
- OL-3: Projection records are checked as in MILE-007 Q-10 (format, `method_id`, `library_ref` shape, `input_set_sha256` against the given set); a mismatch rejects the input (`VP07_ORIGIN_RECORD_INVALID`).

## 3. Status and diagnostic rules

| Situation | Result | Code |
|---|---|---|
| Origin mode and `edge_styles` in one request | FAIL | `VP07_ORIGIN_STYLE_CONFLICT` (new) |
| Origin mode with a view other than `cube.flow` | FAIL | `VP07_ORIGIN_VIEW` (new) |
| Statement path with a statement set that fails SS-1…SS-4 | FAIL | the VP-10 statement codes, prefixed `VP07_` (Q-9) |
| Projection record does not match the set (OL-3) | FAIL | `VP07_ORIGIN_RECORD_INVALID` (new) |
| `derived` edge without resolvable basis (OL-2) | rendered as not bound; warning | `VP07_ORIGIN_UNRESOLVED` (new) |
| Concept outside the mapping table (AD-2 plus Q-2) | FAIL | `VP07_ADAPTER_MAPPING` (existing) |
| Without origin mode | 0.7.5 behaviour | unchanged |

## 4. Acceptance criteria

| AC | Requirement | Evidence |
|---|---|---|
| VP076-01 | `0.7.0…0.7.5` outputs pinned before code and byte-identical afterwards; VP-09, VP-10, VP-11 unchanged | pins, `VP07_SHA256SUMS.txt` |
| VP076-02 | OL-1…OL-3, OT, OG for both paths | vectors OL-01…OL-12 (§5) |
| VP076-03 | Every row of §3 | vectors |
| VP076-04 | Text-only check: for every edge the origin text is present in the SVG and in the report's `origin_ledger` | test over all vectors |
| VP076-05 | No colour carries the origin; dash geometry only (ES-6) | test |
| VP076-06 | G6 = CLI byte-identical; `cube_plan_check` PASS | adapter test |
| VP076-07 | Independent oracle for OL-01…OL-12 committed before code (TASK-064) | `oracles/independent_ol01_ol12.json` |

## 5. Vectors (planned; fixed in TASK-064)

| ID | Case | Expected |
|---|---|---|
| OL-01 | C4-02 statement set as `/2`, all source statements `declared` | all solid, `· declared` |
| OL-02 | C4-02 aggregated (`all`) through a projection record | `api → db` dashed, `· derived from s-1, s-2` |
| OL-03 | C4-03: `api → db` once `declared`, once `derived` with basis | one solid, one dashed, both with text |
| OL-04 | `statement-set/1` (no origin) | all dotted, `· origin not bound` |
| OL-05 | `origin: unknown` | dotted, `· origin unknown` |
| OL-06 | `derived` without basis | dotted, warning `VP07_ORIGIN_UNRESOLVED` |
| OL-07 | migration plan in `/10` with mixed origins (plan path) | styles per dependency |
| OL-08 | origin mode plus `edge_styles` | FAIL `VP07_ORIGIN_STYLE_CONFLICT` |
| OL-09 | origin mode with `cube.phases` | FAIL `VP07_ORIGIN_VIEW` |
| OL-10 | projection record with wrong `input_set_sha256` | FAIL `VP07_ORIGIN_RECORD_INVALID` |
| OL-11 | OL-03 with `locale de` | German texts and legend |
| OL-12 | G6 round trip of OL-02 and `cube_plan_check` | equal to CLI, PASS |

## 6. Boundaries

- The line style shows what is **declared** about the origin, not whether it is true.
- Dashed against dotted is the weakest distinction (MILE-003 mockups, open question 3); the text carries the origin on its own, and the visual check of TASK-068 asks for it.
- Large flows stay subject to the panel budgets of VP-06/VP-07 and, remotely, to the CPU limit of the G5 Worker (MILE-010 spec §10).

## 7. Detail questions (resolved 2026-11-02, all as proposed)

| ID | Question | Decision | Reason |
|---|---|---|---|
| **Q-1** | How is origin mode switched on? | Opt-in flag **`origin_lines`** (G6 source option, CLI `--origin-lines`), only with profile `0.7.6` | keeps every existing call byte-identical |
| **Q-2** | Which concepts does the statement path map? | AD-2 **plus** `Z:boundary:boundary` → `governance-boundary.boundary`, `Z:module-body:tool` → `module-bodies.tool`, `Y:resource-object:artifact` → `resource-objects.artifact` (forms as for their families); closed table, unknown still `VP07_ADAPTER_MAPPING` | the C4 and DSM cases need exactly these; anchors exist in `symbols.json` |
| **Q-3** | Panels for statements? | Partition **`subject`** or **`object`**; no steps, no tracks | statements have no plan steps |
| **Q-4** | Unknown and not bound: same line? | **Both dotted**, distinguished by text | M-01A has three line styles; a fourth would weaken the set |
| **Q-5** | Style per edge or per predicate? | **Per edge** via `data-declaration-ref` | one predicate can have different origins (C4-03) |
| **Q-6** | Wording? | en: `declared`, `derived from …`, `origin unknown`, `origin not bound`; de: `deklariert`, `abgeleitet aus …`, `Herkunft unbekannt`, `Herkunft nicht gebunden` | as the MILE-003 handover; `locale` as in 0.7.5 |
| **Q-7** | Long source lists? | At most **three** statement IDs in the label, then `+n`; the full list in the report's `origin_ledger` | label length (≤ 40 characters per legend label stays) |
| **Q-8** | PO-1 header? | `FIXTURE ASSERTIONS` in 0.7.6 only, by post-processing the frozen header | PO-1 without touching VP-02 |
| **Q-9** | Codes for invalid statement sets? | Reuse the VP-10 checks SS-1…SS-4 with `VP07_` codes (`VP07_STATEMENT_SET_INVALID`, `…_REF_UNKNOWN`, `…_PREDICATE_INVALID`) | one rule set, printer-specific prefix |
| **Q-10** | Arrowhead for derived edges? | **Neutral** `relation-arrows.reference` for all; `relation-arrows.derivation` is not used | D-5: the arrowhead must not encode origin twice or imply causality |
