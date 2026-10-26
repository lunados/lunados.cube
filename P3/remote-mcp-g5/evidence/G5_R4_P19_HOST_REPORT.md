# G5 R4 — Host acceptance P1.9 Declared Comparison Profile

**Date:** 2026-10-26 · **Host:** Claude (claude.ai, remote MCP connector "AIAEAO Cube G5 Remote") · **Deployed core version:** `2d75e2c6-fa63-464b-803f-541fd914d703` (`aiaeao-cube-g5-core`, uploaded 2026-10-26)
**Source:** `main` at `d7ddb36` (merge of `feature/p19-comparison-profile`), assembled with `assemble_core.py` (87 staged files, P0 lock `cb259c59…a1`).
**Scope:** P1.9-13 (remote parity of C-01…C-20), P1.9-14 (observable deploy) and P1.9-15 (four golden comparisons live). No code, repository, Cloudflare or secret changes during the run.

## 1. Discovery (P1.9-14)

`cube_discover_surface` — observed:

| Field | Expected | Observed | Result |
|---|---|---|---|
| `release.version` | `P3-MCP-REMOTE/0.3.0-proof` or later | `P3-MCP-REMOTE/0.3.0-proof` | PASS |
| `remote_adapter.version` | same | `P3-MCP-REMOTE/0.3.0-proof` | PASS |
| `p19_comparison.profile` | `P1.9/comparison-profile-v1` | `P1.9/comparison-profile-v1` | PASS |
| `p19_comparison.activation` | explicit `/4` only | `explicit_context_format_4_only` | PASS |
| `p19_comparison.statistics_computed_by_cube` / `evaluation_performed_by_cube` | `false` / `false` | `false` / `false` | PASS |
| `deployment.remote_status` | `G5_PROOF_NOT_PRODUCTION_AUTHORIZED` | unchanged | PASS |
| `p16_instantiation`, `p18_simulation` | unchanged | unchanged | PASS |

## 2. Vectors C-01…C-20 (P1.9-13)

20 `cube_validate` calls with `input_text`, `input_format: acg_text` and the materialised `/4` context from `P1/comparison-profile-v1/fixtures/c01_c20_materialized.json`. Expected values from `oracles/independent_c01_c20.json`.

| ID | Expected | Observed | Required code present | Result |
|---|---|---|---|---|
| C-01 | PASS | PASS | — | PASS |
| C-02 | FAIL · COMPARISON_ARMS | FAIL | yes (+ REFERENCE_MISSING) | PASS |
| C-03 | FAIL · COMPARISON_ARMS | FAIL | yes | PASS |
| C-04 | FAIL · COMPARISON_PAIRING | FAIL | yes | PASS |
| C-05 | FAIL · COMPARISON_CONFOUNDED | FAIL | yes | PASS |
| C-06 | FAIL · COMPARISON_CONFOUNDED | FAIL | yes | PASS |
| C-07 | PASS | PASS | — | PASS |
| C-08 | FAIL · COMPARISON_OUTCOME_INVALID | FAIL | yes | PASS |
| C-09 | FAIL · COMPARISON_OUTCOME_INVALID | FAIL | yes | PASS |
| C-10 | FAIL · COMPARISON_OUTCOME_INCONSISTENT | FAIL | yes | PASS |
| C-11 | FAIL · COMPARISON_AGGREGATION_UNDECLARED | FAIL | yes | PASS |
| C-12 | PASS (ranking flip) | PASS | — | PASS |
| C-13 | FAIL · COMPARISON_OUTCOME_CONFLICT | FAIL | yes | PASS |
| C-14 | FAIL · COMPARISON_SPLIT_MIXED | FAIL | yes | PASS |
| C-15 | FAIL · COMPARISON_OUTCOME_TYPE | FAIL | yes | PASS |
| C-16 | PASS | PASS | — | PASS |
| C-17 | FAIL · REPLAY_RECORD_MISMATCH | FAIL | yes | PASS |
| C-18 | FAIL · REPLAY_DIVERGENT | FAIL | yes | PASS |
| C-19 | UNRESOLVED · REPLAY_DIVERGENT | UNRESOLVED | yes | PASS |
| C-20 | MCP error · P1_MCP_CONFIG_INVALID | MCP error `P1_MCP_CONFIG_INVALID` (stage `p1_adapter`) | yes | PASS |

**20/20.** Every report carried `comparison_profile: P1.9/comparison-profile-v1`, `evaluation_performed_by_cube: false`, `transport: remote_mcp_streamable_http`, and `epistemic_warrant`, `current_authority`, `canonical_admission` = `NOT_EVALUATED`.

## 3. Golden comparisons (P1.9-15)

| Golden | Outcomes | Observed | Server `declared_context_sha256` | Local canonical hash | Result |
|---|---|---|---|---|---|
| `golden_exp002b.json` | 36 | PASS, 0 diagnostics | `af00aaf1…3105` | `af00aaf1…3105` | PASS |
| `golden_exp003.json` | 4 | PASS, 0 diagnostics | `ac869d3f…bdef` | `ac869d3f…bdef` | PASS |
| `golden_exp007.json` | 4 | PASS, 0 diagnostics | `36d69116…58fd` | `36d69116…58fd` | PASS |
| `golden_exp009d.json` | 30 + `replay_of` | PASS, 0 diagnostics | `f687d1a1…e051` | `c4db63ee…9e10` (file) / `f687d1a1…e051` (with `0.0` written as `0`) | PASS |

The EXP-009-D digest difference is transport formatting only: the host serialised the JSON numbers `0.0` (four `switch_rate` values and the `mean_work` margin) as `0`. Re-hashing the fixture with that single substitution reproduces the server digest exactly. The semantic content is identical.

## 4. Not tested / limits

- Client-side SVG hashing is not part of P1.9 (no P2 change).
- `serverInfo.version` of the gateway still reports the Charge 3 value; the gateway was intentionally not redeployed. `cube_discover_surface` is the authoritative version source.
- PASS states that the declarations are coherent. It does not state that a comparison was fair, that parity held, or that any outcome is true.

## 5. Overall

**PASS** — P1.9-13, P1.9-14 and P1.9-15 accepted on the live G5 proof service. Status remains `G5_PROOF_NOT_PRODUCTION_AUTHORIZED`.
