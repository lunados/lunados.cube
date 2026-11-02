# P1.13 — Control Flow Profile and Trace Conformance · Acceptance specification

**Status:** SPECIFIED. MILE-008 decisions D-1…D-8 apply (2026-11-02); detail questions Q-1…Q-10 resolved 2026-11-02 (all as proposed). Not implemented.
**Numbering:** New profile `P1.13/control-flow-profile-v1`, context `aiaeao.cube.binding-context/9`, directory `P1/control-flow-profile-v1/`. Builds on P1.12 (`binding-context/8`). P1.7 stays reserved.
**Basis:** Morphology v9.4 (no change); P1.10.1 D-2 and P1.12 D-3 (incomplete declaration → UNRESOLVED, never FAIL); P1.12 coverage, population rules and typed instances; MILE-002 gap ledger G-07 (control-flow and transition semantics) and reports BPMN-01, BPMN-02, BPMN-03; BPMN 2.0.2 §10.6.2, §13.4.1, §13.4.2 (local PDF referenced by hash in the MILE-002 source lock); MILE-008 decisions (`docs/02-Milestones/MILE-008-control-flow.md`); check cases `docs/09-Research/control-flow/CHECK-CASES.json` (`aefe6aa`, fixed before this specification).
**Motivation:** Findings of the baseline run (TASK-048, all synthetic):

| Finding | Effect today |
|---|---|
| A routing to an element that is not a target of the gateway passes | `routedTo(i1/tok-route, ship)`: PASS |
| A token on an undeclared flow passes | `onFlow(i1/tok-stock, f-ghost)`: PASS |
| Two contradictory routings of one token pass one by one | BPMN-01 other branch: PASS; the exclusivity check is not executable |
| Condition order, default and the inputs of a join are not part of any contract | BPMN-01 exclusivity, BPMN-02 synchronisation: not executable |

P1.13 adds a **declared control flow** (gateways, flows, condition order, default) and binds trace statements to it. P1 checks the declaration and single statements; the evaluation of a trace per instance belongs to the LIB entry `analyze.trace-conformance/v1` (D-4, §6). Nothing here executes a process or evaluates a condition (D-5).

## 0. Scope

| In scope | Out of scope |
|---|---|
| Exclusive and parallel gateways, split and join (D-2) | Inclusive, event-based, complex gateways (declared: UNRESOLVED, not judged) |
| Flow binding of routing and on-flow statements | Condition expressions and their evaluation |
| Trace conformance per instance in LIB: exclusivity, condition order (from recorded outcomes), join, split, merge | Instance completion, compensation, error events, engine logs |
| Local G4 and discovery (D-7) | G5; rendering (VR-12) |

## 1. Design summary

1. **New context version** `aiaeao.cube.binding-context/9`, a strict superset of `/8` with no new required fields. `/9` activates P1.13 rules; `/1…/8` stay byte-identical. The validator projects `/9` to `/8`, runs P1.12 unchanged and adds the control-flow checks (Q-10).
2. **Control flow (CF).** `control_flow.gateways[]` declares each gateway with `type`, `incoming` flows and `outgoing` flows; an outgoing flow names its `target`, and at an exclusive gateway optionally an `order` and a `condition_ref`, or `default: true`. Gateways, flows and targets are declared referents (Q-1, Q-2).
3. **Trace binding (TB).** A token referent may carry `at_gateway` (Q-3). Predicate contracts mark their role with `control_flow_role` ∈ {`routing`, `on_flow`} (Q-4). A routing statement must lead to a target of an outgoing flow of the token's gateway; an on-flow statement must name a declared flow.
4. **Trace conformance (TC, LIB).** `analyze.trace-conformance/v1` reads the declared control flow, the trace (tokens with instance, position, routing, flow and recorded condition outcomes), the coverage declarations and one claim, and returns a typed result per instance (§6).
5. **Diagnostics** follow P1.10/P1.12: context checks after all P1.12 checks, JSON Pointers into `control_flow/gateways/i` or the referent; FAIL outranks UNRESOLVED.

### 1.1 Shape (illustrative, synthetic)

```json
{
  "format": "aiaeao.cube.binding-context/9",
  "referents": [
    {"ref": "bpmn:xor", "concept_id": "Y:identified-object:work-item", "home": "Y", "layers": ["α"], "provenance_status": "declared_unverified"},
    {"ref": "bpmn:f-manual", "concept_id": "Y:identified-object:work-item", "home": "Y", "layers": ["α"], "provenance_status": "declared_unverified"},
    {"ref": "bpmn:i1/tok-route", "concept_id": "Y:resource-object:evidence", "home": "Y", "layers": ["α"], "provenance_status": "declared_unverified",
     "instance_ref": "bpmn:i1", "at_gateway": "bpmn:xor"}
  ],
  "predicate_contracts": [
    {"predicate_id": "routedTo", "subject_concept_ids": ["Y:resource-object:evidence"], "object_concept_ids": ["Y:identified-object:work-item"],
     "direction": "subject_to_object", "control_flow_role": "routing"}
  ],
  "control_flow": {"gateways": [
    {"gateway": "bpmn:xor", "type": "exclusive", "incoming": ["bpmn:f-checked"],
     "outgoing": [{"flow": "bpmn:f-manual", "target": "bpmn:approve-manual", "order": 1, "condition_ref": "model:bpmn-order#amount>1000"},
                  {"flow": "bpmn:f-auto", "target": "bpmn:approve-auto", "default": true}]}
  ]}
}
```

→ `rel("routedTo", Y:α:Evidence["bpmn:i1/tok-route"], Y:α:WorkItem["bpmn:ship"])`: FAIL · `P1_FLOW_UNDECLARED` (ship is no target of an outgoing flow of `bpmn:xor`).

## 2. Status and diagnostic rules (P1)

| Situation | Status | Diagnostic |
|---|---|---|
| Exclusive gateway with more than one default, duplicate or missing `order` among conditional flows, or `order` on the default | FAIL | `P1_CONTROL_FLOW_INVALID` (new) |
| Parallel gateway with `default`, `order` or `condition_ref` | FAIL | `P1_CONTROL_FLOW_INVALID` |
| A flow outgoing from two gateways, or incoming to two gateways | FAIL | `P1_CONTROL_FLOW_INVALID` |
| Gateway `type` outside {`exclusive`, `parallel`} | UNRESOLVED | `P1_CONTROL_FLOW_UNSUPPORTED` (new) |
| Routing statement to an element that is not a target of an outgoing flow of the token's `at_gateway`, or `at_gateway` not an exclusive gateway | FAIL | `P1_FLOW_UNDECLARED` (new) |
| On-flow statement naming a referent that is no declared flow | FAIL | `P1_FLOW_UNDECLARED` |
| Routing statement from a token without `at_gateway` | UNRESOLVED | `P1_TOKEN_POSITION_UNDECLARED` (new) |
| Gateway, flow or target not a declared referent; `at_gateway` not a declared gateway | UNRESOLVED | `P1_BINDING_CONTEXT_REQUIRED` (existing) |
| Malformed `control_flow` (schema) | MCP error | `P1_MCP_CONFIG_INVALID` (existing) |
| Any P1.13 field inside a `/1…/8` context | MCP error | `P1_MCP_CONFIG_INVALID` (existing) |
| All P1.12 rows | unchanged | unchanged |

## 3. Rules in detail

**Control flow (CF)**
- CF-1: `gateway`, every `incoming` flow, every outgoing `flow` and `target` resolve to declared referents.
- CF-2: Exclusive: at most one outgoing flow has `default: true`; every other outgoing flow carries an integer `order` ≥ 1, unique within the gateway; the default carries no `order`. `condition_ref` is an optional pointer to where the condition is written; P1 never reads it.
- CF-3: Parallel: no `default`, `order` or `condition_ref`.
- CF-4: A flow is outgoing from at most one gateway and incoming to at most one gateway.
- CF-5: An unsupported `type` is reported once per gateway as UNRESOLVED; its flows still count as declared for TB-2.

**Trace binding (TB)**
- TB-1: A statement whose predicate has `control_flow_role: routing` has a token as subject. The token's `at_gateway` must name an exclusive gateway and the object must be the `target` of one of its outgoing flows.
- TB-2: A statement whose predicate has `control_flow_role: on_flow` must name, as object, a flow that is incoming or outgoing at a declared gateway.
- TB-3: Predicates without `control_flow_role` are unaffected. P1.12 instance and coverage checks apply unchanged.

## 4. Acceptance criteria

| AC | Requirement | Evidence |
|---|---|---|
| P1.13-01 | No change to Morphology, P0, P1.1…P1.12 artifacts; `SHA256SUMS` diff empty | file diff |
| P1.13-02 | `/1…/8` byte-identical, including all previous vector suites and goldens | regression suite |
| P1.13-03 | `context-v9.schema.json` strict superset of `/8` | schema tests |
| P1.13-04 | CF-1…CF-5, TB-1…TB-3 | vectors KF-01…KF-09 (§5) |
| P1.13-05 | Every row in §2 yields exactly the stated status and code | one test per row |
| P1.13-06 | Independent oracle for KF-01…KF-09, transcribed from `CHECK-CASES.json` before code | `oracles/independent_kf01_kf09.json` |
| P1.13-07 | LIB entry of §6 reproduces CF-11…CF-29 with an independent oracle committed before the evaluator | lunados.lib entry cases |
| P1.13-08 | Local G4: `cube_validate` accepts `/9`; local discovery lists `binding-context/9` with entry profile `P1.13/control-flow-profile-v1` | adapter test |
| P1.13-09 | Re-run of the BPMN cases as `/9` with expectations committed before the run | research run |
| P1.13-10 | Synthetic golden with control flow, trace binding and coverage, no client data | `fixtures/golden_control_flow.json` |

## 5. Vectors (from the check cases)

| ID | Case | P1 (`cube_validate`, `/9`) |
|---|---|---|
| KF-01 | CF-01 base model, routing to approve-manual | PASS |
| KF-02 | CF-02 two defaults | FAIL · `CONTROL_FLOW_INVALID` |
| KF-03 | CF-03 duplicate order | FAIL · `CONTROL_FLOW_INVALID` |
| KF-04 | CF-04 default at a parallel gateway | FAIL · `CONTROL_FLOW_INVALID` |
| KF-05 | CF-05 inclusive gateway | UNRESOLVED · `CONTROL_FLOW_UNSUPPORTED` |
| KF-06 | CF-06 routing to ship | FAIL · `FLOW_UNDECLARED` |
| KF-07 | CF-07 token on f-ghost | FAIL · `FLOW_UNDECLARED` |
| KF-08 | CF-08 `/8` without control flow (regression) | PASS |
| KF-09 | CF-09 routing from a token without `at_gateway` | UNRESOLVED · `TOKEN_POSITION_UNDECLARED` |

The LIB cases CF-11…CF-29 become the cases of `analyze.trace-conformance/v1` (§6), unchanged.

## 6. LIB entry `analyze.trace-conformance/v1`

**Inputs:** `control_flow` (as in §1), `trace` (tokens: `token`, `instance`, optional `at`, `routed_to`, `on_flow`, `conditions` {flow → true/false}), `coverage` (P1.12 declarations), `claim` (`check` ∈ {`exclusive`, `condition_order`, `join`, `split`, `merge`}, `gateway`, `instance`). **Output:** `aiaeao.trace-conformance-result/v1` with `status`, `value`, details and `missing_scope` when uncovered. Pure, declarative, no condition evaluation.

| Check | Covered when (Q-7) | PASS | FAIL | UNRESOLVED |
|---|---|---|---|---|
| `exclusive` | outgoing `routedTo` of every token at the gateway in the instance | `exclusive_one_path` | `exclusive_two_paths`, `exclusive_no_path` | `coverage_undeclared` |
| `condition_order` | as `exclusive` | `condition_first_true`, `default_without_true` | `default_with_true_condition`, `not_first_true` | `coverage_undeclared`, `conditions_unrecorded` |
| `join` | incoming `onFlow` of every incoming and outgoing flow, for the instance | `join_complete`, `join_waiting` | `join_incomplete` | `coverage_undeclared` |
| `split` | as `join` | `split_complete` | `split_incomplete` | `coverage_undeclared` |
| `merge` | as `join` | `merge_pass_through` | `merge_mismatch` | `coverage_undeclared` |

- TC-1 (exclusive): each token at the gateway is one activation; it must have exactly one routing.
- TC-2 (condition order): walk the conditional flows by `order`; an unknown outcome before the first true one → `conditions_unrecorded`; the first true flow must be taken; if all are recorded false, the default must be taken.
- TC-3 (join): an activation is a token on an outgoing flow; each activation needs one token per incoming flow of the same instance; tokens of other instances are listed as `foreign` and never count; no activation with missing inputs → `join_waiting` listing them; surplus tokens are counted in `excess`, never FAIL (D-6).
- TC-4 (split): each token on the incoming flow is one activation and needs one token on every outgoing flow.
- TC-5 (merge): every incoming token yields exactly one outgoing token.
- TC-6: several activations of one check → FAIL if any fails, else UNRESOLVED if any is unresolved, else PASS; details per activation.

## 7. Detail questions (resolved 2026-11-02, all as proposed)

| ID | Question | Decision | Reason |
|---|---|---|---|
| **Q-1** | What is a flow? | A **declared referent** named in `control_flow`; the profile does not fix its concept | on-flow statements and coverage need flows as referents (as in P1.12 K-14) |
| **Q-2** | What is a gateway? | Also a declared referent, concept free | tokens point at it (`at_gateway`) |
| **Q-3** | Where is the token's position? | Optional referent field **`at_gateway`**, like `instance_ref` | the routing statement itself does not name the gateway |
| **Q-4** | Which predicates are bound? | Predicate contract field **`control_flow_role`** ∈ {`routing`, `on_flow`}; others unaffected | no hard-coded predicate names |
| **Q-5** | Codes? | `P1_CONTROL_FLOW_INVALID` (FAIL), `P1_CONTROL_FLOW_UNSUPPORTED` (UNRESOLVED), `P1_FLOW_UNDECLARED` (FAIL), `P1_TOKEN_POSITION_UNDECLARED` (UNRESOLVED) | the working titles of the check cases |
| **Q-6** | Where are condition outcomes recorded? | **Only in the LIB trace input** (`conditions` per routing token); the Cube context never carries condition values | the Cube stays free of runtime values |
| **Q-7** | Coverage for LIB checks? | **Reuse P1.12 declarations**: outgoing `routedTo` per token, incoming `onFlow` per flow and instance; uncovered → UNRESOLVED with the missing scope | one notion of "surveyed" |
| **Q-8** | Is a waiting join a violation? | **No**: `join_waiting` is PASS and lists the missing inputs | it answers "why does it wait?", nothing was violated |
| **Q-9** | Several activations? | Per activation; FAIL > UNRESOLVED > PASS overall, details per activation (TC-6) | an instance can pass a gateway more than once |
| **Q-10** | Relation to P1.12? | `/9` strict superset of `/8`; validator projects `/9` → `/8`, runs P1.12 unchanged, then CF and TB | same pattern as P1.12 over P1.11 |

## 8. Precisions found in review (TASK-052)

These close two gaps between §3 and the check cases; both implementations (P1.13 and the LIB entry) already behave this way.

- **CF-2a:** An exclusive gateway with exactly one outgoing flow that carries neither `order`, `condition_ref` nor `default` is valid (an exclusive merge, as `bpmn:merge` in the check cases). `order` is required only when a gateway has more than one outgoing flow or the flow carries `condition_ref`.
- **CF-2b:** The default flow carries neither `order` nor `condition_ref`.
