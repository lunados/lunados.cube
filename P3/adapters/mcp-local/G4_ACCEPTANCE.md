# G4 Acceptance Gate — evidence-first

**Prior gates:** G0 ACCEPTED (user), G1 ACCEPTED with Claude Resources bridge limitation and successful tool fallback, G2 ACCEPTED, G3 ACCEPTED. These acceptance statements are user-reported; do not mistake them for automated CI signatures.

| Item | Verification | Current status |
|---|---|---|
| G4 source conformance | 56 new tests, manifest golden and Draft 2020-12 schema | PASS locally |
| G1/G2 frozen regressions | 137 offline tests | PASS locally |
| G3 cross-domain independence | 41 independent offline tests | PASS locally |
| P1.5 core conformance | Full unchanged P1.5 oracle | PASS locally |
| P0 pinned v9.4 snapshot | 13 locked source files and MCP index | PASS locally |
| Legacy printer compatibility | Four unchanged tools, frozen VP-06 fixture | PASS offline; SDK target pending |
| Seven MCP tools via genuine SDK/stdio | `sdk_g4_stdio_smoke.py` | **PENDING on macOS** |
| 14 Resources and P0 fallback via genuine SDK | same smoke | **PENDING on macOS** |
| G4 discovery in Claude host | `cube_discover_surface` | **PENDING** |
| P1 status vs P2 render separation in Claude | G3 previously observed; verify no regression | **PENDING G4 reconfirmation** |
| GitHub workflow | `.github/workflows/cube-p3-mcp-g4.yml` optional, not deployed | **PENDING** |

**Release rule:** do not mark G4 ACCEPTED until the user confirms real SDK + host tests. G4 release candidate may be distributed locally for this testing. P0/P1/P2 canonical source is unchanged.

## Non-implications

- G4 describes a **local** interface, not an HTTP or Remote MCP server.
- P0 integrity does not validate source truth.
- P1 PASS does not grant runtime authority or canonical admission.
- P2 projection PASS does not assert P1 semantics.
- An absent Resource in Claude does not mean Resources are absent in the MCP server; the Tool fallback is an accepted host compatibility path.
