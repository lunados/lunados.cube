# Visual Printer roadmap after VP-02 (local evaluation only)

- **VP-00 / VP-01 — Baseline**: Frozen P0/P1 inputs, 129 Unicode anchors, four local static SVG templates. 29 regression tests, preserved byte-identically.
- **VP-02 — View Grammar (this delivery)**: Implemented independent Cube namespace `cube.flow`, `cube.diagramm`, `cube.tree`; two fixtures each; deterministic SVGs, provenance pointers, negative conformance controls, schema and visual comparison. `lens=neutral`, `granularity=standard`, no 3D. Automated acceptance PASS, human visual acceptance outstanding.
- **VP-03 — Lens Profiles (deferred)**: Scope-driven semantics-preserving selection/perspective profiles. Same evidence set, multiple projections without invented meaning. Require acceptance of VP-02 first.
- **VP-04 — Granularity / Complexity Budget (deferred)**: Level 0/1/2, focus, aggregation provenance, deterministic refusal to hide data silently, paging where necessary. Defaults must be test-derived, not morphological constants.
- **VP-05 — Combinatorial Conformance (deferred)**: View×Lens×Granularity compatibility matrix with accessible render-output regressions and independent agent exercises.
- **VP-06 — Distribution (deferred)**: Optional publication of the static projection contract, independently executable local printer. No application server/editor.
- **VP-3D — Deferred Research**: Separate proof of need after reliable 2D cross-agent/browser UX. No 3D module, axis coordinate contract or free-form 3D in VP-02.

Nothing in this roadmap authorizes mutating P0, P1 Extended, the production Cube manifest or the Planner UI.
