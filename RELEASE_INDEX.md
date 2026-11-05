# AIAEAO Cube — Release index

**State:** 2026-11-02 (after MILE-011). This repository holds the reference (P0), the validators (P1), the local SVG printers (P2) and the MCP adapters (P3). Everything runs locally except the remote proof G5, which is **not authorized for production** ([known limits](P3/remote-mcp-g5/KNOWN_LIMITS.md)). Roadmap and milestones: [`docs/01-roadmap/ROADMAP.md`](docs/01-roadmap/ROADMAP.md).

## Layers

### P0 — reference

| Package | Version | Entry |
|---|---|---|
| [`AIAEAO_Pure_Cube_P0_v9.4`](AIAEAO_Pure_Cube_P0_v9.4) | v9.4; pinned P0 lock `cb259c5962a61c507ace6260d37ae364cf6658794a115052e3bc4fefdca477a1` (G5) | Morphology, notation grammar, visual symbols; read-only, hash-verified |

### P1 — validation (`cube_validate`)

| Package | Profile | Context |
|---|---|---|
| [`P1/contract-v1`](P1/contract-v1) | P1.1 contract freeze | — |
| [`P1/visual-grammar-v1`](P1/visual-grammar-v1) | basic visual grammar v1 | — |
| [`P1/semantic-validator-v1`](P1/semantic-validator-v1) | P1.4 semantic validator `P1-VC/1.0.0` | `binding-context/1` |
| [`P1/release-v1`](P1/release-v1) | P1.5 conformance and release | — |
| [`P1/instantiation-profile-v1`](P1/instantiation-profile-v1) | P1.6 instantiation | `/2` |
| [`P1/simulation-profile-v1`](P1/simulation-profile-v1) | P1.8 simulation | `/3` |
| [`P1/comparison-profile-v1`](P1/comparison-profile-v1) | P1.9 comparison | `/4` |
| [`P1/migration-profile-v1`](P1/migration-profile-v1) | P1.10 migration | `/5` |
| [`P1/migration-profile-v2`](P1/migration-profile-v2) | P1.10.1 dependency gap | `/6` |
| [`P1/migration-methods-v1`](P1/migration-methods-v1) | P1.11 migration methods | `/7` |
| [`P1/coverage-instance-profile-v1`](P1/coverage-instance-profile-v1) | P1.12 coverage and instances | `/8` |
| [`P1/control-flow-profile-v1`](P1/control-flow-profile-v1) | P1.13 control flow | `/9` |
| [`P1/relation-origin-profile-v1`](P1/relation-origin-profile-v1) | P1.14 relation origin | `/10` |

P1.7 is reserved (Principal → Authority). Each context version is a strict superset of the previous one.

### P2 — local SVG printers

| Package | Printer profiles | Views |
|---|---|---|
| [`P2/visual-printer-2d-lab`](P2/visual-printer-2d-lab) | VP-01 `P2-VP-2D/0.1.0`, VP-02 `P2-VP-VIEWS/0.2.0`, VP-03 `P2-VP-LENSES/0.3.0` | 2D lab, views, lenses |
| [`P2/visual-printer-granularity-v1`](P2/visual-printer-granularity-v1) | VP-04 `P2-VP-GRANULARITY/0.4.0` | granularity and budgets |
| [`P2/visual-printer-conformance-v1`](P2/visual-printer-conformance-v1) | VP-05 `P2-VP-CONFORMANCE/0.5.0` | combinatorial conformance |
| [`P2/visual-printer-release-v1`](P2/visual-printer-release-v1) | VP-06 `P2-VP/1.0.0-rc1` | local release of VP-01…VP-05 (`cube_render_svg`) |
| [`P2/visual-printer-migration-v1`](P2/visual-printer-migration-v1) | VP-07 `P2-VP-MIGRATION/0.7.0`…`0.7.6` | `cube.phases`, `cube.flow` (0.7.6: origin lines, statement sets) |
| [`P2/visual-printer-sequence-v1`](P2/visual-printer-sequence-v1) | VP-08 `P2-VP-SEQUENCE/0.8.0` | `cube.sequence` |
| [`P2/visual-printer-axes-v1`](P2/visual-printer-axes-v1) | VP-09 `P2-VP-AXES/0.9.0`…`0.9.3` | `cube.axes` (0.9.3: X × Y, crossing status) |
| [`P2/visual-printer-cells-v1`](P2/visual-printer-cells-v1) | VP-10 `P2-VP-CELLS/0.10.0`, `0.10.1`, `0.11.0` | `cube.cells` (0.11.0: statement sets) |
| [`P2/visual-printer-instances-v1`](P2/visual-printer-instances-v1) | VP-11 `P2-VP-INSTANCES/0.12.0` | `cube.instances` |
| [`P2/visual-printer-landscape-v1`](P2/visual-printer-landscape-v1) | VP-12 `P2-VP-LANDSCAPE/0.12.0` | `cube.landscape` |

Older printer profiles stay byte-identical; each newer profile is opt-in and pinned against its predecessors.

### lunados.lib — function library (sibling repository)

Entries read by the Cube, never recomputed: `analyze.population/v1` (coverage populations), `project.aggregate-relations/v1` (statement-set aggregation, MILE-007), `analyze.trace-conformance/v1` (trace conformance, MILE-008).

### P3 — MCP adapters and hosts

| Package | Version | Scope |
|---|---|---|
| [`P3/adapters/mcp-local`](P3/adapters/mcp-local) | label `P3-MCP-LOCAL/0.3.0-rc1` (G6); since then extended to `/9`, `/10` and the profiles of MILE-007…011 without a new label | local stdio MCP: ten tools, P0 resources, P1 `/1…/10`, P2 printers and plan views |
| [`P3/remote-mcp-g5`](P3/remote-mcp-g5) | core `P3-MCP-REMOTE/0.9.0-proof`, gateway `0.2.0-proof` | remote proof on Cloudflare: same ten tools, byte-identical results; [ledger](P3/remote-mcp-g5/G5_ACCEPTANCE.md), [known limits](P3/remote-mcp-g5/KNOWN_LIMITS.md) |
| [`P3/public-reference-mcp`](P3/public-reference-mcp) | `lunados-cube` 0.2.0 | separate public reader; no effect on P0 or G5 |
| [`P3/host-integrations`](P3/host-integrations) | — | host bindings for ChatGPT web and Codex ([index](P3/host-integrations/ACCEPTANCE_INDEX.md)) |
| [`P3/charge3-p16`](P3/charge3-p16) | — | historical P1.6 charge 3 evidence |

## Checks

- Each package carries its own tests, vector runners and `SHA256SUMS`; newer profiles carry pin scripts for their predecessors.
- Each milestone has a closing check under [`docs/10-Evidence`](docs/10-Evidence) (`verify_mile00x.py` / `verify_mile01x.py` with `verification.json`).
- G5: `P3/remote-mcp-g5/scripts/verify_g5.py`, `verify_release.py`, offline parities `r5_parity.py`, `r6_parity.py`, live acceptance `r5_remote_acceptance.py`, `r6_remote_acceptance.py`.

## History

The text below is the previous index of 2026-10-24 (VP-06 release candidate), kept unchanged.

## AIAEAO Visual Printer – VP-06 Full Release Candidate

This is a **repository-root overlay package**, not an already deployed service. The Python printer itself lives in `P2/visual-printer-release-v1/`; all VP-01–VP-05 predecessors are preserved unchanged in their sibling P2 folders.

To review **locally**, unpack with Finder and open `P2/visual-printer-release-v1/quick_preview.html`, then run:

```bash
cd P2/visual-printer-release-v1
python3 scripts/verify_vp06.py
python3 -m vpprint capabilities
```

The optional folders `.github/workflows/` and `AIAEAO_Pure_Cube_P0_v9.4/validation/v1/visual/printer/v1/` are intended **only for a later, separate reviewed GitHub publication**. They must be merged from the repository root. No existing P0/P1 asset is overwritten by this ZIP; the optional webroot contains only new static printer metadata.

**Important:** The URL in the metadata is a potential static GET reference; the SVG printer itself always runs locally. This is **not** an online `/print` API or a web application. No 3D or automatic multi-SVG generation is included.

Further documentation: `P2/visual-printer-release-v1/README.md`, `agent/AGENT_QUICKSTART.md`, `DEPLOYMENT_GUIDE.md`, `VP06_CONTRACT.md`.
