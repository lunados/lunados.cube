# P1.10.1 — Declared Migration Profile, revision: dependency gap · Acceptance specification

**Status:** DRAFT 2026-10-26 — decisions D-1…D-7 open (§6). Not ready for implementation until they are resolved.
**Numbering:** Revision of P1.10 (`P1.10/migration-profile-v1`, released with PR #10/#11, G5 core `0.4.0-proof`). P1.10 stays frozen; P1.10.1 is a new, explicitly activated profile (D-1). P1.7 stays reserved for the Principal → Authority holder chain.
**Basis:** `P1/migration-profile-v1/P1_10_ACCEPTANCE_SPEC.md` (PH-1, TR-1…TR-3, DP-1…DP-6, D-1…D-8), `cube_p110/validator.py` (`_plan`: DP-3, DP-4 only when the object is retired at the next phase); Morphology v9.4 §5.10 (local precedence, no total order), §7.6.1 (R01-AC02); VP-07.1 draft (`P2/visual-printer-migration-v1/VP07_1_ACCEPTANCE_SPEC.md`, item (d) / D-7).
**Motivation:** A field test of P1.10 + VP-07 with a real migration inventory (2026-10-26; about 33 referents, 47 dependencies, 4 steps p0–p3; client details withheld) produced requirement C-7:

| Finding | Effect in P1.10 |
|---|---|
| A dependency ends before the target phase although its object is never retired, and it has neither `successor_ref` nor `dropped` | PASS, no diagnostic. DP-4 only fires when the dependency ends exactly at the phase that retires its object. |
| In the field test this was an inventory error | Visible only as an empty bar after p1 in `cube.phases`; the P1 report was silent. |

Synthetic example: Integration `import-job` `depends-on` Resource `mailbox-x`, `holds_in: [p0, p1]`; the plan has p0…p3; `mailbox-x` is never retired; no `successor_ref`, no `dropped` → today PASS.

P1.10.1 adds one structural check, `P1_MIGRATION_DEPENDENCY_GAP` (UNRESOLVED): the declaration does not say why a dependency stops. It never checks a live system, never decides an order, and never claims the dependency still exists.

## 0. Scope

| In scope | Out of scope |
|---|---|
| Rule DG-1…DG-5: dependency ends before the target phase without an explaining declaration | Inferring that the dependency still exists, or that it was removed in reality |
| New context version that activates the rule (D-1); P1.10 behaviour unchanged for `/5` | Changing P1.10 artifacts, its predicate profile, or `/1…/5` behaviour |
| Optional `ends_reason` declaration to close a gap without `dropped` (D-4) | Start gaps (dependency begins after `current` without introduction or predecessor), see §7 |
| Local MCP and G5 parity; observable deploy | Rendering — handled by VP-07.1 (D-6) |

## 1. Design summary

1. **New context version** `aiaeao.cube.binding-context/6`, a strict superset of `/5` with no new required fields. `/6` activates P1.10.1 rules; `/5` contexts behave byte-identically to P1.10 (D-1).
2. **Rule DG.** For every dependency whose `holds_in` ends at phase *k* before the plan's `target` phase, at least one of the following must be declared, otherwise `P1_MIGRATION_DEPENDENCY_GAP` (UNRESOLVED):
   - the object is retired at *k+1* (then P1.10 DP-4 applies unchanged);
   - the subject is retired at *k+1* (D-3);
   - `successor_ref` (validated per D-5);
   - `"dropped": true` with `witness_ref` (as P1.10 DP-4);
   - `ends_reason` (D-4).
3. **Diagnostics** follow P1.10: plan checks after all P1.9 checks, JSON Pointers into `migration_plans[i].dependencies[m]`, UNRESOLVED as a coverage gap, never FAIL.

### 1.1 Shape (illustrative, synthetic)

```json
{
  "format": "aiaeao.cube.binding-context/6",
  "scope_ref": "acme:migration",
  "predicate_profile_refs": ["P1.10/migration-predicates-v1"],
  "migration_plans": [{
    "plan_id": "mp-acme", "scope": "acme:migration",
    "phases": [{"phase_id": "p0", "role": "current"}, {"phase_id": "p1", "role": "intermediate"},
               {"phase_id": "p2", "role": "intermediate"}, {"phase_id": "p3", "role": "target"}],
    "transitions": [],
    "dependencies": [
      {"dependency_id": "d-import", "subject": "acme:import-job", "predicate_id": "depends-on",
       "object": "acme:mailbox-x", "kind": "job", "holds_in": ["p0", "p1"], "witness_ref": "repo:example/jobs/import"}
    ]
  }]
}
```

→ UNRESOLVED · `P1_MIGRATION_DEPENDENCY_GAP` at `/migration_plans/0/dependencies/0`: "ends at p1 before target p3; mailbox-x is not retired at p2; no successor_ref, dropped or ends_reason".

## 2. Status and diagnostic rules

| Situation | Status | Diagnostic |
|---|---|---|
| Dependency ends before `target` without any DG-2 explanation | UNRESOLVED | `P1_MIGRATION_DEPENDENCY_GAP` (new) |
| `ends_reason` present but not a declared value or without `witness_ref` (D-4) | UNRESOLVED | `P1_MIGRATION_DEPENDENCY_GAP` (new) |
| `successor_ref` present on a gap-ending dependency but the successor does not share subject and predicate or does not start at *k+1* (D-5 = a) | FAIL | `P1_MIGRATION_SUCCESSOR_INVALID` (P1.10, reused) |
| `ends_reason` inside a `/5` context | MCP error | `P1_MCP_CONFIG_INVALID` (existing) |
| All P1.10 rows of §2 | unchanged | unchanged |

Precedence follows P1.10: FAIL outranks UNRESOLVED; a dependency already reported as `P1_MIGRATION_DANGLING_DEPENDENCY` or `P1_MIGRATION_SUCCESSOR_MISSING` is not additionally reported as gap.

## 3. Rules in detail (DG)

- DG-1: Applies only in `/6` contexts and only to dependencies with a contiguous `holds_in` (P1.10 DP-1) inside a plan with valid phases (PH-1).
- DG-2: Let *k* be the last phase of `holds_in` and *t* the `target` phase. If *k* < *t*, the end must be explained by one of: object retired at *k+1*; subject retired at *k+1* (D-3); `successor_ref`; `dropped: true` with `witness_ref`; `ends_reason` (D-4).
- DG-3: Object retired at a phase later than *k+1* does **not** explain the end (the object still exists at *k+1*).
- DG-4: Ending at *t* never produces a gap. A dependency that ends at the retiring phase of its object stays P1.10 DP-4 territory (no double report).
- DG-5: The check is declarative only; `ends_reason` and `dropped` are declarations, not proof.

## 4. Acceptance criteria

| AC | Requirement | Evidence |
|---|---|---|
| P1.10.1-01 | No change to Morphology, P0, P1.1…P1.10 artifacts; `SHA256SUMS` diff empty | file diff |
| P1.10.1-02 | `/1…/5` byte-identical: M-01…M-22, C-01…C-20, S-01…S-17, R-01…R-13, P1.10 golden | regression suite |
| P1.10.1-03 | `context-v6.schema.json` strict superset of `/5` | schema tests |
| P1.10.1-04 | DG-1…DG-5 | G-01…G-10 |
| P1.10.1-05 | Every row in §2 yields exactly the stated status and code | one test per row |
| P1.10.1-06 | M-01…M-22 re-run as `/6` give the P1.10 results, except where a gap is listed in the oracle | `/6` regression |
| P1.10.1-07 | Independent oracle for G-01…G-10, transcribed before code | `oracles/independent_g01_g10.json` |
| P1.10.1-08 | Local MCP and G5 parity for G-01…G-10 | adapter parity test |
| P1.10.1-09 | Observable deploy: `cube_discover_surface` gains `p1101_migration` (or updated `p110_migration`, D-7); remote version bumped | live discover check |
| P1.10.1-10 | Synthetic golden: the P1.10 golden as `/6` stays PASS; a variant with one unexplained end yields exactly one gap | `fixtures/golden_gap_synthetic.json` |

## 5. Alignment vectors (exit check)

Base case G-01: four phases p0…p3; `import-job depends-on mailbox-x`, `holds_in [p0, p1]`; no transitions; witness present.

| ID | Case | Expected |
|---|---|---|
| G-01 | Base case as `/6` | UNRESOLVED · `MIGRATION_DEPENDENCY_GAP` |
| G-02 | G-01 as `/5` | PASS (P1.10 unchanged) |
| G-03 | G-01 with `holds_in [p0…p3]` | PASS |
| G-04 | G-01 with `dropped: true` | PASS |
| G-05 | G-01 with a transition retiring `mailbox-x` at p2 | UNRESOLVED · `MIGRATION_SUCCESSOR_MISSING` (P1.10 DP-4), no `MIGRATION_DEPENDENCY_GAP` (DG-4) |
| G-06 | G-01 with `mailbox-x` retired at p3 | UNRESOLVED · `MIGRATION_DEPENDENCY_GAP` (DG-3) |
| G-07 | G-01 with `import-job` retired at p2 (D-3 = a) | PASS |
| G-08 | G-01 with `successor_ref` to a dependency `import-job depends-on mailbox-y`, `holds_in [p2, p3]` | PASS |
| G-09 | G-08 with the successor starting at p3 (D-5 = a) | FAIL · `MIGRATION_SUCCESSOR_INVALID` |
| G-10 | G-01 with `ends_reason: "scope_end"` and witness (D-4 = a) | PASS |

G-05 shows the boundary to P1.10: the end is explained by the retirement, the missing successor stays a DP-4 finding, and no gap is added.

## 6. Decisions (open)

| Decision | Options | Proposal | Consequence of the proposal |
|---|---|---|---|
| D-1 Activation and naming | (a) new context `binding-context/6`, profile `P1.10.1/migration-profile-v2`, directory `P1/migration-profile-v2/` · (b) opt-in field in `/5` · (c) change `/5` | **(a)** | `/5` stays frozen as deployed (a new field in `/5` would turn today's MCP error into a different result); same pattern as P1.8 → P1.9 → P1.10. |
| D-2 Status | (a) UNRESOLVED (coverage gap, like `SUCCESSOR_MISSING`) · (b) FAIL | **(a)** | The declaration is incomplete, not contradictory; consistent with DP-4. |
| D-3 Subject retirement explains the end | (a) yes · (b) no | **(a)** | A job that is switched off ends all its dependencies; requiring `dropped` on each would be noise. |
| D-4 Explicit end reason | (a) optional `ends_reason` ∈ {`scope_end`, `replaced_outside_plan`, `other`} with `witness_ref` · (b) only `dropped` | **(a)** | Distinguishes "not migrated, deliberately" from "out of this plan's scope"; stays a declaration. |
| D-5 Successor validation for gap ends | (a) apply P1.10 successor rules (same subject and predicate, starts at *k+1*) · (b) presence only | **(a)** | A successor that does not continue the dependency explains nothing. |
| D-6 VP-07 marking | (a) VP-07.1 draws an end cap and lists `VP07_DECLARED_GAP` (VP-07.1 D-7, migration source carries `target_step`, `successor`, `dropped`) · (b) list only · (c) no VP change | **(a)** | Picture and P1 report agree, as for dangling and premature cells. |
| D-7 G5 surface | (a) new descriptor `p1101_migration` beside `p110_migration` · (b) extend `p110_migration` with `binding_context_formats [/5, /6]` | **(a)** | `p110_migration` stays as accepted in the P1.10 host report. |

## 7. Not part of P1.10.1

- **Start gap:** a dependency that begins after `current` without introduction of its object, without a predecessor pointing at it, and without a declared start reason. Symmetric to DG; to be specified separately if the field test shows it.
- Transitive propagation (a gap in A affecting B); rights and inheritance on resources.
