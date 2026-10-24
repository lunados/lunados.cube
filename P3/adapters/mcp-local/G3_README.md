# CP-001 / G3 — Cross-Domain MCP Host Proof

**Proof version:** `P3-MCP-G3/0.1.0-proof` · **Status:** Local offline PASS, SDK-on-Mac and independent Claude host test PENDING.

## What G3 does—and does not do

G3 is a **test/evidence package**, not a new MCP service or seventh tool. All six existing MCP tools, signatures, MCP Resources and P0/P1/P2 reference implementations remain unchanged.

The cross-domain chain intentionally consists of **independent** results:

1. P0: read `aiaeao://p0/resources/v1`, followed by `https://cube.lunados.net/v9.4/grammar/concepts.json` through the pinned `cube_read_reference` fallback. Reassemble every UTF-8 page and *independently hash transmitted bytes*.
2. P1: `cube_validate` the existing `P1/semantic-validator-v1/fixtures/migration.acg` with its declared context; separately test a syntactically invalid expression (`FAIL`) and missing context (`UNRESOLVED`).
3. P2: **supply the existing VP-03 bundle independently** from `P2/visual-printer-release-v1/examples/flow_provenance_standard.vp03.bundle.json`; then use `cube_prepare_print`, `cube_check_print`, and `cube_render_svg`.
4. Compare the returned VP-04 job, VP-06 audit report and SVG bytes against the frozen golden files of the same example.
5. Produce **three separate traces** with a P1 status of `PASS`, `FAIL`, or `UNRESOLVED`, all with valid P2 `PASS`. There is **no implied ACG-to-VP03 association**, no inferred P1 validity of the display data, and no overall semantic PASS.

The generated `trace_status: COMPLETE` means only that this **test workflow** ran and its invariant checks passed. It is not an evidence, truth, authority, or admission conclusion.

## Mac installation — keep the Finder + rsync workflow

Unpack ZIP with Finder. From the existing Git checkout root (not from the parent of the extracted package):

```bash
cd "$HOME/Downloads/lunados.cube"
rsync -av "$HOME/Downloads/AIAEAO_Cube_MCP_G3_Cross_Domain_Proof/P3/" ./P3/
cd P3/adapters/mcp-local
source .venv/bin/activate
```

Verify that the Finder-created folder exists and is readable before running `rsync`. This package contains **only new P3 files**, not replacement sources for P0/P1/P2.

## Gates

```bash
python scripts/verify_g3.py
python scripts/sdk_g3_stdio_smoke.py
```

The first test needs only Python 3.10+ standard library for adapter tests; the frozen P1.5 release gate uses its existing optional dependencies as before. The second test requires the previously installed **official `mcp==2.0.0` SDK** and starts the genuine separate MCP `stdio` server process (not a mock or direct function call). To save evidence **outside the repository** (optional):

```bash
python scripts/sdk_g3_stdio_smoke.py --evidence /tmp/aiaeao-g3-mcp-stdio.json
```

Do not describe the SDK/Host tests as PASS until those commands have actually been run on the target Mac and then by Claude. See `G3_CLAUDE_TEST_PROMPT.md` and `G3_HOST_ACCEPTANCE.md`.

## Proof trace format

`evidence/G3_OFFLINE_TRACE.json` demonstrates `aiaeao.cube.g3-cross-domain-evidence/1`, as specified by `spec/G3_CROSS_DOMAIN_EVIDENCE.schema.json`. It records **independent evidence per domain** and specifically fixes `cross_domain_link: NOT_ESTABLISHED` and `acg_to_vp03_mapping: NOT_PERFORMED`.

Offline evidence is from direct frozen core functions—not MCP protocol. The separate `sdk_g3_stdio_smoke.py` is designed to repeat the entire chain over the actual `stdio` transport on your Mac. Claude-host orchestration is the final G3 acceptance.

## Non-implications

- P0 digest confirms integrity relative to an explicitly pinned documentary reference, not its truth.
- P1 `PASS` only describes the submitted ACG+context under P1-VC/1.0.0, not a visual scene.
- P2 `PASS` means *the separately supplied* VP-03 declaration can be rendered, not that P1 certified it.
- `FAIL` / `UNRESOLVED` P1 are normal successful MCP tool responses, not printer blockers.
- No ACG→SVG mapping, P1-to-P2 evidence promotion, remote MCP, WebMCP, filesystem/tool side effects, admission, or delegated execution authority.

**G4** is where `cube_discover_surface`, adapter versioning, capability metadata, release packaging, CI and GitHub publication are considered; none are silently introduced here.
