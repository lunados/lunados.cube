# CP-001 / G1 — P0 MCP Resources Proof

**Status:** implementation and offline regression **PASS**; real MCP SDK `stdio` and Claude Desktop resources/read **pending on user's Mac**. This package is **not** a remote MCP service or a deployment authorization.

**Approval:** G0 / CP-001 accepted (user, 2026-10-24). Scope: G1 only (P0 resources). G2 P1 validation, G3 cross-domain proof, G4 public release and G5 remote are not in this package.

## What is new

- `aiaeao_mcp_local/p0_resources.py` registers exactly **13 pinned canonical P0 URLs** as MCP Resources plus **1 digest index** (`aiaeao://p0/resources/v1`).
- `p0_snapshot/` contains byte-for-byte v9.4 reference files from the existing P1-Extended archive. Their SHA-256 digests were checked against the P0 root manifest (see lock file). The archived root manifest also matches the public repository Git blob observed on `main` (2026-10-24).
- Reads use the *original public `https://cube.lunados.net/...` URIs as identifiers only*. Nothing is fetched from the network. Content is served from offline pinned local bytes. There is no arbitrary filesystem or arbitrary URL read operation.
- Each MCP Resource supplies source SHA-256 in metadata/description; the index Resource supplies the complete digest catalogue and a lock hash. Content is never Unicode-normalized, truncated or reserialized.
- The four existing `cube_*print`/`cube_get_capabilities` **Tools remain exactly as in 0.1.1**. There is **no P1 validator**.

## Files changed from P3-MCP-LOCAL/0.1.1

- `aiaeao_mcp_local/server.py`: registers P0 resources, no tool changes
- `aiaeao_mcp_local/p0_resources.py`: new read-only resource registry
- `p0_snapshot/`: new pinned P0 assets and lock
- `scripts/verify_g1.py`: independent offline gate
- `scripts/sdk_g1_resources_smoke.py`: actual MCP v2 `stdio` client integration test
- `tests/test_p0_resources.py`: safety, byte-parity, integrity and registration tests

All changes stay in `P3/`. **No files in P0, P1, P2, or Cloudflare are modified.**

## Apply in an existing repository checkout

From the root of `lunados.cube` (where `P2/` exists):

```bash
# Copy the P3/ directory from the extracted G1 ZIP into this repository.
rsync -av /path/to/extracted/G1_PACKAGE/P3/ ./P3/
cd P3/adapters/mcp-local
source .venv/bin/activate     # use your existing 0.1.1 venv, or create one
python scripts/verify_g1.py
python scripts/sdk_g1_resources_smoke.py
python scripts/sdk_stdio_smoke.py
```

Expected SDK G1 line:

```text
PASS G1 MCP SDK v2 stdio: 14 resources, 4 byte-parity reads, unknown URI rejection, 4 legacy tools
```

The last command is the **unchanged** legacy VP-06 printer stdio test. Python 3.11+ and `mcp==2.0.0` from `requirements-mcp.txt` are required for the SDK tests. There is no new dependency.

## Claude Desktop G1 host acceptance

Restart Claude Desktop after updating the local P3 server (the same Python executable/path as before). Resource selection/support varies by client. Inspect MCP Resources in the host, if exposed, and ask it to read:

- `https://cube.lunados.net/v9.4/morphology.md`
- `https://cube.lunados.net/v9.4/grammar/concepts.json`
- `aiaeao://p0/resources/v1` (SHA-256 index)

Claude should confirm the fixed reference version `v9.4`, name the source and verified digest of each, and explicitly say that P0 resource reading is **not** P1 validation and not truth/authority/admission. If Claude Desktop has no resource-list/read affordance, record a **HOST_RESOURCE_UNAVAILABLE** interoperability issue; do not invent a new `cube_read_reference` Tool unless that limitation is established. See `G1_HOST_ACCEPTANCE.md`.

## Exit conditions

Gate G1 PASS requires **SDK protocol test + real host reading two references**, and the offline tests. If the host cannot read Resources, G1 remains **HOST_PENDING** and CP-001's conditional fallback can be evaluated. All P3 code here is PoC, not an approved production endpoint. An agent may still use original public HTTPS references independently.
