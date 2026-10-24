# G5 — Cloudflare deployment, controlled proof only

**Prerequisites:** Cloudflare account with Workers enabled; Wrangler authenticated; Node 20+ and npm; Python 3.13; `uv` (for Python Workers). AIAEAO Pure Cube repository has the fully accepted G4 installation. **This is a two-Worker setup.**

## 1. Set up outside Downloads (macOS)

As previously validated, unzip with Finder and copy the extracted G5 folder with Finder to `~/cube-patches/`. From the existing Git checkout (preferably under `~/Development/lunados.cube`):

```sh
rsync -av "$HOME/cube-patches/AIAEAO_Cube_MCP_G5_Remote_Cloudflare_Proof/P3/" ./P3/
```

Do not sync the outer ZIP directory into `./P3/`; the path must end at its **inner `P3/`**.

## 2. Offline gate, no Cloudflare access

```sh
python3 P3/remote-mcp-g5/scripts/verify_g5.py
```

Expected `PASS G5 OFFLINE` and 14 passing contract tests. The generated, gitignored deploy candidate is `P3/remote-mcp-g5/.g5-runtime/`.

## 3. Deploy **private Python Worker** first (G5-R1)

```sh
cd P3/remote-mcp-g5/.g5-runtime
uv run pywrangler deploy
```

Uses `wrangler.jsonc` with `workers_dev: false` and no custom domain. If the upload/import fails, **stop** and capture the error as `PYODIDE_RUNTIME_BLOCKED`; do not rewrite the P1/P2 logic or substitute a fake renderer. `uv run pywrangler dev` may help diagnose first, but the actual Cloudflare execution must still be tested.

**NOTE:** Since Pywrangler bundling of dynamic imports and auxiliary reference files is not proven in this environment, this deployment step is an explicit experiment. Do not silently claim success from the CPython unit tests alone.

## 4. Deploy **authenticated JS MCP Gateway** (G5-R2)

In a *separate terminal*:

```sh
cd P3/remote-mcp-g5/gateway
npm install
npm run check:syntax
npm run dry-run
npx wrangler login
npx wrangler secret put MCP_BEARER_TOKEN
npm run deploy
```

Generate the token offline beforehand with e.g. `python3 -c 'import secrets; print(secrets.token_urlsafe(48))'`. **Do not paste tokens into command history, issue trackers or chat.** `secret put` prompts securely. Keep the token in your local secure credential store.

The gateway `wrangler.jsonc` connects to the private core by Service Binding (`CORE → aiaeao-cube-g5-core`). The gateway exposes **only** `/mcp` and unauthenticated `/health`. The gateway requires bearer authorization for `/mcp`; the Python core must have **no public workers.dev route**.

For browser-based clients, set `MCP_ALLOWED_ORIGIN` to one approved origin in Gateway configuration. The default is **reject all requests with an Origin header**; native clients without one are permitted after bearer authentication. Never set `*`.

## 5. Real remote smoke (G5-R3)

From your repo root, activate the existing G4 MCP SDK venv:

```sh
cd P3/adapters/mcp-local
source .venv/bin/activate
export AIAEAO_G5_URL='https://<deployed-gateway>.workers.dev/mcp'
export AIAEAO_G5_TOKEN='<local secret, do not commit or share>'
python ../../../P3/remote-mcp-g5/scripts/sdk_remote_smoke.py
```

The test checks bearer rejection, wrong Origin rejection, seven tools, fourteen P0 Resources, a P1 semantic `FAIL` delivered as a **normal tool result**, an invalid P1 context delivered as an **error**, and **byte-identical** SVG/report parity with local VP-06.

The smoke includes no prompts to update/modify the repository and produces no server-side files. Replace inline token exports with a secure local mechanism in a real deployment.

## 6. Host acceptance (G5-R4)

Connect a real remote MCP client supporting the modern 2026-07-28 protocol and an HTTP bearer token. Test `cube_discover_surface`, P0 fallback, `cube_validate` and `cube_render_svg`. Some clients cannot configure arbitrary Authorization headers or support only OAuth: **record HOST_UNSUPPORTED**; do not weaken authentication to make one client connect.

## 7. Stop / rollback

Keep `cube.lunados.net` unchanged. On any severe discrepancy immediately disable the public Gateway Worker (Cloudflare dashboard or Wrangler delete); remove the private Core Worker once logs/evidence are collected. Rotate the bearer token after the PoC. Do not publish a custom domain until authentication, rate limits, monitoring, costs and runtime compatibility are separately accepted.

## 8. G5 Consolidation: post-MIME freeze evidence

Apply the P3-only consolidated release overlay. Run offline gate and asset checksum gate. In the Gateway directory run `npm install --package-lock-only --ignore-scripts && npm ci && npm audit && npm run check:freeze && npm run dry-run`. Preserve the generated `package-lock.json` in Git. The updated Gateway needs redeployment to publish its newly lock-derived `text/markdown` registration. Because the private Python core now also obtains MIME metadata from the lock, redeploy it too. **Do not change the accepted P0/P1/P2 core or cube.lunados.net.**

From the repo root with the G4 MCP Python venv and `AIAEAO_G5_URL` and `AIAEAO_G5_TOKEN` exported from a secure source:

```sh
python3 P3/remote-mcp-g5/scripts/sdk_remote_smoke.py --evidence P3/remote-mcp-g5/evidence/G5_R3_REMOTE_RECHECK.json
```

The sanitized JSON contains no token, prompts or arbitrary response bodies. The host should independently re-read `morphology.md` and `visual/README.md` via MCP Resource Discovery and confirm `text/markdown`, rehash SVG bytes, and capture a new G5-R4 report. Do not mark G5-R4 ACCEPTED before those tests.
