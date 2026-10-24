# G5 – Consolidation & Release Freeze Candidate

**Cut:** 2026-10-24.  **Profile:** `P3-MCP-REMOTE/0.1.0-proof` (functional proof).  **Status:** `SOURCE_FROZEN_CANDIDATE` — production remains `G5_PROOF_NOT_PRODUCTION_AUTHORIZED`.

## Consolidated changes

1. Both Python Core bundling hotfixes merged in `python-core/wrangler.jsonc`, covering 40 frozen non-Python runtime assets (14 P0, 20 P1, 6 P2). `scripts/check_runtime_assets.py` enforces config and SHA-256 coverage.
2. MCP v2 Gateway handler corrected to `handler.fetch(forward)` (user proved successful remotely after change).
3. Direct JS dependencies pinned: `@modelcontextprotocol/server@2.4.0`, `zod@4.6.7`; deployment tool `wrangler@4.152.0` fixed as a proposed known version. **This package does not contain a real npm-generated package-lock** (npm registry not accessible in build environment). The working Mac contains the existing audited npm install/lock; regenerate the lock against pinned package.json, then commit it after audit.
4. P0 MIME metadata now flows from locked `mime_type` entries, including `text/markdown` on markdown resources. This **specific fix has not yet been redeployed and verified on Cloudflare**.
5. Acceptance ledger differentiates offline local verification, user-reported R3 remote success and independent Claude R4 report; it never fabricates a persistent log or production approval.

## Freeze gates on the Mac

From repository root after Finder+rsync of this ZIP's `P3/` overlay:

```sh
python3 P3/remote-mcp-g5/scripts/verify_g5.py
python3 P3/remote-mcp-g5/scripts/verify_release.py
cd P3/remote-mcp-g5/gateway
npm install --package-lock-only --ignore-scripts
npm ci
npm audit --omit=dev
npm audit
npm run check:freeze
npm run dry-run
cd "$HOME/Downloads/lunados.cube"
python3 P3/remote-mcp-g5/scripts/verify_release.py --require-npm-lock
```

To preserve reproducibility, **commit `gateway/package-lock.json`** alongside `gateway/package.json`, after confirming audit is green. Do not commit `node_modules`, `.g5-runtime`, secrets or live environment variables.

## Controlled post-freeze redeploy (separate gate)

Changing Gateway P0 MIME requires a Gateway deploy. Core MIME reporting was also aligned; redeploy private Core first, then Gateway, then run the remote SDK smoke with sanitized evidence to a local file (see `DEPLOYMENT.md`). G5-R4 remains formally INCOMPLETE until a fresh host check of resource MIME and the independent SVG hash/evidence reconciliation. Never change the public `cube.lunados.net` domain.

## SHA-256 and source verification

`SHA256SUMS.txt` pins all distributed files in the overlay, except itself. `scripts/verify_release.py` checks this list plus the frozen P0 registry metadata. `scripts/verify_g5.py` assembles the 77 frozen source files without modifying them; `check_runtime_assets.py` verifies 40 asset hashes.

## Rollback

If the updated Gateway fails remote smoke, redeploy the last known-good Gateway revision. Keep the private Python Core on a non-public route. If there is an authentication concern, disable the public Gateway and rotate the proof bearer token. Never alter P0/P1/P2 contracts for transport repair.
