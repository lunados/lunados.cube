# G5 — known limits of the current remote state

**As of:** 2026-11-02 (MILE-012). **Deployed:** private core `P3-MCP-REMOTE/0.9.0-proof` (Cloudflare version `445c6d50-…`), gateway `0.2.0-proof`. **Status:** remote proof, `G5_PROOF_NOT_PRODUCTION_AUTHORIZED`; these limits are accepted, not fixed (MILE-012 D-2, D-3).

## What works remotely

- All ten tools and fourteen P0 resources; P0 reads, P1 validation `/1…/10` (P1.6…P1.14), P2 legacy printing and the plan tools with VP-07…VP-11.
- Every result that arrives is byte-identical to the local G4/G6 result for the same input: offline 88/88 (R5) and 26/26 (R6), live every completed call ([ledger](G5_ACCEPTANCE.md)).
- A failure never changes or truncates a result: a call above a limit ends with an error (`isError`), never with a different payload.

## Limits

| Limit | What happens | Evidence |
|---|---|---|
| **CPU per call in the core** | The largest plan calls can end with `G5_CORE_UNAVAILABLE`: `cube_plan_check` on 26 `cube.flow` panels (P-K07-flow), the plan flow with 33 origin edges (P-OL-07), and occasionally the call right after such an abort (P-K08-sequence). The core tail shows `exceededCpu` at 139 ms (R5) and `CpuLimitExceeded` at 522 ms (R6). | [R5 core tail](evidence/G5_R5_CORE_CPU_EVENT.json), [R6 core tail](evidence/G5_R6_CORE_CPU_EVENT.json), [R5 spec §10](G5_R5_ACCEPTANCE_SPEC.md) |
| **Sporadic abort without a cause** | In one of three R6 runs a small validation (V-HO-11) ended with `G5_CORE_UNAVAILABLE`; the core tail shows no cause. | [R6 run 2](evidence/G5_R6_LIVE_SCRIPT_RUN2.json), [host report](evidence/G5_R6_HOST_REPORT.md) |
| **Shared bearer token** | Access is a single static token (`MCP_BEARER_TOKEN`), no OAuth, no per-user quotas, no rate limiter. | [SECURITY.md](SECURITY.md) |
| **Gateway version label** | R6 added the `cube_plan_source` argument `origin_lines`; the gateway still reports `0.2.0-proof`, so two gateway builds share one label. | commit `c120c3c`, `gateway/src/index.mjs` |
| **No stability proof** | No full live run without any abort exists for R5 or R6; no continuous monitoring. | [ledger](G5_ACCEPTANCE.md) |

The cut-off points differ (139 ms, 522 ms) and lie far below the 30 s default of the Workers Paid plan; this fits the Workers Free plan (10 ms nominal with tolerated bursts). The account's plan is not recorded here.

## Baseline of the current state (MILE-012, 2026-11-02)

One run of each live script against core `0.9.0-proof` and gateway `0.2.0-proof`, bearer token unchanged:

| Run | Result | Deviations |
|---|---|---|
| [R5](evidence/G5_M12_BASELINE_R5.json) | 86/88 | D-01: only `release.version` and `remote_adapter.version` differ (R5 expects `0.8.0-proof`, `0.9.0-proof` is deployed); all other discovery fields match. P-K08-sequence: `G5_CORE_UNAVAILABLE` (same diagnostic digest as every earlier abort). P-K07-flow completed this time |
| [R6](evidence/G5_M12_BASELINE_R6.json) | 25/26 | P-OL-07 `cube_plan_views`: `G5_CORE_UNAVAILABLE` |

Every other call is byte-identical to its fixed expectation. The general remote smoke test ran before both scripts.

## Way out for heavy tasks

Run them locally: the G4/G6 tools of the local adapter (`P3/adapters/mcp-local`) produce the same bytes without a CPU limit. A heavy remote call that ended with `G5_CORE_UNAVAILABLE` can simply be repeated locally with the same arguments.

## Options for later (not planned)

- Workers Paid for the account and `limits.cpu_ms` on the core (default 30 s, up to 5 min), which also caps cost per call.
- Another path for heavy tasks (for example, keeping them local by design).
- OAuth 2.1, rate limits, observability, rollback and secret rotation, cost alerts: gate R7 in the [ledger](G5_ACCEPTANCE.md).
- A new gateway version label at the next gateway deployment.
