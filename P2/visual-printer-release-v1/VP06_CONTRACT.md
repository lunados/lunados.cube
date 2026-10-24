# P2-VP/1.0.0-rc1 – Cube Visual Printer Release Facade

## What is frozen

- `cube.flow`, `cube.diagramm`, `cube.tree` = Cube **view IDs**; none is a Planner UI mode.
- Five `cube.lens.*` IDs = selection of explicit, unverified facet bindings only; no inference.
- `overview`, `standard`, `detail` = hard-capped reduction levels; no unbounded scene graph.
- Input is **VP-04 request**, prepared from a **VP-03 bundle**, with SHA-256 declaration lock. The bundled VP-01–VP-05 source implementations are kept unchanged and their own checks are executed as the baseline.
- Output is deterministic SVG and a JSON report with nested unmodified VP-05 conformance audit. Errors are machine-readable JSON on stderr (exit 2).
- Rendering is read-only and stateless. No server, browser-based editor, data store, runtime effects, automatic multi-SVG generation or 3D.

## CLI contract

`python3 -m vpprint capabilities` → JSON capability card (stdout, exit 0).

`python3 -m vpprint prepare --bundle <VP03.json> --lens <cube.lens.*> --granularity <level> --out <new-job.json> [--overflow summarize|reject] [--focus node:core] [--max-items N] [--max-edges N]` → VP-04 job; no overwrite; validates the bundle and selected facet declaration; digest locks the exact descriptive snapshot, **not its truth**.

`python3 -m vpprint check --input <VP04.json>` → full VP-06 success report to stdout, renders SVG **in memory** only; no filesystem print output.

`python3 -m vpprint print --input <VP04.json> --out <new-directory>` → `render.svg` and `report.json` in a **single newly created output directory**; output cannot exist in advance. Both outputs are staged together then published by renaming the directory. Validate before stage/write. There is no general transactional guarantee against power loss or hostile concurrent writers.

Exit 2 → one diagnostic object on stderr, no print directory on request failure. Do not treat these diagnostics as P1 semantic validation findings.

## ID scope and provenance

A successful print validates the **structural display contract** of submitted data, not that a source concept actually exists externally or a witness is authentic. The source status is `declared_unverified`. The `request_sha256` is SHA-256 of the canonical indented UTF-8 JSON representation produced by `vpprint.encode`; the `source_bundle_sha256` retains VP-04's canonical compact JSON hashing (not the hash of an arbitrary JSON file's whitespace).

SVG data preserve declared glyph anchors but individual Unicode fonts render differently by OS. The published static Cube manifest points to local CLI instructions and never advertises a callable online print endpoint. Nothing here updates or redefines Morphology v9.4, P0, P1 or the Cube validation semantics.

## Intentionally deferred

- True multi-SVG batch export or automatic panel partitioning; existing VP-05 `split_feasibility` is only a bounded heuristic.
- Semantic classification of unstructured source text or automatic facet inference.
- Full ACG→display mapping, arbitrarily large data, universally optimal layout, chart unit conversion or external measurement provenance verification.
- 3D spatial coordinates, WebGL, authentication, storage, monitoring, public renderer service.
