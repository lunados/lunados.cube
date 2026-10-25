# P1.8 — Declared Simulation Profile · Acceptance specification

**Status:** SPECIFIED, decisions D-1…D-5 resolved 2026-10-25 — ready for implementation.
**Numbering:** P1.7 remains reserved for the Principal → Authority holder chain (P1.6 D-3) and the R-03 profile/concept observation (G5 R4 report, Annex A.1). P1.8 does not depend on P1.7.
**Basis:** Morphology v9.4 §§3.1 (F, M), 5.14, 6.2.5, 6.3.2, 7.12–7.13; P1.4 method typing (P1.4-08, P1.4-11); P1.6 instantiation profile; EXP-024 (Cube readiness vs local evaluation).
**Motivation:** Experiments that cannot be *executed* by the Cube (EXP-007, 009-D, 010, 013, 024 and parts of 011/012) should still be *described* in the Cube domain: as a declared method, a declared world and a declared evaluation result. Then the Cube reference can host them as reference cases, a separate evaluator runs them, and the Functions Library holds the method contracts. Three capabilities are missing today:

1. **Method return typing.** An `application` has no result type, so `rel(…, method(…), …)` stays `P1_PREDICATE_PROFILE_MISSING` ("nested expression return types are undefined in P1.1").
2. **Scenario / world container.** Nothing declares that a set of referents forms one closed simulated world in a non-operative mode.
3. **Evaluator descriptor and result witness.** Nothing declares *who* evaluates a method in a scenario, what it returns, and which witness backs the returned result.

## 0. Scope

| In scope | Out of scope |
|---|---|
| Declared return types for `method_contracts` and typed use of an `application` as a relation operand or slot target | Return types for nested `rel(…)` (path → predicate inference stays forbidden) |
| A declared, closed scenario with mode `simulation` or `replay` | Mode `operative`; any real effect; any change to M qualifier semantics (P1.4-11 stays) |
| Declared evaluators and evaluation records with typed outputs and a witness pointer | Running a simulation, verifying digests or witness truth, scoring results |
| Method contracts carrying an optional pinned Functions Library reference | A Functions Library service, fetching or resolving library entries |
| Unchanged `cube_validate` signature, local MCP and G5 Remote | New MCP tools, HTTP API, P2 auto-mapping |

## 1. Design summary

1. **New context version** `aiaeao.cube.binding-context/3`, a strict superset of /2 with three optional additions: method return fields, `scenarios`, and `evaluators` + `evaluation_records`, plus an optional top-level `evaluation_frame`. Contexts in /1 and /2 behave byte-identically to today.
2. **Return typing** applies only to `application` nodes whose method contract declares `return_concept_ids`. The application then counts as a typed **relation operand** for predicate typing (P1.4). P1.6 slots hold referent IDs only, so an application can never be a slot target. Applications as arguments of other applications stay untyped in P1.8. Return typing does **not** create or bind a referent.
3. **Scenario:** a named, scoped, closed world. If `evaluation_frame.scenario_ref` is set, every reference in the input must be a member of that scenario's `world_refs`, and every applied method must be `pure_declarative`.
4. **Evaluation record:** describes that a declared evaluator ran (or will run) a declared method in a declared scenario and produced declared output referents, backed by a witness pointer. The Cube checks only structure, typing and the presence of the witness. Evaluation results are never evaluated, verified or promoted.
5. **Library pin:** `method_contracts[].library_ref = {library_id, entry_id, revision, sha256}` records where the contract comes from. P1.8 checks only the format of the pin. It never fetches the entry.

### 1.1 Shape (illustrative)

```json
{
  "format": "aiaeao.cube.binding-context/3",
  "reference_version": "v9.4",
  "evaluation_frame": {"scenario_ref": "sc-010-central"},
  "method_contracts": [{
    "method_id": "verify.qualified-reuse/v1", "revision": "lib:v1", "scope": "s", "origin": "illustrative_fixture",
    "argument_min": 1, "argument_max": 1, "argument_concept_ids": ["Y:resource-object:artifact"],
    "effect_class": "pure_declarative",
    "return_concept_ids": ["Y:resource-object:evidence"], "return_cardinality": "one",
    "library_ref": {"library_id": "aiaeao.functions", "entry_id": "verify.qualified_reuse", "revision": "v1",
                    "sha256": "<64 hex>"}
  }],
  "scenarios": [{
    "scenario_id": "sc-010-central", "revision": "exp010:v1", "scope": "s", "origin": "illustrative_fixture",
    "mode": "simulation", "world_refs": ["a1", "ev-out", "claim1"],
    "parameters": {"cost_profile": "central", "seed": 8},
    "assumption_refs": ["claim1"], "method_ids": ["verify.qualified-reuse/v1"]
  }],
  "evaluators": [{
    "evaluator_id": "eval:exp010-python", "revision": "v1", "scope": "s", "origin": "illustrative_fixture",
    "kind": "local_script", "method_ids": ["verify.qualified-reuse/v1"],
    "output_concept_ids": ["Y:resource-object:evidence", "Y:resource-object:artifact"]
  }],
  "evaluation_records": [{
    "record_id": "run-1", "scenario_ref": "sc-010-central", "evaluator_ref": "eval:exp010-python",
    "method_id": "verify.qualified-reuse/v1", "input_digest": "sha256:<64 hex>",
    "output_refs": ["ev-out"], "witness_ref": "witness:exp010/RESULTS.json", "status": "declared"
  }]
}
```

## 2. Status and diagnostic rules

| Situation | Status | Diagnostic (new unless noted) |
|---|---|---|
| `application` used as operand or slot target, contract without `return_concept_ids` | UNRESOLVED | `P1_METHOD_RETURN_UNDECLARED` |
| Declared return type not admitted by the predicate signature, or `return_cardinality = many` used as a relation operand | FAIL | `P1_METHOD_RETURN_TYPE` |
| `rel(…)` used as operand (nested relation) | UNRESOLVED | `P1_PREDICATE_PROFILE_MISSING` (existing, unchanged) |
| `evaluation_frame.scenario_ref` names no declared scenario | UNRESOLVED | `P1_SCENARIO_REQUIRED` |
| Reference in input not in the active scenario's `world_refs` | FAIL | `P1_SCENARIO_WORLD_VIOLATION` |
| Scenario `mode` not in {simulation, replay}, or a method in the frame is not `pure_declarative`, or a method is not listed in `method_ids` | FAIL | `P1_SCENARIO_MODE` |
| Evaluation record names an undeclared evaluator, or an evaluator not declared for that method | UNRESOLVED | `P1_EVALUATOR_UNDECLARED` |
| Output referent concept not in evaluator `output_concept_ids`, or an output typed as an X judgment endpoint (Conclusion, Satisfaction, Completion, Admission, Authority) | FAIL | `P1_EVALUATION_OUTPUT_TYPE` |
| Evaluation record without `witness_ref` | UNRESOLVED | `P1_EVALUATION_WITNESS_MISSING` |
| `input_digest` malformed, or record `scenario_ref`/`method_id` inconsistent with scenario | FAIL | `P1_EVALUATION_RECORD_INCONSISTENT` |
| Malformed `library_ref` (missing field, non-hex sha256) | invalid input (MCP error) | `P1_MCP_CONFIG_INVALID` (existing) |
| /3-only fields inside a /1 or /2 context | invalid input (MCP error) | `P1_MCP_CONFIG_INVALID` (existing) |

Precedence follows P1.4-14 and P1.6: FAIL outranks UNRESOLVED, and NOT_EVALUATED is never PASS. Scenario checks run after referent binding and before predicate typing. Evaluation-record checks run only when `evaluation_records` is present.

## 3. Rules in detail

### 3.1 Return typing (MR)

- MR-1: `return_concept_ids` is a non-empty list of instantiable concept IDs. X dimensions and relation arrows are rejected (config error).
- MR-2: `return_cardinality` ∈ {one, many}. A relation operand requires `one`. All declared return concepts must be admitted by the predicate side (sound subset check, no "any of").
- MR-3: The return type is used for typing only. It does not create a referent, does not bind, and does not satisfy `referent_binding`.
- MR-4: A method whose return type is an X judgment endpoint (Conclusion, Satisfaction, Completion, Admission, Authority) is rejected (config error). A method may produce Evidence, Artifact, Content, Annotation or X Result, but never a judgment.
- MR-5: Return typing never makes a nested `rel` typed. "No predicate inference from a path" (relations.json `non_implications`) stays intact.

### 3.2 Scenario (SC)

- SC-1: A scenario is closed: membership is only what `world_refs` lists, and every member must be a declared referent.
- SC-2: `mode` ∈ {simulation, replay}. `operative` is out of scope for P1.8 and fails.
- SC-3: Inside an `evaluation_frame`, every applied method must be `pure_declarative` **and** listed in the scenario's `method_ids`.
- SC-4: `parameters` are JSON scalars only. They are recorded, not interpreted.
- SC-5: `assumption_refs` must point to Y Annotation members of the world, so an assumption is an explicit claim and not hidden configuration.
- SC-6: A scenario is not an Event and not a Thread. It neither admits nor records anything canonically.

### 3.3 Evaluator and evaluation record (EV)

- EV-1: `kind` ∈ {local_script, external_simulator, proof_tool, human_review}. The kind is descriptive only.
- EV-2: An evaluator may only be referenced for the methods it lists.
- EV-3: Outputs must be declared members of the scenario world, with concepts in `output_concept_ids`. X judgment endpoints are never allowed (see MR-4).
- EV-3a (D-4): An output may be an `X:endpoint:result`. It must then be fully instantiated under P1.6 (binding-context/3 inherits /2 instantiation profiles), with `action_ref` pointing to an X Action that represents the evaluation run and is itself a world member. All P1.6 diagnostics apply unchanged, e.g. a missing `action_ref` stays `P1_INSTANTIATION_SLOT_MISSING`.
- EV-4: A `witness_ref` is required. Its presence satisfies the declaration shape only, `witness_truth = NOT_EVALUATED`.
- EV-5: `input_digest` has the form `sha256:<64 lowercase hex>`. The Cube never recomputes or compares it.
- EV-6: `status` ∈ {declared, unresolved}. There is no `verified` or `passed` value.

### 3.4 Report boundary

- The P1 report schema stays unchanged. The adapter envelope adds `simulation_profile: "P1.8/simulation-profile-v1"` (only for /3) and `evaluation_performed_by_cube: false`.
- `canonical_admission`, `current_authority`, `epistemic_warrant` stay `NOT_EVALUATED`, and `source_warrant` stays `declared_unverified`, also for complete scenarios and records.

## 4. Acceptance criteria

| AC | Requirement | Evidence (to be produced) |
|---|---|---|
| P1.8-01 | No change to Morphology v9.4, P0, P1.1 frozen files, report.schema.json, P1.6 artifacts | baseline hash snapshot reused, `SHA256SUMS.txt` diff empty |
| P1.8-02 | /1 and /2 behaviour byte-identical: full P1.4 suite, F01–F25, R-01…R-13 | regression suite, identical `input_sha256`/`declared_context_sha256` |
| P1.8-03 | `context-v3.schema.json` published; strict superset of /2; /3 fields rejected in /1 and /2 | schema tests, S-14 |
| P1.8-04 | Return typing per MR-1…MR-5, including rejection of judgment return types | tests S-01…S-04 + config tests |
| P1.8-05 | Scenario rules SC-1…SC-6 | tests S-05…S-08 |
| P1.8-06 | Evaluator and record rules EV-1…EV-6 incl. EV-3a | tests S-09…S-13, S-16, S-17 |
| P1.8-07 | Every row in §2 yields exactly the stated status and code | one test per row |
| P1.8-08 | Library pin format checked, never resolved; no network access from P1 | test with unreachable `library_id` still PASS on format |
| P1.8-09 | Non-promotion (§3.4) asserted in every positive test | assertion in every PASS test |
| P1.8-10 | Deterministic JSON-Pointer diagnostics into `scenarios[i]`, `evaluation_records[i]`, `method_contracts[i]` | snapshot tests |
| P1.8-11 | New codes registered in a P1.8 `DIAGNOSTIC_EXTENSION.json` and `RULE_COVERAGE.json` with Morphology references | file diff |
| P1.8-12 | Independent oracle for S-01…S-17, transcribed before execution | `oracles/independent_s01_s17.json` |
| P1.8-13 | Local MCP and G5 Remote return identical reports for S-01…S-17 | adapter parity test |
| P1.8-14 | **Observable deploy:** `cube_discover_surface` gains a `p18_simulation` descriptor **and** the remote version string is bumped (`P3-MCP-REMOTE/0.2.0-proof` or later) | live discover check |
| P1.8-15 | Two golden reference cases materialised: one from EXP-010 (method + scenario + record) and one from EXP-024 Charge 3 | `fixtures/golden_exp010.json`, `fixtures/golden_exp024.json`, both PASS |

`PASS` in this matrix means the listed test ran successfully. It does not mean a simulation result is correct, reproducible or authorised.

## 5. Alignment vectors (exit check)

Expected statuses fixed **before** implementation:

| ID | Case | Expected overall |
|---|---|---|
| S-01 | `rel("supports", verify.qualified-reuse/v1(Y:α:Artifact["a1"]), Y:α:Annotation["claim1"])`, return Evidence, `supports` Evidence → Annotation | PASS |
| S-02 | Same, contract without `return_concept_ids` | UNRESOLVED · `METHOD_RETURN_UNDECLARED` |
| S-03 | Same, return type Annotation (not admitted as `supports` subject) | FAIL · `METHOD_RETURN_TYPE` |
| S-04 | `rel("supports", rel(…), …)` with /3 | UNRESOLVED · `PREDICATE_PROFILE_MISSING` (regression) |
| S-05 | S-01 inside `evaluation_frame` of a `simulation` scenario, all refs in world | PASS |
| S-06 | S-05 with `a1` missing from `world_refs` | FAIL · `SCENARIO_WORLD_VIOLATION` |
| S-07 | S-05 with method `effect_class = effectful_declared` | FAIL · `SCENARIO_MODE` |
| S-08 | S-05 with scenario `mode = operative` | FAIL · `SCENARIO_MODE` |
| S-09 | S-05 + complete evaluation record (evaluator covers method, output Evidence, witness) | PASS, `evaluation_performed_by_cube: false` |
| S-10 | S-09 without `witness_ref` | UNRESOLVED · `EVALUATION_WITNESS_MISSING` |
| S-11 | S-09 with an evaluator not declared for the method | UNRESOLVED · `EVALUATOR_UNDECLARED` |
| S-12 | S-09 with output referent typed `X:endpoint:conclusion` | FAIL · `EVALUATION_OUTPUT_TYPE` |
| S-13 | S-09 with `input_digest = "md5:…"` | FAIL · `EVALUATION_RECORD_INCONSISTENT` |
| S-14 | /3 `scenarios` field inside a /2 context | MCP error · `P1_MCP_CONFIG_INVALID` |
| S-15 | `evaluation_frame.scenario_ref` pointing to an undeclared scenario | UNRESOLVED · `SCENARIO_REQUIRED` |
| S-16 | S-09 with output `X:endpoint:result` fully instantiated via P1.6 (`action_ref` → X Action "evaluation run", performed by the evaluator Actor) | PASS |
| S-17 | S-16 with the Result lacking `action_ref` | UNRESOLVED · `P1_INSTANTIATION_SLOT_MISSING` |

Not expected to change, stated explicitly so that no improvement is over-read: typing of nested `rel` (S-04), 011-A associativity, any execution or correctness of EXP-007/009-D/010/013 results, RCP effect probes, external gates of EXP-017/018/022.

## 6. Decisions (resolved 2026-10-25)

| Decision | Resolution | Consequence |
|---|---|---|
| D-1 Numbering | **P1.8.** P1.7 stays reserved for the Principal → Authority holder chain. | Independent of P1.7. Folder `P1/simulation-profile-v1/`. |
| D-2 Frame vs. M qualifier | **Context-level `evaluation_frame`.** `@M` stays presentation-only (P1.4-11). | No change to qualifier semantics or qualification profiles. |
| D-3 Library pin | **Optional.** `library_ref` is format-checked when present, never resolved. | Simulations may exist before the Functions Library does. |
| D-4 Result as X Result | **Yes, allowed.** An output may be a P1.6-instantiated `X:endpoint:result` (EV-3a). | Adds S-16, S-17. P1.8 depends on the P1.6 runtime. |
| D-5 Replay semantics | **No prior record required in P1.8.** `replay` is a declared mode only. | Replay-against-record is a P1.9 candidate. |
