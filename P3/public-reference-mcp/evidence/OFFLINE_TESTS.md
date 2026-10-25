# Public Reference MCP – offline build evidence

- Node 22: `node --check src/worker.mjs` – PASS.
- Node 22: `node --test test/*.test.mjs` – 7/7 PASS.
- Manifest source shape checked against GitHub public repository
  `lunados/lunados.cube`, file `AIAEAO_Pure_Cube_P0_v9.4/manifest.json`:
  `reference_version`, `point_of_truth`, `entrypoints`, `assets` with
  `href`, `media_type`, `sha256`, `bytes`.
- The worker resolves all asset URLs from the **current runtime manifest**;
  the v9.4 repository source is only a fixture/schema reference.
- Generator tested with a fake URL for package layout validation only;
  no non-deployed URL is stored in the actual installed plugin.
- Cloudflare deployment/dry-run, HTTP fetch to the live origin, MCP client
  handshake on Cloudflare and ChatGPT plugin tool visibility: PENDING.
