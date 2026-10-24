# VP-03 — Lens Profiles / Projection Grammar

**Contract:** `P2-VP-LENSES/0.3.0` · **Input:** `aiaeao.cube.vp03-lens-bundle/1` · **Output report:** `aiaeao.cube.vp03-print-report/1`.

## Purpose

A perspective switch for the **same, unchanged** authored VP-02 view plan. `cube.flow`, `cube.diagramm`, and `cube.tree` retain identical geometry, declarations, ordered node/edge/sample sets and quantitative values. The only changing layer is *presentational emphasis* of explicitly annotated targets.

The five supported profiles are:

| Contract ID | P1 VG domain token | Intended display question (not a conclusion) |
| --- | --- | --- |
| `cube.lens.semantics` | `domain.semantics` | Which identifiers, types and declared relations should be inspected? |
| `cube.lens.provenance` | `domain.provenance` | Which declared source pointers, revisions and origins should be inspected? |
| `cube.lens.execution` | `domain.execution` | Which planned/declared operations or objects merit attention? Not proof of a Run. |
| `cube.lens.governance` | `domain.governance` | Which stated boundaries or policy questions merit attention? Not current grants/admission. |
| `cube.lens.epistemology` | `domain.epistemology` | Which claims, evidence questions or uncertainty need scrutiny? Not truth. |

These are **display perspectives** from existing P1 VG domain color roles. They are *not* the five ordered X contract-pair dimensions, and do not create additional X/Y/Z definition homes, new P1 validation predicates, or Planner views. The IDs are separate from the `cube.*` view namespace.

## Deterministic selection contract

- The immutable embedded `view_plan` is an ordinary VP-02 object, including `lens: neutral`, `granularity: standard` and `printer_profile: P2-VP-VIEWS/0.2.0`. Its canonical JSON digest is pinned in `source_view_sha256`.
- `facet_bindings` are *explicit*, individually source-referenced **authored display declarations**, not ontology classifications inferred from ID, text, color or glyph. Each has an exact lens, target kind and target ID, `declaration_ref` with `fixture:` or `decl:` prefix, an explanatory note, and `basis: declared_unverified`.
- Flow/tree valid targets: `node` (plan item ID), `edge` (`e1`, `e2`, ... in the exact VP-02 edge-array order). Chart valid targets: `sample` (sample ID), `metric` (exact metric ID).
- Duplicate `(lens,target_kind,target_id)`, wrong target kind/ID, unsupported lens, missing focus, malformed declaration, status promotion or changed source digest are **errors**. A missing binding never causes model-driven auto-inference.
- The selected view is rendered first, byte-identically to VP-02. VP-03 then overlays a domain-accent **dashed outline on selected nodes**, accent strokes on selected declared edges, underlines for selected chart samples, and a marker on the declared chart metric. Original labels, glyphs, lines, direction, values, axes, orders and edge declarations are preserved.
- ALL input source items remain present and readable in every lens. No filter, aggregation, omission, cross-source semantic join, opacity-hiding or new relationship occurs; **granularity remains `standard`** until VP-04.
- Selected focus and its source pointers are available via SVG `data-vp03-*` attributes and embedded XML `<metadata>` with JSON. The JSON report includes the entire unchanged VP-02 report and both source-plan and printed-SVG hashes.

## Identity / epistemic boundaries

The renderer evaluates only display-plan consistency. `render_status=PASS` is **not** P1 semantic-conformance PASS and does not attest an actual original source, event, clock, measurement, observation, action outcome, truth, authority, admission or grant. All such fields stay `NOT_EVALUATED`. All display annotations are `declared_unverified` even if a note uses words such as "evidence". The color merely indicates which declared focus the current *projection* uses; it does not declare a fact.

No network, app, JS, SVG templates loaded from users, filesystem state, runtime engine, execution gateway or new P1/P0 ontology is introduced. Presentation does not silently classify the semantic role of a node. A diagram's shape or location is no witness of execution.

## Bounded VP-03 fixture scope

Three source views (one per view family) × five declared lenses = **15 SVGs** and 15 signed-by-content print reports. Each bundle contains the *same VP-02 source view plan for all five lenses*, with its hash pinned. Facet declarations are deliberately hypothetical demonstration examples; no P1 typed context or external attestation is bound. Alternate VP-02 source fixtures remain unchanged for VP-02 regression.

## Rejected or deferred

- Perspective filters that hide nodes; lens-driven graph rewrites; automatic lens relevance; auto-aggregations: **VP-04 or later, not VP-03**.
- Lens inference from Unicode glyph, domain color, `form_id`, `semantic_ref` or token naming: **forbidden**.
- New temporal, governance, execution or epistemological conclusions from focus: **forbidden**.
- P0/P1 changes, remote SVG printing, interactive UI/editor, 3D, installed font delivery: **out of scope**.

## Schema and conformance

`LENS_BUNDLE.schema.json` is a standalone Draft 2020-12 schema incorporating the *unchanged* VP-02 view-plan structure. Python performs additional cross-document/content invariants: SHA pin, exact target matching, duplicates, typed view compatibility and P0/P1 Unicode anchor validation. `LENS_PRINT_REPORT.schema.json` independently checks serialized reports. The local verification script runs all VP-01 and VP-02 tests before testing VP-03.
