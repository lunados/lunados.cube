# P1.14 — Declared Relation Origin Profile · Acceptance specification

**Status:** SPECIFIED. MILE-011 decisions D-1…D-8 apply (2026-11-02); detail questions Q-1…Q-9 resolved 2026-11-02 (all as proposed). Not implemented.
**Numbering:** New profile `P1.14/relation-origin-profile-v1`, context `aiaeao.cube.binding-context/10`, directory `P1/relation-origin-profile-v1/`. Builds on P1.13 (`binding-context/9`). P1.7 stays reserved.
**Basis:** Morphology v9.4 (no change); `relations.json` `qualified_relation_form` (`Rel(subject, predicate, object; {…, origin?, evidence?, …})`); P1.4 contract notes (a relation with parameters is UNRESOLVED without a typed parameter contract); MILE-002 gap ledger G-02 and reports C4-02, C4-03; MILE-007 statement sets and LIB `project.aggregate-relations/v1` (derived statements with `origin` and `derived_from`); MILE-011 decisions (`docs/02-Milestones/MILE-011-relation-origin.md`).
**Motivation:** Findings of MILE-002 (C4-03, all synthetic):

| Finding | Effect today |
|---|---|
| A condensed relation is written like a declared one | `rel("uses", Boundary[api], Boundary[db])`: PASS, although `api → db` exists only as an implied relation |
| The form of `relations.json` has no contract | `rel("uses", …; origin="derived")`: UNRESOLVED · `P1_PREDICATE_PROFILE_MISSING` |
| Marking needs a separate predicate | `uses.derived` with a required qualifier works only if the author chooses it; nothing enforces it |
| `provenance_status` exists only for referents | the origin of a relation is never bound |

P1.14 binds the **origin of a relation** (`declared`, `derived`, `unknown`) and, for `derived`, its **basis**. P1 checks the declaration; it never computes an origin, never derives a relation and never compares with a foreign model (D-2, D-3; MILE-011 "Rahmenbedingungen").

## 0. Scope

| In scope | Out of scope |
|---|---|
| Typed relation parameters `origin` and `basis` for predicates that opt in | Any other relation parameter (stays UNRESOLVED as in P1.4) |
| Declared bases: source statements or a lunados.lib projection record, read only | Recomputing an aggregation; checking a basis against a foreign model |
| Origin on migration-plan dependencies and on statement-set entries (resolution rules, §3 OR-6, OR-7) | Rendering (VP-07.6, own spec) |
| Local G4 and discovery; G5 in TASK-067 | Truth of `declared` (a false `declared` is not detectable here) |

## 1. Design summary

1. **New context version** `aiaeao.cube.binding-context/10`, a strict superset of `/9` with no new required fields. `/10` activates P1.14 rules; `/1…/9` stay byte-identical. The validator projects `/10` to `/9`, runs P1.13 unchanged and adds the origin checks (as P1.13 over P1.12).
2. **Opt-in per predicate.** A predicate contract may carry `origin_binding: "required"` (Q-1). For such a predicate, a relation must carry the parameter `origin`; the parameters `origin` and `basis` are typed, all others stay as before.
3. **Values** `origin ∈ {declared, derived, unknown}` (Q-2). `unknown` is a valid, honest declaration; a missing origin is not.
4. **Bases.** `/10` adds an optional list `origin_bases[]`. A basis is either a list of source statements (IDs of a declared statement set) or a lunados.lib projection record, identified by its digest and `library_ref` (Q-3, Q-4). A `derived` relation names one basis with `basis="<basis_id>"`.
5. **Diagnostics** follow P1.12/P1.13: context checks after all P1.13 checks; FAIL outranks UNRESOLVED; JSON Pointers into `origin_bases/i`.

### 1.1 Shape (illustrative, synthetic)

```json
{
  "format": "aiaeao.cube.binding-context/10",
  "predicate_contracts": [
    {"predicate_id": "uses", "subject_concept_ids": ["Z:boundary:boundary"], "object_concept_ids": ["Z:boundary:boundary"],
     "direction": "subject_to_object", "origin_binding": "required"}
  ],
  "origin_bases": [
    {"basis_id": "b-api-db", "kind": "statements", "set_id": "c4-shop", "statement_ids": ["s-1", "s-2"], "witness_ref": "synthetic:c4#shop"},
    {"basis_id": "b-agg", "kind": "projection_record", "record_sha256": "<sha256>", "statement_id": "d-1",
     "library_ref": {"library_id": "lunados.lib", "entry_id": "project.aggregate-relations", "revision": 1, "sha256": "<INDEX value>"}}
  ]
}
```

- `rel("uses", Z:α:Boundary["c4:shop/api"], Z:α:Boundary["c4:shop/db"])` → UNRESOLVED · `P1_ORIGIN_UNDECLARED`
- `rel("uses", …; origin="derived", basis="b-api-db")` → PASS
- `rel("uses", …; origin="derived")` → UNRESOLVED · `P1_ORIGIN_BASIS_MISSING`
- `rel("uses", …; origin="inferred")` → FAIL · `P1_ORIGIN_INVALID`

## 2. Status and diagnostic rules (P1)

| Situation | Status | Diagnostic |
|---|---|---|
| Predicate with `origin_binding: required`, relation without `origin` | UNRESOLVED | `P1_ORIGIN_UNDECLARED` (new) |
| `origin` outside {`declared`, `derived`, `unknown`}, or not a string | FAIL | `P1_ORIGIN_INVALID` (new) |
| `origin="derived"` without `basis` | UNRESOLVED | `P1_ORIGIN_BASIS_MISSING` (new) |
| `basis` with `origin` `declared` or `unknown` | FAIL | `P1_ORIGIN_INVALID` |
| `basis` names no declared `origin_bases` entry | UNRESOLVED | `P1_BINDING_CONTEXT_REQUIRED` (existing) |
| A parameter other than `origin` and `basis`, or `origin`/`basis` on a predicate without `origin_binding` | UNRESOLVED | `P1_PREDICATE_PROFILE_MISSING` (existing, unchanged) |
| Malformed `origin_bases` (schema, duplicate `basis_id`, statement IDs not unique) | MCP error | `P1_MCP_CONFIG_INVALID` (existing) |
| Any P1.14 field inside a `/1…/9` context | MCP error | `P1_MCP_CONFIG_INVALID` (existing) |
| All P1.13 rows | unchanged | unchanged |

## 3. Rules in detail

**Origin (OR)**
- OR-1: `origin_binding` is either absent or `"required"`. Absent: P1.13 behaviour, including UNRESOLVED for any parameter.
- OR-2: With `origin_binding: required`, the relation's parameters may be exactly `origin`, or `origin` and `basis`. `origin` is a string from the closed set.
- OR-3: `derived` requires `basis`; `declared` and `unknown` forbid it.
- OR-4: `basis` resolves to exactly one `origin_bases` entry. P1 checks the entry's shape only: `kind` `statements` needs `set_id` and a non-empty `statement_ids`; `kind` `projection_record` needs `record_sha256`, `statement_id` and a `library_ref` of the shape of MILE-007 Q-10. P1 never opens a set or a record.
- OR-5: Origin is independent of the predicate: `uses` may be declared or derived; a separate derivation predicate (`uses.derived`) remains possible and is not required.
- OR-6 (plans): In `/10`, a migration-plan dependency may carry `origin` and `basis` with the same rules; for a predicate with `origin_binding: required` a dependency without `origin` is reported as UNRESOLVED · `P1_ORIGIN_UNDECLARED` with a pointer to the dependency (Q-6).
- OR-7 (statement sets): `aiaeao.cube.statement-set/2` is `/1` plus optional `origin` and `basis` per statement; the same OR-2…OR-4 apply when a printer resolves the set against a `/10` context (resolution, not a P1 verdict; Q-5).

## 4. Acceptance criteria

| AC | Requirement | Evidence |
|---|---|---|
| P1.14-01 | No change to Morphology, P0, P1.1…P1.13 artifacts; `SHA256SUMS` diff empty | file diff |
| P1.14-02 | `/1…/9` byte-identical, including all previous vector suites, goldens and G4/G5 parities | regression suite |
| P1.14-03 | `context-v10.schema.json` strict superset of `/9`; `statement-set/2` strict superset of `/1` | schema tests |
| P1.14-04 | OR-1…OR-7 | vectors HO-01…HO-12 (§5) |
| P1.14-05 | Every row in §2 yields exactly the stated status and code | one test per row |
| P1.14-06 | Independent oracle for HO-01…HO-12, committed before code (TASK-064) | `oracles/independent_ho01_ho12.json` |
| P1.14-07 | Local G4: `cube_validate` accepts `/10`; discovery lists `binding-context/10` with entry profile `P1.14/relation-origin-profile-v1` and the three new codes | adapter test |
| P1.14-08 | Synthetic golden with declared, derived (both basis kinds) and unknown relations, no client data | `fixtures/golden_relation_origin.json` |

## 5. Vectors (planned; fixed in TASK-064)

| ID | Case | P1 (`cube_validate`, `/10`) |
|---|---|---|
| HO-01 | C4-03 `api → db` without origin | UNRESOLVED · `ORIGIN_UNDECLARED` |
| HO-02 | HO-01 with `origin="derived", basis="b-api-db"` (statements) | PASS |
| HO-03 | HO-01 with `origin="derived", basis="b-agg"` (projection record of C4-02) | PASS |
| HO-04 | `origin="derived"` without basis | UNRESOLVED · `ORIGIN_BASIS_MISSING` |
| HO-05 | `origin="inferred"` | FAIL · `ORIGIN_INVALID` |
| HO-06 | `origin="declared", basis="b-api-db"` | FAIL · `ORIGIN_INVALID` |
| HO-07 | `origin="unknown"` | PASS |
| HO-08 | C4-02 source statement `order-controller → db`, `origin="declared"` | PASS |
| HO-09 | `basis="b-ghost"` (not declared) | UNRESOLVED · `BINDING_CONTEXT_REQUIRED` |
| HO-10 | predicate without `origin_binding`, relation with `origin` | UNRESOLVED · `PREDICATE_PROFILE_MISSING` (as today) |
| HO-11 | `/9` context KF-01 unchanged (regression) | PASS |
| HO-12 | migration plan in `/10`, one dependency without origin (OR-6) | UNRESOLVED · `ORIGIN_UNDECLARED` |

## 6. Boundaries

- A wrong `origin="declared"` passes. Detecting it needs a comparison with the source model (adapter or LIB), outside MILE-011.
- P1 does not check that a basis really yields the relation; it checks that a basis is named and well-formed. A printer that reads a projection record checks its digest and shape (MILE-007 Q-10), never recomputes it.
- Everything stays `declared_unverified`; `epistemic_warrant`, `current_authority`, `canonical_admission` stay `NOT_EVALUATED`.

## 7. Detail questions (resolved 2026-11-02, all as proposed)

| ID | Question | Decision | Reason |
|---|---|---|---|
| **Q-1** | Where is origin switched on? | Predicate contract field **`origin_binding: "required"`**; no global switch | opt-in per predicate, as `control_flow_role` in P1.13; other predicates keep their behaviour |
| **Q-2** | Which values? | **`declared`, `derived`, `unknown`**, closed | M-01A and C4-03; `unknown` keeps the honest case visible |
| **Q-3** | How is a basis named in ACG? | Parameter **`basis="<basis_id>"`** referring to a declared `origin_bases` entry | ACG parameters are scalars; the context carries the structure |
| **Q-4** | Which basis kinds? | **`statements`** (set ID and statement IDs) and **`projection_record`** (record digest, statement ID, `library_ref`) | covers hand-written sources and the MILE-007 aggregation |
| **Q-5** | How do statement sets carry origin? | **`aiaeao.cube.statement-set/2`** = `/1` + optional `origin`, `basis` per statement; `/1` unchanged | keeps VP-10 0.11.0 byte-identical; the printer of VP-07.6 reads `/2` |
| **Q-6** | Do plan dependencies get origin? | **Yes, optional fields** `origin`, `basis` on dependencies in `/10`, same rules (OR-6) | D-4: origin in plans and in statements |
| **Q-7** | Codes? | `P1_ORIGIN_UNDECLARED` (UNRESOLVED), `P1_ORIGIN_BASIS_MISSING` (UNRESOLVED), `P1_ORIGIN_INVALID` (FAIL) | the working titles of D-2, D-3 |
| **Q-8** | Origin on the derivation predicate `uses.derived`? | Allowed and checked like any other predicate; **no implicit origin from the predicate name** | no hard-coded predicate names (as P1.13 Q-4) |
| **Q-9** | Relation to P1.13? | `/10` strict superset of `/9`; validator projects `/10` → `/9`, runs P1.13 unchanged, then OR | same pattern as P1.13 over P1.12 |
