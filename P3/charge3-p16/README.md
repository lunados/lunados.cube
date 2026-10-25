# AIAEAO Cube P1.6 — Charge 3: MCP & G5 Integration

**State:** implementation and local CPython offline checks; **NO** G5 deployment, real Cloudflare/Pyodide remote proof, host acceptance, or production authorization.

## Baseline and freeze

Target: local `lunados.cube.zip` uploaded 2026-10-25 containing Charge 2. The patch is additive at the P3 transport/bundling layer; `P0`, `P1` (including frozen P1.1–P1.5 **and** P1.6 Charge 2), `P2`, the local G4 golden discovery, and the complete G5 Gateway `index.mjs` with seven tool schemas are not modified. No public Cube reference content or Z-zone semantics change.

The historical **G5 source-freeze manifest** `P3/remote-mcp-g5/SHA256SUMS.txt` is deliberately not rewritten. Because Charge 3 adds new versioned P3 source, it cannot be used as a checksum acceptance for this new overlay; it documents the older candidate. `P3/charge3-p16/CHARGE3_SOURCE_SHA256SUMS.txt` and the patch-level manifest are the checksum gates for this newer overlay. Continue using P1.5/P1.6 frozen gates for old files.

## Routing

* `cube_validate` with `binding-context/1` or without context: **exact** frozen `SemanticValidator`; no new wrapper fields and no silent automatic upgrade.
* `cube_validate` with `binding-context/2`: `P16Validator` in-process. Only X endpoint referent-binding judgments gain scoped slot verification. The *existing* P1 report schema/check order remains unchanged; `binding_context_profile` is added to the **transport envelope only for /2**.
* Unknown context format: MCP configuration error (`isError=true`), not a fake semantic `FAIL`. Missing /2 module: `P1_MCP_P16_UNAVAILABLE`, never silently reverts to /1.
* Existing `cube_discover_surface` local G4 golden output intentionally stays byte-identical. Remote G5 discovery includes a separate `p16_instantiation` descriptor (no tool signature change).
* G5 private Python Core stages P1.6 code plus the **SHA-pinned** `instantiation_reference_v1.json` (`+1` Wrangler Text asset, 40 old frozen assets still verified). The Gateway and credential policy are unchanged.
* `source_warrant=declared_unverified`, `epistemic_warrant`, `current_authority`, `canonical_admission=NOT_EVALUATED`. Status `PASS` proves shape/type constraints **only**.

## One-command offline acceptance (from repo root)

```bash
python3 P3/charge3-p16/scripts/verify_charge3.py
```

This runs the entire P1.6 Charge 2 gate with P1.5 freeze, G4 and its earlier G3/G2 tests, G5 offline assembly/security/bundling tests, Charge 3 local static MCP vectors, and a **fresh Python process** validating the actual staged `.g5-runtime` with R-01…R-13. The test harness materializes vectors **as static data** in `fixtures/r01_r13_materialized.json`, with **expected values independently transcribed** in Charge 2's oracle; fixture *construction* originally reused Charge 2's helper and is **not** represented as an independent fixture author.

The SDK v2 local stdio smoke remains a separate *actual host* step on the user's Mac:

```bash
cd P3/adapters/mcp-local
source .venv/bin/activate
python scripts/sdk_g4_stdio_smoke.py
```

## Real G5 remote proof (explicit approval, not run by package)

First run the existing G5 `sdk_remote_smoke.py` baseline after a controlled Core redeployment, then from root:

```bash
python3 P3/charge3-p16/scripts/sdk_p16_remote_smoke.py \
  --evidence P3/remote-mcp-g5/evidence/P16_CHARGE3_REMOTE_R01_R13.json
```

The test uses `AIAEAO_G5_URL` and `AIAEAO_G5_TOKEN` from secure local environment configuration, official MCP SDK v2 and `httpx2`; it checks all 13 returned semantic statuses/diagnostics through the protected HTTP MCP protocol and produces optional **sanitized** evidence (no secret, full context, or source expression). No R-01–R-13 **remote** execution is claimed here. Keep `G5_PROOF_NOT_PRODUCTION_AUTHORIZED` even after a proof pass; production approval is separate.

## Moving the checkout later

Paths use source-file ancestry, not an absolute path. Once the offline gate and MCP host checks are accepted, moving from `~/Downloads/lunados.cube` to `~/SitesHeroku/lunados.cube` is sensible, **but not part of Charge 3**. Check Git worktree, regenerate/reconfigure path-bound virtualenv or MCP host stdio settings (e.g. Zed/Claude/Codex) and rerun offline/SDK gates from the new location. Do not move mid-charge or equate a local `mv` with G5 deployment.
