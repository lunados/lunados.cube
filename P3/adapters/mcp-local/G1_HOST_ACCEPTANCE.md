# G1 — P0 MCP Resource Host Acceptance (Claude Desktop)

**Gate:** CP-001/G1, not G2/G3. **Status:** Pending host evidence.

## Checklist

- [ ] The same `aiaeao-cube` local stdio server starts with the existing Claude Desktop config.
- [ ] `resources/list` exposes 13 canonical reference URIs and `aiaeao://p0/resources/v1` (14 in total); order stable across calls.
- [ ] Host actually **reads** `https://cube.lunados.net/v9.4/morphology.md` from MCP Resources (not a web fetch), describes v9.4 and confirms its SHA-256 matches the index.
- [ ] Host actually **reads** `https://cube.lunados.net/v9.4/grammar/concepts.json` from MCP Resources (not a web fetch), confirms its SHA-256 matches the index.
- [ ] Unknown resource URI is rejected; no arbitrary HTTP/FS fetching.
- [ ] The four existing printer tools still work; `cube_get_capabilities` still reports P1 validation unavailable.
- [ ] No assertion of authenticated truth, permission/admission or automatic P1 validation.

## Client instructions

> Use **only MCP resources** exposed by the local AIAEAO Cube server. List resources, then read the `aiaeao://p0/resources/v1` index. Read the Morphology v9.4 and Concepts v9.4 resources. Name their exact URIs, byte counts and SHA-256 digests, comparing them with the index. Then list the four printer Tools and state whether a P1 validator exists. If MCP Resources are not supported in this host, say so explicitly and do not substitute a web search.

Record client, version, observed tool names, resource URIs, hashes, whether reads came through MCP, any errors, and test date. Report **PASS** only after actual host evidence; SDK success alone is insufficient.
