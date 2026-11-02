# P1.12 — Declared Coverage and Instance Profile · Acceptance specification

**Status:** SPECIFIED — decisions D-1…D-6 and detail questions Q-1…Q-6 resolved 2026-11-01 (all as proposed) — **IMPLEMENTED locally 2026-11-01** (TASK-033, K-01…K-21 21/21); LIB entry `analyze.population/v1` (TASK-034), printer VP-10 (TASK-035), local G4/G6 adapter and MILE-002 re-run 7/7 (TASK-036, 2026-11-02). G5 and host acceptance are the follow-up step (D-5).
**Numbering:** New profile `P1.12/coverage-instance-profile-v1`, context `aiaeao.cube.binding-context/8`, directory `P1/coverage-instance-profile-v1/`. Builds on P1.11 (`binding-context/7`). P1.7 stays reserved for the Principal → Authority holder chain.
**Basis:** Morphology v9.4 (no change); P1.10.1 D-2 (incomplete declaration → UNRESOLVED, never FAIL); `context-v7.schema.json` (`referent`, `predicate` with `additionalProperties: false`); P0 concept `Y:identified-object:bounded-execution`; MILE-002 gap ledger G-01 (completeness and population) and G-08 (instance correlation); MILE-004 learning balance (rank 1 and 2) and probe E-2/L-2; MILE-005 decisions D-1…D-6 (`docs/02-Milestones/MILE-005-completeness-instances.md`); check cases `docs/09-Research/completeness-instances/CHECK-CASES.json` (21 cases, committed before this specification).
**Motivation:** Two gaps found in the grammar comparison (all synthetic, no client data):

| Finding | Effect today (baseline run TASK-030) |
|---|---|
| "Checked empty" and "unknown" cannot be told apart; counting rules over statement sets are not checkable | ARC-02 count rule, ARC-03 absence, DSM-03 empty-known, BPMN-01 exclusivity, BPMN-02 synchronisation: not executable |
| Instance membership is bound only by scope overloading | A join pairing tokens of instances i1 and i2 in one shared trace scope: PASS |

P1.12 adds **declared coverage** (what has been surveyed completely), **declared population rules** (absence, count, join activation) and **typed instance membership**. P1 checks declarations and single statements; the evaluation of a rule over a statement set belongs to a LIB entry (D-6, §6). Nothing here inspects a live system or claims that a surveyed state is true.

## 0. Scope

| In scope | Out of scope |
|---|---|
| `coverage_declarations`: referent × predicate × direction, or a single pair (D-2) | Coverage per view; coverage inferred from a view's contents |
| `population_rules`: `absence`, `count`, `join_activation`, declared and checked for coverage (D-3) | Evaluating rules over statement sets inside `cube_validate` (D-6 → LIB) |
| Optional `instance_ref` on referents; `requires_same_instance` on predicate contracts (D-4) | Control-flow semantics, exclusivity per gateway type, trace conformance (G-07) |
| Local MCP G4/G6 and discovery (D-5) | Remote G5 and host acceptance (follow-up, D-5) |
| Status and diagnostics for the above | Rendering (separate printer revision, TASK-035) |

## 1. Design summary

1. **New context version** `aiaeao.cube.binding-context/8`, a strict superset of `/7` with no new required fields. `/8` activates P1.12 rules; `/1…/7` stay byte-identical (D-1).
2. **Coverage (CV).** A `coverage_declarations[]` entry states that all statements of one predicate in one direction at one referent — or one ordered pair — are surveyed. Optional `instance_ref` restricts the declaration to statements of that instance (Q-2). Absence inside a declared scope is "checked empty"; outside it is unknown.
3. **Population rules (PR).** A `population_rules[]` entry declares an `absence`, `count` or `join_activation` rule. P1 checks that the rule is well formed and covered by a declaration; uncovered → UNRESOLVED `P1_COVERAGE_UNDECLARED` (D-3). P1 never counts.
4. **Instances (IN).** A referent may carry `instance_ref`, naming a declared referent of concept `Y:identified-object:bounded-execution` (Q-1). A predicate contract may set `requires_same_instance: true`; a statement with that predicate whose endpoints carry different `instance_ref` → FAIL `P1_INSTANCE_MISMATCH`; a missing `instance_ref` on either endpoint → UNRESOLVED `P1_INSTANCE_UNDECLARED`.
5. **Diagnostics** follow P1.10: context checks after all P1.11 checks, JSON Pointers into `coverage_declarations[i]`, `population_rules[i]` or the referent; FAIL outranks UNRESOLVED.

### 1.1 Shape (illustrative, synthetic)

```json
{
  "format": "aiaeao.cube.binding-context/8",
  "scope_ref": "bpmn:trace",
  "referents": [
    {"ref": "bpmn:i1", "concept_id": "Y:identified-object:bounded-execution", "home": "Y", "layers": ["α"], "provenance_status": "declared_unverified"},
    {"ref": "bpmn:i2", "concept_id": "Y:identified-object:bounded-execution", "home": "Y", "layers": ["α"], "provenance_status": "declared_unverified"},
    {"ref": "bpmn:i1/tok-stock", "concept_id": "Y:resource-object:evidence", "home": "Y", "layers": ["α"], "provenance_status": "declared_unverified", "instance_ref": "bpmn:i1"},
    {"ref": "bpmn:i2/tok-credit", "concept_id": "Y:resource-object:evidence", "home": "Y", "layers": ["α"], "provenance_status": "declared_unverified", "instance_ref": "bpmn:i2"}
  ],
  "predicate_contracts": [
    {"predicate_id": "joins", "revision": "example/1", "scope": "bpmn:trace", "origin": "illustrative_fixture",
     "subject_concept_ids": ["Y:resource-object:evidence"], "object_concept_ids": ["Y:resource-object:evidence"],
     "direction": "subject_to_object", "requires_same_instance": true}
  ],
  "coverage_declarations": [
    {"declaration_id": "cv-tp-in", "scope": "referent_relation_direction", "referent": "am:transaction-processing",
     "predicate_id": "realizes", "direction": "incoming", "witness_ref": "model:archimate-billing#view-full"}
  ],
  "population_rules": [
    {"rule_id": "pr-fp", "kind": "count", "referent": "am:financial-processing", "predicate_id": "composedOf",
     "direction": "outgoing", "min": 2, "max": 3, "witness_ref": "model:archimate-billing#local_count_rule"}
  ]
}
```

→ `rel("joins", Y:α:Evidence["bpmn:i1/tok-stock"], Y:α:Evidence["bpmn:i2/tok-credit"])`: FAIL · `P1_INSTANCE_MISMATCH`. Context check: UNRESOLVED · `P1_COVERAGE_UNDECLARED` at `/population_rules/0` (no declaration covers outgoing `composedOf` of `am:financial-processing`).

## 2. Status and diagnostic rules

| Situation | Status | Diagnostic |
|---|---|---|
| Population rule not covered by any coverage declaration (CV-3) | UNRESOLVED | `P1_COVERAGE_UNDECLARED` (new) |
| Statement with a `requires_same_instance` predicate, endpoints with different `instance_ref` | FAIL | `P1_INSTANCE_MISMATCH` (new) |
| Statement with a `requires_same_instance` predicate, `instance_ref` missing on one or both endpoints | UNRESOLVED | `P1_INSTANCE_UNDECLARED` (new) |
| `instance_ref` names an undeclared referent or one not of concept `bounded-execution` (Q-1) | UNRESOLVED | `P1_BINDING_CONTEXT_REQUIRED` (existing) |
| Coverage declaration or rule names an undeclared referent or predicate | UNRESOLVED | `P1_BINDING_CONTEXT_REQUIRED` (existing) |
| Malformed declaration or rule (schema) | MCP error | `P1_MCP_CONFIG_INVALID` (existing) |
| Any P1.12 field inside a `/1…/7` context | MCP error | `P1_MCP_CONFIG_INVALID` (existing) |
| Scope-per-instance case (instance as `scope_ref`) | unchanged | `P1_REFERENT_MISMATCH`, `P1_SCOPE_CONFLICT` (existing) |
| All P1.11 rows | unchanged | unchanged |

Precedence follows P1.10: FAIL outranks UNRESOLVED. A rule already reported for an unknown referent is not additionally reported as `P1_COVERAGE_UNDECLARED`.

## 3. Rules in detail

**Coverage (CV)**
- CV-1: `scope` is `referent_relation_direction` (fields `referent`, `predicate_id`, `direction` ∈ {`outgoing`, `incoming`}) or `pair` (fields `subject`, `predicate_id`, `object`). Every declaration carries `witness_ref`.
- CV-2: A `referent_relation_direction` declaration covers every pair at that referent in that direction for that predicate; a `pair` declaration covers exactly one ordered pair. There is no view-level declaration (D-2).
- CV-3: A population rule is covered if a declaration with the same predicate covers every pair the rule can range over (`count`, `join_activation`: referent and direction; `absence`: the pair or the referent in either direction).
- CV-4: Optional `instance_ref` on a declaration restricts coverage to statements whose endpoints carry that instance (Q-2).
- CV-5: Declarations are statements of survey scope, not proof; P1 never infers coverage from the absence of statements.

**Population rules (PR)**
- PR-1: `kind` ∈ {`absence`, `count`, `join_activation`}; `count` carries integer `min` ≥ 0 and optional `max` ≥ `min`; `absence` names a pair; `join_activation` names an instance, a gateway referent and its incoming flows with per-flow `min` (default 1).
- PR-2: P1 checks well-formedness (schema), referent and predicate resolution, and coverage (CV-3). It does not evaluate the rule.
- PR-3: Evaluation is delegated to the LIB entry of §6; the result maps to PASS / FAIL / UNRESOLVED as in §6.

**Instances (IN)**
- IN-1: `instance_ref` is optional on any referent; it names a declared referent of concept `Y:identified-object:bounded-execution` (Q-1).
- IN-2: `requires_same_instance` is an optional boolean on a predicate contract (default false).
- IN-3: For a statement whose predicate requires the same instance: equal `instance_ref` → no finding; different → FAIL `P1_INSTANCE_MISMATCH`; missing on either endpoint → UNRESOLVED `P1_INSTANCE_UNDECLARED`.
- IN-4: Predicates without `requires_same_instance` are unaffected by `instance_ref`.
- IN-5: Scope-based instance handling (P1.1 resolver, `scope_ref`) is unchanged; IN adds a typed check and does not replace scope checks.

## 4. Acceptance criteria

| AC | Requirement | Evidence |
|---|---|---|
| P1.12-01 | No change to Morphology, P0, P1.1…P1.11 artifacts; `SHA256SUMS` diff empty | file diff |
| P1.12-02 | `/1…/7` byte-identical, including all previous vector suites and goldens | regression suite |
| P1.12-03 | `context-v8.schema.json` strict superset of `/7` | schema tests |
| P1.12-04 | CV-1…CV-5, PR-1…PR-3, IN-1…IN-5 | vectors K-01…K-21 (§5) |
| P1.12-05 | Every row in §2 yields exactly the stated status and code | one test per row |
| P1.12-06 | Independent oracle for K-01…K-21, transcribed from `CHECK-CASES.json` before code | `oracles/independent_k01_k21.json` |
| P1.12-07 | LIB entry of §6 reproduces the LIB expectations of CC-01…CC-16 with an independent oracle | lunados.lib entry cases |
| P1.12-08 | Local MCP G4/G6: `cube_validate` accepts `/8`; local discovery lists `binding-context/8` with entry profile `P1.12/coverage-instance-profile-v1` | adapter test, discover check |
| P1.12-09 | Re-run of MILE-002 cases: BPMN-03 shared gives FAIL `P1_INSTANCE_MISMATCH` as `/8`; scoped case unchanged | research run with expectation committed before |
| P1.12-10 | Synthetic golden: one context with all three blocks, no client data | `fixtures/golden_coverage_instance.json` |

## 5. Vectors (from the check cases)

Each vector is the profile translation of one check case (`CHECK-CASES.json`, committed `52cc773`). Status and layer come from the case; codes as in §2.

| ID | Case | P1 (`cube_validate`, `/8`) | LIB (§6) |
|---|---|---|---|
| K-01 | CC-01 ARC-03 service view, absence of any realizer of TP | context: UNRESOLVED · `COVERAGE_UNDECLARED` | UNRESOLVED · coverage_undeclared |
| K-02 | CC-02 full view, incoming `realizes` of TP declared; absence Billing → TP | PASS | PASS · absent_checked (0) |
| K-03 | CC-03 as K-02; absence Accounting → TP | PASS | FAIL · absence_contradicted (1) |
| K-04 | CC-04 DSM pair (printer, parser) declared; absence printer → parser | PASS | PASS · absent_checked (0) |
| K-05 | CC-05 as K-04; absence validator → printer | context: UNRESOLVED · `COVERAGE_UNDECLARED` | UNRESOLVED · coverage_undeclared |
| K-06 | CC-06 outgoing `dependsOn` of printer declared; absence printer → resolver | PASS | PASS · absent_checked (0) |
| K-07 | CC-07 as K-06; absence printer → validator | PASS | FAIL · absence_contradicted (1) |
| K-08 | CC-08 outgoing `composedOf` of Financial Processing declared; count 2…3 | PASS | PASS · within_bounds (3) |
| K-09 | CC-09 same rule, no declaration | context: UNRESOLVED · `COVERAGE_UNDECLARED` | UNRESOLVED · coverage_undeclared |
| K-10 | CC-10 declared, one target only | PASS | FAIL · out_of_bounds (1) |
| K-11 | CC-11 outgoing `routedTo` of i1/tok-route declared; count 1…1, one path | PASS | PASS · within_bounds (1) |
| K-12 | CC-12 as K-11, two paths | PASS (each statement) | FAIL · out_of_bounds (2) |
| K-13 | CC-13 count 1…1, no declaration | context: UNRESOLVED · `COVERAGE_UNDECLARED` | UNRESOLVED · coverage_undeclared |
| K-14 | CC-14 join activation i1; incoming `onFlow` of both flows declared for i1 (CV-4) | PASS | PASS · join_enabled |
| K-15 | CC-15 join activation i2; declared for i2; no stock token | PASS | FAIL · join_not_enabled |
| K-16 | CC-16 join activation i2; no declaration | context: UNRESOLVED · `COVERAGE_UNDECLARED` | UNRESOLVED · coverage_undeclared |
| K-17 | CI-01 shared scope, `joins` i1/tok-stock → i2/tok-credit, `requires_same_instance` | FAIL · `INSTANCE_MISMATCH` | — |
| K-18 | CI-02 scope per instance (regression) | FAIL · `REFERENT_MISMATCH`, `SCOPE_CONFLICT` | — |
| K-19 | CI-03 `joins` within i1 | PASS | — |
| K-20 | CI-04 `instance_ref` only on i1/tok-stock | UNRESOLVED · `INSTANCE_UNDECLARED` | — |
| K-21 | CI-05 `routedTo` without `requires_same_instance` | PASS | — |

Translation notes: CC-14…CC-16 declare coverage per incoming flow referent (`f-stock-done`, `f-credit-done`) with predicate `onFlow`, direction `incoming` and `instance_ref` (CV-4); the check cases expressed this as one declaration "incoming to join". K-12 shows the separation: each statement is valid on its own; only the set evaluation finds two paths.

## 6. LIB counterpart (D-6)

A lunados.lib entry `analyze.population/v1` (working title) evaluates one population rule over a statement set:

- **Roles:** `statements` (set of declared statements), `coverage` (coverage declarations), `rule` (one population rule), `instances` (optional `instance_ref` map).
- **Output:** a typed result `aiaeao.population-result/v1` (first use of LR-1): `value` ∈ {`absent_checked`, `absence_contradicted`, `within_bounds`, `out_of_bounds`, `join_enabled`, `join_not_enabled`, `coverage_undeclared`}, `count`, `covered_by` (declaration IDs), `missing_scope` (when uncovered).
- **Status mapping:** `absent_checked`, `within_bounds`, `join_enabled` → PASS; `absence_contradicted`, `out_of_bounds`, `join_not_enabled` → FAIL; `coverage_undeclared` → UNRESOLVED. An uncovered rule is never FAIL.
- **Non-implications:** a declared survey scope is not proof of completeness in the world; "absent_checked" means "no statement in the declared scope", not "does not exist".
- **Effect class:** `pure_declarative`. Independent oracle and reference cases CC-01…CC-16.

## 7. Decisions (resolved 2026-11-01, MILE-005, all as proposed)

| Decision | Options | Resolution | Consequence |
|---|---|---|---|
| D-1 Profile cut and number | (a) one profile, `binding-context/8` · (b) two profiles | **(a)** | One specification, one oracle, one acceptance; sections CV/PR and IN stay separable. |
| D-2 Coverage unit | (a) referent × predicate × direction plus pair · (b) pair only · (c) per view | **(a)** | Row-level declarations are consistent by construction; no view-level overclaim. |
| D-3 Status when uncovered | (a) UNRESOLVED with own code · (b) new status | **(a)** | P1 status set unchanged; consistent with P1.10.1 D-2. |
| D-4 Instance binding | (a) typed optional `instance_ref` plus `requires_same_instance` · (b) convention "instance = scope" | **(a)** | Detects cross-instance joins in a shared scope. |
| D-5 Delivery | (a) local G4/G6 now, G5 later · (b) G5 now | **(a)** | G5 descriptor and host acceptance follow when the profile is stable. |
| D-6 Population evaluation | (a) profile declares, P1 checks declarations, LIB evaluates · (b) declarations only | **(a)** | `cube_validate` stays a single-expression check. |

## 8. Detail questions (resolved 2026-11-01, all as proposed)

| Q | Question | Resolution |
|---|---|---|
| Q-1 | Must `instance_ref` name a declared referent of concept `Y:identified-object:bounded-execution`, or is it a free scoped identifier? | **Declared referent of that concept** — typed per D-4, resolvable, no free text (IN-1). |
| Q-2 | May a coverage declaration carry `instance_ref` to restrict its scope to one instance (needed for CC-14…CC-16)? | **Yes**, optional (CV-4). |
| Q-3 | Final names of the new codes | Keep `P1_COVERAGE_UNDECLARED`, `P1_INSTANCE_MISMATCH`, `P1_INSTANCE_UNDECLARED`. |
| Q-4 | Unknown referents/predicates in declarations and rules | Reuse `P1_BINDING_CONTEXT_REQUIRED` (UNRESOLVED); schema errors stay `P1_MCP_CONFIG_INVALID`. |
| Q-5 | Profile ID and directory | `P1.12/coverage-instance-profile-v1`, `P1/coverage-instance-profile-v1/`, `context-v8.schema.json`. |
| Q-6 | Local discovery | Add `binding-context/8` with entry profile P1.12 to the local validation discovery (PR #31 format). |

## 9. Not part of P1.12

- Control-flow profile and trace conformance (G-07), instance display in flows (VR-12), relation origin (G-02, VR-01), result schemas for other LIB methods (LR-1 beyond this entry).
- Remote G5 descriptor and host acceptance (D-5, follow-up).
- Temporal versioning of coverage (a declaration holds for the stated model state only).
