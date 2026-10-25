# Paste into a new Codex macOS App conversation

Use **only** the configured MCP server `aiaeao_cube_g5` (a local Keychain credential adapter connecting to the existing Cloudflare G5 remote MCP). Do not substitute the local G4 server, public read-only Cube plugin, Github files, a web search, or invented responses.

Execute real MCP calls; do not change repository, server, credentials or configuration:

1. Call `cube_discover_surface` and report P0/P1/P2 versions, deployment.remote_mcp_available and remote status.
2. List all seven G5 MCP tools and actually call **each**: cube_get_capabilities, cube_prepare_print, cube_check_print, cube_render_svg, cube_read_reference, cube_validate, cube_discover_surface. Reuse valid fixtures actually available to the host; do not invent.
3. List 14 pinned P0 resources using MCP Resource Discovery. If Resource Discovery is unavailable in the host, explicitly record `AC-05 INCOMPLETE` and show the `cube_read_reference` fallback separately; don't claim 14 resources were read merely because the surface advertises them.
4. Verify P0 SHA-256 and P1 PASS/FAIL/UNRESOLVED when inputs are available; check deterministic P2 SVG golden byte hash with reference fixtures.
5. Verify separation: no inferred truth, Authority, Admission, automatic ACG→SVG mapping, or shared overall status.
6. Confirm no token was exposed. Never output credentials, headers, process environments or debug logs containing tokens.
7. Report AC-01 through AC-08 as PASS/FAIL/INCOMPLETE/HOST_UNSUPPORTED, with the exact tool names actually executed. Distinguish a configured server from a connected and authenticated server. Confirm the Claude integration has **not been modified**; independently testing Claude again is a separate check.

Definition of Done: all eight ACs PASS on actual Codex macOS, not just remote SDK or local tests.
