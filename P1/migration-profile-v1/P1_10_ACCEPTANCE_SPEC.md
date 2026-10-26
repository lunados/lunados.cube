# P1.10 — Declared Migration Profile · Acceptance specification

**Status:** SPECIFIED, decisions D-1…D-8 resolved 2026-10-26 (D-1, D-3, D-5, D-7 as proposed with precisions; D-4 deviates from the draft proposal; D-8 added during review) — ready for implementation.
**Numbering:** P1.7 stays reserved for the Principal → Authority holder chain. P1.10 builds on P1.9 (`binding-context/4`) and does not depend on P1.7.
**Basis:** Morphology v9.4 §2.9 (referent binding; constraint C011 in `grammar/constraints.json`), §§5.6, 5.10, 5.11 (qualified relation expression, no flattening into one predicate list; local precedence without a total order belongs to a Relation Type / Pattern Contract; typed paths), §7.6.1 (REL-01, R01-AC02; `supersedes` and `references` are existing reference-vocabulary names, and P1.1 `predicate_registry.json` ships no built-in signatures), §3.6 (T roles incl. `scheduling`; D.2 "order is not scheduling"), §§6.4.1–6.4.2 (module bodies: Integration, Runtime, Provider, Third-party Dependency), §5.18 (Decision Trace — out of scope). References confirmed against `morphology.md` (v9.4 P0 snapshot) on 2026-10-26; §§3.7, 3.10 and 5.7–5.9 of the draft basis dropped as not applicable.
**Motivation:** A first test case (an infrastructure migration inventory, 2026-10-26, client details withheld) described a real system with P1.1 contexts only. Result:

| Finding | Effect today |
|---|---|
| Vocabulary fits: `Integration`, `Provider`, `ThirdPartyDependency`, `Resource`, `Actor` resolve; scoped predicates `depends-on`, `supersedes` (required T), `references` typed correctly; reversed direction and missing T FAIL as expected | P1 is usable for single claims |
| Every migration context must re-declare the same predicate contracts by hand | No reusable migration vocabulary; signatures drift between contexts |
| One expression per `cube_validate` call; the inventory (20 dependencies) is 20 unrelated calls | No statement about the inventory **as a whole** |
| "Current" and "target" state exist only in labels and free text | The Cube cannot say that a dependency still points at a provider that is retired in the target state |
| The most important finding of the test case — a dependency that outlives its provider (system mailboxes whose recovery addresses live on the provider retired first) — was found by reading, not by the Cube | The ordering risk of a migration is invisible to P1 |

P1.10 lets a context **declare** a migration plan — phases, transitions, and the dependency inventory as data — and lets P1 check its **structural consistency**. It never checks a live system and never decides an order.

## 0. Scope

| In scope | Out of scope |
|---|---|
| A reusable, pinned migration predicate profile (closed, profile-local predicate set with typed signatures) | A universal predicate registry or any change to Morphology v9.4 / P1.1 `predicate_registry.json` |
| A declared migration plan: ordered phases, transitions (retire / introduce), dependency inventory with phase validity | Discovering dependencies, scanning repositories, probing DNS or APIs |
| Structural checks: dangling dependencies, missing successors, phase ordering, typing, witnesses | Proving that a dependency exists, that a cutover happened, or that an order is safe |
| One `cube_validate` call checks the whole declared inventory against the plan | New MCP tools; P2 rendering changes (separate profile, see §7) |
| Unchanged `cube_validate` signature; local MCP and G5 Remote | Choosing, ranking or admitting a migration order (§5.18 Decision Trace; comparison of plan variants stays P1.9) |

## 1. Design summary

1. **New context version** `aiaeao.cube.binding-context/5`, a strict superset of /4 with two optional additions: `predicate_profile_refs` and `migration_plans`. Contexts in /1…/4 behave byte-identically.
2. **Migration predicate profile** `P1.10/migration-predicates-v1`: a closed set of predicate contracts (§3.1) shipped with the profile and imported by reference. Imported contracts are bound to the importing context's `scope_ref` (D-8). Context-local `predicate_contracts` stay possible; a local contract may not redefine an imported `predicate_id` (D-2).
3. **Phases:** an ordered list with exactly one `current` and one `target` phase and any number of `intermediate` phases.
4. **Transitions:** each retires and/or introduces referents at a phase boundary, carries a T qualifier with role `scheduling` (only; D-4) and a witness. A transition that retires X and introduces Y is the plan form of `rel("supersedes", Y, X) @T(...)`.
5. **Dependencies:** the inventory as data — subject, predicate, object, kind, the phases in which it holds, a witness (source location). Each is typed against the imported or local predicate contracts exactly as a P1.1 `rel(...)` would be.
6. **Checks** run after all P1.9 checks and only when `migration_plans` is present. The expression in `input_text` stays a normal P1 expression; plan checks are reported in the same report (D-5).

### 1.1 Shape (illustrative, synthetic, abridged)

Abridged: `context_id`, `source_kind`, `layers`/`provenance_status` of referents and local contracts are omitted for readability. All names are synthetic.

```json
{
  "format": "aiaeao.cube.binding-context/5",
  "reference_version": "v9.4",
  "scope_ref": "acme:migration",
  "predicate_profile_refs": ["P1.10/migration-predicates-v1"],
  "referents": [
    {"ref": "acme:contact-outbox", "concept_id": "Z:module-body:integration", "home": "Z"},
    {"ref": "acme:system-mailbox", "concept_id": "Y:resource-object:resource", "home": "Y"},
    {"ref": "acme:legacy-team-mail", "concept_id": "Z:module-body:provider", "home": "Z"},
    {"ref": "acme:legacy-system-mail", "concept_id": "Z:module-body:provider", "home": "Z"},
    {"ref": "acme:new-mail", "concept_id": "Z:module-body:provider", "home": "Z"}
  ],
  "migration_plans": [{
    "plan_id": "mp-mail", "revision": "draft:2026-10-26", "scope": "acme:migration", "origin": "external_declaration_unverified",
    "phases": [
      {"phase_id": "p0", "role": "current"},
      {"phase_id": "p1", "role": "intermediate"},
      {"phase_id": "p2", "role": "target"}
    ],
    "transitions": [
      {"transition_id": "t-team-mail", "at_phase": "p1", "retires": ["acme:legacy-team-mail"], "introduces": ["acme:new-mail"],
       "T": {"role": "scheduling", "value": "TBD"}, "witness_ref": "doc:example-contract#scope"},
      {"transition_id": "t-system-mail", "at_phase": "p2", "retires": ["acme:legacy-system-mail"], "introduces": [],
       "T": {"role": "scheduling", "value": "TBD"}, "witness_ref": "doc:example-contract#scope"}
    ],
    "dependencies": [
      {"dependency_id": "d-01", "subject": "acme:contact-outbox", "predicate_id": "sends-via", "object": "acme:legacy-system-mail",
       "kind": "job", "holds_in": ["p0", "p1"], "successor_ref": "d-01b", "witness_ref": "repo:example/outbox-job"},
      {"dependency_id": "d-01b", "subject": "acme:contact-outbox", "predicate_id": "sends-via", "object": "acme:new-mail",
       "kind": "job", "holds_in": ["p2"], "witness_ref": "plan:mp-mail#d-01b"},
      {"dependency_id": "d-07", "subject": "acme:system-mailbox", "predicate_id": "recovers-via", "object": "acme:legacy-team-mail",
       "kind": "account", "holds_in": ["p0", "p1"], "witness_ref": "repo:example/mailbox-config"}
    ]
  }]
}
```

`d-07` FAILs `P1_MIGRATION_DANGLING_DEPENDENCY`: it is declared to hold in `p1`, but its object is retired at `p1`. This is the ordering risk of the test case, now visible to P1.

## 2. Status and diagnostic rules

| Situation | Status | Diagnostic (new) |
|---|---|---|
| `predicate_profile_refs` names an unknown or unpinned profile | MCP error | `P1_MCP_CONFIG_INVALID` (existing) |
| A local `predicate_contracts` entry redefines an imported `predicate_id` (D-2) | MCP error | `P1_MCP_CONFIG_INVALID` (existing) |
| `predicate_profile_refs` present but the context has no `scope_ref` (D-8) | MCP error | `P1_MCP_CONFIG_INVALID` (existing) |
| `migration_plans[i].scope` differs from the context `scope_ref` (D-8) | UNRESOLVED | `P1_MIGRATION_SCOPE_MISMATCH` |
| Phases not exactly one `current` and one `target`, duplicate `phase_id`, or `current` not first / `target` not last | FAIL | `P1_MIGRATION_PHASES` |
| Transition, dependency or `successor_ref` names an undeclared phase, referent or dependency | UNRESOLVED | `P1_MIGRATION_REFERENCE_MISSING` |
| Dependency subject/object concept IDs not admitted by its predicate signature | FAIL | `P1_PREDICATE_SIGNATURE` (P1.1, reused) |
| A referent is retired at phase *p* and a dependency on it is declared to hold in *p* or later | FAIL | `P1_MIGRATION_DANGLING_DEPENDENCY` |
| A dependency on a retired referent ends at the retiring phase without `successor_ref` and without `"dropped": true` | UNRESOLVED | `P1_MIGRATION_SUCCESSOR_MISSING` |
| A successor dependency points at a referent that is not introduced by the plan or present in every phase it holds in | FAIL | `P1_MIGRATION_SUCCESSOR_INVALID` |
| A referent is introduced after a dependency on it is declared to hold | FAIL | `P1_MIGRATION_PREMATURE_DEPENDENCY` |
| A referent is retired twice, or retired before it is introduced | FAIL | `P1_MIGRATION_TRANSITION_CONFLICT` |
| Transition without T, with a T role other than `scheduling` (D-4), or without `witness_ref` | UNRESOLVED | `P1_QUALIFIER_PROFILE_MISSING` (existing) |
| Dependency without `witness_ref` | UNRESOLVED | `P1_EVALUATION_WITNESS_MISSING` (P1.8, reused) |
| `input_text` is `rel("supersedes", Y, X)` and the plan has no transition retiring X and introducing Y (D-5; only `supersedes` triggers this check in v1) | FAIL | `P1_MIGRATION_EXPRESSION_MISMATCH` |
| /5-only fields inside a /1…/4 context | MCP error | `P1_MCP_CONFIG_INVALID` (existing) |

Precedence follows P1.4-14, P1.6, P1.8 and P1.9: FAIL outranks UNRESOLVED, and NOT_EVALUATED is never PASS.

## 3. Rules in detail

### 3.1 Migration predicate profile (PP)

- PP-1: `P1.10/migration-predicates-v1` ships as a pinned JSON file with SHA-256 in `SHA256SUMS.txt`. Each entry is a P1.1 predicate contract shape with `origin: "profile_declaration_unverified"` — a new origin value accepted only inside /5 and only for imported entries, so /1…/4 origin enums stay untouched. Optionally the import may also carry a `library_ref` of the P1.8/P1.9 shape (`library_id`, `entry_id`, `revision`, `sha256`); the pinned file stays authoritative, and a SHA-256 mismatch between both is `P1_MCP_CONFIG_INVALID` (D-3).
- PP-2: Proposed initial set (D-1), all `direction: subject_to_object`:

| predicate_id | Subject concepts | Object concepts | Required qualifiers |
|---|---|---|---|
| `depends-on` | Integration, Actor, Runtime | Provider, ThirdPartyDependency, Resource | – |
| `sends-via` | Integration, Actor | Provider, ThirdPartyDependency | – |
| `syncs-with` | Integration | Provider, ThirdPartyDependency | – |
| `stores-in` | Integration, Resource | Provider, ThirdPartyDependency | – |
| `references` | Resource | Provider, ThirdPartyDependency, Resource | – |
| `hosted-by` | Integration, Runtime, Resource | Provider, ThirdPartyDependency | – |
| `recovers-via` | Resource | Provider, ThirdPartyDependency, Resource | – |
| `supersedes` | Provider | Provider, ThirdPartyDependency | T |

- PP-3: Concept IDs are the full Morphology IDs (`Z:module-body:integration`, …); the short names above are for reading only.
- PP-4: Predicates stay profile-local. Adoption into a later Morphology version is not implied. `supersedes` and `references` are reference-vocabulary names in P1.1 (§7.6.1.2); the profile gives them a signature as the registry requires, in a **narrowed** reading: `supersedes` here means one provider replacing another, not the correction or replacement of a record or assertion (R01-AC04). `Principal` is deliberately not admitted in v1, to stay clear of the reserved P1.7 (D-1); it can be added in a later profile revision.
- PP-5 (scope binding, D-8): an imported contract carries no fixed scope; on import its `scope` is set to the importing context's `scope_ref`. A context that imports a profile must declare `scope_ref`, and every `migration_plans[i].scope` must equal it.

### 3.2 Phases and transitions (PH, TR)

- PH-1: `phases` is ordered; order is the declared sequence, not chronology. No dates are compared; `T.value` stays uninterpreted (as P1.8 SC-4).
- TR-1: `retires` and `introduces` list referent refs declared in `referents`. A referent not introduced by any transition exists from `current` on; a referent not retired exists until `target`.
- TR-2: Each referent may be retired at most once and introduced at most once; introduce-before-retire is required when both happen.
- TR-3: Every transition carries T with role `scheduling` and a `witness_ref`. Other T roles, including `effective-interval`, are not admitted on transitions (D-4, Morphology §3.6: `effective-interval` qualifies bindings and rules; the validity window of a dependency is carried structurally by `holds_in`).

### 3.3 Dependencies (DP)

- DP-1: `holds_in` is a non-empty, contiguous run of declared phases.
- DP-2: Typing is the P1.1 predicate check against imported plus local contracts; subject and object must be declared referents.
- DP-3 (dangling): if the object is retired at phase *p*, `holds_in` must end before *p*.
- DP-4 (successor): a dependency ending at a retiring phase needs either `successor_ref` (a dependency with the same subject and predicate, holding from *p*) or `"dropped": true` with a `witness_ref`. Missing both is UNRESOLVED — a coverage gap, not an error.
- DP-5: `kind` ∈ {job, sync, dns, auth, account, api, data, docs, other} is a closed descriptive enum and drives no rule (D-6).
- DP-6: Optional `schedule` (string, e.g. `"every 1m"`) is carried through uninterpreted.

### 3.4 Report boundary

- The P1 report schema stays unchanged. The adapter envelope adds `migration_profile: "P1.10/migration-profile-v1"` (only for /5) and keeps `evaluation_performed_by_cube: false`.
- Plan diagnostics use JSON Pointers into `migration_plans[i].phases[j]`, `…transitions[k]`, `…dependencies[m]`.
- `canonical_admission`, `current_authority`, `epistemic_warrant` stay `NOT_EVALUATED`; `source_warrant` stays `declared_unverified`. A PASS plan is a consistent **declaration**, not a safe or executed migration.

## 4. Acceptance criteria

| AC | Requirement | Evidence (to be produced) |
|---|---|---|
| P1.10-01 | No change to Morphology v9.4, P0, frozen P1.1, report.schema.json, P1.6, P1.8 and P1.9 artifacts | `SHA256SUMS.txt` diff empty |
| P1.10-02 | /1…/4 behaviour byte-identical: P1.4 suite, F01–F25, R-01…R-13, S-01…S-17, C-01…C-20, all goldens | regression suite |
| P1.10-03 | `context-v5.schema.json` published; strict superset of /4; /5 fields rejected in /1…/4 | schema tests, M-20 |
| P1.10-04 | Predicate profile rules PP-1…PP-5, pinned file, scope binding | M-02, M-03, M-21 + config tests |
| P1.10-05 | Phase and transition rules PH-1, TR-1…TR-3 | M-04…M-08, M-22 |
| P1.10-06 | Dependency rules DP-1…DP-6 | M-09…M-17 |
| P1.10-07 | Every row in §2 yields exactly the stated status and code | one test per row |
| P1.10-08 | Non-promotion (§3.4) asserted in every positive test | assertion in every PASS test |
| P1.10-09 | Deterministic JSON-Pointer diagnostics, ordered by plan, then dependency index | snapshot tests |
| P1.10-10 | New codes in `DIAGNOSTIC_EXTENSION.json` and `RULE_COVERAGE.json` with Morphology references | file diff |
| P1.10-11 | Independent oracle for M-01…M-22, transcribed before execution | `oracles/independent_m01_m22.json` |
| P1.10-12 | Local MCP and G5 Remote return identical reports for M-01…M-22 | adapter parity test |
| P1.10-13 | **Observable deploy:** `cube_discover_surface` gains a `p110_migration` descriptor; remote version bumped | live discover check |
| P1.10-14 | One synthetic golden plan with ≥ 15 dependencies, ≥ 3 phases, ≥ 1 dangling dependency in a negative control and its corrected PASS variant; no client names, domains, mailboxes or repository paths (D-7) | `fixtures/golden_migration_synthetic.json` |

`PASS` in this matrix means the listed test ran successfully. It does not mean that a dependency exists, that the inventory is complete, or that a migration order is safe.

## 5. Alignment vectors (exit check)

Base case M-01: three phases (current, intermediate, target); one transition at `p1` retiring `old` and introducing `new`; dependency `d1` (`job → old`, holds in `p0`) with `successor_ref` `d2` (`job → new`, holds in `p1`, `p2`); all witnesses present; profile imported.

| ID | Case | Expected overall |
|---|---|---|
| M-01 | Base case | PASS |
| M-02 | M-01 with unknown profile ref | MCP error · `P1_MCP_CONFIG_INVALID` |
| M-03 | M-01 with a local contract redefining `depends-on` | MCP error · `P1_MCP_CONFIG_INVALID` |
| M-04 | No `target` phase | FAIL · `MIGRATION_PHASES` |
| M-05 | `target` not last | FAIL · `MIGRATION_PHASES` |
| M-06 | Transition at undeclared phase | UNRESOLVED · `MIGRATION_REFERENCE_MISSING` |
| M-07 | `old` retired twice | FAIL · `MIGRATION_TRANSITION_CONFLICT` |
| M-08 | Transition without T | UNRESOLVED · `QUALIFIER_PROFILE_MISSING` |
| M-09 | `d1` holds in `p0`, `p1` | FAIL · `MIGRATION_DANGLING_DEPENDENCY` |
| M-10 | `d1` without `successor_ref` | UNRESOLVED · `MIGRATION_SUCCESSOR_MISSING` |
| M-11 | M-10 with `"dropped": true` and witness | PASS |
| M-12 | `d2` points at a referent that is itself retired at `p2` while `d2` holds in `p2` | FAIL · `MIGRATION_SUCCESSOR_INVALID` |
| M-13 | `d2` holds in `p0` (before `new` is introduced) | FAIL · `MIGRATION_PREMATURE_DEPENDENCY` |
| M-14 | `d1` subject typed `Resource` with `sends-via` | FAIL · `PREDICATE_SIGNATURE` |
| M-15 | `d1` without witness | UNRESOLVED · `EVALUATION_WITNESS_MISSING` |
| M-16 | `holds_in` not contiguous (`p0`, `p2`) | FAIL · `MIGRATION_PHASES` |
| M-17 | Recovery case: `mailbox recovers-via old`, holds in `p0`, `p1` | FAIL · `MIGRATION_DANGLING_DEPENDENCY` |
| M-18 | `input_text` = `rel("supersedes", new, old) @T(scheduling)` with M-01 | PASS |
| M-19 | M-18 with reversed arguments | FAIL · `PREDICATE_SIGNATURE` |
| M-20 | `migration_plans` inside a /4 context | MCP error · `P1_MCP_CONFIG_INVALID` |
| M-21 | M-01 with `migration_plans[0].scope` ≠ `scope_ref` | UNRESOLVED · `MIGRATION_SCOPE_MISMATCH` |
| M-22 | M-01 with the transition T role `effective-interval` | UNRESOLVED · `QUALIFIER_PROFILE_MISSING` |

Not expected to change, stated explicitly: whether a declared dependency exists live; completeness of the inventory; whether a cutover happened; which order is better (that remains a P1.9 comparison of plan variants).

## 6. Decisions (resolved 2026-10-26)

| Decision | Options | Resolution | Consequence |
|---|---|---|---|
| D-1 Initial predicate set | (a) the eight of PP-2 · (b) only `depends-on`, `supersedes`, `references` (as tested) · (c) open set, context-defined | **(a)**, without `Principal` in `recovers-via`; `supersedes` in the narrowed reading of PP-4 | Covers mail, storage, chat and account recovery from the test case; stays clear of the reserved P1.7; no clash with the record-history sense of `supersedes`. |
| D-2 Local redefinition of imported predicates | (a) forbidden · (b) local overrides import | **(a)** | Signatures cannot drift between contexts that claim the same profile. |
| D-3 Profile location | (a) pinned file in `P1/migration-profile-v1/` · (b) Functions Library entry via `library_ref` · (c) both, library optional | **(c)**; `library_ref` in the P1.8/P1.9 shape, pinned file authoritative, SHA-256 mismatch is a config error | Works now; can move into `lunados.lib` without a format change. |
| D-4 T roles for transitions | (a) `scheduling` only · (b) `scheduling` or `effective-interval` | **(a)** — deviates from the draft proposal | Morphology §3.6 binds `effective-interval` to bindings and rules; a dependency's validity window is already `holds_in`. Admitting another role later needs a profile revision (M-22). |
| D-5 Relation of `input_text` to the plan | (a) plan checks run for any expression · (b) only when the expression references a plan referent · (c) a dedicated no-op expression | **(a)** + consistency check, triggered only by `supersedes` in v1 (M-18/M-19) | One call validates the whole inventory; a `supersedes` claim cannot contradict its plan; other expressions stay ordinary P1 expressions. |
| D-6 Dependency `kind` | (a) descriptive enum, no rules · (b) kind-specific rules (e.g. `job` needs `schedule`) | **(a)** | Keeps P1.10 structural; kind-specific rules can follow from use. |
| D-7 Golden fixture source | (a) synthetic plan modelled on the test case, no client names · (b) real client inventory | **(a)**; also no client repository paths (example in §1.1 made synthetic) | The Cube repository and `cube.lunados.net` are reference material; client data stays out. A real inventory is validated through the context at run time only. |
| D-8 Scope of imported predicates (added in review) | (a) imported contracts take the importing context's `scope_ref` · (b) the profile carries a fixed scope that contexts must adopt | **(a)** + `migration_plans[i].scope == scope_ref` (PP-5, M-21) | The P1.1 validator selects contracts only by `scope == scope_ref`; a fixed profile scope would never match. Plan and context scope cannot diverge silently. |

## 7. Related, not part of P1.10

- **P2:** predicate-specific edge styles (today `supersedes` and `depends-on` render identically as neutral reference arrows) and materialised multi-panel export when a budget overflows. To be specified separately as a P2 profile.
- **P1.9 reuse:** alternative migration orders can be declared as P1.9 comparisons of plan variants once P1.10 plans exist.
