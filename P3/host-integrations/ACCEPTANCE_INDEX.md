# Two independent host acceptance tracks

**Freeze principle:** The Cube topology, P0 reference, P1 semantic validator, P2 printer, G5 protected server, its token gate, public read-only server, and the existing `lunados-cube` personal plugin are unchanged. This is a host-distribution overlay only.

| Track | Prepared offline | Actual host acceptance | Required action |
|---|---|---|---|
| Codex macOS G5 | Keychain bridge tested; non-destructive config installer tested | **PENDING** | Install adapter, restart Codex, invoke tools and resources |
| ChatGPT Web public MCP | Existing public server contract smoke script provided | **PENDING / possible entitlement restriction** | Register native custom MCP in ChatGPT Web, install and invoke tool |

## Final evidence

- `codex/CODEX_HOST_ACCEPTANCE.md` records AC-01 through AC-08. Must distinguish stdio adapter transport from remote Cloudflare Streamable HTTP. Do not claim 14 resources read if Codex does not surface resource APIs.
- `chatgpt-web/WEB_HOST_ACCEPTANCE.md` records AC-01 through AC-08. Actual ChatGPT Web MCP call is mandatory; Node direct smoke is insufficient.
- Host acceptance logs should omit tokens, Authorization headers, environment dumps, Keychain values, private credentials, account IDs and personally identifiable information.
- Keep screenshots and other private host-specific logs outside Git until reviewed.

## Host unsupported is a valid, non-destructive outcome

If GUI Codex blocks all supported transports or cannot enumerate resources, record HOST_UNSUPPORTED or INCOMPLETE; do not make G5 weaker. If ChatGPT Web disallows Add custom MCP server because of account or workspace permissions, record BLOCKED_BY_PLAN_OR_WORKSPACE; do not fabricate Web availability or redeploy a duplicate MCP server.
