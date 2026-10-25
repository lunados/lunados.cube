# P1.6 — X-Endpoint Instantiation Profile · Acceptance specification

**Status:** V1.1 CONTRACT CANDIDATE — not implemented or deployed. Based on draft 2026-10-25.
**Scope of this delivery:** Specification, additive /2 schemas, reference vocabulary and schema-preflight only; runtime validator acceptance remains OPEN.
**Basis:** Morphology v9.4 §§2.9 (D.3/D.5), 3.12, 6.2.1–6.2.5, 7.37; P1.3 contract notes §3; P1.4 acceptance matrix.
**Motivation:** In P1-VC/1.0.0 every X Key-Pair endpoint resolves to `requires_binding_profile` and yields `P1_INSTANTIATION_PROFILE_REQUIRED` (UNRESOLVED). binding-context/1 defines no such profile. This blocks the structural share of EXP-011 (Evidence → supports → Conclusion), EXP-014 (M02, M04, M11) and the preflight of EXP-019-RCP (Authority, Admission). Probe evidence: Cube alignment run 2026-10-25 against G5 Remote.

## 0. Scope

| In scope | Out of scope |
|---|---|
| The 10 X endpoints: Perception, Conclusion, Authority, Admission, Expectation, Satisfaction, Delegation, Completion, Action, Result | The 7 Z zones (`Z:zone:*`), which keep `P1_INSTANTIATION_PROFILE_REQUIRED` (separate AC later) |
| A declarative, fixture-scoped instantiation profile carried in the caller context | Any truth, Authority, Admission, warrant or effect evaluation |
| New P1 diagnostics for slot presence and slot typing | Changes to Morphology v9.4, P0 assets, P1.1 frozen files or report.schema.json |
| Local MCP and G5 Remote through the unchanged `cube_validate` signature | New MCP tools, HTTP API, P2 mapping |

## 1. Design summary

1. **New context version** `aiaeao.cube.binding-context/2`: an additive successor of /1 with one optional array `instantiation_profiles` and two permitted referent properties (`instantiation_profile_ref`, `slots`). The `format` tag changes to /2; the /1 parser, files and behaviour remain unchanged. “Superset” concerns expressible declarations, not acceptance of identical byte strings with different format tags.
2. An **instantiation profile** declares, for one X endpoint concept, which typed **slots** a referent of that concept must fill with other referents declared in the same context.
3. A referent whose `concept_id` is an X endpoint is bindable only if (a) a profile for that concept is in scope **and** (b) the referent declares a `slots` object that satisfies the profile.
4. The slot table (§3) is a **validator vocabulary profile**, like `concept_keys.json`: it is derived from §6.2 and cites it, but it is **not** a new Morphology catalog. Callers may narrow a profile (fewer allowed types, more required slots). They may not widen it beyond the reference slot table.
5. Passing an instantiation check states only that the declared structure is complete and well-typed. `canonical_admission`, `current_authority` and `epistemic_warrant` stay `NOT_EVALUATED` without exception.

### 1.1 Complete positive fixture (schema-valid)

The machine-readable, fully specified `/2` example is `fixtures/valid_conclusion_context_v2.json`. It includes the existing mandatory `/1` root fields (`context_id`, `source_kind`, `predicate_contracts`), the declared X scope, Evidence and Annotation referents, plus the typed Conclusion slots. Its `profile.scope`, referent `scope_ref` and `pair_scope_ref` all select the same declared Observation scope `obs1`.

### 1.2 Slot kinds and scope selection

Slot descriptor kinds are **`ref`**, **`enum`** and **`string`**. A `ref` has immutable `cardinality` (`one` = string, `many` = nonempty array of strings) and a nonempty allowlist of concept IDs. `enum` has a nonempty `values` allowlist and uses a string value. `string` is an unconstrained declared nonempty literal where the reference table calls for textual attributes (`action_kind`, `limits`, `method`); it is never an Authority, warrant, permission or validated external method invocation.

Reference concepts, slot kind and cardinality cannot be changed by caller profiles. Every reference-table required slot must remain required. Caller narrowing is limited to **smaller nonempty concept/enum allowlists**, **marking optional slots required** and **dropping optional slots** (thus disallowing their use); adding unknown slots or making required slots optional is a widening configuration error. Duplicate names within one profile, duplicate `profile_ref`, or duplicate `(concept_id, scope)` profiles without explicit selection follow §2 and §2.1.

The single `pair_scope_ref` slot must point to a declared X Scope referent *of the exact endpoint-specific type* in `instantiation_reference_v1.json`. The target ID must equal the endpoint referent's `scope_ref` and the selected profile's `scope`. Neither an untyped scope string nor a scope concept borrowed from a different Key Pair is sufficient.

## 2. Status and diagnostic rules

| Situation | Status | Diagnostic (new unless noted) |
|---|---|---|
| X endpoint, no matching profile in scope | UNRESOLVED | `P1_INSTANTIATION_PROFILE_REQUIRED` (existing) |
| Profile in scope, referent declares no `slots` or misses a required slot | UNRESOLVED | `P1_INSTANTIATION_SLOT_MISSING` |
| Slot points to a ref not declared in the context | UNRESOLVED | `P1_BINDING_CONTEXT_REQUIRED` (existing, slot path) |
| Slot filled with a referent whose concept is not allowed | FAIL | `P1_INSTANTIATION_SLOT_TYPE` |
| Enum slot value outside declared values; wrong cardinality; undeclared slot name | FAIL | `P1_INSTANTIATION_SLOT_SIGNATURE` |
| Conditional rule violated (§3.2) | FAIL | `P1_INSTANTIATION_CONDITION` |
| Reference cycle across declared `delegated_from_ref` Authority lineage or `supersedes_ref` Expectation lineage (including self-loops) | FAIL | `P1_INSTANTIATION_CYCLE` |
| Two profiles for the same concept/scope without explicit selection | UNRESOLVED | `P1_INSTANTIATION_PROFILE_AMBIGUOUS` (mirrors P1.4-05) |
| Profile widens the reference slot table (even if it would accept an otherwise forbidden substitution) | invalid input (MCP error) | `P1_MCP_CONFIG_INVALID` (existing) |
| Endpoint at β/ζ without `witness_ref` | UNRESOLVED | `P1_LAYER_WITNESS_MISSING` (existing; checked before slots) |

Precedence follows P1.4-14: FAIL outranks UNRESOLVED, and `NOT_EVALUATED` is never PASS. For a missing conditionally required Admission slot (`authority_ref` after `admitted`, `refusal_ref` after `refused`), the **specific** `P1_INSTANTIATION_CONDITION` FAIL takes precedence over generic `P1_INSTANTIATION_SLOT_MISSING`. A malformed/widening caller profile is **invalid input**, not a semantic FAIL report.

### 2.1 Profile lookup, schema checks and cycles

- `instantiation_profile_ref` is resolved by **exact** ID in the same caller context. Unknown explicit ID gives `P1_INSTANTIATION_PROFILE_REQUIRED` UNRESOLVED; an explicitly chosen profile of a different endpoint/scope is a contradictory declaration (`P1_INSTANTIATION_PROFILE_SELECTION`, FAIL). If none is explicitly selected, select only a unique `(concept_id, scope)` profile. Multiple such candidates yield `P1_INSTANTIATION_PROFILE_AMBIGUOUS` UNRESOLVED.
- Duplicate `profile_ref`, invalid slot signatures, non-table slot descriptors or widening profiles are **configuration errors** (`P1_MCP_CONFIG_INVALID`), not typed referent findings.
- A missing in-context slot reference yields `P1_BINDING_CONTEXT_REQUIRED` UNRESOLVED at the exact slot/item JSON Pointer. A declared referent with the wrong concept yields `P1_INSTANTIATION_SLOT_TYPE` FAIL. Caller profile invalidity is detected **before** referent evaluation.
- `P1_INSTANTIATION_CYCLE` is limited to the explicit ancestry edges `Authority.delegated_from_ref` and `Expectation.supersedes_ref`. It does **not** reject arbitrary cross-referent cycles, since the reference morphology does not generally require acyclicity.
- A `witness_ref` is a declarative pointer, not proof of witness truth. Missing β/ζ witness retains precedence over missing instantiation slots when no stronger FAIL is present.
- Diagnostics use RFC 6901 JSON Pointers, e.g. `/referents/3/slots/basis_refs/0` (not `referents[i].slots.basis_refs`). Stable ordering and FAIL > UNRESOLVED remain mandatory.


## 3. Reference slot table (derived from Morphology v9.4 §6.2)

Every profile additionally requires `pair_scope_ref` → the endpoint-specific X scope. The exact mapping for the five Key Pairs is fixed in `instantiation_reference_v1.json`: Perception/Conclusion → Observation; Authority/Admission → Policy; Expectation/Satisfaction → Conversation; Delegation/Completion → Contract; Action/Result → Event. A valid-looking X scope of the **wrong** pair is `P1_INSTANTIATION_SLOT_TYPE` FAIL.

| Endpoint | Required slots → allowed concepts | Optional slots | Source |
|---|---|---|---|
| **Perception** | `observer_ref` → Y Actor, Principal · `observed_refs`[1..n] → Y Evidence, Artifact, Content, X Result | `limits` (`string` slot) | §6.2.1 |
| **Conclusion** | `basis_refs`[1..n] → X Perception, Y Evidence · `proposition_ref` → Y Annotation · `disposition` ∈ {verifies, refutes, unresolved} | `method` (`string` declaration of F method ID; no method certification) | §6.2.1 |
| **Authority** | `holder_ref` → Y Actor · `source_ref` → Z Grant · `action_kind` (`string` slot) · `resource_scope_ref` → Y Resource, Z Project Boundary, Z Thread Boundary | `delegated_from_ref` → X Authority | §6.2.2 |
| **Admission** | `request_ref` → X Action · `principal_ref` → Y Principal · `decision` ∈ {admitted, refused} | `authority_ref` → X Authority · `refusal_ref` → Z Refusal | §6.2.2 |
| **Expectation** | — (scope only) | `work_item_ref` → Y Work Item · `supersedes_ref` → X Expectation | §6.2.3 |
| **Satisfaction** | `expectation_ref` → X Expectation · `criteria_ref` → Y Annotation | `measurement_source_ref` → Y Source, Evidence | §6.2.3 |
| **Delegation** | `delegator_ref`, `delegatee_ref` → Y Actor · `authority_source_ref` → X Authority, Z Grant | `expectation_ref` → X Expectation · `work_item_ref` → Y Work Item | §6.2.4 |
| **Completion** | `delegation_ref` → X Delegation · `basis_refs`[1..n] → Y Evidence, Y Outcome, X Result | — | §6.2.4 |
| **Action** | `performed_by_ref` → Y Actor | `executed_as_ref` → Y Principal | §6.2.5 |
| **Result** | `action_ref` → X Action | `artifact_refs` → Y Artifact, Evidence | §6.2.5 |

### 3.1 Non-substitution rules (always FAIL with `P1_INSTANTIATION_SLOT_TYPE`)

These are the type confusions the experiments probed. A wrong referent under a **valid narrow** profile yields `P1_INSTANTIATION_SLOT_TYPE` FAIL. If a caller profile attempts to expand the allowed types so that such a substitution would become accepted, reject the profile first with `P1_MCP_CONFIG_INVALID` (invalid input). No forbidden substitution can be accepted:

| Forbidden fill | Morphology rule | Experiment origin |
|---|---|---|
| Z Capability or Y Capability Profile / Role Binding as Authority `source_ref` | "a technically possible Capability is not Authority"; "Role … does not independently grant Authority" | RCP-01, RCP-02; 014-S06 |
| X Completion, Y Outcome or X Result in `expectation_ref`/`criteria_ref` of Satisfaction | `Completion != Satisfaction`, `Result != Outcome` | 014-M02, 014-S08 |
| Y Outcome as `delegation_ref` of Completion, or Completion without Delegation | `Outcome != Completion` | 014-M02 |
| X Satisfaction or X Completion in Conclusion `basis_refs` | `Conclusion != Satisfaction` | 014-M04 |
| Y Annotation in Result `action_ref` / X Result rewritten as Annotation | `Event != Annotation` | 014-S08 |

### 3.2 Conditional rules (`P1_INSTANTIATION_CONDITION`, FAIL)

- C-ADM-1: `decision = refused` requires `refusal_ref`; `decision = admitted` requires `authority_ref`.
- C-ADM-2: `decision = admitted` with `refusal_ref` present → FAIL.
- C-AUT-1: `delegated_from_ref` must not point to the same referent and must not create an Authority lineage cycle → covered by `P1_INSTANTIATION_CYCLE`.
- C-CON-1: `disposition` other than `unresolved` with only Perception bases is allowed structurally; the report must still carry `epistemic_warrant = NOT_EVALUATED`.

## 4. Acceptance criteria

| AC | Requirement | Evidence (to be produced) |
|---|---|---|
| P1.6-01 | No change to Morphology v9.4, P0 assets, P1.1 frozen files, report.schema.json | baseline hash snapshot reused, `SHA256SUMS.txt` diff empty |
| P1.6-02 | binding-context/1 behaviour byte-identical for all existing fixtures (F01–F25, P1.4 tests, golden examples) | regression suite |
| P1.6-03 | binding-context/2 schema added as a backward-behaviour-preserving extension; /1 untouched; unknown keys rejected | `context-v2.schema.json`, schema tests |
| P1.6-04 | Instantiation-profile schema with slot kinds `ref` (one/many), `enum`, and `string`, plus `revision`, `scope`, `origin` | `INSTANTIATION_PROFILES.schema.json` |
| P1.6-05 | Reference slot table (§3) shipped as validator vocabulary profile with section citations; correct pair-scope mapping enforced; caller profiles may only narrow it | `instantiation_reference_v1.json`, widening test → config error |
| P1.6-06 | All 10 X endpoints bindable with a complete, well-typed profile → `referent_binding = PASS` | one positive test per endpoint |
| P1.6-07 | Every row in §2 plus profile-selection semantics in §2.1 produces exactly the stated status and diagnostic code | one test per row |
| P1.6-08 | Every non-substitution rule in §3.1 rejects, distinguishing typed semantic FAIL from invalid widening profile config | one negative test per row |
| P1.6-09 | Conditional rules C-ADM-1/2 and cycle detection enforced | tests |
| P1.6-10 | PASS never alters `canonical_admission`, `current_authority`, `epistemic_warrant` (`NOT_EVALUATED`) or `source_warrant` (`declared_unverified`) | assertion in every positive test |
| P1.6-11 | Z zones unchanged: still `P1_INSTANTIATION_PROFILE_REQUIRED` with /2 context | regression test |
| P1.6-12 | β/ζ endpoints still require `witness_ref` before slot evaluation | test |
| P1.6-13 | Deterministic RFC 6901 JSON-Pointer diagnostics into `/referents/{i}/slots/{name}` | snapshot tests |
| P1.6-14 | Local MCP and G5 Remote return identical reports for the alignment set (§5); `cube_discover_surface` lists the new context and profile versions | adapter parity test |
| P1.6-15 | New diagnostic codes registered in `DIAGNOSTIC_EXTENSION.json` and `RULE_COVERAGE.json` with Morphology references | file diff |
| P1.6-16 | Independent oracle for §5 (separately written decision table, as P1.5) | oracle vectors |

`PASS` in this matrix means the listed test ran successfully. It does not imply that a declared Authority exists, that an Admission happened, or that a Conclusion is warranted.

## 5. Alignment re-run set (exit check)

After implementation these cases are re-run against G5 Remote. Expected statuses are fixed **before** the run:

| ID | Origin | Case | Expected overall |
|---|---|---|---|
| R-01 | EXP-011-A path | `rel("supports", Y:α:Evidence, X:α:Conclusion)` with complete Conclusion profile and `supports` contract Evidence → Conclusion | PASS |
| R-02 | EXP-011 | Same, Conclusion without `basis_refs` | UNRESOLVED · `SLOT_MISSING` |
| R-03 | EXP-014-M02 | Satisfaction with `expectation_ref` → X Completion | FAIL · `SLOT_TYPE` |
| R-04 | EXP-014-M04 | Conclusion `disposition = verifies`, `basis_refs` → X Satisfaction | FAIL · `SLOT_TYPE` |
| R-05 | EXP-014-M04 | Conclusion `disposition = verifies`, valid Evidence basis | PASS, `epistemic_warrant = NOT_EVALUATED` |
| R-06 | RCP-01 | Authority `source_ref` → Z Capability | FAIL · `SLOT_TYPE` |
| R-07 | RCP-02 | Authority `source_ref` → Y Role Binding | FAIL · `SLOT_TYPE` |
| R-08 | RCP-09 / 014-M03 | Admission `decision = admitted` without `authority_ref` | FAIL · `CONDITION` |
| R-09 | RCP-09 | Admission `decision = refused` with `refusal_ref` → Z Refusal | PASS, `canonical_admission = NOT_EVALUATED` |
| R-10 | 014-S08 | Result without `action_ref` | UNRESOLVED · `SLOT_MISSING` |
| R-11 | 015-H3 | Perception at ζ without `witness_ref` | UNRESOLVED · `LAYER_WITNESS_MISSING` |
| R-12 | Regression | X:α:Conclusion with binding-context/1 | UNRESOLVED · `INSTANTIATION_PROFILE_REQUIRED` |
| R-13 | Scope guard | Z:α:Ownership with binding-context/2 | UNRESOLVED · `INSTANTIATION_PROFILE_REQUIRED` |

Not expected to change (explicitly, so that no improvement is over-read): EXP-011-A composition of nested `rel` (still UNRESOLVED, nested return types undefined), 014-M08/M10 (multi-expression identity and parent cycles), RCP effect probes (real runtime required).

## 6. Open decisions

- **D-1 ADOPTED FOR P1.6:** Missing unconditional slot → UNRESOLVED. Explicit contradictions and missing conditionally required Admission authorizations → FAIL per C-ADM-1.
- **D-2 ADOPTED FOR P1.6:** Slot table is a versioned **P1 validator vocabulary profile**, not normative P0. Any morphological promotion requires separate §D.5 adoption.
- **D-3 DEFERRED TO P1.7:** Admission Principal vs Authority holder is a typed cross-referent delegation/identity problem, not P1.6. Do not enforce simple equality or claim authorization without a validated effective-principal/authority chain.
- **D-4 DEFERRED:** All seven Z zones remain unchanged and UNRESOLVED on profile-required lookups. Whether their future implementation shares mechanics or uses its own profile family is a separate decision.
