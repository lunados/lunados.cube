# SPEC acceptance – Public Reference Access

| AC | Mechanism | Evidence and release gate |
|---|---|---|
| 01 | `tools/list` advertises exactly `cube_read_public_reference`; `tools/call` runs server-side | Offline PASS; actual ChatGPT plugin call PENDING deployment/update |
| 02 | Default `manifest` GET returns unchanged `content`, version, point_of_truth, entrypoints, assets | Offline PASS; live host PENDING |
| 03 | Keys `core`, `ebnf`, `ast_schema` are resolved from same-call manifest | Offline PASS synthetic; live host PENDING |
| 04 | Rejects unknown keys, arbitrary URLs, forbidden host and cross-host redirects | Offline PASS |
| 05 | SHA-256 of downloaded bytes compared against manifest; errors never include wrong raw content | Offline PASS; live source tests PENDING |
| 06 | Staged `read-cube` skill prioritizes MCP; curl only when shell/network available | Source prepared; plugin update PENDING |
| 07 | Completely separate public Worker without G5 binding or auth configuration | Architecture/code PASS; deployment separation PENDING |

**Release statuses**

- Worker code: locally tested and staged for independent Cloudflare deployment.
- Existing ChatGPT plugin `lunados-cube` v0.1.0: **not modified yet**.
- Update candidate `lunados-cube` v0.2.0: source prepared; generated `mcp.json`
  requires the real deployed URL. Backend tool not yet visible in ChatGPT.
- `cube.lunados.net`, normative grammar, protected G5: not changed.

## Final live ChatGPT acceptance prompt

> Use only the `lunados-cube` plugin and its actual `cube_read_public_reference`
> MCP tool. Read `manifest` with no arguments; report the current
> `reference_version` and list `point_of_truth`, `entrypoints`, `assets`.
> Read `core` and two grammar files (`ebnf`, `ast_schema`) if listed;
> report exact `source_url`, content size, and `sha256_verified`.
> Finally ask for an intentionally nonexistent `asset_key` and show the
> structured refusal. Do not use shell curl or the protected G5 MCP.

Success requires actual tool calls from the ChatGPT-hosted plugin, not mock tests.
