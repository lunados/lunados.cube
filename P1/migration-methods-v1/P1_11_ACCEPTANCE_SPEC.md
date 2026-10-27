# P1.11 — Migration method catalog · Acceptance specification

**Status:** ACCEPTED 2026-10-27 (F-01…F-16 16/16 local and via G4; live G5 host acceptance PASS, `P3/remote-mcp-g5/evidence/G5_R4_P111_HOST_REPORT.md`); decisions D-1…D-9 resolved 2026-10-27 (all as proposed).
**Numbering:** P1.7 stays reserved for the Principal → Authority holder chain. P1.11 builds on P1.10.1 (`binding-context/6`) and does not depend on P1.7.
**Requirement:** C-10 from the running migration field test (2026-10-27; about 37 referents, 56 dependencies, steps p0–p3; client details withheld). Prerequisite for F axes in the declared axes view (VP-09, C-8).
**Basis:** Morphology v9.4 §3.7 (F describes methods over qualified referents; candidate families decision, dialectics, experimentation, exploration, evaluation, feedback/regulation, projection, promotion are compositions, not objects), §5.7 (primitive families incl. *Transition / supersession* `state/version₁ → state/version₂`; composite patterns), §5.18 (Decision Trace), §7.12.1 (PAT-* Pattern Contract: roles, required predicates, qualifiers, output claims, permitted side effects), §3.13 (F stays a candidate, no accepted registry or calculation authority), `core.json` `qualifiers.F.method_profile_required_for_binding = true`; P1.4-11 (F qualifier needs one scoped `pure_declarative` method contract); P1.8 `method_contracts` (argument and return typing, `library_ref`); P1.10 predicate profile import (PP-1…PP-5, D-2, D-8).
**Motivation:** In the field test every statement `@F(method=…)` needs its own scoped, `pure_declarative` method contract in the context. The same four or five operations (import mailboxes, rebuild a site, retire a provider, rewrite a job) are re-declared in every context, with drifting argument types, and none of them can be attached to the migration plan itself: the plan says *that* a provider is retired at p2, not *how* the dependants move.

| Finding | Effect today |
|---|---|
| F requires a scoped `pure_declarative` contract per context | Same methods re-declared by hand; IDs and argument types drift |
| Method contracts have no link to transitions or dependencies | "How" a transition or successor happens lives only in free text |
| No migration vocabulary for F | An F axis (C-8 priority 2: method per component) has no data |

P1.11 ships a **pinned, reusable method catalog** imported by reference, exactly like the P1.10 predicate profile, and lets a migration plan **bind** catalog methods to transitions and dependencies. The Cube checks declaration, typing and structural fit. It never executes a method, never judges whether a method is suitable and never orders methods.

## 0. Scope

| In scope | Out of scope |
|---|---|
| Pinned catalog `P1.11/migration-methods-v1` with typed method contracts | Running, simulating or scheduling a method; checking that it happened |
| Import by `method_profile_refs`; imported contracts bound to the importing `scope_ref` | Ranking or recommending methods; cost, risk or effort |
| Method bindings on transitions and dependencies, typed against the contract | Changing the meaning of the morphology F families or adding a coordinate |
| `@F(method="migrate.…/v1")` in expressions resolves against imported contracts (P1.4-11 unchanged) | New MCP tools; P2 changes (VP-09 reads the result later) |
| Optional pin to the Functions Library (`library_ref`, P1.8 format) | Fetching library entries |

## 1. Design summary

1. **Context `aiaeao.cube.binding-context/7`:** strict superset of /6 with optional `method_profile_refs` (top level) and optional method bindings inside `migration_plans` (§3.3). /1…/6 behave byte-identically.
2. **Catalog:** a pinned JSON profile (SHA-256 fixed in code and in `SHA256SUMS.txt`), `origin: profile_declaration_unverified`, unscoped in the file, scoped to the importing context on import (P1.10 D-8 pattern). A local `method_contracts` entry may not redefine an imported `method_id`.
3. **Method contract** reuses the P1.8 shape (`method_id`, `revision`, `argument_min/max`, `argument_concept_ids`, `effect_class`, optional `return_concept_ids`, `library_ref`) plus profile-only documentary fields (`primitive`, `roles`, `notes`) that are dropped on projection to /6 (D-4).
4. **Bindings:** a transition or dependency may name a method and its arguments (role → ref). P1.11 checks: method known, arity, argument concept types, and the role fit with the plan (§3.4).
5. **F qualifier:** imported contracts are visible to the unchanged P1.4 F check, so `rel(...) @F(method="migrate.import/v1", …)` resolves without a hand-written contract.

### 1.1 Shape (illustrative, synthetic, abridged)

```json
{
  "format": "aiaeao.cube.binding-context/7",
  "scope_ref": "acme:migration",
  "predicate_profile_refs": ["P1.10/migration-predicates-v1"],
  "method_profile_refs": ["P1.11/migration-methods-v1"],
  "migration_plans": [{
    "plan_id": "mp-mail",
    "transitions": [{
      "transition_id": "t-mail", "at_phase": "p2", "retires": ["acme:legacy-mail"], "introduces": ["acme:new-mail"],
      "T": {"role": "scheduling"}, "witness_ref": "plan:mp-mail#t-mail",
      "methods": [
        {"method_id": "migrate.import/v1", "arguments": {"source": "acme:legacy-mail", "target": "acme:new-mail"},
         "witness_ref": "plan:mp-mail#import"},
        {"method_id": "migrate.retire/v1", "arguments": {"retired": "acme:legacy-mail"}}
      ]
    }],
    "dependencies": [{
      "dependency_id": "d-shop-a", "subject": "acme:shop", "predicate_id": "sends-via", "object": "acme:legacy-mail",
      "kind": "job", "holds_in": ["p0", "p1"], "successor_ref": "d-shop-b",
      "method": {"method_id": "migrate.rewrite/v1", "arguments": {"dependant": "acme:shop", "new_object": "acme:new-mail"}}
    }]
  }]
}
```

Catalog entry (abridged):

```json
{"method_id": "migrate.import/v1", "revision": "P1.11/migration-methods-v1", "origin": "profile_declaration_unverified",
 "primitive": "transition_supersession", "roles": ["source", "target"],
 "argument_min": 2, "argument_max": 2,
 "argument_concept_ids": [["Y:resource-object:resource", "Z:module-body:provider", "Z:module-body:third-party-dependency"],
                          ["Y:resource-object:resource", "Z:module-body:provider"]],
 "effect_class": "pure_declarative",
 "notes": ["Names an external operation; the Cube neither runs nor admits it (D-5)."]}
```

## 2. Status and diagnostic rules

| Situation | Status | Diagnostic |
|---|---|---|
| `method_profile_refs` names an unknown or unpinned catalog, or the file digest differs | MCP error | `P1_MCP_CONFIG_INVALID` (existing) |
| A local method contract redefines an imported `method_id` | MCP error | `P1_MCP_CONFIG_INVALID` (existing) |
| Binding names a `method_id` that is neither imported nor declared locally | UNRESOLVED | `P1_MIGRATION_METHOD_UNKNOWN` (new) |
| Binding with wrong roles, wrong arity, or an argument whose referent concept is not allowed for the role | FAIL | `P1_MIGRATION_METHOD_SIGNATURE` (new) |
| Binding argument names an undeclared referent | UNRESOLVED | `P1_MIGRATION_REFERENCE_MISSING` (P1.10, reused) |
| Binding does not fit the plan: e.g. `retire` on a referent the transition does not retire, `import`/`rebuild` target not introduced at or before the phase, `rewrite` on a dependency without `successor_ref` (D-7) | FAIL | `P1_MIGRATION_METHOD_PLAN` (new) |
| Binding without `witness_ref` where the catalog entry requires one (D-8) | UNRESOLVED | `P1_EVALUATION_WITNESS_MISSING` (existing) |
| Method bindings in a /6 context | MCP error | `P1_MCP_CONFIG_INVALID` (existing) |
| `@F(method=…)` with an imported method | as P1.4-11 | unchanged codes |
| All P1.10 / P1.10.1 rows | unchanged | unchanged |

`epistemic_warrant`, `current_authority` and `canonical_admission` stay `NOT_EVALUATED`. A PASS means the declared bindings are well typed and fit the declared plan; it never means the method is appropriate, complete or was carried out.

## 3. Rules in detail

### 3.1 Catalog (MC)

- MC-1: Pinned by SHA-256 like PP-1; header `format: aiaeao.cube.p1.11.method-profile/1`, `profile_id`, `reference_version: v9.4`, `scope_binding: importing_context_scope_ref`.
- MC-2: Every entry is unscoped in the file, `origin: profile_declaration_unverified`, `effect_class` per D-5, and declares named `roles` matching `argument_min/max`.
- MC-3: `argument_concept_ids` per role is a list of admissible concept IDs (D-4 widens the P1.8 one-ID-per-argument form inside the profile; the /6 projection expands to the P1.8 form or omits typing).
- MC-4: Catalog contents per D-2; each entry carries `primitive` (D-3) as documentary metadata.

### 3.2 Import (MI)

- MI-1: Imported contracts get `scope = scope_ref` of the importing context (P1.10 D-8).
- MI-2: The projection for the unchanged P1.4/P1.8 path appends imported contracts to `method_contracts` with `origin: external_declaration_unverified` and drops profile-only fields.
- MI-3: Local `method_contracts` remain allowed for methods outside the catalog.

### 3.3 Bindings (MB)

- MB-1: Transition: optional `methods` array of `{method_id, arguments: {role: ref}, witness_ref?}`.
- MB-2: Dependency: optional `method` object of the same shape (one method per dependency, D-6).
- MB-3: Arguments are referent refs of the context; each declared role appears exactly once.

### 3.4 Plan fit (MP, D-7)

- MP-1: `migrate.retire`: `retired` ∈ the transition's `retires`.
- MP-2: `migrate.import` / `migrate.rebuild`: `target` is introduced at or before the transition's phase, or present from the `current` phase.
- MP-3: `migrate.rewrite` on a dependency: the dependency has a `successor_ref`; `new_object` is the successor's object.
- MP-4: `migrate.reconfigure` (if adopted): the argument is neither retired nor introduced by that transition.
- MP-5: No rule compares methods with each other or derives an order from them.

### 3.5 Catalog v1 and binding details (MV)

Clarification transcribed together with the oracle (no decision changed).

| Method | Roles (admissible concept IDs) | Binding point | Primitive |
|---|---|---|---|
| `migrate.import/v1` | `source` (Resource, Provider, Third-party Dependency) · `target` (Resource, Provider) | transition | derivation |
| `migrate.rebuild/v1` | `target` (Resource, Provider, Integration, Runtime) | transition | transition_supersession |
| `migrate.retire/v1` | `retired` (Provider, Third-party Dependency, Integration, Runtime, Resource) | transition | transition_supersession |
| `migrate.rewrite/v1` | `dependant` (Integration, Actor, Runtime) · `new_object` (Provider, Third-party Dependency, Resource) | dependency | transition_supersession |
| `migrate.reconfigure/v1` | `target` (Provider, Third-party Dependency, Runtime, Resource) | transition | transition_supersession |

- MV-1: Concept IDs in the table are the P0 IDs `Y:resource-object:resource`, `Z:module-body:provider`, `Z:module-body:third-party-dependency`, `Z:module-body:integration`, `Z:module-body:runtime`, `Y:identity-anchor:actor`.
- MV-2: A catalog method bound at the wrong binding point FAILs with `P1_MIGRATION_METHOD_PLAN`.
- MV-3: `migrate.rewrite`: `dependant` must be the dependency's subject (in addition to MP-3).
- MV-4: MP-2 "present from the current phase" means: the target is not introduced by any transition of the plan.
- MV-5: Bindings to a **local** method contract (MI-3) use positional role names `arg1 … argN`; arity follows `argument_min/max`, typing follows `argument_concept_ids` when declared; plan-fit rules apply to catalog methods only.
- MV-6: Binding shape errors (not an object, empty `arguments`, non-string refs) are configuration errors (`P1_MCP_CONFIG_INVALID`).

## 4. Acceptance criteria

| AC | Requirement | Evidence |
|---|---|---|
| P1.11-01 | /1…/6 reports byte-identical to P1.10.1 (M-, C-, G-vectors) | regression run |
| P1.11-02 | Catalog pinning and import MC-1…MC-4, MI-1…MI-3 | F-01…F-04 |
| P1.11-03 | Binding typing MB-1…MB-3 | F-05…F-09 |
| P1.11-04 | Plan fit MP-1…MP-5 | F-10…F-13 |
| P1.11-05 | `@F(method=…)` resolves against imported contracts; P1.4 codes unchanged otherwise | F-14, F-15 |
| P1.11-06 | Every row in §2 yields exactly the stated status and code | one test per row |
| P1.11-07 | G4 adapter and G5 descriptor dispatch /7; live host acceptance | host report |
| P1.11-08 | Synthetic golden: three workstreams, every transition and successor bound to a method, one deliberate misfit | fixture |
| P1.11-09 | No client data | review |

## 5. Alignment vectors (exit check)

| ID | Case | Expected |
|---|---|---|
| F-01 | /7 context importing the catalog, no bindings | PASS |
| F-02 | Unknown catalog ID | MCP error · `P1_MCP_CONFIG_INVALID` |
| F-03 | Catalog file altered (digest) | MCP error · `P1_MCP_CONFIG_INVALID` |
| F-04 | Local contract redefines `migrate.import/v1` | MCP error · `P1_MCP_CONFIG_INVALID` |
| F-05 | Transition bound to `migrate.import/v1`, correct roles and types | PASS |
| F-06 | Binding to `migrate.unknown/v1` | UNRESOLVED · `P1_MIGRATION_METHOD_UNKNOWN` |
| F-07 | `import` with one argument | FAIL · `P1_MIGRATION_METHOD_SIGNATURE` |
| F-08 | `import` target is an Actor | FAIL · `P1_MIGRATION_METHOD_SIGNATURE` |
| F-09 | Argument names an undeclared ref | UNRESOLVED · `P1_MIGRATION_REFERENCE_MISSING` |
| F-10 | `retire` on a referent the transition does not retire | FAIL · `P1_MIGRATION_METHOD_PLAN` |
| F-11 | `import` target introduced only after the transition | FAIL · `P1_MIGRATION_METHOD_PLAN` |
| F-12 | `rewrite` on a dependency without successor | FAIL · `P1_MIGRATION_METHOD_PLAN` |
| F-13 | `rewrite` whose `new_object` differs from the successor's object | FAIL · `P1_MIGRATION_METHOD_PLAN` |
| F-14 | `rel("supersedes", …) @F(method="migrate.import/v1", …)` with imported catalog | PASS (given a matching F qualifier profile) |
| F-15 | Same expression without `method_profile_refs` | UNRESOLVED · `P1_QUALIFIER_PROFILE_MISSING` (P1.4, unchanged) |
| F-16 | Method bindings in a /6 context | MCP error · `P1_MCP_CONFIG_INVALID` |

## 6. Relation to the morphology F families

The eight candidate families of §3.7 (decision, dialectics, experimentation, exploration, evaluation, feedback/regulation, projection, promotion — the requirement text lists seven; *dialectics* is the eighth) are **composite patterns** (§5.7): Decision = judgment → selection → admission → action; Promotion = candidate + evidence + review + authority → admitted change; and so on. Migration operations such as import, rebuild, retire or rewrite are of a different kind: each describes one **state/version change of a referent**, which §5.7 lists as the primitive family *Transition / supersession* (`state/version₁ → state/version₂`; "not destructive overwrite").

Consequences (D-3):

- The migration methods form their **own profile-local layer** below the composite families. Each entry declares `primitive: transition_supersession` (or `derivation` for `import`, D-3) as documentary metadata; no new family, no new coordinate, no change to §3.7.
- The composite families stay available for what *surrounds* a migration: choosing a method is a **decision** (§5.18 Decision Trace, out of scope as in P1.10), checking a cutover is an **evaluation**, the dual-run phase can be **feedback/regulation**, releasing the target is a **promotion**. P1.11 does not model these; a later profile could reference catalog bindings as their inputs.
- §7.12.1 PAT-* is the technical home a catalog entry approximates (roles, required predicates, permitted side effects). P1.11 implements only roles, typing and plan fit; side effects stay declared text (D-5).

## 7. Decisions (resolved 2026-10-27, all as proposed)

| Decision | Options | Resolution | Consequence |
|---|---|---|---|
| D-1 Placement and version | (a) new P1 profile P1.11, context `/7`, package `P1/migration-methods-v1` · (b) revision P1.10.2 inside `migration-profile-v2` | **(a)** | Separate pinned catalog and import; P1.10.1 stays frozen. |
| D-2 Catalog contents v1 | (a) `migrate.import`, `migrate.rebuild`, `migrate.retire`, `migrate.rewrite` · (b) (a) + `migrate.reconfigure` (settings/DNS change of a kept referent) · (c) (b) + `migrate.dual-run` (parallel operation over a phase range) | **(b)** | Covers the field-test operations; dual-run is a phase-range property better expressed by overlapping dependencies, so it waits. |
| D-3 Relation to F families | (a) own layer, `primitive` = §5.7 *Transition / supersession* (import optionally *derivation*) · (b) each method assigned to one of the eight families · (c) families themselves as catalog entries | **(a)** | No forced mapping (import is not a "projection", retire is not a "decision"); families stay composites around the migration (§6). |
| D-4 Argument typing | (a) named roles with a list of admissible concept IDs per role (profile-local), projected to /6 by omitting typing · (b) P1.8 form: exactly one concept ID per position | **(a)** | Real providers are Provider *or* Third-party Dependency; (b) would force one catalog entry per combination. |
| D-5 Effect class | (a) `pure_declarative` + note "names an external operation; the Cube neither runs nor admits it" · (b) new effect class `external_declared` (needs a P1.4 change) | **(a)** | P1.4-11 unchanged: the declaration is descriptive; the real-world effect is never claimed. |
| D-6 Binding points | (a) transitions (`methods`, several) and dependencies (`method`, one) inline · (b) separate plan-level `method_bindings` list with references | **(a)** | Readable next to what it describes; one dependency changes in one way. |
| D-7 Plan-fit rules | (a) MP-1…MP-4 as structural FAIL · (b) typing only, no plan fit · (c) plan fit as UNRESOLVED | **(a)** | A `retire` of something the transition does not retire is a contradiction inside the declaration, like P1.10 conflicts. |
| D-8 Witness | (a) optional per binding; required for entries marked `requires_witness` (none in v1) · (b) always required | **(a)** | Transition and dependency already carry witnesses; no double bookkeeping. |
| D-9 G5 / MCP | (a) G4 adapter + G5 descriptor in the same step, host acceptance as P1.10.1 · (b) local only first | **(a)** | Same delivery path as P1.10 and P1.10.1. |

## 8. Not part of P1.11

- Choosing, ranking or scheduling methods (Decision Trace §5.18).
- Method parameters (`θ`) beyond named roles, e.g. batch sizes or cutover windows.
- Composite patterns around migrations (evaluation of a cutover, promotion of the target).
- P2 display of methods (VP-09 F axes; VP-07 adapter transcription of bindings).
