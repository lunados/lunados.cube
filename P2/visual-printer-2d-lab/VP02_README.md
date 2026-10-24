# AIAEAO Visual Printer — VP-02 Cube View Grammar

A runnable, reproducible **local 2D SVG** projection lab adding `cube.flow`, `cube.diagramm` and `cube.tree` to the unchanged VP-01 four-template reference lab.

**No server, database, web request, GUI editor, SVG input parser, authentication, runtime authority, or 3D.** The `cube.*` view IDs are distinct from the AIAEAO Planner modes.

## Quick start (macOS/Linux, Python 3.10+)

Extract ZIP using Finder or your preferred archive tool, then from the extracted package root:

```bash
cd P2/visual-printer-2d-lab
python3 scripts/verify_vp02.py
open view_preview.html  # macOS Finder also works
```

To render a flow fixture from an authored JSON plan:

```bash
python3 -m vpviews \
  --input view_fixtures/01_cube_flow_migration.json \
  --output /tmp/cube-flow.svg \
  --report /tmp/cube-flow.print-report.json
```

Use `python3 -m vpviews --help` for CLI usage. The self-contained reference bundle is under `reference/` and is source-locked by the earlier VP-01 `SOURCE_LOCK.json`. **Do not place VP-02 files into the immutable P0/P1 release directories.** The code and fixtures are experimental P2 outputs and have not been deployed to GitHub or Cloudflare.

## Artifact map

- `vpviews/` — new stateless projection printer and CLI, Python stdlib only.
- `view_fixtures/` — 6 authored JSON plans; two per view.
- `view_outputs/` — 6 golden SVGs plus 6 machine-readable, signed-by-content SHA-256 print reports.
- `view_previews/` — optional PNG raster previews for reference; SVG is authoritative *as display output*.
- `view_preview.html` — local static side-by-side review of the six SVG files (no JS).
- `view_tests/` — conformance and negative tests for naming, relation direction, chart data and tree integrity.
- `VIEW_PLAN.schema.json` and `PRINT_REPORT.schema.json` — structural contracts (Draft 2020-12).
- `VIEW_GRAMMAR.md` and `VP02_ACCEPTANCE.md` — precise scope, constraints, evaluation checklist.
- `VP02_SHA256SUMS.txt`, `VP02_RELEASE_MANIFEST.json`, `LOCAL_TEST_REPORT_VP02.json` — package manifest, reproducible hashes, test report.
- `vp2d/`, `fixtures/`, `outputs/`, `reference/`, `preview.html` — unchanged VP-01 package including four original SVGs.

## Validation boundary

The printer's `PASS` means only **the SVG faithfully displays a locally valid authored view plan**. It is not AIAEAO P1 `PASS`, a typed-relationship signature, proof of observations, security admission, or runtime execution. The view renderer assumes no total natural ordering of Y/Z entities; flow and tree orders must be explicitly authored.

## Dependencies

Runtime/testing: Python standard library. Independent JSON Schema oracle (optional for `verify_vp02.py`): `jsonschema>=4.22`. Preview PNG generation (optional): `cairosvg` and system fonts. Neither external dependency is required to print valid SVGs or to run structural/negative tests.

## Next decisions

1. Inspect and accept/revise VP-02's three view layouts in `view_preview.html`.
2. On acceptance: implement **lens profiles separately**, keeping source model unchanged.
3. Then explore **granularity/depth-of-field controls** with aggregation provenance and explicit budgets.
4. 3D is a later, explicitly gated experiment, not part of the implementation here.
