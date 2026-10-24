# CP-001 / G2 — P1 MCP Validation Proof

**Status:** Local offline verification PASS; official MCP SDK stdio/Claude host proof PENDING on user's Mac. This is not a remote service and has NOT been deployed.

## Scope

Adds **one** tool, `cube_validate`, to the existing `P3/adapters/mcp-local` server. It calls the **unchanged** `P1/semantic-validator-v1/cube_semantic/validator.py` and retains the four VP-06 Tools, one G1.1 P0 Tool fallback, and 14 native G1 MCP Resources. Requires existing checkout with `P0`, `P1`, `P2` and G1/G1.1 `P3` in the repository root. This ZIP is a **P3-only overlay**, not a standalone installer.

Expected Tools order after G2:

1. `cube_get_capabilities` (printer-only, legacy contract unchanged)
2. `cube_prepare_print`
3. `cube_check_print`
4. `cube_render_svg`
5. `cube_read_reference` (G1.1 fallback)
6. **`cube_validate`** (G2)

The legacy `cube_get_capabilities` card deliberately continues to describe the P2 printer as `p1_validation: false`. Its old `adapter.tools` array lists the historical **four printer tools only**. This is intentional compatibility; full `cube_discover_surface`/updated version registry is deferred to G4. Use `tools/list` for actual MCP tool availability.

## MCP tool signature

```python
cube_validate(
    input_text: str,
    input_format: 'acg_text' | 'json_ast' = 'acg_text',
    context: dict | None = None,
    qualification_profiles: dict | None = None
)
```

- `input_text` is the exact Unicode string encoded as UTF-8 by the adapter. For `json_ast`, pass JSON **text as a string**, not a decoded dict.
- `context` is a P1.1 `binding-context/1` declaration object, **not** a user identity or trusted evidence. No server-side fixture selection, paths, URLs, environment access or remote lookup.
- `qualification_profiles` is the separate optional P1.4 `qualification-profiles/1` declaration object. A supplied context or witness reference is **unverified**.
- Size limits: 2 MiB JSON request, 1 MiB UTF-8 input text. No file writes or network access.

## Response semantics

Successful MCP call has `isError=false` for **all three** semantic outcomes `PASS`, `FAIL`, `UNRESOLVED`. `structuredContent.report` is the **exact original** P1 `aiaeao.cube.validation-report/1` object. Its eight canonical check IDs are preserved, along with `epistemic_warrant`, `current_authority`, `canonical_admission` all equal to `NOT_EVALUATED`.

Invalid context, qualification profile, argument shape, or too-large inputs have `isError=true` and a small, sanitized `P1_MCP_*` diagnostic with `semantic_status: NOT_EVALUATED`. These are comparable to P1 CLI exit 3 (configuration), **not** semantic `FAIL`.

`declared_context_sha256` and `declared_qualification_profiles_sha256` cover stable, sorted-key, compact UTF-8 JSON **re-serialization** of the received MCP objects. They are not digests of the original literal JSON wire encoding. P1 report `input_sha256` covers the exact UTF-8 encoding of `input_text`. Duplicate object keys cannot be represented after MCP JSON decoding; callers requiring a literal, byte-for-byte context JSON audit must use the frozen P1 CLI or a separately designed raw-input interface.

**No P1-to-VP03 visual-plan conversion, no P1-triggered SVG, no facts asserted, no Admission or Authority.** Visual printing remains independent and `declared_unverified`.

## Local install (Mac)

Unzip into Downloads. From repository root `~/Downloads/lunados.cube`:

```bash
rsync -av "$HOME/Downloads/AIAEAO_Cube_MCP_G2_P1_Validation_Proof/P3/" ./P3/
cd P3/adapters/mcp-local
source .venv/bin/activate
python scripts/verify_g2.py
python scripts/sdk_g2_stdio_smoke.py
# For additional regression checks:
python scripts/sdk_g1_tool_fallback_smoke.py
python scripts/sdk_stdio_smoke.py
```

**Expected** `PASS G2 OFFLINE: 137 P3 tests, frozen P1.5 gate...` followed by `PASS G2 official MCP SDK v2 stdio: 6 tools...` on an installed SDK-v2 Mac. `sdk_g2_stdio_smoke.py` was not executed in the build container because `mcp==2.0.0` is not installed there; the local in-memory/core parity and complete P1.5 gate passed.

Restart Claude Desktop fully after updating source. The host bridge can expose Tools even when it does not expose native Resources. That restriction does not change G2.

## MCP host-acceptance checklist

1. Agent discovers exactly six tools, including `cube_validate`.
2. `cube_validate` with migration ACG and provided migration P1 context → semantic `PASS`, `isError=false`.
3. Same ACG without context → `UNRESOLVED`, `isError=false`.
4. Invalid ACG syntax → `FAIL`, `isError=false`.
5. Invalid P1 context → MCP `isError=true`, `P1_MCP_CONFIG_INVALID`; not a semantic `FAIL`.
6. Agent reports P1 check statuses and **all three `NOT_EVALUATED`** fields correctly; doesn't interpret P1 `PASS` as truth or execution permission.
7. G1 P0 read fallback and four VP-06 tools still function.
8. Source hash and original P1 report compared to original P1 CLI.

Log limitations such as Claude bridge hiding native Resources independently, per G1 acceptance.

## Release policy

Gate G2 local implementation tested; **not** GitHub/Cloudflare deployment and **not** G3 acceptance. Do not commit G1/G1.1/G2 piecemeal until the user approves a consolidated P3 release at G4.
