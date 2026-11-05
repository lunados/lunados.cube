# G5 — known limits of the current remote state

**As of:** 2026-11-05 (MILE-015, R9). **Deployed:** private core `P3-MCP-REMOTE/0.9.2-proof` (Cloudflare version `f4458919-1b94-462e-8dc9-2cb95c51ff86`) on Workers Paid with `limits.cpu_ms` 30 000, gateway `0.2.0-proof`. **Status:** remote proof, `G5_PROOF_NOT_PRODUCTION_AUTHORIZED`; the remaining limits are accepted, not fixed (MILE-012 D-2, D-3).

## What works remotely

- All ten tools and fourteen P0 resources; P0 reads, P1 validation `/1…/11` (P1.6…P1.15), P2 legacy printing and the plan tools with VP-07…VP-11 (migration printer up to 0.7.8).
- Every result that arrives is byte-identical to the local G4/G6 result for the same input: offline 88/88 (R5) and 26/26 (R6), live every completed call; R8 live 33/33 including VP-07.7; R9 live 51/51 including P1.15 and VP-07.8 ([ledger](G5_ACCEPTANCE.md)).
- A failure never changes or truncates a result: a call above a limit ends with an error (`isError`), never with a different payload.

## Limits

| Limit | What happens | Evidence |
|---|---|---|
| **CPU per call in the core** (eased in R8) | Up to R6 the largest plan calls could end with `G5_CORE_UNAVAILABLE` (`exceededCpu` at 139 ms in R5, `CpuLimitExceeded` at 522 ms in R6) on the free plan. Since R8 the account runs Workers Paid with `limits.cpu_ms` 30 000: P-OL-07, P-K07-flow and P-K08-sequence completed in the R8 live run (longest wall time 1.07 s). A call above 30 s CPU still ends with an error; plans much larger than the tested ones are not measured. | [R8 live](evidence/G5_R8_LIVE_SCRIPT.json), [R5 core tail](evidence/G5_R5_CORE_CPU_EVENT.json), [R6 core tail](evidence/G5_R6_CORE_CPU_EVENT.json) |
| **Sporadic abort without a cause** | In one of three R6 runs a small validation (V-HO-11) ended with `G5_CORE_UNAVAILABLE`; the core tail shows no cause. Not seen in the single R8 run; whether it was a side effect of the CPU limit is open. | [R6 run 2](evidence/G5_R6_LIVE_SCRIPT_RUN2.json), [host report](evidence/G5_R6_HOST_REPORT.md) |
| **Shared bearer token** | Access is a single static token (`MCP_BEARER_TOKEN`), no OAuth, no per-user quotas, no rate limiter. | [SECURITY.md](SECURITY.md) |
| **Gateway version label** | R6 added the `cube_plan_source` argument `origin_lines`; the gateway still reports `0.2.0-proof`, so two gateway builds share one label. | commit `c120c3c`, `gateway/src/index.mjs` |
| **No stability proof** | R8 is the first full live run without any abort (33/33, one run); there is no repeated run and no continuous monitoring. | [ledger](G5_ACCEPTANCE.md) |

The earlier cut-off points (139 ms, 522 ms) lie far below the 30 s of Workers Paid and fit the Workers Free plan (10 ms nominal with tolerated bursts). The account was moved to Workers Paid on 2026-11-05 (MILE-013 D-4).

## Baseline of the current state (MILE-012, 2026-11-02)

One run of each live script against core `0.9.0-proof` and gateway `0.2.0-proof`, bearer token unchanged:

| Run | Result | Deviations |
|---|---|---|
| [R5](evidence/G5_M12_BASELINE_R5.json) | 86/88 | D-01: only `release.version` and `remote_adapter.version` differ (R5 expects `0.8.0-proof`, `0.9.0-proof` is deployed); all other discovery fields match. P-K08-sequence: `G5_CORE_UNAVAILABLE` (same diagnostic digest as every earlier abort). P-K07-flow completed this time |
| [R6](evidence/G5_M12_BASELINE_R6.json) | 25/26 | P-OL-07 `cube_plan_views`: `G5_CORE_UNAVAILABLE` |

Every other call is byte-identical to its fixed expectation. The general remote smoke test ran before both scripts.

## R8 (MILE-013, 2026-11-05)

One run of `scripts/r8_remote_acceptance.py` against core `0.9.1-proof` and gateway `0.2.0-proof` after the general remote smoke test: [33/33](evidence/G5_R8_LIVE_SCRIPT.json), tools and health as expected. Longest calls: P-OL-07 1.07 s, P-K07-flow 1.03 s (wall time per step, client side).

## R9 (MILE-015, 2026-11-05)

One run of `scripts/r9_remote_acceptance.py` against core `0.9.2-proof` and gateway `0.2.0-proof` after the general remote smoke test: [51/51](evidence/G5_R9_LIVE_SCRIPT.json), tools and health as expected. Longest calls: P-OL-07 1.08 s, P-K07-flow 1.06 s, P78-01 0.22 s (wall time per step, client side).

## Way out for heavy tasks

Run them locally: the G4/G6 tools of the local adapter (`P3/adapters/mcp-local`) produce the same bytes without a CPU limit. A heavy remote call that ended with `G5_CORE_UNAVAILABLE` can simply be repeated locally with the same arguments.

## Options for later (not planned)

- Raising `limits.cpu_ms` (up to 5 min) if larger plans need it; cost alerts for the paid plan.
- Another path for heavy tasks (for example, keeping them local by design).
- OAuth 2.1, rate limits, observability, rollback and secret rotation, cost alerts: gate R7 in the [ledger](G5_ACCEPTANCE.md).
- A new gateway version label at the next gateway deployment.
