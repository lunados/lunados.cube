# G5 R5 — Control flow and plan views remote · Acceptance specification

**Status:** DRAFT. MILE-010 decisions D-1…D-8 apply (2026-11-02); detail questions Q-1…Q-10 open (§7). Not implemented.
**Release:** core `P3-MCP-REMOTE/0.8.0-proof` (from `0.7.0-proof`, MILE-006); still `G5_PROOF_NOT_PRODUCTION_AUTHORIZED`.
**Requirement:** MILE-010 US-030, US-031, TASK-058…062.
**Basis:** G5 core and gateway (`python-core/core_runtime.py`, `gateway/src/index.mjs`), `scripts/assemble_core.py`, `scripts/check_runtime_assets.py`, `scripts/verify_g5.py`; local G4/G6 (`P3/adapters/mcp-local`: `p1_adapter.py` with `/9`, `plan_views.py` with VP-07…VP-11); R4 P1.12 expectations and host report (MILE-006).

All examples are synthetic.

## 0. Scope

| In scope | Out of scope |
|---|---|
| `cube_validate` with `binding-context/9` (P1.13) and its discovery block | New P1 rules; lunados.lib remote |
| `cube_plan_source`, `cube_plan_views`, `cube_plan_check` with VP-07, VP-08, VP-09, VP-10, VP-11 | New views or printer changes |
| Staging, asset rules and offline gates for the added packages | Production approval, OAuth, rate limits, `cube.lunados.net` |
| Deployment of core **and** gateway (three new tools) and host acceptance R5 | A visual check (outputs are byte-identical to the checked local ones, D-8) |

## 1. Design summary

1. **Same code, staged.** The core already stages the local adapter package `aiaeao_mcp_local` unchanged; it contains `p1_adapter.py` (`/9`) and `plan_views.py` (G6). R5 stages what they import: `P1/control-flow-profile-v1/cube_p113` and the plan printer packages with their siblings (`vpmigration`, `vpsequence`, `vpaxes`, `vpcells`, `vpinstances`) and runtime data files. No source file is rewritten.
2. **Core dispatch.** Three new operations call `plan_views.plan_source`, `plan_views.plan_views` and `plan_views.plan_check`; a `PlanFailure` becomes `{ok: false, diagnostic}` with the local diagnostic unchanged.
3. **Gateway.** Three tools with input schemas equal to the local tool signatures; the tool list grows from seven to ten.
4. **Discovery.** The remote surface gains `p113_control_flow` (as `p112_coverage_instance`) and `P2.plan_views` with `remote_available: true`.
5. **Equality.** Remote results equal local results byte for byte (D-4); limits and error codes as local (D-5).

## 2. Operations and wire

| Tool | Core operation | Local function | Result |
|---|---|---|---|
| `cube_plan_source` | `cube_plan_source` | `plan_views.plan_source(context, plan_id, printer, **options)` | source document |
| `cube_plan_views` | `cube_plan_views` | `plan_views.plan_views(source, view, granularity, **options)` | `aiaeao.cube.plan-views/1` |
| `cube_plan_check` | `cube_plan_check` | `plan_views.plan_check(result)` | check report |
| `cube_validate` | unchanged | `p1_adapter.validate` (now with `/9`) | unchanged, plus `transport` as today |

- **RW-1:** Options are passed exactly as the local server passes them (`track_map` → `tracks`, `hide_ledger` false → absent, `None` dropped).
- **RW-2:** A `PlanFailure` returns `{ok: false, diagnostic}` with the local `aiaeao.cube.mcp-plan-diagnostic/1` or printer diagnostic unchanged; the gateway marks it `isError`. Missing or mistyped arguments return `G5_ARGUMENTS_INVALID` as for the other tools.
- **RW-3:** Plan results carry no added field (no `transport`), so they stay byte-identical to local results (Q-3).

## 3. Limits

| Limit | Local (G6) | Remote |
|---|---|---|
| Request | 2 MiB arguments (`P3_PLAN_INPUT_INVALID`) | gateway body 2 MiB + 4 KiB (unchanged); then the local check |
| SVG | 512 KiB (`P3_PLAN_SVG_TOO_LARGE`) | the local check |
| Response | 2 MiB canonical payload (`P3_PLAN_RESPONSE_TOO_LARGE`) | the local check; the gateway's core-reply cap must leave room for the wire envelope (Q-4) |

Over a limit the result is an error; nothing is truncated or split.

## 4. Staging and assets

- **ST-1:** `assemble_core.py` adds `P1/control-flow-profile-v1/cube_p113` and, for the printers, every package directory that `plan_views.py` and its printers put on `sys.path` (Q-5). Files are copied byte for byte; the manifest lists their SHA-256.
- **ST-2:** Every non-Python file the added code reads at runtime (locale files, pinned catalogs, schemas) is covered by the Text rules in `python-core/wrangler.jsonc`; `check_runtime_assets.py` counts them by family and checks digests (Q-5).
- **ST-3:** `assemble_core.py` gains self-checks: KF-01…KF-09 through `cube_validate`, one vector per view through the plan operations, and `/9` in the discovery.

## 5. Runtime measurement (D-6)

- **RM-1:** Offline, the core measures CPU time per call for every plan vector (CPython, assembled runtime) and records the largest per view.
- **RM-2:** Live, the acceptance records the wall time of the largest vector per view (Q-7).
- **RM-3:** A view whose live call ends in `G5_CORE_UNAVAILABLE` (runtime limit) is removed from the remote scope by D-6; VP-10 and VP-11 stay if they pass. The removal is a new core version and is reported.

## 6. Acceptance criteria and evidence (planned, fixed in TASK-059)

| AC | Requirement | Evidence |
|---|---|---|
| R5-01 | P0, P1, P2, local adapter and lunados.lib unchanged; only `P3/remote-mcp-g5` changes | file diff |
| R5-02 | Offline: every plan vector (K-01…K-18, O-01…O-10, S-01…S-16, I-01…I-34) and every `/9` vector (KF-01…KF-09, the seven BPMN re-run cases) gives through the assembled core the same canonical result as locally | parity report |
| R5-03 | Offline: R1–R4 gates unchanged (`verify_g5.py`, contract tests, P1.12 parity 21/21), asset coverage, tool count 10 | gate output |
| R5-04 | Runtime measurement per RM-1 | report |
| R5-05 | Live: discovery, `/9` cases and KF vectors, one vector per view with SVG digest, `cube_plan_check`, one limit case, one argument error, as expected | host report R5 |
| R5-06 | Expectations committed before core and gateway code | git order |

Evidence: `evidence/G5_R5_EXPECTATIONS.json`, `evidence/G5_R5_OFFLINE_PARITY.json`, `evidence/G5_R5_HOST_REPORT.md`.

## 7. Detail questions (proposals, open)

| ID | Question | Proposal | Reason |
|---|---|---|---|
| **Q-1** | Tool names and schemas? | **Same names as local** (`cube_plan_source`, `cube_plan_views`, `cube_plan_check`); gateway schemas mirror the local signatures (all options optional and typed as locally, e.g. `records` list, `axis_order` list) | one vocabulary for host and documentation |
| **Q-2** | How are plan errors returned? | `{ok: false, diagnostic}` with the **local diagnostic unchanged**, `isError` in MCP, as the local server does | equal error codes (D-5) |
| **Q-3** | `transport` field on plan results? | **No**; only `cube_validate` and `cube_render_svg` keep theirs | byte-identity with local results (D-4) |
| **Q-4** | Gateway cap for core replies? | Raise from 2 MiB to **2 MiB + 64 KiB** so that the plan limit (2 MiB payload) triggers first and the local error code arrives; nothing else changes | otherwise a response close to 2 MiB would end in `G5_CORE_OUTPUT_TOO_LARGE` instead of `P3_PLAN_RESPONSE_TOO_LARGE` |
| **Q-5** | Which packages and files are staged? | Exactly what an import and file-read trace of all vectors in an empty directory needs, nothing more; listed in the manifest and counted by family in `check_runtime_assets.py` | minimal and checkable; no hidden reads |
| **Q-6** | Discovery? | Remote surface gains `p113_control_flow` (profile, `binding-context/9`, false flags as P1.13) and `P2.plan_views` = local `capabilities()` with `remote_available: true` and `transport: streamable_http` | honest per-feature statement |
| **Q-7** | How is runtime judged before deployment? | Offline CPython CPU per call; **proceed if every vector stays under 2 s**; live timing of the largest vector per view is recorded; a view that fails live by runtime limit is removed per RM-3 | Pyodide is slower than CPython; 2 s leaves a wide margin below the Worker CPU limit |
| **Q-8** | Versions? | Core `P3-MCP-REMOTE/0.8.0-proof`; gateway `0.2.0-proof` (`/health` and server info), because the tool list changes | visible in discovery and health check |
| **Q-9** | Live acceptance set? | Discovery; `/9`: the seven BPMN re-run cases and KF-01…KF-09; plan: K-01 (`cube.phases`), one `cube.flow` vector, one `cube.sequence` vector, one `cube.axes` vector, S-04 (`cube.cells`), I-22 (`cube.instances`) and I-34 (German); `cube_plan_check` on I-22; one SVG-limit case; one argument error. Expected status, codes and SVG SHA-256 fixed in TASK-059 | covers both parts, every printer and every error path once |
| **Q-10** | Deployment steps for the user? | Short addendum to `DEPLOYMENT.md`: `verify_g5.py`, deploy core, deploy gateway (no new secret), `sdk_remote_smoke.py` (now ten tools), then reconnect the connector in the host so the new tools appear | the gateway must be redeployed this time; the host caches the tool list |
