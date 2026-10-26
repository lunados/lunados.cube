# VP-07 — Migration Plan Views · Acceptance specification

**Status:** DRAFT 2026-10-26 — decisions D-1…D-8 open (§6). Not ready for implementation until they are resolved.
**Profile (proposed):** `P2-VP-MIGRATION/0.7.0`, additive to the frozen `P2-VP/1.0.0-rc1` release facade (VP-06).
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
| CLI first; MCP surface per D-6 | Changes to VP-01…VP-06 artifacts, P0 symbols, P1 contracts |

## 1. Design summary

1. **New view `cube.phases`** (`P2-VP-MIGRATION/0.7.0`). Columns = migration steps in declared order; rows = subjects; a cell lists the objects the subject depends on in that step (from `holds_in`); a transition marker sits on the column boundary where an object is retired or introduced. Budgets per granularity (§3.1).
2. **Edge style profile.** Optional `edge_styles` in the view plan map `predicate_id` → one token from a closed set `{solid, dashed, dotted, double}` plus a declared legend label. The arrowhead stays the neutral reference arrow; style carries only the declared legend text (§3.2).
3. **Panel export.** `vpprint print-panels` partitions an over-budget view by a declared key (`subject`, `object`, `step`, or `track`) and writes `panel-NN.svg` per panel, `index.svg` (or `index.html`, D-4) and one `report.json` with a global coverage ledger (§3.3).
4. **Adapter `from-plan`.** Reads a `binding-context/5`, one `plan_id` and a declared slice (track, step range, subjects), and emits VP-03 bundles: `cube.flow` per step, or one `cube.phases`. Mapping is a fixed table (§3.4); `declaration_ref` points into the context by JSON Pointer; the source context digest is recorded.

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
| A cell holds in a step at or after the transition that retires its object | Rendered, cell marked with the declared-conflict pattern; report lists it | `VP07_DECLARED_CONFLICT` (warning, not a verdict) |
| `edge_styles` uses a style outside the closed set, maps one predicate twice, or has no legend | FAIL | `VP07_EDGE_STYLE` |
| `edge_styles` present but an edge's predicate has no entry | Rendered `solid`, legend row "unstyled" | `VP07_EDGE_STYLE_DEFAULT` (warning) |
| Panel partition key not declared, or a panel exceeds its budget after partition | FAIL | `VP07_PANEL_PARTITION` |
| Union of panels does not cover every item and edge of the source view | FAIL | `VP07_PANEL_COVERAGE` |
| `from-plan` context not `binding-context/5`, unknown `plan_id`, or slice selects nothing | FAIL | `VP07_ADAPTER_INPUT` |
| `from-plan` referent concept without a mapping row (§3.4) | FAIL | `VP07_ADAPTER_MAPPING` |
| Any VP-06 rule violated by a generated bundle | FAIL | existing VP-06 code |

`VP07_DECLARED_CONFLICT` mirrors P1.10 `P1_MIGRATION_DANGLING_DEPENDENCY` visually; it is computed from the declared cells only and never replaces the P1 report.

## 3. Rules in detail

### 3.1 View `cube.phases` (PV)

- PV-1: Budgets (rows × steps × cells): overview 3 × 4 × 6, standard 6 × 5 × 12, detail 8 × 6 × 24 (D-1). Over budget → `overflow` as in VP-04 (`summarize` | `reject`) or panel export (§3.3).
- PV-2: Steps are drawn left to right in declared order; no step width encodes time.
- PV-3: A cell is drawn as a horizontal bar across its steps, labelled with the object label and predicate legend. Objects reuse P0 anchors and forms; no new glyphs (P0 frozen).
- PV-4: Transition markers: a vertical tick on the step boundary with the declared `id`; retire = outlined, introduce = filled (shape only, no colour semantics). Legend mandatory.
- PV-5: Declared conflicts (§2) use one hatch pattern, explained in the legend as "declared to hold after its object is retired". No red, no status colour.
- PV-6: Row order = declared order; no sorting by inferred importance.

### 3.2 Edge styles (ES)

- ES-1: Closed set `{solid, dashed, dotted, double}`; at most one style per `predicate_id` per view.
- ES-2: Arrowhead remains `relation-arrows.reference` for every style (no causal or temporal glyph).
- ES-3: Legend is rendered whenever `edge_styles` is present; each legend label is declared text (≤ 40 chars).
- ES-4: Applies to `cube.flow`, `cube.tree` and `cube.phases`; VP-06 views without `edge_styles` render byte-identically.

### 3.3 Panel export (PE)

- PE-1: `vpprint print-panels --input <VP04.json> --partition <subject|object|step|track> --out <new-dir>`.
- PE-2: Partition is deterministic: stable order by declared order, then ID. Items may repeat across panels for context; each repetition is listed.
- PE-3: Every source item and edge appears in ≥ 1 panel (`VP07_PANEL_COVERAGE`). The report holds a global ledger: per panel shown/omitted IDs, plus a union check.
- PE-4: Index shows panel titles and a thumbnail grid; it is display-only (D-4).
- PE-5: Output directory staged and published atomically as in VP-06.

### 3.4 Adapter `from-plan` (AD)

- AD-1: `vpprint from-plan --context <ctx.json> --plan <plan_id> [--track <name>] [--steps p0:p3] [--subjects id,…] --view <cube.flow|cube.phases> --out <new-dir>` writes VP-03 bundle(s) and a `mapping.json`.
- AD-2: Fixed mapping table (concept → anchor, form): `Z:module-body:integration` → `module-bodies.integration`, `form.module-block`; `…:provider` → `module-bodies.provider`; `…:third-party-dependency` → `module-bodies.third-party-dependency`; `…:runtime` → `module-bodies.runtime`; `Y:resource-object:resource` → `resource-objects.resource`, `form.resource-card`; `Y:identity-anchor:actor` → `identity-anchors.actor`, `form.identity-chip`. Unknown concept → `VP07_ADAPTER_MAPPING`.
- AD-3: `declaration_ref` = `decl:<context_id>#<JSON Pointer>`; `source_view_sha256` computed as in VP-04; context SHA-256 recorded in `mapping.json`.
- AD-4: Facets are generated only from declared fields: `kind`, `schedule` → execution; `witness_ref` → provenance; witness prefix (e.g. `plan:` vs. repository path) → epistemology note "planned" vs. "found in source", as declared text (D-5).
- AD-5: Track selection uses a declared field (D-3); the adapter never groups by name patterns.
- AD-6: The adapter runs no P1 validation. Running P1.10 first is recommended, not required.

### 3.5 Report boundary

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
| VP07-09 | Local MCP and G5 parity for whatever D-6 exposes | adapter parity test |
| VP07-10 | No client data in fixtures, examples or previews | review |

## 5. Alignment vectors (exit check)

| ID | Case | Expected |
|---|---|---|
| V-01 | `cube.phases`, 1 row, 4 steps, 2 cells, 1 transition | PASS |
| V-02 | Steps out of declared order | FAIL · `VP07_PHASES_STEPS` |
| V-03 | Cell with non-contiguous steps | FAIL · `VP07_PHASES_STEPS` |
| V-04 | Cell references unknown object | FAIL · `VP07_PHASES_REFERENCE` |
| V-05 | Cell holds after its object's retirement | PASS + `VP07_DECLARED_CONFLICT` |
| V-06 | Standard budget exceeded, overflow `reject` | FAIL (VP-04 code) |
| V-07 | Standard budget exceeded, overflow `summarize` | PASS, loss ledger lists omitted cells |
| V-08 | Only one step | FAIL · `VP07_PHASES_STEPS` |
| V-09 | `cube.flow` with `edge_styles` solid/dashed | PASS, legend rendered |
| V-10 | Style `red` | FAIL · `VP07_EDGE_STYLE` |
| V-11 | Predicate styled twice | FAIL · `VP07_EDGE_STYLE` |
| V-12 | VP-06 example without `edge_styles` | PASS, SVG byte-identical to VP-06 |
| V-13 | 12-cell `cube.phases`, `--partition subject` | PASS, panels cover all cells |
| V-14 | Partition key `colour` | FAIL · `VP07_PANEL_PARTITION` |
| V-15 | Single subject exceeding the panel budget | FAIL · `VP07_PANEL_PARTITION` |
| V-16 | Tampered panel ledger (item missing) | FAIL · `VP07_PANEL_COVERAGE` |
| V-17 | `from-plan` on P1.10 M-01 context, `--view cube.flow` | PASS |
| V-18 | `from-plan` on a /4 context | FAIL · `VP07_ADAPTER_INPUT` |
| V-19 | `from-plan` with an unmapped concept | FAIL · `VP07_ADAPTER_MAPPING` |
| V-20 | `from-plan` on P1.10 golden, `--view cube.phases` + `print-panels` | PASS, coverage complete |

## 6. Decisions (open)

| Decision | Options | Proposal | Consequence |
|---|---|---|---|
| D-1 `cube.phases` budgets | (a) as PV-1 · (b) larger detail level | **(a)** | Readable on one A4/screen page; larger plans go through panels. |
| D-2 Release facade | (a) new profile `P2-VP-MIGRATION/0.7.0` beside `P2-VP/1.0.0-rc1` · (b) bump facade to `P2-VP/1.1.0-rc1` | **(a)** | VP-06 stays frozen; G5 adds one profile. |
| D-3 Track field | (a) optional `track` on dependencies in a P1.10 revision · (b) adapter argument mapping subjects to tracks · (c) no tracks | **(b)** now, **(a)** as P1.10 follow-up | No P1 change needed for VP-07; tracks become first-class later. |
| D-4 Panel index | (a) `index.svg` · (b) `index.html` (static, no script) | **(a)** | Stays within "deterministic SVG" output; no HTML surface. |
| D-5 Epistemology note from witness prefix | (a) declared prefix list in the adapter call · (b) fixed prefixes | **(a)** | No hard-coded project conventions in the Cube. |
| D-6 MCP surface | (a) CLI only · (b) new tool `cube_render_plan` (from-plan + print-panels, returns SVGs inline) · (c) extend `cube_prepare_print` | **(b)** after CLI acceptance | One call from a host produces all panels; existing tools unchanged. |
| D-7 Declared-conflict hatch | (a) render and list · (b) list only | **(a)** | The ordering risk becomes visible without a status colour. |
| D-8 Golden fixture | (a) synthetic, modelled on the test case · (b) real inventory | **(a)** | Client data stays out of the Cube repository. |

## 7. Not part of VP-07

- Rights on resources (shares, teams, broken inheritance) — requirement C-4, P1 first.
- Transitive dependency propagation — requirement C-1, P1 first.
- Dates and durations on a time axis.
