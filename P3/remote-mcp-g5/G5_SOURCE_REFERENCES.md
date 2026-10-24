# Sources used for G5 implementation (verified 2026-10-24)

1. Cloudflare — [Build Remote MCP Server](https://developers.cloudflare.com/agents/model-context-protocol/guides/remote-mcp-server/), revised 2026-10-22. Stateless `createMcpHandler` recommended, `McpAgent` deprecated for new work.
2. Cloudflare official example — [Minimal MCP server](https://github.com/cloudflare/agents/blob/main/examples/mcp-server/README.md), current `@modelcontextprotocol/server` v2 and `createMcpHandler` usage.
3. MCP — [2026-07-28 transport](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http) and [protocol transition](https://blog.modelcontextprotocol.io/posts/2026-07-28/). One POST endpoint, no protocol session.
4. Cloudflare — [Python Workers](https://developers.cloudflare.com/workers/languages/python/), [packages](https://developers.cloudflare.com/workers/languages/python/packages/), [bundled files](https://developers.cloudflare.com/workers/languages/python/examples/), 2026 documentation. Python Workers run on Pyodide and have platform-specific bundle/runtime constraints requiring actual test.
5. MCP Python SDK v2 — [Client transports](https://py.sdk.modelcontextprotocol.io/client/transports/). Bearer headers via `httpx2.AsyncClient` and `streamable_http_client`.
6. AIAEAO — G4 local accepted profile `P3-MCP-LOCAL/0.2.0-rc1`, P0 v9.4, P1 `P1-VC/1.0.0`, P2 `P2-VP/1.0.0-rc1` and user-provided Claude Host Acceptance in this project.

Cloudflare's deploy/SDK specifications evolve. Package source is a test candidate until real account deployment and remote SDK checks pass; references alone do not prove compatibility.
