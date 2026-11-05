# P1.15 — Scope Nesting and Admission Outcomes Profile · Acceptance specification

**Status:** SPECIFIED for TASK-076 (2026-11-05). MILE-015 decisions D-1…D-5 apply; detail questions Q-1…Q-4 resolved below.
**Numbering:** New profile `P1.15/scope-nesting-profile-v1`, context `aiaeao.cube.binding-context/11`, directory `P1/scope-nesting-profile-v1/`. Builds on P1.14 (`binding-context/10`).
**Basis:** Morphology v9.4 (no change); Morphology 01.3 cross-axis readings X × Z (Γ: "inherits Project defaults, may narrow"), Z × T (Admission "decided per concrete request", "must be current at execution"); P1.6 (`instantiation_reference_v1.json`, conditions C-ADM-1/2, scoped profile selection); P1.13 (exclusive gateways, CF-1…CF-5).
**Motivation:** Findings from lunados.explorer E8 (MILE-015 B1–B3):

| Finding | Effect today |
|---|---|
| A plan relation `gated-by(core, admission)` lives in the sheet scope; the bound Admission lives in its Policy scope | after binding, `P1_SCOPE_CONFLICT` twice (referent binding and scope consistency); before binding `P1_INSTANTIATION_PROFILE_REQUIRED` |
| Policies inherit and narrow (organisation ⊃ project ⊃ thread ⊃ request) | one validation scope per context, no declared relation between scopes |
| The Authority of a version approval applies to one Revision | `resource_scope_ref` admits only Resource, Project and Thread boundary |
| A migration describes the admitted and the refused path | P1.6 binds one decision per instance; nothing ties the outcomes of one request together |

P1.15 lets a context **declare** which X scope lies in which, accepts an X endpoint whose scope reaches the validation scope through such a chain, checks the endpoint with P1.6 in its own pair scope, widens the Authority resource scope by Revision and Artifact (reference v2), and ties the outcomes of one Admission request to an exclusive gateway. P1 never decides whether an inner scope is actually narrower (D-4).

## 0. Scope

| In scope | Out of scope |
|---|---|
| `scope_nesting[]`: declared chains of X scopes ending in the context scope | Comparing policy contents; inferring nesting; nesting of Y or Z referents (Z placement such as *hosted-by* is not a scope chain) |
| Relation endpoints that are X endpoints in a nested scope | Plan-level checks of P1.10…P1.14 (unchanged) |
| P1.6 reference v2 for `/11` (Authority `resource_scope_ref` + Revision, Artifact) | Any other slot change; `/2…/10` keep reference v1 |
| Admission outcomes as targets of one exclusive gateway | Evaluating conditions or deciding which outcome holds |
| Local G4 dispatch and discovery | Printer (MILE-016), G5 (own step) |

## 1. Design summary

1. **New context version** `aiaeao.cube.binding-context/11`, a strict superset of `/10` with one new optional field `scope_nesting`. `/1…/10` stay byte-identical. The validator projects `/11` to `/10` (drops `scope_nesting`, narrows instantiation profiles to reference v1), runs P1.14 unchanged and then supersedes the X-endpoint binding results for relation endpoints (§2) and adds outcome checks (§3).
2. **Scope chains** are pairs `{"inner": <X scope ref>, "outer": <X scope ref or the context scope_ref>}` (Q-1: one parent per inner scope; Q-2: kinds may mix, e.g. an Event scope inside a Policy scope — the check is structural only).
3. **Reference v2** (`instantiation_reference_v2.json`, pinned by SHA-256 in `cube_p115`) equals v1 except that the Authority slot `resource_scope_ref` also admits `Y:resource-object:revision` and `Y:resource-object:artifact`.
4. **Admission outcomes** (Q-3): each outcome is its own P1.6 instance; the branch is an exclusive gateway of P1.13 whose outgoing targets are those instances. A migration-plan dependency points at the admitted outcome (Q-4); the gateway names the others.

### 1.1 Shape (illustrative, synthetic)

```json
{
  "format": "aiaeao.cube.binding-context/11",
  "scope_ref": "ctx:sheet",
  "scope_nesting": [
    {"inner": "x:policy/project", "outer": "x:policy/org"},
    {"inner": "x:policy/org", "outer": "ctx:sheet"}
  ],
  "control_flow": {"gateways": [
    {"gateway": "g:decide", "type": "exclusive", "incoming": ["f:in"],
     "outgoing": [{"flow": "f:yes", "target": "adm:yes", "order": 1}, {"flow": "f:no", "target": "adm:no", "default": true}]}
  ]}
}
```

- `rel("gated-by", Z:α:Core["mod.core"], X:α:Admission["adm:yes"])` with `adm:yes` in scope `x:policy/project` → PASS when its P1.6 slots are complete.

## 2. Scope nesting rules (SN)

- **SN-1 (shape, configuration error):** `scope_nesting` is an array of ≤ 512 objects with exactly `inner` and `outer`, both nonempty strings ≤ 512; `inner ≠ outer`; each `inner` occurs at most once.
- **SN-2 (declared ends):** every `inner` is a declared referent whose concept starts with `X:scope:` and whose `scope_ref` is its own ref; every `outer` is the context `scope_ref` or such an X scope referent. Otherwise FAIL `P1_SCOPE_NESTING_INVALID` with pointer `/scope_nesting/i`.
- **SN-3 (chain):** following `outer` from any `inner` must reach the context `scope_ref` without revisiting a scope. A cycle or a chain that ends elsewhere is FAIL `P1_SCOPE_NESTING_INVALID`.
- **SN-4 (binding):** for a relation endpoint whose referent is an `X:endpoint:*` with `scope_ref ≠` the validation scope: if its scope reaches the validation scope by a valid chain (SN-2, SN-3), the two `P1_SCOPE_CONFLICT` diagnostics of the lower layers for that endpoint are superseded and the endpoint is checked by P1.6 (reference v2) in its own pair scope; P1.6 diagnostics are reported as usual. Without such a chain the conflict stays.
- **SN-5 (limits):** nesting never rescues Y or Z referents, X scope referents used directly as endpoints, or predicate contracts from foreign scopes.
- **SN-6 (reference v2):** in `/11` every X endpoint check uses reference v2; instantiation profiles must not widen v2 (configuration error otherwise). The `/10` projection narrows each profile to v1 so that the unchanged lower layers accept it.
- **SN-7:** SN checks run on every validation of a `/11` context, like the P1.14 plan checks; context-level findings use stage `scope_consistency`.

## 3. Admission outcome rules (AO)

- **AO-1:** an exclusive gateway with two or more outgoing targets of concept `X:endpoint:admission` declares the outcomes of one request: all such targets carry the same `request_ref` slot, and at most one has `decision = admitted`. Otherwise FAIL `P1_ADMISSION_OUTCOME_CONFLICT` with pointer `/control_flow/gateways/i`.
- **AO-2:** every such outcome is checked by P1.6 (reference v2, its pair scope, SN-4); C-ADM-1/2 apply per outcome.
- **AO-3:** parallel gateways and gateways with fewer than two Admission targets are not affected.

## 4. Status and diagnostics

| Situation | Status | Diagnostic |
|---|---|---|
| Invalid nesting declaration (SN-2, SN-3) | FAIL | `P1_SCOPE_NESTING_INVALID` (new), stage `scope_consistency` |
| Outcomes with different requests or two admitted (AO-1) | FAIL | `P1_ADMISSION_OUTCOME_CONFLICT` (new), stage `referent_binding` |
| X endpoint in a foreign scope without valid chain | FAIL | `P1_SCOPE_CONFLICT` (unchanged) |
| P1.6 findings in the pair scope | as P1.6 | P1.6 codes (reused) |
| Malformed `/11` field, profile widening v2 | configuration error | as P1.14 |

FAIL outranks UNRESOLVED. `epistemic_warrant`, `current_authority`, `canonical_admission` stay `NOT_EVALUATED`.

## 5. Vectors (SN-01…SN-14, synthetic)

One synthetic base context (scope `ctx:sheet`): Z Core `mod.core`; Y Actor `act:holder`, `act:caller`; Y Principal `pr:person`; Z Grant `gr:key`; Y Resource `res:store`; Y Revision `rev:v1`; X scopes `x:policy/org`, `x:policy/project` (Policy), `x:event/call` (Event); X Action `act-call` (Event scope), Authority `auth` (Policy `x:policy/project`), Admission `adm` (Policy `x:policy/project`, admitted with complete slots); predicate `gated-by` Core → Admission in `ctx:sheet`. Input: `rel("gated-by",Z:α:Core["mod.core"],X:α:Admission["adm"])` unless stated.

| ID | Case | Expected | Required | Forbidden |
|---|---|---|---|---|
| SN-01 | base without `scope_nesting` | FAIL | `P1_SCOPE_CONFLICT` | `P1_SCOPE_NESTING_INVALID` |
| SN-02 | `x:policy/project` ⊂ `ctx:sheet` | PASS | – | `P1_SCOPE_CONFLICT` |
| SN-03 | `x:policy/project` ⊂ `x:policy/org` ⊂ `ctx:sheet` | PASS | – | `P1_SCOPE_CONFLICT` |
| SN-04 | chain ends in an undeclared scope `x:elsewhere` | FAIL | `P1_SCOPE_NESTING_INVALID` | – |
| SN-05 | cycle `org` ⊂ `project` ⊂ `org` | FAIL | `P1_SCOPE_NESTING_INVALID` | – |
| SN-06 | `inner` names the Z referent `mod.core` | FAIL | `P1_SCOPE_NESTING_INVALID` | – |
| SN-07 | SN-02 with `principal_ref` removed from `adm` | UNRESOLVED | `P1_INSTANTIATION_SLOT_MISSING` | `P1_SCOPE_CONFLICT` |
| SN-08 | SN-02 with `authority_ref` removed (admitted) | FAIL | `P1_INSTANTIATION_CONDITION` | `P1_SCOPE_CONFLICT` |
| SN-09 | SN-02, Authority `resource_scope_ref` = `rev:v1` (reference v2) | PASS | – | `P1_INSTANTIATION_SLOT_TYPE` |
| SN-10 | SN-02 plus refused outcome `adm-no` (same request, `refusal_ref` Z Refusal) and an exclusive gateway with both | PASS | – | `P1_ADMISSION_OUTCOME_CONFLICT` |
| SN-11 | SN-10 with a different `request_ref` on `adm-no` | FAIL | `P1_ADMISSION_OUTCOME_CONFLICT` | – |
| SN-12 | SN-10 with `adm-no` also admitted (with authority) | FAIL | `P1_ADMISSION_OUTCOME_CONFLICT` | – |
| SN-13 | SN-10 with `refusal_ref` removed from `adm-no` | FAIL | `P1_INSTANTIATION_CONDITION` | `P1_ADMISSION_OUTCOME_CONFLICT` |
| SN-14 | SN-02, relation object is the Y Resource `res:store` with foreign `scope_ref` `x:policy/project` (predicate widened to Resource) | FAIL | `P1_SCOPE_CONFLICT` | – |

## 6. Acceptance

| ID | Criterion | Evidence |
|---|---|---|
| P1.15-01 | Oracle `oracles/independent_sn01_sn14.json` committed before runtime code; SN-01…SN-14 match | `tests/test_p115.py` |
| P1.15-02 | `/1…/10` reports byte-identical (P1.14 HO vectors, P1.6 fixture, P1.13 KF vectors) | regression test |
| P1.15-03 | Configuration errors: malformed `scope_nesting`, duplicate `inner`, profile widening v2 | tests |
| P1.15-04 | Reference v2 pinned; differs from v1 only in Authority `resource_scope_ref` | test |
| P1.15-05 | G4 dispatches `/11`; discovery lists the two new codes | P3 test |
| P1.15-06 | lunados.explorer: F05 and F03a relations to bound Admissions without `P1_SCOPE_CONFLICT`; all five sheets still P1 PASS for their plans | explorer print run |

## 7. Decisions on detail questions

| ID | Question | Decision |
|---|---|---|
| Q-1 | One or several parents per scope | One (`inner` unique); inheritance is a tree |
| Q-2 | Mixed scope kinds in a chain | Allowed; structural check only (D-4) |
| Q-3 | Where do outcomes live | P1.6 instances + P1.13 exclusive gateway (D-5); no new P1.6 field |
| Q-4 | What does `gated-by` in a plan point to | The admitted outcome; the gateway names the others |
