# AIAEAO Visual Printer – Agent Quickstart (VP-06)

**For Claude, Grok, Codex and other AI agents.** This is a local, read-only **presentation projection**, not a semantic validator, runtime, application, or callable web endpoint.

## Before printing

1. Use the **v9.4** Cube concept/Unicode reference and existing declared VP-02/VP-03 source structures. The printer **does not convert arbitrary natural language or ACG into an audited view plan**. Construct the view plan and facet declarations explicitly; do not pretend they were proven by P1.
2. Select exactly **one** View: `cube.flow` (directed *declared* links), `cube.diagramm` (numeric measurement with explicit source/unit), `cube.tree` (one actual declared rooted hierarchy; no invented parent).
3. Select one Lens (`cube.lens.semantics`, `.provenance`, `.execution`, `.governance`, `.epistemology`). The requested lens **must have explicit facet_bindings** in the source. Lens changes emphasis, **not meaning**. If absent, report an error; do not infer.
4. Select Granularity: `overview` (narrow), `standard` (default), `detail` (all declared items within the hard cap; otherwise error). Use `focus` for a requested source item. Default to `overflow=summarize` and **always disclose omitted IDs**.
5. If a display cannot be made without synthetic relations, arbitrary numeric values, invented hierarchy or undeclared facets, **refuse that projection**, explaining the missing declaration.

## Executable steps

From `P2/visual-printer-release-v1/`:

```bash
python3 -m vpprint capabilities
python3 -m vpprint prepare --bundle examples/flow_provenance_standard.vp03.bundle.json --lens cube.lens.provenance --granularity standard --out /tmp/cube-job.json
python3 -m vpprint check --input /tmp/cube-job.json > /tmp/cube-check.json
python3 -m vpprint print --input /tmp/cube-job.json --out /tmp/cube-print
```

Output: `/tmp/cube-print/render.svg` and `/tmp/cube-print/report.json` (output folder must not exist). On failure exit code **2** and **one JSON diagnostic on stderr**; no print directory is created by a validation failure. `prepare` creates an explicit VP-04 job and a source SHA-256 *declaration lock*. It does not verify source truth. You can also pass an already complete VP-04 job to `check`/`print`.

Read `report.json` first when describing the picture: inspect `decision.action`, `loss_ledger`, `split_feasibility` and `conformance.invariants_passed`. Never describe a summarized image as exhaustive. **`SPLIT_RECOMMENDED` describes a feasibility heuristic, not a generated multi-SVG export.**

## Response rules for an agent

- Name the selected View, Lens and Granularity; disclose source declaration status (`declared_unverified`).
- State how many items or original edges were excluded. If none, state complete **for the submitted declared view plan**, not for the world.
- Do not infer temporal order from layout direction, causality from an arrow, or Authority/Admission from colors.
- If the command exits 2, report the exact `code` and `message`, request the missing declared data or a different supported projection. Do not rewrite the source silently.
- Treat SVG fonts as platform-specific; do not assume every Unicode mathematical glyph renders identically across clients.

## Compatibility IDs (do not rename)

Views: `cube.flow`, `cube.diagramm`, `cube.tree` are **Cube display** IDs, not Planner UI modes. Lens names and granularity levels are likewise presentation parameters, not new v9.4 ontology.

The printer works fully offline with Python 3.10+ stdlib. `jsonschema` is optional for independent release QA, **not** for printing. No JavaScript, no login, no SVG assets, no browser or network access are needed.
