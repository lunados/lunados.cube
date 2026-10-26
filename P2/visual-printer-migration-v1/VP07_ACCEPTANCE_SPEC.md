# VP-07 — Migration Plan Views · Acceptance specification

**Status:** SPECIFIED, decisions D-1…D-11 resolved 2026-10-26 (D-1, D-4, D-6, D-7 with precisions from code review; D-9…D-11 added in review; §6) — ready for implementation.
**Profile:** `P2-VP-MIGRATION/0.7.0`, additive to the frozen `P2-VP/1.0.0-rc1` release facade (VP-06). Own package and CLI `python3 -m vpmigration` in `P2/visual-printer-migration-v1/`; `vpprint` stays unchanged (D-2).
**Code review 2026-10-26:** VP-02 `vpviews/printer.py` (`_common`, `exact_keys`, `_edges`), VP-03 `vplenses/printer.py`, VP-04 `vpgranularity/printer.py` (`CAPS`, `_select_flow`, `_assemble`), VP-05 `vpconformance/conformance.py` (`NO_ACTIVE_SVG_CONTENT`, `_split_study`), VP-06 `vpprint/core.py`, `__main__.py`; G4 `bridge.py` limits (512 KiB per SVG, 2 MiB per request).
**Basis:** VP-06 contract (`P2/visual-printer-release-v1/VP06_CONTRACT.md`, "Intentionally deferred": multi-SVG batch export, ACG→display mapping); VP-02 view grammar (`VIEW_GRAMMAR.md`), VP-03 lens grammar (`VP03_LENS_GRAMMAR.md`), VP-04 granularity, VP-05 conformance; P1.10 declared migration profile (`binding-context/5`).
**Motivation:** A migration inventory test case (2026-10-26, client details withheld; 33 referents, 47 dependencies, 4 migration steps) is bound and validated with P1.10, but cannot be shown with P2:

| Finding | Effect today |
|---|---|
| A `cube.flow` holds 2…4 nodes and ≤ 8 edges (standard: 4/4) | 47 dependencies need ≥ 12 hand-built bundles; the overview level drops exactly the migration target |
| Every edge must use `relation-arrows.reference` (`vpviews/printer.py`) | `depends-on` and `supersedes` look identical; the reader cannot tell an inventory edge from a replacement |
| No automatic multi-SVG export (VP-06 deferred) | `split_feasibility` reports e.g. "4 panels" but produces one SVG |
| No view across migration steps | The central question — *what does subject X depend on in step p0 vs. p3, and where does it break?* — has no picture |
| Bundles are written by hand (sha256 over `view_plan`, `decl:` prefixes, form per anchor) | Four format errors before the first render; authoring cost is the main adoption risk |

VP-07 adds three display capabilities and one deterministic adapter. It never infers a dependency, an order, a causality or a verdict; everything shown remains `declared_unverified`.

## 0. Scope

| In scope | Out of scope |
|---|---|
| New view `cube.phases`: subjects × migration steps, with declared objects per cell and transition markers | Gantt charts, dates on a time axis, durations (P1.10 never compares dates) |
| Declared edge styles per `predicate_id` (closed style set, legend mandatory) | Colour or style that implies status, success, risk or causality |
| Materialised multi-panel export: N SVGs + index + one coverage report | Optimal layout or proven minimal partition |
| Adapter `from-plan`: P1.10 `binding-context/5` plan → VP-03 bundle(s), deterministic | ACG text → display mapping (stays deferred); P1 validation inside P2 |
| CLI `python3 -m vpmigration` (D-2) | Changes to VP-01…VP-06 artifacts or `vpprint` subcommands, P0 symbols, P1 contracts |
| | MCP tool `cube_render_plan` (follow-up step, D-6) |

## 1. Design summary

The frozen VP-02…VP-06 chain cannot carry a new view or extra plan fields (VP-02 `_common`/`exact_keys` allow three views, no extra keys and one profile; VP-03 calls VP-02 `validate`; VP-04 fixes budgets in `CAPS`; VP-05 checks `VIEWS`). VP-07 therefore has two paths:

- **Path P (phases):** a parallel, self-contained stack for `cube.phases` — VP-07 plan → budget/reduction → audit → SVG. It reuses VP-01 primitives and P0/P1 anchor checks by import, never by editing.
- **Path F (flow/tree):** unchanged VP-06 jobs, rendered by the frozen `render_job`, then **post-processed** for edge styles and legend, the same layering pattern VP-03 and VP-04 already use (D-9). The nested VP-05 audit stays unmodified.

1. **New view `cube.phases`** (`P2-VP-MIGRATION/0.7.0`, lens `neutral` only in 0.7.0). Columns = migration steps in declared order; rows = subjects; a cell is a bar for one declared dependency across its steps (from `holds_in`); a transition marker sits on the column boundary where an object is retired or introduced. Budgets per granularity (§3.1).
2. **Edge style profile (Path F).** A VP-07 envelope `aiaeao.cube.vp07-styled-print/1` carries an unchanged VP-04 job plus `edge_styles` mapping `predicate_id` → one token of `{solid, dashed, dotted, double}` and a declared legend label. The arrowhead stays the neutral reference arrow (§3.2). In `cube.phases`, the same `edge_styles` apply to the cell bars.
3. **Panel export.** `vpmigration print-panels` partitions a VP-07 migration source (D-10) by a declared key (`subject`, `object`, `step`, or `track`) into valid plans — VP-03 bundles for `cube.flow`, VP-07 plans for `cube.phases` — renders each, and writes `panel-NN.svg`, a text-only `index.svg` (D-4) and one `report.json` with a global coverage ledger. `vpmigration check-panels` re-verifies a finished directory (§3.3).
4. **Adapter `from-plan`.** Reads a `binding-context/5`, one `plan_id` and a declared slice (track map, step range, subjects), and emits one VP-07 migration source (D-10) plus `mapping.json`. Mapping is a fixed table (§3.4); `declaration_ref` points into the context by JSON Pointer; the source context digest is recorded.

### 1.1 Shape (illustrative, synthetic)

```json
{
  "printer_profile": "P2-VP-MIGRATION/0.7.0",
  "reference_version": "v9.4",
  "view": "cube.phases",
  "lens": "neutral",
  "granularity": "standard",
  "title": "Outbound mail · steps p0 → p3",
  "steps": [{"id": "p0", "label": "current"}, {"id": "p1", "label": "team mail"}, {"id": "p2", "label": "system mail"}, {"id": "p3", "label": "target"}],
  "rows": [{"id": "outbox", "anchor_id": "module-bodies.integration", "form_id": "form.module-block", "label": "contact outbox", "semantic_ref": "Z:α:Integration[\"acme:outbox\"]"}],
  "objects": [
    {"id": "old-smtp", "anchor_id": "module-bodies.third-party-dependency", "label": "legacy SMTP"},
    {"id": "new-smtp", "anchor_id": "module-bodies.provider", "label": "new mail service"}
  ],
  "cells": [
    {"row": "outbox", "object": "old-smtp", "predicate_id": "sends-via", "steps": ["p0", "p1"], "declaration_ref": "decl:ctx#/migration_plans/0/dependencies/0"},
    {"row": "outbox", "object": "new-smtp", "predicate_id": "sends-via", "steps": ["p2", "p3"], "declaration_ref": "decl:ctx#/migration_plans/0/dependencies/1"}
  ],
  "transitions": [{"id": "t2", "at": "p2", "retires": ["old-smtp"], "introduces": [], "declaration_ref": "decl:ctx#/migration_plans/0/transitions/1"}],
  "edge_styles": [{"predicate_id": "sends-via", "style": "solid", "legend": "sends via"}],
  "declaration_status": "declared_unverified"
}
```

## 2. Status and diagnostic rules

All diagnostics follow VP-06: one JSON object on stderr, exit 2, no output directory on failure.

| Situation | Result | Diagnostic (new) |
|---|---|---|
| `cube.phases` with steps not in declared order, duplicate step, or < 2 steps | FAIL | `VP07_PHASES_STEPS` |
| Cell references unknown row, object or step; transition at unknown step | FAIL | `VP07_PHASES_REFERENCE` |
| Cell `steps` not contiguous | FAIL | `VP07_PHASES_STEPS` |
| A cell holds in a step at or after the transition that retires its object | Rendered, cell marked with hatch A; report lists it | `VP07_DECLARED_CONFLICT` (warning, not a verdict) |
| A cell holds in a step before the transition that introduces its object (D-7) | Rendered, cell marked with hatch B; report lists it | `VP07_DECLARED_PREMATURE` (warning, not a verdict) |
| `cube.phases` above its budget (rows, cells or lanes per row, §3.1) with overflow `reject`, any overflow at `detail`, or more steps than the level allows (steps are never summarized) | FAIL | `VP07_PHASES_BUDGET` |
| `cube.phases` with a lens other than `neutral` | FAIL | `VP07_PHASES_LENS` |
| `edge_styles` uses a style outside the closed set, maps one predicate twice, or has no legend | FAIL | `VP07_EDGE_STYLE` |
| `edge_styles` present but an edge's predicate has no entry | Rendered `solid`, legend row "unstyled" | `VP07_EDGE_STYLE_DEFAULT` (warning) |
| Panel partition key not declared, or a panel exceeds its budget after partition | FAIL | `VP07_PANEL_PARTITION` |
| Union of panels does not cover every item and edge of the source view, or `check-panels` finds a file, digest or ledger mismatch | FAIL | `VP07_PANEL_COVERAGE` |
| Migration source not `aiaeao.cube.vp07-migration-source/1`, or above its hard limits (D-10) | FAIL | `VP07_SOURCE_INVALID` |
| `from-plan` context not `binding-context/5`, unknown `plan_id`, or slice selects nothing | FAIL | `VP07_ADAPTER_INPUT` |
| `from-plan` referent concept without a mapping row (§3.4), or a `ref` that is not a valid display ID / exceeds 60 chars without a label-map entry (D-11) | FAIL | `VP07_ADAPTER_MAPPING` |
| Track or label map not declared JSON, maps an unknown subject, or assigns a subject twice | FAIL | `VP07_ADAPTER_INPUT` |
| Any VP-06 rule violated by a generated bundle | FAIL | existing VP-06 code |

`VP07_DECLARED_CONFLICT` and `VP07_DECLARED_PREMATURE` mirror P1.10 `P1_MIGRATION_DANGLING_DEPENDENCY` and `P1_MIGRATION_PREMATURE_DEPENDENCY` visually; they are computed from the declared cells and transitions only and never replace the P1 report.

## 3. Rules in detail

### 3.1 View `cube.phases` (PV)

- PV-1: Budgets (rows × steps × cells, lanes per row): overview 3 × 4 × 6, 2 lanes; standard 6 × 5 × 12, 3 lanes; detail 8 × 6 × 24, 4 lanes (D-1). A lane holds one bar; bars of one row that overlap in steps need separate lanes. Over budget → `overflow` as in VP-04 (`summarize` | `reject`) or panel export (§3.3). As in VP-04, `detail` never omits: over budget at `detail` is always `reject`.
- PV-1a: `summarize` keeps rows in declared order and cells in declared order until a cap is reached; every omitted row, cell and transition is listed by ID in report and SVG metadata (one embedded ledger, as VP-04).
- PV-2: Steps are drawn left to right in declared order; no step width encodes time.
- PV-3: A cell is drawn as a horizontal bar across its steps, labelled with the object label and predicate legend. Objects reuse P0 anchors and forms; no new glyphs (P0 frozen).
- PV-4: Transition markers: a vertical tick on the step boundary with the declared `id`; retire = outlined, introduce = filled (shape only, no colour semantics). Legend mandatory.
- PV-5: Declared conflicts (§2) use hatch A (diagonal `/`, legend "declared to hold after its object is retired"); premature cells use hatch B (diagonal `\`, legend "declared to hold before its object is introduced") (D-7). Hatches are explicit `line` elements clipped by geometry, not `<pattern>`/`url()`, so the VP-05 rule `NO_ACTIVE_SVG_CONTENT` (no `use`, `image`, `href`) holds unchanged. No red, no status colour.
- PV-7: Lens is `neutral` only in 0.7.0; lens emphasis for `cube.phases` is deferred.
- PV-6: Row order = declared order; no sorting by inferred importance.

### 3.2 Edge styles (ES)

- ES-1: Closed set `{solid, dashed, dotted, double}`; at most one style per `predicate_id` per view.
- ES-2: Arrowhead remains `relation-arrows.reference` for every style (no causal or temporal glyph).
- ES-3: Legend is rendered whenever `edge_styles` is present; each legend label is declared text (≤ 40 chars).
- ES-4: Applies to `cube.flow`, `cube.tree` (Path F) and `cube.phases` (Path P). Path F renders the unchanged VP-06 job with the frozen `render_job`, then sets `stroke-dasharray` (dashed `8 5`, dotted `2 4`) or a second parallel line (double) on the `line` children of each `g[data-predicate-id]`, and extends the canvas for the legend as VP-04 does for its ledger (D-9). The arrowhead `path` is not restyled.
- ES-5: A VP-06 job without `edge_styles` is never routed through VP-07; with `edge_styles` the report carries both `base_svg_sha256` (VP-06 output) and `svg_sha256` (styled), plus the unmodified VP-06 result.
- ES-6: Lens edge emphasis of VP-03 (stroke colour/width) remains visible; styles change only dash geometry, never colour.

### 3.3 Panel export (PE)

- PE-1: `vpmigration print-panels --source <vp07-migration-source.json> --view <cube.flow|cube.phases> --partition <subject|object|step|track> --granularity <level> [--lens <cube.lens.*>] --out <new-dir>`. The input is a VP-07 migration source (D-10), never a VP-04 request: VP-02 already rejects any flow above 4 nodes / 8 edges at bundle validation, so an over-budget VP-04 request cannot exist.
- PE-2: Partition is deterministic: stable order by declared order, then ID. Items may repeat across panels for context; each repetition is listed.
- PE-3: Every source item and edge appears in ≥ 1 panel (`VP07_PANEL_COVERAGE`). The report holds a global ledger: per panel shown/omitted IDs, plus a union check.
- PE-4: `index.svg` is a drawn table of contents: per panel title, partition key value, shown counts, repeated IDs and the global coverage result; no thumbnails, because VP-05 `NO_ACTIVE_SVG_CONTENT` forbids `image`/`use`/`href` (D-4). Display-only.
- PE-6: `vpmigration check-panels --dir <dir>` re-verifies a finished directory: every file listed with its SHA-256, the union check against the embedded source digest, and each panel's own report. Any mismatch → `VP07_PANEL_COVERAGE`.
- PE-5: Output directory staged and published atomically as in VP-06.

### 3.4 Adapter `from-plan` (AD)

- AD-1: `vpmigration from-plan --context <ctx.json> --plan <plan_id> [--tracks <tracks.json> --track <name>] [--labels <labels.json>] [--steps p0:p3] [--subjects id,…] --out <new-file.json>` writes one VP-07 migration source and a sibling `mapping.json`. Views and panels are produced afterwards by `print-panels` (§3.3).
- AD-2: Fixed mapping table (concept → anchor, form): `Z:module-body:integration` → `module-bodies.integration`, `form.module-block`; `…:provider` → `module-bodies.provider`; `…:third-party-dependency` → `module-bodies.third-party-dependency`; `…:runtime` → `module-bodies.runtime`; `Y:resource-object:resource` → `resource-objects.resource`, `form.resource-card`; `Y:identity-anchor:actor` → `identity-anchors.actor`, `form.identity-chip`. Unknown concept → `VP07_ADAPTER_MAPPING`.
- AD-3: `declaration_ref` = `decl:<context_id>#<JSON Pointer>`; `source_view_sha256` computed as in VP-04; context SHA-256 recorded in `mapping.json`.
- AD-4: Facets are generated only from declared fields: `kind`, `schedule` → execution; `witness_ref` → provenance; witness prefix (e.g. `plan:` vs. repository path) → epistemology note "planned" vs. "found in source", as declared text (D-5).
- AD-5: Track selection uses a declared track map file `aiaeao.cube.vp07-track-map/1` (subject ref → track name; each subject at most once) (D-3); the adapter never groups by name patterns.
- AD-7: Labels and IDs (D-11): display ID and label = referent `ref` verbatim when it matches the VP-01 ID pattern `^[A-Za-z][A-Za-z0-9_.:-]{0,99}$` and has ≤ 60 chars; otherwise a declared label map `aiaeao.cube.vp07-label-map/1` (ref → id, label) must cover it, else `VP07_ADAPTER_MAPPING`. Step labels are `phase_id · role`. No label is invented.
- AD-8: Facets come only from AD-4. A lens without generated facets is rejected downstream exactly as in VP-06 (`VP06_LENS_NOT_DECLARED`); for adapter output this means execution, provenance and epistemology are available, the others are not.
- AD-9: For `cube.flow` per step, a step in which the slice has no declared dependency produces no panel and is listed in `mapping.json` as `empty_steps`; every emitted dependency yields ≥ 2 nodes (subject, object), so the VP-02 minimum is met.
- AD-6: The adapter runs no P1 validation. Running P1.10 first is recommended, not required.

### 3.5 Migration source (MS, D-10)

- MS-1: Format `aiaeao.cube.vp07-migration-source/1`: `source_context_sha256`, `context_id`, `plan_id`, `steps`, `rows`, `objects`, `cells`, `transitions`, `edge_styles?`, `facet_bindings`, `declaration_status: declared_unverified`.
- MS-2: No panel budget; hard limits 200 rows, 200 objects, 5000 cells, 1000 transitions, 2 MiB.
- MS-3: The source is never rendered directly; only `print-panels` turns it into valid VP-03 bundles (flow) or VP-07 plans (phases).

### 3.6 Report boundary

- VP-06 report fields unchanged; VP-07 adds `migration_view_profile`, `edge_style_ledger`, `panel_ledger`, `declared_conflicts`.
- `canonical_admission`, `current_authority`, `epistemic_warrant` stay `NOT_EVALUATED`; `source_status` stays `declared_unverified`.

## 4. Acceptance criteria

| AC | Requirement | Evidence |
|---|---|---|
| VP07-01 | VP-01…VP-06 artifacts byte-identical; all VP-06 examples render byte-identical SVGs | SHA256 diff, regression run |
| VP07-02 | `cube.phases` rules PV-1…PV-6 | V-01…V-08 |
| VP07-03 | Edge styles ES-1…ES-4 | V-09…V-12 |
| VP07-04 | Panel export PE-1…PE-5, coverage proven per run | V-13…V-16 |
| VP07-05 | Adapter AD-1…AD-6; same input → byte-identical bundles | V-17…V-20, determinism test |
| VP07-06 | Every row in §2 yields exactly the stated result and code | one test per row |
| VP07-07 | No colour or glyph implies status; legend present whenever styles, markers or hatch are used | visual review checklist extension |
| VP07-08 | Synthetic golden: plan with ≥ 30 dependencies, 4 steps, 2 tracks → `from-plan` + `print-panels` covers all items; one declared conflict rendered and listed | `fixtures/golden_migration_views.json` + outputs |
| VP07-09 | Deferred with D-6: VP-07 exposes no MCP tool; `cube_discover_surface` unchanged | G4/G5 suites unchanged |
| VP07-10 | No client data in fixtures, examples or previews | review |
| VP07-11 | Migration source, track map, label map and `check-panels` rules MS-1…MS-3, AD-5, AD-7…AD-9, PE-6 | V-21…V-28 |
| VP07-12 | Path F: unchanged VP-06 result nested; `base_svg_sha256` equals the frozen `render_job` output for the same job | V-09, V-12, V-26 |

## 5. Alignment vectors (exit check)

| ID | Case | Expected |
|---|---|---|
| V-01 | `cube.phases`, 1 row, 4 steps, 2 cells, 1 transition | PASS |
| V-02 | Cell steps listed out of the declared step order | FAIL · `VP07_PHASES_STEPS` |
| V-03 | Cell with non-contiguous steps | FAIL · `VP07_PHASES_STEPS` |
| V-04 | Cell references unknown object | FAIL · `VP07_PHASES_REFERENCE` |
| V-05 | Cell holds after its object's retirement | PASS + `VP07_DECLARED_CONFLICT` |
| V-06 | Standard budget exceeded, overflow `reject` | FAIL · `VP07_PHASES_BUDGET` |
| V-07 | Standard budget exceeded, overflow `summarize` | PASS, loss ledger lists omitted cells |
| V-08 | Only one step | FAIL · `VP07_PHASES_STEPS` |
| V-09 | `cube.flow` with `edge_styles` solid/dashed | PASS, legend rendered |
| V-10 | Style `red` | FAIL · `VP07_EDGE_STYLE` |
| V-11 | Predicate styled twice | FAIL · `VP07_EDGE_STYLE` |
| V-12 | VP-06 example without `edge_styles` | PASS, SVG byte-identical to VP-06 |
| V-13 | 12-cell migration source, `print-panels --view cube.phases --partition subject` | PASS, panels cover all cells |
| V-14 | `print-panels` with partition key `colour` | FAIL · `VP07_PANEL_PARTITION` |
| V-15 | `print-panels --partition subject`, one subject alone exceeds the panel budget | FAIL · `VP07_PANEL_PARTITION` |
| V-16 | `check-panels` on a directory whose report ledger lost one cell ID | FAIL · `VP07_PANEL_COVERAGE` |
| V-17 | `from-plan` on P1.10 M-01 context, then `print-panels --view cube.flow --partition step` | PASS |
| V-18 | `from-plan` on a /4 context | FAIL · `VP07_ADAPTER_INPUT` |
| V-19 | `from-plan` with an unmapped concept | FAIL · `VP07_ADAPTER_MAPPING` |
| V-20 | `from-plan` on P1.10 golden, then `print-panels --view cube.phases` | PASS, coverage complete |
| V-21 | Cell holds before its object is introduced | PASS + `VP07_DECLARED_PREMATURE` |
| V-22 | Row needs 4 lanes at `standard`, overflow `reject` | FAIL · `VP07_PHASES_BUDGET` |
| V-23 | `cube.phases` with `cube.lens.execution` | FAIL · `VP07_PHASES_LENS` |
| V-24 | `print-panels` given a VP-04 request instead of a migration source | FAIL · `VP07_SOURCE_INVALID` |
| V-25 | `check-panels` on a directory with one panel SVG altered | FAIL · `VP07_PANEL_COVERAGE` |
| V-26 | Path F job with `edge_styles`; `base_svg_sha256` = frozen `render_job` SVG | PASS |
| V-27 | `from-plan` on a context with a `ref` containing a space, no label map | FAIL · `VP07_ADAPTER_MAPPING` |
| V-28 | Track map assigns one subject to two tracks | FAIL · `VP07_ADAPTER_INPUT` |

## 6. Decisions (resolved 2026-10-26)

| Decision | Options | Resolution | Consequence |
|---|---|---|---|
| D-1 `cube.phases` budgets | (a) as PV-1 · (b) larger detail level | **(a)** + lane cap per row (2/3/4) and no omission at `detail` | Readable on one page; a row cannot grow unbounded; `detail` keeps the VP-04 meaning. |
| D-2 Release facade | (a) new profile `P2-VP-MIGRATION/0.7.0` beside `P2-VP/1.0.0-rc1` · (b) bump facade to `P2-VP/1.1.0-rc1` | **(a)** in an own package and CLI `vpmigration` | VP-06 including `vpprint/__main__.py` stays byte-identical. |
| D-3 Track field | (a) optional `track` on dependencies in a P1.10 revision · (b) adapter argument mapping subjects to tracks · (c) no tracks | **(b)** now as declared track map; **(a)** later as a new P1 profile revision | No P1 change for VP-07; P1.10 is released and stays frozen. |
| D-4 Panel index | (a) `index.svg` · (b) `index.html` (static, no script) | **(a)**, text-only table of contents, no thumbnails | Stays within VP-05 `NO_ACTIVE_SVG_CONTENT`. |
| D-5 Epistemology note from witness prefix | (a) declared prefix list in the adapter call · (b) fixed prefixes | **(a)**; an unlisted prefix yields no note and no error | No hard-coded project conventions in the Cube. |
| D-6 MCP surface | (a) CLI only · (b) new tool `cube_render_plan` · (c) extend `cube_prepare_print` | **(a)** for VP-07; (b) as a separate follow-up with paging within 512 KiB per SVG / 2 MiB per call | Smaller acceptance scope; G4/G5 unchanged by VP-07. |
| D-7 Declared-conflict hatch | (a) render and list · (b) list only | **(a)**, extended to premature cells (hatch B) | Both P1.10 ordering findings are visible without status colour. |
| D-8 Golden fixture | (a) synthetic, modelled on the test case · (b) real inventory | **(a)** | Client data stays out of the Cube repository. |
| D-9 Edge style mechanism (added) | (a) post-process an unchanged VP-06 result, styles in a VP-07 envelope · (b) own flow/tree renderer | **(a)** | Same layering as VP-03/VP-04; every edge group already carries `data-predicate-id`; VP-05 audit stays nested and unmodified. |
| D-10 Panel input (added) | (a) new VP-07 migration source format, output of `from-plan` · (b) VP-04 request as drafted | **(a)** + `check-panels` | (b) cannot exist above budget (VP-02 caps); the source has hard limits instead of panel budgets. |
| D-11 Labels and IDs from P1.10 (added) | (a) `ref` verbatim, optional declared label map · (b) derived labels | **(a)**; steps `phase_id · role` | P1.10 has no label fields; nothing is invented. |

## 7. Not part of VP-07

- Rights on resources (shares, teams, broken inheritance) — requirement C-4, P1 first.
- Transitive dependency propagation — requirement C-1, P1 first.
- Dates and durations on a time axis.
