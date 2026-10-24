# AIAEAO Visual Printer — VP-03 Lens Profiles

VP-03 extends the VP-02 local reference lab with **five declared, deterministic perspective profiles** across the unchanged views `cube.flow`, `cube.diagramm` and `cube.tree`. It creates SVG outputs, not an application.

## What changed

- `vplenses/` — a small Python standard-library-only lens renderer/CLI, reusing VP-02 exactly.
- `lens_bundles/` — three fully self-contained, source-SHA-pinned input bundles; each supports the same five lens profiles.
- `lens_outputs/` — 15 golden SVGs with 15 machine-readable print reports.
- `lens_preview.html` — static local side-by-side 3×5 comparison, opening directly in Finder/Safari or Chrome; no JS.
- `lens_previews/` — raster previews (reference only; native Unicode fallback may differ on macOS).
- `LENS_BUNDLE.schema.json`, `LENS_PRINT_REPORT.schema.json`, `VP03_LENS_GRAMMAR.md` and acceptance record.
- Unmodified VP-01/VP-02 files, tests, fixtures and reference/source hashes remain in the same lab tree.

## Quick start

Extract the ZIP in Finder. In a terminal in `P2/visual-printer-2d-lab`:

```bash
python3 scripts/verify_vp03.py
open lens_preview.html
```

Print the **same input** from another perspective (change only `--lens`):

```bash
python3 -m vplenses --input lens_bundles/flow_migration.json \
  --lens cube.lens.provenance --output /tmp/cube-provenance.svg \
  --report /tmp/cube-provenance.json

python3 -m vplenses --input lens_bundles/flow_migration.json \
  --lens cube.lens.governance --output /tmp/cube-governance.svg \
  --report /tmp/cube-governance.json
```

Lens values: `cube.lens.semantics`, `cube.lens.provenance`, `cube.lens.execution`, `cube.lens.governance`, `cube.lens.epistemology`.

The source plan remains `lens: neutral`, `granularity: standard`; the selected perspective is **not** injected into the underlying source. The bundle contains authored lens-binding pointers; these are *illustrative unverified declarations*, not recovered semantic evidence. All source objects and arrows/values remain visible.

## Test and release boundaries

`python3 scripts/verify_vp03.py` runs the previous 85 VP-01/02 tests, the 28 VP-03 negative/invariant tests, all 15 snapshots/reports, SHA locks, XML integrity, and optionally the independent Draft 2020-12 JSON Schema checks if `jsonschema` is installed. Output includes specific NOT_EVALUATED statuses for actual P1 validation, authority, truth, and browser-dependent Unicode typography.

No GitHub/Cloudflare deployment and no modification to the frozen P0/P1 artifact families. No 3D and no VP-04 aggregation logic. This is a reproducible local proof-of-concept, pending visual acceptance.
