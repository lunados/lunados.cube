# G5 R3 – Runtime reference asset bundling hotfix

## Why

Remote G5 progressed past P0 resource catalog and failed at P1 `UNRESOLVED`.
The prior P0-only bundling patch includes P0 JSON/MD/EBNF, but excludes the frozen
P1 baseline resources opened by `cube_resolver.Resolver` and P2 reference JSON
opened by `vp2d/printer.py`. Both groups require explicit Wrangler Text bundling.

This patch extends the **private Python Worker** configuration to include all
non-Python assets in the existing frozen G5 assembly. It does **not** modify the
P0/P1/P2 source, MCP Gateway, secrets, local MCP adapter, or public domain.

## Apply (Finder + rsync)

Unpack ZIP in Finder and copy extracted folder into `~/cube-patches/`.
Run from local repository root:

```sh
rsync -av "$HOME/cube-patches/AIAEAO_Cube_G5_Runtime_Assets_Hotfix/P3/" ./P3/
python3 P3/remote-mcp-g5/scripts/verify_g5.py
python3 P3/remote-mcp-g5/scripts/check_runtime_assets.py
cd P3/remote-mcp-g5/.g5-runtime
uv run pywrangler deploy
```

Then, from repo root with existing `.venv` and exported
`AIAEAO_G5_URL` and `AIAEAO_G5_TOKEN`:

```sh
python3 P3/remote-mcp-g5/scripts/sdk_remote_smoke.py
```

### Gates

- Local: 40 frozen asset manifests checksum-verified and covered by Wrangler.
- Cloudflare build: verify upload listing includes P1 baseline `concepts.json`,
  `source_lock.json`, and P2 reference `p0-symbols-v9.4.json`.
- Remote: P1 UNRESOLVED and PASS, P2 bit-identical SVG.

A successful upload alone does **not** prove Pyodide runtime execution.
If the smoke test fails again, examine its `structured_content` for the exact
MCP error and avoid modifying the frozen functional core.
