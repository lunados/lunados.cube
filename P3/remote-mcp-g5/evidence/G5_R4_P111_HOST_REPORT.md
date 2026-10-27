# G5 R4 — Host acceptance P1.11 Migration method catalog (`binding-context/7`)

**Date:** 2026-10-27 · **Host:** Claude (claude.ai, remote MCP connector "AIAEAO Cube G5 Remote") · **Deployed core version:** `372a6160-f265-4a1a-aadb-d86ac51ad549` (`aiaeao-cube-g5-core`, uploaded 2026-10-27, 8365.44 KiB / gzip 1905.53 KiB, startup 1623 ms; "No targets deployed" as expected for the private core)
**Source:** `main` at `f9e0921` (merge of PR #19 `feature/p111-method-catalog`), assembled with `assemble_core.py` (98 staged files incl. `cube_p111`, P0 lock `cb259c59…a1`). Gateway unchanged, not redeployed. Deployed with `uv` 0.13.5.
**Scope:** P1.11-07 (G4/G5 dispatch of `/7`, live host acceptance) and P1.11-08 (golden live). No code, repository, Cloudflare or secret changes during the run.

## 1. Discovery

| Field | Expected | Observed | Result |
|---|---|---|---|
| `release.version`, `remote_adapter.version` | `P3-MCP-REMOTE/0.6.0-proof` | `P3-MCP-REMOTE/0.6.0-proof` | PASS |
| `p111_migration_methods.profile` | `P1.11/migration-methods-v1` | same | PASS |
| `p111_migration_methods.activation` | explicit `/7` only | `explicit_context_format_7_only` | PASS |
| `p111_migration_methods.catalog_methods` | import, rebuild, retire, rewrite, reconfigure (`/v1`) | same | PASS |
| `p111_migration_methods.additional_diagnostics` | METHOD_UNKNOWN, METHOD_SIGNATURE, METHOD_PLAN | same | PASS |
| `method_execution_by_cube` / `live_system_checked_by_cube` / `migration_order_decided_by_cube` / `evaluation_performed_by_cube` | `false` ×4 | `false` ×4 | PASS |
| `p1101_migration`, `p110_migration`, `p16_instantiation`, `p18_simulation`, `p19_comparison`, `deployment.remote_status` | unchanged | unchanged | PASS |

## 2. Vectors (live `cube_validate`)

Contexts from `P1/migration-methods-v1/fixtures/f01_f16_materialized.json`, expectations from `oracles/independent_f01_f16.json`. F-03 (catalog digest altered) needs a patched pin and is covered locally only; F-04, F-07, F-09, F-11, F-13 are covered locally and by the offline G4/G5 parity (15/15). F-10 and F-12 were sent as one combined context.

| ID | Case | Expected | Observed (remote) | Result |
|---|---|---|---|---|
| F-01 | `/7` with catalog, no bindings | PASS | PASS, no diagnostics | PASS |
| F-02 | unknown catalog `…-v9` | MCP error `P1_MCP_CONFIG_INVALID` | `P1_MCP_CONFIG_INVALID` | PASS |
| F-05 | import + retire on the transition, rewrite on the dependency | PASS | PASS, no diagnostics | PASS |
| F-06 | `migrate.unknown/v1` | UNRESOLVED · METHOD_UNKNOWN | UNRESOLVED · METHOD_UNKNOWN | PASS |
| F-08 | import target is an Actor | FAIL · METHOD_SIGNATURE | FAIL · METHOD_SIGNATURE ("not admissible for role target", MC-3) | PASS |
| F-10 + F-12 | retire on a non-retired referent; rewrite without successor | FAIL · METHOD_PLAN ×2 | FAIL · METHOD_PLAN (MP-1) and METHOD_PLAN (MP-3) | PASS |
| F-14 | `supersedes … @T(scheduling) @F(method="migrate.import/v1")` with catalog | PASS | PASS, `qualifier_typing` PASS | PASS |
| F-15 | same without `method_profile_refs` | UNRESOLVED · QUALIFIER_PROFILE_MISSING | UNRESOLVED · "F requires one scoped pure_declarative method declaration" | PASS |
| F-16 | method bindings in a `/6` context | MCP error `P1_MCP_CONFIG_INVALID` | `P1_MCP_CONFIG_INVALID` | PASS |
| G-01 (P1.10.1 regression) | `/6`, ends at p1, never retired | UNRESOLVED · DEPENDENCY_GAP, envelope P1.10.1 | same, `migration_profile: P1.10.1/migration-profile-v2` | PASS |

Every `/7` result carried `migration_profile: "P1.11/migration-methods-v1"`, `method_execution_by_cube: false`, `evaluation_performed_by_cube: false`, `source_warrant: declared_unverified`, `transport: remote_mcp_streamable_http`, and `epistemic_warrant`, `current_authority`, `canonical_admission` = `NOT_EVALUATED`.

## 3. Golden (P1.11-08)

`P1/migration-methods-v1/fixtures/golden_methods_synthetic.json`, case GM-misfit: the three-workstream plan (33 dependencies, 4 transitions) with 8 transition bindings and 16 rewrite bindings, one of them deliberately wrong (`migrate.retire/v1` on `acme:archive-store` at `t-mail-cut`).

| Case | Expected | Observed | Result |
|---|---|---|---|
| GM-misfit | FAIL, exactly one METHOD_PLAN | FAIL, one METHOD_PLAN at `/migration_plans/0/transitions/1/methods/2/arguments/retired` (MP-1); all other 23 bindings without diagnostic | PASS |

GM-pos (same plan without the misfit) is PASS locally and through the offline parity; the live GM-misfit result shows that every other binding of GM-pos passes on the host as well.

## 4. Verdict

P1.11-07 (G4/G5 dispatch, live host acceptance) and P1.11-08 (golden live): **PASS**.

Limits: synthetic declared data only; a PASS means the declared bindings are well typed and fit the declared plan, never that a method is appropriate or was carried out. Remote status stays `G5_PROOF_NOT_PRODUCTION_AUTHORIZED`.
