# AIAEAO Cube Visual Printer – VP-06 Local Release

**P2-VP/1.0.0-rc1 · Final stage VP-01–VP-06 · Morphology v9.4**

A deterministic, **offline** Unicode-based SVG printer with a single, documented agent CLI. It consumes **explicitly authored** VP-03 display bundles / VP-04 projection jobs and returns SVG plus verifiable loss and conformance reports. It does **not** accept arbitrary natural-language diagrams or claim that source declarations are semantically/empirically true.

## 60-second start on macOS

Unzip via Finder. From the extracted package root:

```bash
cd P2/visual-printer-release-v1
python3 -m vpprint capabilities
python3 -m vpprint prepare --bundle examples/flow_provenance_standard.vp03.bundle.json --lens cube.lens.provenance --granularity standard --out /tmp/print-job.json
python3 -m vpprint check --input /tmp/print-job.json
python3 -m vpprint print --input /tmp/print-job.json --out /tmp/aiaeao-print
open /tmp/aiaeao-print/render.svg
```

**Output folder must be new.** If `/tmp/print-job.json` or `/tmp/aiaeao-print` already exists, use different paths. This is deliberately fail-closed. Output directory has `render.svg` and `report.json`. The report is an independent JSON artifact including the complete VP-05 audit, displayed/omitted source IDs, chosen lens, granularity and split recommendation (if any).

Inspect [quick_preview.html](quick_preview.html) directly in Finder for four deterministic golden SVGs (`cube.flow`, `cube.diagramm`, `cube.tree` overview/detail); no HTTP server required.

## What is in this delivery

| Component | Purpose |
| --- | --- |
| `vpprint/` | Unified Python API + CLI: `capabilities`, `prepare`, `check`, `print` |
| `agent/AGENT_QUICKSTART.md` | Instructions for Claude, Grok, Codex or other compatible agents |
| `agent/AGENT_SYSTEM_SNIPPET.md` | Concise, copyable integration prompt |
| `examples/` | 4 editable VP-04 jobs, matching VP-03 bundles, golden SVGs + reports |
| `spec/` | JSON Schema Draft 2020-12 for result and diagnostic objects |
| `tests/` | Independent VP-06 contract, safety and CLI tests |
| `scripts/verify_vp06.py` | Includes frozen VP-01–VP-05 regression, full matrix, schemas, locks, package integrity |
| `../visual-printer-2d-lab/` | Frozen VP-01–VP-03 implementations and examples |
| `../visual-printer-granularity-v1/` | Frozen VP-04 implementation |
| `../visual-printer-conformance-v1/` | Frozen VP-05 independent conformance oracle and 90-case matrix |
| `../../AIAEAO_Pure_Cube_P0_v9.4/validation/v1/visual/printer/v1/` | **Optional static website overlay**: published metadata, NOT a hosted printer |
| `../../.github/workflows/cube-vp06-conformance.yml` | Optional CI workflow for installing into a GitHub repository |

## Verify locally

```bash
cd P2/visual-printer-release-v1
python3 scripts/verify_vp06.py
```

The printer uses **Python 3.10+ stdlib only**, with no browser/network requirement. The exhaustive independent JSON Schema gate uses optional `jsonschema>=4,<5`; the included CI workflow installs it. `CairoSVG/Pillow` are optional for raster previews only. No external fonts are bundled or redistributed.

## Contracts and boundaries

- 3 Cube **views** `cube.flow`, `cube.diagramm`, `cube.tree` (not the three Planner UI views).
- 5 Lenses `cube.lens.semantics`, `.provenance`, `.execution`, `.governance`, `.epistemology`. Source must declare matching facets; **no inference**.
- 3 granularity levels `overview`, `standard`, `detail`; subset selection and exact loss ledger, **no invented data**.
- Source bundle and print job versions remain VP-03 and VP-04. The VP-06 facade does not silently migrate syntax or alter established semantics.
- `SPLIT_RECOMMENDED` is an advisory conformance decision. VP-06 is **not** a multi-SVG printer.
- No P1 semantic validation, real Witness verification, Authority, Admission, empirical truth, live agents, server, app, or 3D.

Read [`VP06_CONTRACT.md`](VP06_CONTRACT.md), [`VP06_ACCEPTANCE.md`](VP06_ACCEPTANCE.md), and [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md). **Publishing is optional and requires a separate GitHub/Cloudflare action.** Neither P0 nor P1 is modified in this build.
