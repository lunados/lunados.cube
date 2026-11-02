# G5 R4 — Host acceptance P1.12 Declared Coverage and Instance Profile (`binding-context/8`)

**Date:** 2026-11-02
**Host:** Claude (claude.ai session, remote MCP connector "AIAEAO Cube G5 Remote")
**Deployed core version:** `42e7b8a9-0086-43fd-bb33-1757fae1f32c` (`aiaeao-cube-g5-core`; 8412.22 KiB, gzip 1917.43 KiB; startup 682 ms; "No targets deployed", as expected for the private core)
**Source:** branch `feature/mile006-remote-and-order` at `49e3893`, assembled with `assemble_core.py` (103 staged files incl. `cube_p112`; P0 lock `cb259c59…a1`). Deployed by the user with `uv run pywrangler deploy`. Gateway unchanged and not redeployed.
**Expectations:** [`G5_R4_P112_EXPECTATIONS.json`](G5_R4_P112_EXPECTATIONS.json), committed in `68ba97f` before the core change and the deployment.
**Scope:** MILE-006 TASK-038 (D-2: `/8` in `cube_validate` plus discovery; plan views stay local).
**Conduct:** Run live by the agent over the connector (D-3). No code, repository, Cloudflare or secret changes during the run.

## 1. Discovery

| Field | Expected | Observed | Result |
|---|---|---|---|
| `release.version`, `remote_adapter.version` | `P3-MCP-REMOTE/0.7.0-proof` | same | PASS |
| `p112_coverage_instance.profile` | `P1.12/coverage-instance-profile-v1` | same | PASS |
| `p112_coverage_instance.binding_context_formats` / `activation` | `/8` only, `explicit_context_format_8_only` | same | PASS |
| `p112_coverage_instance.additional_diagnostics` | COVERAGE_UNDECLARED, INSTANCE_MISMATCH, INSTANCE_UNDECLARED | same | PASS |
| `population_evaluation_by_cube`, `coverage_inferred_by_cube`, `live_system_checked_by_cube`, `evaluation_performed_by_cube` | `false` ×4 | `false` ×4 | PASS |
| `p16_instantiation`, `p18_simulation`, `p19_comparison`, `p110_migration`, `p1101_migration`, `p111_migration_methods`, `deployment.remote_status` | unchanged | unchanged | PASS |

## 2. Vectors (live `cube_validate`)

Contexts come from `P1/coverage-instance-profile-v1/fixtures/k01_k21_materialized.json`; expectations from the independent oracle (`8297b82`).

| ID | Case | Expected | Observed (remote) | Result |
|---|---|---|---|---|
| K-01 | absence of any realizer of TP, no coverage | UNRESOLVED · COVERAGE_UNDECLARED | same | PASS |
| K-02 | incoming `realizes` of TP declared; absence Billing → TP | PASS | PASS, no diagnostics | PASS |
| K-05 | pair (printer, parser) declared; rule validator → printer | UNRESOLVED · COVERAGE_UNDECLARED | same | PASS |
| K-09 | count 2…3, no coverage | UNRESOLVED · COVERAGE_UNDECLARED | same | PASS |
| K-12 | exactly one path, declared | PASS | PASS | PASS |
| K-13 | exactly one path, no coverage | UNRESOLVED · COVERAGE_UNDECLARED | same | PASS |
| K-14 | join activation i1, flows declared for i1 | PASS | PASS | PASS |
| K-16 | join activation i2, no coverage | UNRESOLVED · COVERAGE_UNDECLARED | same | PASS |
| K-17 | shared scope, cross-instance `joins`, `requires_same_instance` | FAIL · INSTANCE_MISMATCH | FAIL · INSTANCE_MISMATCH ("i1/tok-stock is in i1, i2/tok-credit is in i2") | PASS |
| K-18 | instance as scope (regression) | FAIL · REFERENT_MISMATCH, SCOPE_CONFLICT; no INSTANCE_* | same | PASS |
| K-19 | `joins` within i1 | PASS | PASS | PASS |
| K-20 | `instance_ref` only on i1/tok-stock | UNRESOLVED · INSTANCE_UNDECLARED | same ("no instance_ref on i2/tok-credit") | PASS |
| K-21 | `routedTo`, `requires_same_instance: false` | PASS | PASS | PASS |

Every `/8` result carried:
- `coverage_profile: P1.12/coverage-instance-profile-v1` and `population_evaluation_by_cube: false`;
- `migration_profile: P1.11/migration-methods-v1` and `transport: remote_mcp_streamable_http`;
- `epistemic_warrant`, `current_authority` and `canonical_admission` = `NOT_EVALUATED`.

## 3. Errors, golden, regressions

| Case | Expected | Observed | Result |
|---|---|---|---|
| K-08 context as `/7` (P1.12 fields in `/7`) | MCP error `P1_MCP_CONFIG_INVALID` | `P1_MCP_CONFIG_INVALID` | PASS |
| K-08 with coverage scope `view` | MCP error `P1_MCP_CONFIG_INVALID` | `P1_MCP_CONFIG_INVALID` | PASS |
| VP-10 golden GC-en context (`/8`, P1.10 profile predicate `references`, pair and row declaration) | PASS | PASS, no diagnostics | PASS |
| P1.11 F-01 (`/7`) | PASS; envelope P1.11, no `coverage_profile` | same | PASS |
| BPMN-03 shared as `/1` (MILE-002 case file) | PASS (unchanged `/1`) | PASS, no P1.11/P1.12 envelope fields | PASS |

The golden case also confirms the P1.12 fix `5f32bce` remotely: profile predicates resolve.

## 4. Transfer check

For every request, the remote envelope's `declared_context_sha256` (canonical sorted-key JSON) equals the digest of the source context in the repository. That is 16 of 16: K-01, K-02, K-05, K-09, K-12, K-13, K-14, K-16, K-17, K-18, K-19, K-20, K-21, GC-en, F-01 and BPMN-03 `/1`. The host transmitted the contexts unchanged.

## 5. Result

**PASS.** All expectations met: 13 vectors, 2 errors, golden and 2 regressions. `/8` is available through the remote connector; the profile is still `remote_proof_not_accepted` for production (unchanged release status).

## 6. Not covered

- Plan views remote (D-2).
- LIB evaluation (lunados.lib `analyze.population/v1`, not part of the Cube).
- K-03, K-04, K-06, K-07, K-10, K-11, K-15: same P1 path as the accepted vectors; covered by the offline parity 21/21.
- Independent second host (only Claude was used).
