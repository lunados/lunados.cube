# VP-09.3 — X × Y from declared instances and the status of a crossing · Acceptance specification

**Status:** SPECIFIED for TASK-078 (2026-11-05). Decisions D-1…D-6 confirmed by the user as proposed; vectors X-01…X-12 below, oracle `oracles/independent_x01_x12.json` before code. 0.9.0…0.9.2 are pinned by the existing goldens and regression digests (`golden_axes.json`, `golden_v092.json`, `regression_090_digests.json`, `regression_091_digests.json`).
**Profile:** `P2-VP-AXES/0.9.3`, follow-up to `0.9.2` in `vpaxes`; opt-in via `from-plan --profile`. `0.9.0…0.9.2` byte-identical.
**Basis:** Morphology v9.4 §3.3 (X × Y is the canonical Dimension × Identity Anchor matrix; blank cells impose no relation); Morphology 01.3 cross-axis matrices (status canonical / illustrative / derived per crossing); P1.6 instantiation profiles and slots; VP-09 CM table, D-2 pair list, budgets; VP-09.1 binding ledger.
**Motivation:** lunados.explorer binds X endpoints (Admission, Authority, Action) with P1.6 slots (E8, MILE-015). The plan views draw the endpoint but not who acts under it: the X × Y reading (Γ × Principal = authenticated identity for Admission; Π × Actor = performed-by; Γ × Actor = holder of an Authority) is invisible, and so are slots the instance leaves open.

## 0. Scope

| In scope | Out of scope |
|---|---|
| Pair **X × Y**: rows X dimensions (Ψ Γ Σ Ξ Π), columns Y kinds or Y referents | X × Y from facets or lenses (X × X / X × Z keep their rules) |
| Entries from declared P1.6 slots of X endpoints whose target is a Y referent | Slots targeting Z (Grant, Refusal) or X (they belong to X × Z and X × X, B11/B12) |
| Required Y-typed slots that the instance leaves absent, as entries marked "absent" | Judging why a slot is absent; P1.6 statuses (P1 decides) |
| Status line of the crossing on every 0.9.3 panel (B10) | Changing pairs or rules of 0.9.0…0.9.2 |

## 1. Design

1. **Input.** `from-plan --profile P2-VP-AXES/0.9.3` accepts `binding-context/7…/10`, derives the source with the unchanged VP-07 adapter under `P2-VP-MIGRATION/0.7.8` (the profile that maps X endpoints) and writes the 0.9.2 axes input plus `x_instances[]`: one entry per X endpoint referent that a dependency of the plan slice names, and per X endpoint reached from it through slots (e.g. the request Action and the Authority of an Admission). Each entry: display ID, concept, dimension, and its slots as `{slot, target, target_kind}` for Y targets, plus `{slot, absent: true, kinds}` for a required slot whose descriptor admits Y concepts and that the instance does not carry (descriptor from the context's `instantiation_profiles`). Context `binding-context/10` (instances and profiles are allowed from `/2` on).
2. **Dimension of an endpoint** follows its pair scope (Morphology §6.2): Ψ Observation (Perception, Conclusion), Γ Policy (Authority, Admission), Σ Conversation (Expectation, Satisfaction), Ξ Contract (Delegation, Completion), Π Event (Action, Result).
3. **Cell rule (CM-X):** cell (dimension r, Y value c) lists, for every X endpoint of dimension r, each slot whose target is c (or whose target's kind is c), as `<endpoint> · <slot>`; an absent required slot is listed in the column of the first admitted Y kind as `<endpoint> · <slot> · absent`. Declared fields only, no closure.
4. **Ledger (XL):** every Y-typed slot entry and every absent required Y slot is drawn exactly once or named as out of budget; report and embedded ledger prove it.
5. **Status line (B10):** every 0.9.3 panel names its crossing, the status and the source, e.g. `X × Y · canonical · Morphology §3.3`. Status table (D-3): X × Y canonical (§3.3); X × X illustrative (Annex D.3); X × Z, Y × Z, Y × T, Z × T derived (01.3); Y × Y not listed in 01.3 (`unlisted`); F pairs illustrative (MEAS · FUNC, §3.9).

## 2. Decisions (confirmed 2026-11-05)

| ID | Question | Proposal |
|---|---|---|
| D-1 | Columns | `Y:kind` default (anchor order of AX-3); `Y:referent` allowed as in VP-09 |
| D-2 | Which endpoints | Those named in the plan slice and those reached through their slots; others in the context are ignored and counted in the report |
| D-3 | Status values | `canonical`, `illustrative`, `derived`, `unlisted` with source, text only (no colour) |
| D-4 | Absent slots | Shown, marked `absent`, only for required slots with Y concepts in the descriptor |
| D-5 | Status line on older pairs | Only under 0.9.3; 0.9.0…0.9.2 unchanged |
| D-6 | Locale | German texts in an own pinned locale file (`de-0093.json`), as VP-10.1 |

## 2a. Vectors (X-01…X-12, synthetic)

One synthetic `binding-context/10` (scope `ctx:xy`): Z Core `mod.core`; Y Actor `act:caller`, `act:holder`; Y Principal `pr:person`; Y Resource `res:store`; Y Revision `rev:v1`; Z Grant `gr:key`; Z Refusal `ref:no`; X scopes `x:policy`, `x:event`; X Action `act-call` (event; `performed_by_ref` act:caller, `executed_as_ref` pr:person), Authority `auth` (policy; `holder_ref` act:holder, `source_ref` gr:key, `action_kind`, `resource_scope_ref` res:store), Admission `adm` (policy; `request_ref` act-call, `principal_ref` pr:person, `decision` admitted, `authority_ref` auth); profiles for the three endpoints. Plan `pm-xy`, steps `current`, `beta`: `d1` mod.core gated-by adm, `d2` mod.core reads res:store, `d3` act:caller invoked-by mod.core, all in both steps. Entries are written `<endpoint> · <slot>`.

| ID | Case | Expected |
|---|---|---|
| X-01 | base, rows `X`, cols `Y:kind`, detail | PASS; cells Γ·Actor [auth · holder_ref], Γ·Principal [adm · principal_ref], Γ·Resource [auth · resource_scope_ref], Π·Actor [act-call · performed_by_ref], Π·Principal [act-call · executed_as_ref]; no other cell |
| X-02 | X-01 transposed (rows `Y:kind`, cols `X`) | PASS; same entries, keys transposed |
| X-03 | cols `Y:referent` | PASS; Γ·act:holder, Γ·pr:person, Γ·res:store, Π·act:caller, Π·pr:person with the entries of X-01 |
| X-04 | `principal_ref` removed from adm | PASS; Γ·Principal [adm · principal_ref · absent] |
| X-05 | `source_ref` removed from auth (Z-typed slot) | PASS; cells as X-01 (no entry for source_ref) |
| X-06 | extra Admission `adm-other` in the context, not in the plan and not reached | PASS; cells as X-01; report `x_ignored` = 1 |
| X-07 | plan without d1 (no X endpoint in the slice) | PASS; no non-empty cell; warning `VP09_X_NONE` |
| X-08 | input profile 0.9.2, pair X × Y | error `VP09_AXIS_INVALID` |
| X-09 | 0.9.3, pair Y:kind × Z:kind | PASS; status line `Y × Z · derived · Morphology 01.3` |
| X-10 | X-01 without `instantiation_profiles` | PASS; cells as X-01; report `x_profiles_missing` lists adm, auth, act-call |
| X-11 | X-01 with `--locale de` | PASS; status line `X × Y · kanonisch · Morphologie §3.3` |
| X-12 | X-01 ledger | `x_units` 5, all `drawn`, coverage COMPLETE |

## 3. Acceptance

| ID | Criterion |
|---|---|
| VP093-01 | X-01…X-12 against an oracle committed before code (pair present, entries, absent slots, ledger, status line, D-2 limits, Y:referent columns, budgets, locale) |
| VP093-02 | 0.9.0…0.9.2 outputs byte-identical (pinned before code) |
| VP093-03 | lunados.explorer F05 (XB1 complete) and F03a (XB1/XB2 with absent principal and source) print X × Y; `check-panels` PASS |
| VP093-04 | G6 `cube_plan_views` accepts `X`/`Y:kind` for 0.9.3; G5 as an own step |
