# Copyable prompt for Claude Desktop — G4 only

Run a real MCP tool and host acceptance test for the local **AIAEAO Cube G4** server. Do not edit any files and do not use web search.

1. Call **`cube_discover_surface`** and report the release version, all seven available tools, 14 declared Resource URIs, and separated P0/P1/P2 profiles. Distinguish the **whole-surface** card from legacy **P2-only** `cube_get_capabilities`. Do not report the legacy 0.1.1 adapter card as the G4 release version.
2. Verify `cube_read_reference` can read `aiaeao://p0/resources/v1` via the tool-only bridge; do not pretend to use `resources/read` if the host does not expose it.
3. Use `cube_validate` with a known valid ACG fixture (with declared context), a malformed ACG text and the same valid text without context. Confirm PASS / FAIL / UNRESOLVED remain normal MCP tool results; truth, Authority and Admission remain NOT_EVALUATED.
4. Use a separately supplied VP-03 fixture through `cube_prepare_print`, `cube_check_print`, `cube_render_svg`. Report actual SVG bytes and digest; compare independently when possible.
5. Show that a P1 FAIL does not prevent a successful **independent** P2 display. Confirm none of the seven tools implies automatic ACG→SVG.
6. Report PASS/FAIL per criterion; explicitly list host limitations, missing independent checks and whether G4 can be accepted.

Only genuine tool calls count, no simulated API replies or implementation changes.
