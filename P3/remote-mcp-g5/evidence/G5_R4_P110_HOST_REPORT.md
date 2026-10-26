# G5 R4 — Host acceptance P1.10 Declared Migration Profile

**Date:** 2026-10-26 · **Host:** Claude (claude.ai, remote MCP connector "AIAEAO Cube G5 Remote") · **Deployed core version:** `de946c42-3c92-4151-aa0f-3a8d990ada59` (`aiaeao-cube-g5-core`, uploaded 2026-10-26, 8331.28 KiB / gzip 1900.31 KiB, startup 610 ms; "No targets deployed" as expected for the private core)
**Source:** `feature/p110-migration-profile` at `99ec337`, assembled with `assemble_core.py` (91 staged files, P0 lock `cb259c59…a1`). Gateway unchanged, not redeployed.
**Scope:** P1.10-12 (remote parity of M-01…M-22), P1.10-13 (observable deploy) and P1.10-14 (synthetic golden plan live). No code, repository, Cloudflare or secret changes during the run.

## 1. Discovery (P1.10-13)

`cube_discover_surface` — observed:

| Field | Expected | Observed | Result |
|---|---|---|---|
| `release.version` | `P3-MCP-REMOTE/0.4.0-proof` | `P3-MCP-REMOTE/0.4.0-proof` | PASS |
| `remote_adapter.version` | same | `P3-MCP-REMOTE/0.4.0-proof` | PASS |
| `p110_migration.profile` | `P1.10/migration-profile-v1` | `P1.10/migration-profile-v1` | PASS |
| `p110_migration.activation` | explicit `/5` only | `explicit_context_format_5_only` | PASS |
| `p110_migration.predicate_profiles` | `P1.10/migration-predicates-v1` | same | PASS |
| `p110_migration.transition_t_roles` | `scheduling` only (D-4) | `["scheduling"]` | PASS |
| `live_system_checked_by_cube` / `migration_order_decided_by_cube` / `evaluation_performed_by_cube` | `false` ×3 | `false` ×3 | PASS |
| `deployment.remote_status` | `G5_PROOF_NOT_PRODUCTION_AUTHORIZED` | unchanged | PASS |
| `p16_instantiation`, `p18_simulation`, `p19_comparison` | unchanged | unchanged | PASS |

## 2. Vectors M-01…M-22 (P1.10-12)

22 `cube_validate` calls with `input_text`, `input_format: acg_text`, the materialised context from
`P1/migration-profile-v1/fixtures/m01_m22_materialized.json` and, for M-18/M-19, its qualification profile.
Expected values from `oracles/independent_m01_m22.json`. "Codes" lists the full remote diagnostic code
sequence; it is identical, in order, to the local G4 adapter run.

| ID | Expected | Observed | Codes (remote) | Result |
|---|---|---|---|---|
| M-01 | PASS | PASS | — | PASS |
| M-02 | MCP error · CONFIG_INVALID | MCP error `P1_MCP_CONFIG_INVALID` | — | PASS |
| M-03 | MCP error · CONFIG_INVALID | MCP error `P1_MCP_CONFIG_INVALID` | — | PASS |
| M-04 | FAIL · MIGRATION_PHASES | FAIL | MIGRATION_PHASES | PASS |
| M-05 | FAIL · MIGRATION_PHASES | FAIL | MIGRATION_PHASES | PASS |
| M-06 | UNRESOLVED · MIGRATION_REFERENCE_MISSING | UNRESOLVED | MIGRATION_REFERENCE_MISSING | PASS |
| M-07 | FAIL · MIGRATION_TRANSITION_CONFLICT | FAIL | MIGRATION_TRANSITION_CONFLICT | PASS |
| M-08 | UNRESOLVED · QUALIFIER_PROFILE_MISSING | UNRESOLVED | QUALIFIER_PROFILE_MISSING | PASS |
| M-09 | FAIL · MIGRATION_DANGLING_DEPENDENCY | FAIL | MIGRATION_DANGLING_DEPENDENCY | PASS |
| M-10 | UNRESOLVED · MIGRATION_SUCCESSOR_MISSING | UNRESOLVED | MIGRATION_SUCCESSOR_MISSING | PASS |
| M-11 | PASS | PASS | — | PASS |
| M-12 | FAIL · MIGRATION_SUCCESSOR_INVALID | FAIL | MIGRATION_SUCCESSOR_INVALID, MIGRATION_DANGLING_DEPENDENCY | PASS |
| M-13 | FAIL · MIGRATION_PREMATURE_DEPENDENCY | FAIL | MIGRATION_SUCCESSOR_INVALID, MIGRATION_PREMATURE_DEPENDENCY | PASS |
| M-14 | FAIL · PREDICATE_SIGNATURE | FAIL | REFERENT_MISMATCH, PREDICATE_SIGNATURE ×2 | PASS |
| M-15 | UNRESOLVED · EVALUATION_WITNESS_MISSING | UNRESOLVED | EVALUATION_WITNESS_MISSING | PASS |
| M-16 | FAIL · MIGRATION_PHASES | FAIL | MIGRATION_PHASES | PASS |
| M-17 | FAIL · MIGRATION_DANGLING_DEPENDENCY | FAIL | MIGRATION_DANGLING_DEPENDENCY | PASS |
| M-18 | PASS | PASS | — | PASS |
| M-19 | FAIL · PREDICATE_SIGNATURE | FAIL | PREDICATE_SIGNATURE, MIGRATION_EXPRESSION_MISMATCH | PASS |
| M-20 | MCP error · CONFIG_INVALID | MCP error `P1_MCP_CONFIG_INVALID` | — | PASS |
| M-21 | UNRESOLVED · MIGRATION_SCOPE_MISMATCH | UNRESOLVED | MIGRATION_SCOPE_MISMATCH | PASS |
| M-22 | UNRESOLVED · QUALIFIER_PROFILE_MISSING | UNRESOLVED | QUALIFIER_PROFILE_MISSING | PASS |

**22/22 PASS.** Every semantic result carried `migration_profile: "P1.10/migration-profile-v1"`,
`evaluation_performed_by_cube: false`, `source_warrant: declared_unverified`,
`transport: remote_mcp_streamable_http`, and `epistemic_warrant`, `current_authority`,
`canonical_admission` = `NOT_EVALUATED` (P1.10-08). MCP errors were sanitised
(`files_written: false`, `semantic_status: NOT_EVALUATED`).

## 3. Synthetic golden plan (P1.10-14)

`fixtures/golden_migration_synthetic.json`: 24 dependencies, 3 phases, 2 transitions, 22 referents, no client data (D-7).
Input: `rel("supersedes", new-mail, legacy-mail) @T(scheduling)` with its qualification profile.

| Case | Expected | Observed | Codes | Result |
|---|---|---|---|---|
| G-neg (recovery of the system mailbox still via the provider retired first) | FAIL · MIGRATION_DANGLING_DEPENDENCY | FAIL | MIGRATION_DANGLING_DEPENDENCY at `/migration_plans/0/dependencies/14/holds_in` | PASS |
| G-pos (recovery moved at p1) | PASS | PASS | — | PASS |

The ordering risk of the 2026-10-26 test case — found then by reading — is now reported by the Cube from a declared plan.

## 4. Verdict

P1.10-12 (remote parity, 22/22), P1.10-13 (observable deploy) and P1.10-14 (golden live): **PASS**.

Limits: The run checks the deployed core against declared, synthetic data only. It does not show that a real inventory is complete, that any dependency exists live, or that a migration order is safe. P1.9 vectors were not re-run live in this session; discovery shows `p19_comparison` unchanged. The remote status remains `G5_PROOF_NOT_PRODUCTION_AUTHORIZED`.
