# ChatGPT Web — Public Read-only Cube MCP

**Goal:** Expose `cube_read_public_reference` in ChatGPT Web via the existing deployed public Cloudflare worker (NOT the protected G5 server). The previously saved personal plugin `lunados-cube` v0.2.0 has `mcp.json` but may be imported as **Desktop Only**. That is not equivalent to a Web-native MCP app.

## Existing server; no new implementation

- Native MCP endpoint: `https://lunados-cube-public-reference.jo-885.workers.dev/mcp`
- Authentication: **No authentication**
- One read-only tool: `cube_read_public_reference(asset_key?)`
- `manifest` default, other valid manifest keys; no user paths/URLs, no writes, SHA-256 relative to live manifest.
- Protected `https://aiaeao-cube-g5-gateway.jo-885.workers.dev/mcp` is out of scope and must NOT be entered in this workflow.

## Native ChatGPT Web registration (manual UI action required)

1. On **chatgpt.com**, open **Plugins** and click **+ → Add custom MCP server**. If this control is missing, do not simulate or claim Web compatibility: record `HOST_UNSUPPORTED` or `BLOCKED_BY_PLAN_OR_WORKSPACE` and consult account/workspace permissions.
2. Display name: `Lunados Cube Public Reference (Web)`; optional description: `Read-only live public Cube grammar; no auth.`
3. Connection/URL: `https://lunados-cube-public-reference.jo-885.workers.dev/mcp` (include `/mcp`).
4. Authentication: **No authentication**. Do not configure OAuth, bearer tokens or secrets.
5. Acknowledge the risk warning, select **Create as a plugin**. Review discovered tools: exactly `cube_read_public_reference`.
6. Install the newly registered native MCP plugin from **Personal plugins** (or permitted Workspace plugins).
7. Open a **new ChatGPT Web Work conversation** (or a surface that exposes installed MCP plugins); type `@` and select `Lunados Cube Public Reference (Web)`; use `WEB_ACCEPTANCE_PROMPT.md`.
8. Record actual tool call trace/response and mark ACs in `WEB_HOST_ACCEPTANCE.md`.

The UI registration flow creates an MCP-backed plugin identity. The existing imported `lunados-cube` package **is preserved**; there is no supported binding action available to this workflow that can automatically turn that same plugin into a Web-native app. If the UI offers an explicit **attach/link existing plugin** capability, use that only after verifying it preserves the existing plugin ID and skill; otherwise keep the new Web plugin separate and record `EXISTING_PLUGIN_LINK_PENDING`. Do not create a second server implementation or delete the original skill/plugin. The original v0.2.0 standalone plugin is left unchanged by this package.

## What Web access requires

Custom MCP registration is governed by the user's plan, Workspace capabilities and permissions. Current official docs distinguish full MCP on Business/Enterprise/Edu and read/fetch access on eligible Pro accounts. **Do not assume a specific account is eligible.** If the creation option is absent, it is an entitlement/host gate, not evidence of a failed worker.

- Official registration: https://developers.openai.com/api/docs/guides/custom-mcp-server
- Official Plugin quickstart: https://developers.openai.com/plugins/quickstart
- Current availability details: https://help.openai.com/en/articles/12584461-connecting-custom-mcp-servers-in-chatgpt

## Reproducible technical preflight

From repo root:

```bash
node P3/host-integrations/chatgpt-web/scripts/live_mcp_smoke.mjs \
  'https://lunados-cube-public-reference.jo-885.workers.dev/mcp'
```

This tests the deployed MCP Worker via its HTTP transport: initialized session, exactly one tool, live manifest, core/ebnf/ast_schema, hashes and unknown-key rejection. **It is not a substitute for a genuine tool invocation in ChatGPT Web.** It does not need credentials.

## Rollback

Disable/uninstall only the new Web-native plugin in Plugins settings. Leave the original `lunados-cube` v0.2.0 and the public Worker in place. Do not change or rotate G5 tokens.
