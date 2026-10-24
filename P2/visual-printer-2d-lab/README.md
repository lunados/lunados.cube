# AIAEAO Visual Printer · 2D local lab (experimental)

A small independent **P2** experiment, *not* an update to P1. Uses frozen P0 v9.4 and P1 Visual Grammar projections. No web service, SVG input, runtime authority, fonts, JavaScript, or external libraries required to print SVG.

## Work packages

See [`WORK_PACKAGES.md`](WORK_PACKAGES.md) and [`GATE_2D.md`](GATE_2D.md). This package implements VP-00 and VP-01; VP-02 is only partially automated. VP-03 and 3D are **not** implemented.

## Local use (after extracting ZIP)

```bash
cd P2/visual-printer-2d-lab
python3 scripts/verify_lab.py
python3 scripts/run_local_lab.py
open preview.html # macOS; or open via Finder
```

Print an individual JSON plan:

```bash
python3 -m vp2d --input fixtures/02_migration_relation.json --output /tmp/migration.svg
```

No dependencies except Python 3.10+ standard library. Optional preview PNGs can be generated with `pip install cairosvg` and `python3 scripts/render_pngs.py` (rasterization may change glyph appearance depending on installed fonts). SVG **source remains editable**.

## Source data

`reference/` contains **exact copies** of the P0 core, concept and symbol registries, and P1 form/color, anchor, and display schema. These copies are display inputs only. `SOURCE_LOCK.json` records each SHA-256. This ZIP is not intended to overwrite existing P0/P1 packages.

## Limitation, by design

The printer validates its own presentation plan, **not** ACG typing or proof. A declared reference edge is only an illustration and requires a separate P1 semantic-conformance result. No layout relationship creates an ontology fact, scope crossing, execution permission, current authority, or event occurrence. The frame of a topology diagram is not an operative trust boundary. `semantic_ref` and `qualified_state_witness_ref` are unverified pointers in this experiment. Display-only status remains **UNVERIFIED**.

The four templates deliberately avoid generalized graph auto-layout. This lets us evaluate stable, readable diagrams first. Long labels, multilingual typography, arbitrary graph density, actual responsive constraints, and exact SVG font fallback need VP-02 review and VP-03 hardening.

## Local review

Open `preview.html` in Safari or Chrome. Inspect glyphs, legibility, truncated anchor IDs (full ID is available as the node SVG `<title>` and `data-anchor-id`), line semantics and text-overflow. These checks are deliberately **not** satisfied by passing unit tests. `previews/*.png` are CairoSVG rasterizations made in the build environment; macOS browser rendering can differ.

## Expected outputs

- `outputs/01_contract_pairs.svg`: P0 five X contract pairs, exact canonical order
- `outputs/02_migration_relation.svg`: single **declared** reference
- `outputs/03_thread_sequence.svg`: explicitly fixture-ordered items, no inferred time truth
- `outputs/04_topology_blocks.svg`: illustrative grouping only
- `LOCAL_TEST_REPORT.json`: test counts, hashes, raster preview checks when available
