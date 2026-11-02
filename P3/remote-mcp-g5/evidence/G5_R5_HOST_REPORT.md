# G5 R5 — Host acceptance: control flow (`binding-context/9`) and plan views remote

**Date:** 2026-11-02
**Host:** Claude (claude.ai session in project CUBE, remote MCP connector "AIAEAO Cube G5 Remote")
**Deployed:** core `P3-MCP-REMOTE/0.8.0-proof` and gateway `0.2.0-proof`, as deployed by the user for the scripted live runs ([`G5_R5_LIVE_SCRIPT_RUN4.json`](G5_R5_LIVE_SCRIPT_RUN4.json)). No redeployment between the script runs and this host run.
**Source:** branch `feature/mile010-remote-plan-views` at `75eb528`.
**Expectations:** [`G5_R5_EXPECTATIONS.json`](G5_R5_EXPECTATIONS.json), committed in `a29450a` (TASK-059) before core and gateway code.
**Scope:** MILE-010 TASK-061, spec §8 CL-3: the host subset `host_subset` (D-01, V-KF-08, V-BPMN-01-routed-to-ship-v9, V-BPMN-01-token-position-v9, P-K08-sequence, P-I-14, P-ARG-plan-id). All other chains are covered by the scripted live acceptance.
**Conduct:** Run live by the agent over the connector, with the wire arguments of `scripts/r5_calls.py` passed unchanged; chain steps receive the previous result unchanged (`from`). Digests recomputed with `plan_views.canonical` of the local adapter (read-only checkout). No code, repository, Cloudflare or secret changes during the run.

## 1. Discovery (D-01)

| Field | Expected | Observed | Result |
|---|---|---|---|
| `release.version`, `remote_adapter.version` | `P3-MCP-REMOTE/0.8.0-proof` | same | PASS |
| `p113_control_flow.profile` | `P1.13/control-flow-profile-v1` | same | PASS |
| `p113_control_flow.binding_context_formats` / `activation` | `/9` only | `/9`, `explicit_context_format_9_only` | PASS |
| `p113_control_flow` false flags | `trace_evaluation_by_cube`, `condition_evaluation_by_cube`, `evaluation_performed_by_cube` = `false` | `false` ×3 | PASS |
| `p113_control_flow.additional_diagnostics` | — | CONTROL_FLOW_INVALID, CONTROL_FLOW_UNSUPPORTED, FLOW_UNDECLARED, TOKEN_POSITION_UNDECLARED | noted |
| `domains.P2.plan_views.tools` | `cube_plan_source`, `cube_plan_views`, `cube_plan_check` | same | PASS |
| `domains.P2.plan_views.remote_available` / `transport` | `true` / `streamable_http` | same | PASS |
| `domains.P2.plan_views.printers` | vpmigration, vpsequence, vpaxes, vpcells, vpinstances | same five (as object keys) | PASS |
| `mcp.tools` and tools offered by the connector | the ten gateway tools | ten, same names | PASS |
| `p16_instantiation` … `p112_coverage_instance`, `deployment.remote_status` | unchanged | unchanged (`G5_PROOF_NOT_PRODUCTION_AUTHORIZED`) | PASS |

The gateway version `0.2.0-proof` (`/health`, server info) is not visible to the host through the connector; it was confirmed by the scripted run (`gateway_health_version_as_expected: true`).

## 2. `cube_validate`

Payload digests compare the remote result with `transport` set to the local value (W-2).

| ID | Context | Expected | Observed (remote) | Payload SHA-256 | Result |
|---|---|---|---|---|---|
| V-KF-08 | `/8`, `p113-cf-08`, `onFlow` | PASS, no codes | PASS, no diagnostics | `68f5a3dc…` = expected | PASS |
| V-BPMN-01-routed-to-ship-v9 | `/9`, `p113-cf-06`, `routedTo` → `bpmn:ship` | FAIL · FLOW_UNDECLARED | FAIL · FLOW_UNDECLARED ("'bpmn:ship' is not an outgoing target of exclusive gateway 'bpmn:xor'") | `23cb42ea…` = expected | PASS |
| V-BPMN-01-token-position-v9 | `/9`, `p113-cf-09`, routing token without `at_gateway` | UNRESOLVED · TOKEN_POSITION_UNDECLARED | same | `1bf19a24…` = expected | PASS |

The two `/9` results carry `control_flow_profile: P1.13/control-flow-profile-v1`, `trace_evaluation_by_cube: false` and `condition_evaluation_by_cube: false`; all three carry `epistemic_warrant`, `current_authority` and `canonical_admission` = `NOT_EVALUATED` and `transport: remote_mcp_streamable_http`.

**Transfer check:** for all three, `declared_context_sha256` equals the digest of the context in `r5_calls.py` (3/3).

## 3. Plan chains

| ID | Step | Expected | Observed (remote) | Result |
|---|---|---|---|---|
| P-K08-sequence | `cube_plan_views` (cube.sequence, standard, partition trigger) | ok; profile `P2-VP-SEQUENCE/0.8.0`; SVG `414dda5a…`, `14e60117…`, `c7932a0c…`, `ef2c4489…`, `3fcdad45…` | same; report PASS, coverage COMPLETE 34/34, warning `VP08_SEQUENCE_CONTINUED` (panel-04) | PASS |
| | `cube_plan_check` | PASS, payload `e62a4202…` | PASS, payload `e62a4202…` | PASS |
| P-I-14 | `cube_plan_source` (vpinstances, `plan_id` null, trace and one record) | ok, payload `395fac1a…` | ok, payload `395fac1a…` | PASS |
| | `cube_plan_views` (cube.instances) | ok; profile `P2-VP-INSTANCES/0.12.0`; SVG `799b849b…` | same; 1 violation mark, 5 invariants passed | PASS |
| | `cube_plan_check` | PASS, payload `36f82431…` | PASS (INPUT_DIGEST, DETERMINISTIC_RERENDER, REPORT_MATCH), payload `36f82431…` | PASS |
| P-ARG-plan-id | `cube_plan_source` with `plan_id: "mp-x"` | `isError`, `P3_PLAN_ARGUMENT_INVALID`, payload `f53733db…` | same (stage `input`, `files_written: false`) | PASS |

For the two `cube_plan_views` steps (123 KiB and 41 KiB) the host could not move the full payload byte-exactly into the checkout, so the payload digest itself (`e3b3b969…`, `61e15d5c…`) was not recomputed by the host. It is covered by: every SVG and panel-input digest equal to the expectation, and the unchanged result passed back to `cube_plan_check`, which re-renders remotely and returns the expected PASS payload. The scripted run matched both payload digests.

Before the run, the local functions reproduced all expected digests of the plan chains in the checkout (`plan_views.plan_source/plan_views/plan_check`).

## 4. Result

**PASS.** 7 of 7 host-subset calls as expected (1 discovery, 3 `cube_validate`, 3 plan chains with 6 steps); no deviation. Control flow `/9` and the three plan tools are available through the remote connector; the release stays `remote_proof_not_accepted` (unchanged).

## 5. Not covered

- The other 81 calls: scripted live acceptance (`scripts/r5_remote_acceptance.py`, runs 1–4). Run 4 matched 87 of 88; `P-K07-flow` ends with `G5_CORE_UNAVAILABLE` (`exceededCpu`), the documented R5 limit (spec §10, `G5_R5_CORE_CPU_EVENT.json`).
- Arguments too large to pass by hand in a host (CL-3), e.g. the I-22 context and `cube_plan_check` on I-22.
- Visual check (D-8: outputs byte-identical to the checked local ones).
- Independent second host (only Claude was used).
