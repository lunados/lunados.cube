# G4 Release Notes — Local MCP

Release candidate **P3-MCP-LOCAL/0.2.0-rc1**, CP-001/G4, 2026-10-24.

### Added

- `cube_discover_surface`: one whole-Cube P0/P1/P2 capability card, with precise runtime/host limitations.
- G4 conformance golden JSON, Draft 2020-12 schema, 56 independent regression and negative tests.
- Consolidated P3 delivery containing G1 Resources, G1.1 fallback, G2 Validation and G3 cross-domain proof.
- New macOS target SDK smoke and optional GitHub CI workflow.

### Unchanged / preserved

- P0 v9.4 canonical documentary reference and 13 locked local snapshots, plus MCP Resource index.
- P1 P1-VC/1.0.0 semantics and its eight checks.
- P2 P2-VP/1.0.0-rc1 renderer, layout, SVGs and existing four MCP tool signatures.
- Old `cube_get_capabilities` returns **legacy printer-only** view; its version `P3-MCP-LOCAL/0.1.1` and printer-only tool list are intentionally preserved for backward compatibility. It is not the service-wide discovery channel. Agents should call `cube_discover_surface`.

### Boundaries

No HTTP endpoint, remote MCP, WebMCP, authentication system, background worker, P1 truth evaluation, Authority/Admission, ACG→SVG auto-mapping, or auto-multi-SVG. The online static Cube remains unchanged.

### Remaining acceptance

SDK and Claude actual G4 host checks on user's Mac. No GitHub or Cloudflare change was made by this package.
