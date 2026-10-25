# Lunados Cube – Public Reference MCP (`lunados-cube` 0.2.0)

**Separate public reader; no effect on canonical P0, the topology or G5.**

## Objective

One public, read-only MCP tool `cube_read_public_reference` to read the current
`https://cube.lunados.net/manifest.json` and an optional exact asset key from
its `assets` map. Implemented as a stateless Cloudflare Worker running a backend
HTTPS fetch; the ChatGPT skill and browser are not required to have shell DNS.

The source model is the **live manifest** (not a frozen v9.4 reference). The
Worker never contacts the protected G5-MCP and has no credentials, storage,
write methods, or permission to fetch an arbitrary URL.

## Structure

- `worker/src/worker.mjs` – stateless MCP JSON-RPC HTTP + bounded public GET
- `worker/test/reader.test.mjs` – deterministic offline contract/security tests
- `worker/wrangler.toml` – isolated new Cloudflare Worker; no G5 binding
- `scripts/live_mcp_smoke.mjs` – real remote MCP validation
- `plugin-source/` – **staged** source for an update to existing `lunados-cube`
- `scripts/generate_plugin_update.py` – create a plugin update ZIP **only after** real Worker URL is known
- `ACCEPTANCE.md` – AC-01..07 and evidence status

## Mac: install without modifying G5

1. Unpack the ZIP via Finder, copy extracted folder into `~/cube-patches/`.
2. From the repository root:

```bash
cd "$HOME/Downloads/lunados.cube"
rsync -av "$HOME/cube-patches/AIAEAO_Cube_Public_Reference_MCP/P3/" ./P3/
cd P3/public-reference-mcp/worker
node --check src/worker.mjs
node --test test/*.test.mjs
npx --yes wrangler@4.152.0 deploy --dry-run --outdir dist
```

3. Deploy **only** new public reference Worker:

```bash
npx --yes wrangler@4.152.0 deploy
```

Wrangler prints the real URL. Example structure (DO NOT assume this exact host):
`https://<new-worker>.<account>.workers.dev`. Use the exact printed URL.

4. Validate the HTTP/MCP endpoint, using URL with `/mcp` appended:

```bash
cd "$HOME/Downloads/lunados.cube"
node P3/public-reference-mcp/scripts/live_mcp_smoke.mjs \
  'https://<ACTUAL-NEW-WORKER>.workers.dev/mcp'
```

5. Only after the remote test passes, connect the **existing** plugin ID
`plugins_6addaab50e888191abc5313a51e688d7` using a partial plugin update.
The release ID at packaging time was `pluginrel_6addaab64160819180215c09db4f1742`.
Always refresh the current release before applying an update; never create a new plugin.

```bash
python3 P3/public-reference-mcp/scripts/generate_plugin_update.py \
  --url 'https://<ACTUAL-NEW-WORKER>.workers.dev/mcp' \
  --out "$HOME/Downloads/lunados-cube-0.2.0-update.zip"
```

The generated plugin update includes the existing identity and two manifest
formats, the updated `read-cube` skill and a portable `mcp.json` with a
`streamable-http` server. It does not include an undeployed endpoint in the
current installed plugin. For a managed ChatGPT plugin, pass the generated ZIP
to the plugin editor / ask ChatGPT to install the update after the live endpoint
has been verified. Preserve the existing plugin's visibility and permissions.

## Operational behavior

- Manifest is read **fresh on every tool call**; asset keys are resolved using
  that exact manifest from the same call. Versions are never hard-coded.
- Allowed sources: HTTPS on **exactly** `cube.lunados.net`, no userinfo, custom
  port, query or fragment. Redirects require the same policy and have a cap.
- Requests: JSON POST only to `/mcp`, no remote shell, writes, arbitrary URLs.
- Limits: 32 KiB MCP input, 256 KiB manifest, 512 KiB each asset; 10s origin
  fetch timeout; 3 redirects; explicit Content-Length and streaming limits.
- Body `content` retains decoded UTF-8 original text. SHA-256 is calculated
  over **raw HTTP bytes before decoding**. Mismatches yield an error and no
  asset content; no unverified asset can be presented as verified.
- `sha256_verified: null` for the manifest or assets without a declared hash.
- `retrieved_at` is server UTC ISO8601 time; `source_url` is the actual final
  allowed source URL. A manifest-relative redirect or href can never leave the
  allowlisted origin.
- `/health` is an informational public status, not a live origin check.
- Transport-only MCP JSON-RPC responses are supported. No sessions, prompts,
  resources, write methods, OAuth, bearer or G5 tools.

## Known limits

Cloudflare live deployment, ChatGPT plugin registration and actual web-host
execution are **not proven by offline Node tests**. The deployment and live
plugin acceptance must be executed after installing this package.

Manifest-relative integrity does not guarantee independent source authenticity.
The public endpoint is not a user-authorization or rate-limit system; if this
endpoint is exposed to unrestricted traffic, Cloudflare's platform-level
rate/bot/cost controls must be considered separately. No claims of authority,
admission or governance follow from any reference content.
