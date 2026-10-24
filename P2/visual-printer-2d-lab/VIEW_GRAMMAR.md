# VP-02 — Cube View Grammar (local experimental specification)

**Contract**: `P2-VP-VIEWS/0.2.0`. **Morphology source**: v9.4 / immutable P0. **Visual presentation**: `P1-VG-basic/1.0.0` (copied source-locked). **Scope**: layout projections only. Does not redefine P1 or create runtime/API capabilities.

## Exact namespace (deliberately distinct from AIAEAO Planner)

| Value | Applies to | Accepted input | Rejection / nonimplication |
|---|---|---|---|
| `cube.flow` | Directed, *declared* typed **display** edges | 2–4 nodes; 1–8 declared relation pointers; explicit entire node order; `left-to-right` or `top-down` | `flow`, `planner.flow`, unprofiled directionality, implicit time, causal or typing claims |
| `cube.diagramm` | Comparable quantities | Bar or line; 2–6 numbers; one measure, one named unit, zero-based linear scale and declaration pointer | `chart`, `cube.chart`, unlabeled/mixed units, implicit observation, inferred timestamp order |
| `cube.tree` | Single-root, declared hierarchy | 2–7 nodes; exactly n−1 declared parent→child edges; explicit breadth-first order; ≤4 levels, ≤5 nodes/level | Multiple parents, cycles, orphans, guessed ownership/hierarchy |

`cube.diagramm` is **quantitative** and intentionally retains the user's German spelling. A generic network or architecture visualization is **not** `cube.diagramm` merely because it looks like a diagram.

## Freezes for isolated VP-02 evaluation

`lens: "neutral"` and `granularity: "standard"` **must** be supplied; they are fixed now. Perspective-changing Lens Profiles and adjustable complexity belong to later work packages. No 3D or spatial embedding is provided. The three accepted IDs are view-projection contract keys, **not** new concept IDs, scopes, or axes.

## Input contracts

Schemas: `VIEW_PLAN.schema.json` (Draft 2020-12 structural schema); `PRINT_REPORT.schema.json` for successful outputs. The Python validator adds cross-field rules not expressible in the simple structural schema: identity/order permutations, connected trees, cycle/multiple-parent rejection, value precision, and P0/P1 anchor binding compatibility. Strict JSON loader rejects duplicate object keys and nonfinite JSON constants.

- `cube.flow` requires an explicit, order-preserving full `order` array. The order is **display order only**, never derived chronology. Links require exact `from`, `to`, `predicate_id`, `declaration_ref`, and registered neutral arrow anchor `relation-arrows.reference`. No extra relations are invented.
- `cube.tree` requires exactly one `root_id`, a single parent per nonroot, an acyclic connected structure, and declared parent→child signatures. A DAG cannot be silently collapsed to a tree; switch views or declare a valid tree.
- `cube.diagramm` requires `metric.id`, `unit`, `scale: linear_zero_based`, `declaration_ref`, `evidence_status: declared_unverified`; all sample values finite, nonnegative, ≤1e9 and precision ≤3 decimals. The numbers are **fixture declarations**, not live measurements. Sample array order is an authored category/point order, never temporal attestation.
- No view infers a universal predicate signature, verified provenance or current governance state; a printer-rendered relation may still fail P1 validation. The presence of a textual `declaration_ref` is not an independent attestation.

## Complexity cut — temporary hard limits

Hard layout budgets (node/edge/sample counts above) deliberately produce `ViewError`, rather than silent truncation. All data must remain visible in a single golden SVG. Automatic aggregation, pages, focus selection, lens-specific omission and dynamic depth-of-field are **not implemented in VP-02**.

## Identity, symbols, forms and colors

Every node's `anchor_id` must resolve in P1's 129-anchor registry and its suggested/default `form_id` must match that anchor. The Unicode glyph is copied verbatim as display data, not normalized into canonical identity. Domain accents only apply where permitted. Status accents require an explicit qualified witness reference but **do not validate it**. No font files or external assets are shipped or downloaded.

`data-item-id`, `data-anchor-id`, `data-semantic-ref` (if supplied), and `data-predicate-id`/`data-declaration-ref` are inspectable SVG attributes. A JSON report records displayed IDs, edge declarations (or chart source/unit), the SVG SHA-256 and explicit `NOT_EVALUATED` decisions for semantic conformance, warrant, authority and admission.

## The six authored examples

1. `01_cube_flow_migration`: Artifact→Resource illustrative fixture, rooted in P1 migration.
2. `02_cube_flow_research`: three-node top-down illustration extending the metaphysics theme, **not** a new adopted ontology fact.
3. `03_cube_diagramm_bar`: synthetic inventory count per class, unit `items`.
4. `04_cube_diagramm_line`: synthetic comparative latency, unit `ms`; the polyline does not claim time progression.
5. `05_cube_tree_modules`: authored Core/module grouping, **not** proof of a deployed runtime.
6. `06_cube_tree_resources`: authored grouping of Resource/Artifact/Source/Cache/Revision/Evidence, **not** globally adopted `groups` predicate signatures.

The two flow/tree examples using `fixture:VP02/...` declarations deliberately test display geometry only. They do not inherit P1's typed predicate contracts.

## Known unresolved presentation issues

Actual typographic glyph coverage varies between SVG hosts, browsers, operating systems and installed fonts; some CairoSVG previews render fallback squares for mathematical characters. The original glyph remains in SVG source and is accompanied by a visible text label and inspectable `data-anchor-id`. macOS/Safari, Claude and Grok display fidelity and human acceptance remain open.
