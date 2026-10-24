# G5 security boundary — experiment, NOT a production security review

- **Gateway:** `/mcp` requires bearer token, refuses wrong Origin, caps requests to 2 MiB + framing allowance, caps internal JSON results to 2 MiB, does not allow CORS wildcard, no public filesystem or URL tool.
- **Backend:** Python Worker is configured `workers_dev: false`, no route, accessed only through an internal Service Binding. Confirm this before deploying.
- **Secrets:** Token only through Cloudflare Worker Secrets, never committed. `MCP_BEARER_TOKEN` must be 32+ chars. Rotate/revoke after test.
- **Data:** P0 content is pinned, read-only, hash-verified. Source inputs/ASTs may be sensitive; do not log payload bodies, SVG text or secret headers.
- **Tool contracts:** One allowlist of seven names, one additional internal resource read, no arbitrary code, shell, network URL, file path, writes or general ACG-to-SVG conversion. P1 `FAIL` must be ordinary result; adapter config error must be `isError: true`.
- **Output:** P2 SVG receives the existing active-content guard and 512 KiB limit. No user-authored SVG scripts, hrefs, event handlers or arbitrary external references are allowed.
- **Limitations:** No OAuth, no per-user quotas, no access-control roles, no built-in IP/abuse rate limiter, no resource-metering bound by tokens, no continuous observability or long-running stability proof. Use Cloudflare Access/WAF or OAuth and rate-limit rules before broad exposure.
- **MCP protocol:** Explicitly modern `2026-07-28` with `legacy:'reject'`. This can prevent legacy clients from connecting, intentionally for this proof.
- **Deployment isolation:** NEVER change Cloudflare Pages for `cube.lunados.net`; deploy to temporary Worker domain. Use a private backend Service Binding. Treat any public backend route as a hard failure.
