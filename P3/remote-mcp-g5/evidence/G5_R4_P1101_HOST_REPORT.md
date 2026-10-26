# G5 R4 — Host acceptance P1.10.1 Dependency Gap (`binding-context/6`)

**Date:** 2026-10-26 · **Host:** Claude (claude.ai, remote MCP connector "AIAEAO Cube G5 Remote") · **Deployed core version:** `bb523ec9-ded3-43a5-a7a4-aba045cf6dc8` (`aiaeao-cube-g5-core`, uploaded 2026-10-26, 8352.58 KiB / gzip 1904.91 KiB, startup 780 ms; "No targets deployed" as expected for the private core)
**Source:** `main` at `568ef55` (merge of PR #13 `feature/p1101-dependency-gap`), assembled with `assemble_core.py` (94 staged files, P0 lock `cb259c59…a1`). Gateway unchanged, not redeployed. Deployed with `uv` 0.13.5 (pywrangler requires ≥ 0.13.4).
**Scope:** P1.10.1-08 (remote parity of G-01…G-10), P1.10.1-09 (observable deploy) and P1.10.1-10 (golden gap pair live). No code, repository, Cloudflare or secret changes during the run.

## 1. Discovery (P1.10.1-09)

| Field | Expected | Observed | Result |
|---|---|---|---|
| `release.version`, `remote_adapter.version` | `P3-MCP-REMOTE/0.5.0-proof` | `P3-MCP-REMOTE/0.5.0-proof` | PASS |
| `p1101_migration.profile` | `P1.10.1/migration-profile-v2` | same | PASS |
| `p1101_migration.activation` | explicit `/6` only | `explicit_context_format_6_only` | PASS |
| `p1101_migration.additional_diagnostics` | `P1_MIGRATION_DEPENDENCY_GAP` | same | PASS |
| `p1101_migration.ends_reason_values` | `scope_end`, `replaced_outside_plan`, `other` | same | PASS |
| `live_system_checked_by_cube` / `migration_order_decided_by_cube` / `evaluation_performed_by_cube` | `false` ×3 | `false` ×3 | PASS |
| `p110_migration` | unchanged as accepted in `G5_R4_P110_HOST_REPORT.md` (D-7) | unchanged | PASS |
| `p16_instantiation`, `p18_simulation`, `p19_comparison`, `deployment.remote_status` | unchanged | unchanged | PASS |

## 2. Vectors G-01…G-10 (P1.10.1-08)

10 `cube_validate` calls, `input_text` `rel("depends-on",Z:α:Integration["import-job"],Y:α:Resource["mailbox-x"])`, contexts from `P1/migration-profile-v2/fixtures/g01_g10_materialized.json`, expectations from `oracles/independent_g01_g10.json`.

| ID | Case | Expected | Observed | Codes (remote) | Result |
|---|---|---|---|---|---|
| G-01 | ends at p1, target p3, object never retired | UNRESOLVED · DEPENDENCY_GAP | UNRESOLVED | DEPENDENCY_GAP | PASS |
| G-02 | G-01 as `/5` | PASS (P1.10 unchanged) | PASS, envelope `P1.10/migration-profile-v1` | — | PASS |
| G-03 | holds to target | PASS | PASS | — | PASS |
| G-04 | `dropped: true` | PASS | PASS | — | PASS |
| G-05 | object retired at p2 | UNRESOLVED · SUCCESSOR_MISSING, no gap | UNRESOLVED | SUCCESSOR_MISSING | PASS |
| G-06 | object retired only at p3 | UNRESOLVED · DEPENDENCY_GAP | UNRESOLVED | DEPENDENCY_GAP ("retired only at 'p3'") | PASS |
| G-07 | subject retired at p2 | PASS | PASS | — | PASS |
| G-08 | valid successor from p2 | PASS | PASS | — | PASS |
| G-09 | successor starts at p3 | FAIL · SUCCESSOR_INVALID | FAIL | SUCCESSOR_INVALID (D-5) | PASS |
| G-10 | `ends_reason: scope_end` with witness | PASS | PASS | — | PASS |

**10/10 PASS.** Every `/6` result carried `migration_profile: "P1.10.1/migration-profile-v2"`, `evaluation_performed_by_cube: false`, `source_warrant: declared_unverified`, `transport: remote_mcp_streamable_http`, and `epistemic_warrant`, `current_authority`, `canonical_admission` = `NOT_EVALUATED`.

## 3. Golden gap pair (P1.10.1-10)

`P1/migration-profile-v2/fixtures/golden_gap_synthetic.json`, input `rel("supersedes", new-mail, legacy-mail) @T(scheduling)` with its qualification profile.

| Case | Expected | Observed | Result |
|---|---|---|---|
| GG-pos (P1.10 golden G-pos as `/6`, 24 dependencies) | PASS | PASS, no diagnostics | PASS |
| GG-gap (+ d14 `acme:website hosted-by acme:dns`, `holds_in [p0, p1]`, dns never retired) | UNRESOLVED, exactly one DEPENDENCY_GAP | UNRESOLVED, one DEPENDENCY_GAP at `/migration_plans/0/dependencies/24` | PASS |

The field-test case (a dependency silently stopping while its object lives on) is now reported by P1 itself, not only visible as an empty bar in `cube.phases`.

## 4. Verdict

P1.10.1-08 (remote parity 10/10), P1.10.1-09 (observable deploy) and P1.10.1-10 (golden pair live): **PASS**.

Limits: synthetic declared data only; a gap is a missing declaration, not evidence that the dependency still exists or was removed. M-01…M-22 as `/6` and the P1.10 regression were verified locally (32/32, 72/72) and through the offline G4/G5 parity, not re-run live. Remote status stays `G5_PROOF_NOT_PRODUCTION_AUTHORIZED`.
