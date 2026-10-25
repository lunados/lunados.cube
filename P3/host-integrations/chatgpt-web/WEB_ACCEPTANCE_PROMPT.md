# Paste into ChatGPT Web with newly installed native MCP plugin

Use **only** the native Web MCP plugin `Lunados Cube Public Reference (Web)`; do not use standalone read-cube skill, shell/curl, Codex, browser/web search, GitHub or protected G5. Only real calls to `cube_read_public_reference` count as evidence.

1. Call the public MCP tool with `{}` to fetch the **live** `manifest`. Report `reference_version`, `point_of_truth`, `entrypoints`, and available keys in `assets`.
2. Call the same tool with `asset_key` values `core`, `ebnf`, and `ast_schema` when they exist in that manifest.
3. For each returned asset, compare `source_url`, `content_type`, `sha256_verified` with the actual manifest and independently hash `content` if possible. Never claim verified if a mismatch or no hash is present.
4. Call `cube_read_public_reference({"asset_key":"does_not_exist"})` and inspect the structured failure without pretending a successful read.
5. Confirm no auth/OAuth is requested, no private G5 tools were accessed and no write tool is exposed.
6. Report PASS/FAIL/INCOMPLETE/HOST_UNSUPPORTED for AC-01..AC-08 and actual MCP tool call trace. If no MCP call is visible, report BLOCKED, not PASS.
