# P1.9 — Declared Comparison Profile · Acceptance specification

**Status:** DRAFT 2026-10-25 — decisions D-1…D-6 open (§6). Not ready for implementation until they are resolved.
**Numbering:** P1.7 stays reserved for the Principal → Authority holder chain. P1.9 builds on P1.8 and does not depend on P1.7.
**Basis:** Morphology v9.4 §5.16 (Comparison Protocol, partial comparability), §5.17 (comparative trust), §5.18 (specification vs. run vs. comparison), §7.32 item 4 and §7.38 item 6 (fair control, equally safe competitor), Annex E.2 (do not mix holdouts); P1.8 declared simulation profile, decision D-5 (replay-against-record deferred to P1.9).
**Motivation:** The most informative experiments are not single runs but **paired comparisons under identical conditions**:

| Experiment | Arms | Paired unit | Parity / control condition | Typical outcome |
|---|---|---|---|---|
| EXP-002 A/B | ADM vs. MPC | world stream × seed, 54 scenario cells | identical goal parameters per case; horizon varies for MPC only | ranking flips with depth / uncertainty |
| EXP-003 | STATIC, RULE, ADAPTIVE | scenario cell × seed (720 streams) | same world stream for all three methods | per-metric results, no overall score |
| EXP-007 | direct + 4 strategies | world (108) | identical result tuples, fingerprinted per world | bootstrap interval of time difference |
| EXP-009-D | 7 strategies × 3 switch-cost rates | world (128; calibration / holdout) | full Fixed-achievable coverage; baseline reproduces 009 | no unique dynamic advantage vs. certified Fixed |

P1.8 can declare every arm as a scenario with an evaluation record. It cannot declare **that** two arms were run on the same units, **what** alone was varied, **which** parity held, and **what** the comparison concluded per metric and scope. Today such a claim is either missing or hidden in free text.

## 0. Scope

| In scope | Out of scope |
|---|---|
| A declared Comparison Protocol (§5.16): criteria, direction, tie and non-comparability policy, aggregation | Computing statistics, intervals, significance or effect sizes |
| A declared comparison of ≥ 2 P1.8 scenarios (arms) with pairing, shared and varied parameters, parity witnesses, splits | Choosing a winner, a selection, an Admission or any action (§5.18 Decision Trace) |
| Declared comparison outcomes per metric and scope, typed as Y Annotation | A total order or overall score without a declared aggregation method |
| Replay against a declared record: a replay run that claims to reproduce an earlier record | Recomputing digests, re-running evaluators, verifying witnesses |
| Unchanged `cube_validate` signature; local MCP and G5 Remote | New MCP tools; deciding the MILE-075 product-value comparator (P1.9 only gives it a format) |

## 1. Design summary

1. **New context version** `aiaeao.cube.binding-context/4`, a strict superset of /3 with three optional additions: `comparison_protocols`, `comparisons`, and the record fields `replay_of` + `output_digest`. Contexts in /1, /2 and /3 behave byte-identically.
2. **Comparison Protocol** (§5.16): declares criteria (metrics with direction and unit), the tie / equivalence margin, the non-comparability policy and an optional aggregation method. A numerical comparison never chooses weights by itself.
3. **Comparison:** names its protocol, its arms (each a declared P1.8 scenario with a role), the paired unit, the parameters that must be equal across arms and the ones that are allowed to differ, the parity conditions with witnesses, and the data split.
4. **Outcome:** one declared result per (arm pair, metric, scope, split) from the partial-comparability vocabulary of §5.16. It is a Y Annotation claim backed by a witness, never a Conclusion or a selection.
5. **Replay against record:** an evaluation record in a `replay` scenario may name the record it reproduces. The Cube compares the declared fields as strings. It never recomputes.

### 1.1 Shape (illustrative, EXP-009-D)

```json
{
  "format": "aiaeao.cube.binding-context/4",
  "reference_version": "v9.4",
  "comparison_protocols": [{
    "protocol_id": "cp-009d", "revision": "prereg:2026-10-14", "scope": "exp009d", "origin": "external_declaration_unverified",
    "criteria": [
      {"metric_id": "mean_work", "direction": "lower_better", "unit": "modelled work / event"},
      {"metric_id": "coverage", "direction": "higher_better", "unit": "fraction of Fixed-achievable findings"}
    ],
    "equivalence_margin": {"mean_work": 0.0},
    "non_comparability": "report_incomparable",
    "aggregation": "none"
  }],
  "comparisons": [{
    "comparison_id": "cmp-009d-r05", "protocol_ref": "cp-009d", "scope": "exp009d",
    "arms": [
      {"arm_id": "fixed-cert", "scenario_ref": "sc-009d-fixed-cert-r05", "role": "control"},
      {"arm_id": "cutoff6", "scenario_ref": "sc-009d-cutoff6-r05", "role": "treatment"}
    ],
    "pairing": {"unit": "world", "units_ref": "exp009d:holdout-worlds", "shared_parameters": ["switch_rate", "epochs", "split"], "varied_parameters": ["strategy"]},
    "parity": [{"parity_id": "full-coverage", "kind": "coverage", "witness_ref": "lunados.space:…/results/verdict.json#sha256=…"}],
    "splits": ["calibration", "holdout"],
    "outcomes": [{
      "outcome_id": "o-1", "a": "fixed-cert", "b": "cutoff6", "metric_id": "mean_work",
      "scope": {"switch_rate": 0.05}, "split": "holdout",
      "outcome": "a_preferred",
      "statistic": {"kind": "mean_delta_a_minus_b", "declared_value": -0.41},
      "annotation_ref": "exp009d:claim-fixed-cheaper", "witness_ref": "lunados.space:…/results/summary.json#sha256=…"
    }]
  }]
}
```

Arms are ordinary P1.8 scenarios with their own evaluation records; the comparison only references them.

## 2. Status and diagnostic rules

| Situation | Status | Diagnostic (new) |
|---|---|---|
| `protocol_ref`, arm `scenario_ref` or outcome arm / metric not declared | UNRESOLVED | `P1_COMPARISON_REFERENCE_MISSING` |
| Fewer than two arms, or no arm with role `control` | FAIL | `P1_COMPARISON_ARMS` |
| An arm scenario does not contain the paired `units_ref` in its `world_refs`, or arms differ in mode | FAIL | `P1_COMPARISON_PAIRING` |
| A parameter differs between arms but is not listed in `varied_parameters`, or a `shared_parameters` key is missing in one arm | FAIL | `P1_COMPARISON_CONFOUNDED` |
| Protocol or comparison requires parity and an arm has no parity witness | UNRESOLVED | `P1_COMPARISON_PARITY_MISSING` |
| Outcome value outside the §5.16 vocabulary, or `equivalent_under_criteria` without an equivalence margin for that metric | FAIL | `P1_COMPARISON_OUTCOME_INVALID` |
| Declared statistic sign contradicts the outcome under the metric direction (D-3) | FAIL | `P1_COMPARISON_OUTCOME_INCONSISTENT` |
| Outcome spans several metrics while `aggregation = none`, or names more than two arms | FAIL | `P1_COMPARISON_AGGREGATION_UNDECLARED` |
| Splits declared but an outcome names none, names an undeclared one, or mixes two | FAIL | `P1_COMPARISON_SPLIT_MIXED` |
| Two outcomes for the same (arms, metric, scope, split) with different values | FAIL | `P1_COMPARISON_OUTCOME_CONFLICT` |
| `annotation_ref` not a Y Annotation world member, or typed as an X judgment endpoint | FAIL | `P1_COMPARISON_OUTCOME_TYPE` |
| Outcome without `witness_ref` | UNRESOLVED | `P1_EVALUATION_WITNESS_MISSING` (P1.8, reused) |
| `replay_of` names an undeclared record, or the replayed record differs in `method_id`, evaluator or `input_digest` | FAIL | `P1_REPLAY_RECORD_MISMATCH` |
| Replay record declares `status: declared` with `output_digest` different from the original's (D-5) | FAIL | `P1_REPLAY_DIVERGENT` |
| `replay_of` on a record whose scenario mode is not `replay` | FAIL | `P1_SCENARIO_MODE` (P1.8, reused) |
| /4-only fields inside a /1, /2 or /3 context | MCP error | `P1_MCP_CONFIG_INVALID` (existing) |

Precedence follows P1.4-14, P1.6 and P1.8: FAIL outranks UNRESOLVED, and NOT_EVALUATED is never PASS. Comparison checks run after all P1.8 scenario and record checks and only when `comparisons` is present.

## 3. Rules in detail

### 3.1 Comparison Protocol (CP)

- CP-1: `criteria` is a non-empty list; each `metric_id` is unique and has `direction` ∈ {lower_better, higher_better, none}. A metric with `none` can only receive `equivalent_under_criteria`, `incomparable_under_criteria` or `undetermined_with_available_evidence`.
- CP-2: `aggregation` is `none` or a declared `method_id` of a `pure_declarative` method contract. Weights live in that method, never in the protocol (§5.16: a numerical calculation does not choose weights).
- CP-3: `equivalence_margin` is optional per metric; without it, `equivalent_under_criteria` is not available for that metric.
- CP-4: `non_comparability` ∈ {report_incomparable, report_undetermined}. Incomparability is never equality, and equal assessment is never falsification (§§5.16, 5.17).

### 3.2 Arms and pairing (AR)

- AR-1: `arms` has ≥ 2 entries; `role` ∈ {control, treatment, reference}; at least one `control` (§7.32 item 4: an equally informed, equally safe control).
- AR-2: Every arm scenario contains the declared `pairing.units_ref` (an Artifact listing the paired units) in its `world_refs`. `unit` ∈ {world, seed, cell, world_seed}. The unit list itself is not opened or compared.
- AR-3: For every key in `shared_parameters`, all arms carry the key with an identical JSON scalar. Any other key whose values differ must be in `varied_parameters`. Parameters stay uninterpreted (P1.8 SC-4); only equality is checked.
- AR-4: All arms share one scenario `mode`. A `simulation` arm is not compared with a `replay` arm in one comparison.
- AR-5: `parity` entries have `kind` ∈ {result_equivalence, coverage, digest_equal, declared_other} and a `witness_ref`. If the protocol or comparison lists any parity, each treatment arm needs it. The Cube never checks that parity holds.

### 3.3 Outcomes (OC)

- OC-1: `outcome` ∈ {a_preferred, b_preferred, equivalent_under_criteria, incomparable_under_criteria, undetermined_with_available_evidence} — the §5.16 vocabulary, adopted here as a **profile-local** value set, not as a Morphology enum (D-2).
- OC-2: An outcome compares exactly two arms (`a`, `b`) on exactly one metric, unless `aggregation` names a method; rankings over more arms are sets of pairwise outcomes (D-4).
- OC-3: `scope` maps declared design factors to levels; an outcome without scope covers the whole design. Different scopes may carry different outcomes — a ranking flip is two scoped outcomes, not a conflict.
- OC-4 (D-3): If `statistic.declared_value` is present and the metric has a direction, its sign must agree with the outcome: for `mean_delta_a_minus_b` under `lower_better`, a negative value requires `a_preferred`, a positive one `b_preferred`; zero or a value inside the equivalence margin is compatible only with `equivalent_under_criteria` or `undetermined_with_available_evidence`. The Cube checks the sign of the declared number only. It never computes it.
- OC-5: `annotation_ref` is a Y Annotation world member (Morphology v9.4 D.4: claims are Y Annotation). An outcome is never an X Conclusion, Selection, Admission or Authority, and `a_preferred` is not a decision (§5.18).
- OC-6: If `splits` are declared, every outcome names exactly one (Annex E.2). Calibration and holdout results are never merged in one outcome.

### 3.4 Replay against record (RR)

- RR-1: A record may carry `replay_of: <record_id>` (a record declared in the same context) and `output_digest: sha256:<64 hex>`.
- RR-2: The replaying record must match the original in `method_id`, `evaluator_ref` and `input_digest` (string equality).
- RR-3 (D-5): If both records carry `output_digest` and they differ, a replay with `status: declared` fails `P1_REPLAY_DIVERGENT`. A replay with `status: unresolved` may diverge and is reported UNRESOLVED; divergence is a finding, not hidden.
- RR-4: Equal digests never mean "correct" or "verified"; `witness_truth` stays NOT_EVALUATED.

### 3.5 Report boundary

- The P1 report schema stays unchanged. The adapter envelope adds `comparison_profile: "P1.9/comparison-profile-v1"` (only for /4) and keeps `evaluation_performed_by_cube: false`.
- `canonical_admission`, `current_authority`, `epistemic_warrant` stay `NOT_EVALUATED`; `source_warrant` stays `declared_unverified`, also for complete comparisons.

## 4. Acceptance criteria

| AC | Requirement | Evidence (to be produced) |
|---|---|---|
| P1.9-01 | No change to Morphology v9.4, P0, frozen P1.1, report.schema.json, P1.6 and P1.8 artifacts | `SHA256SUMS.txt` diff empty |
| P1.9-02 | /1, /2 and /3 behaviour byte-identical: P1.4 suite, F01–F25, R-01…R-13, S-01…S-17, both P1.8 goldens | regression suite |
| P1.9-03 | `context-v4.schema.json` published; strict superset of /3; /4 fields rejected in /1–/3 | schema tests, C-20 |
| P1.9-04 | Protocol rules CP-1…CP-4 | C-08, C-09, C-11 + config tests |
| P1.9-05 | Arm and pairing rules AR-1…AR-5 | C-02…C-07 |
| P1.9-06 | Outcome rules OC-1…OC-6 | C-08…C-15 |
| P1.9-07 | Replay rules RR-1…RR-4 | C-16…C-19 |
| P1.9-08 | Every row in §2 yields exactly the stated status and code | one test per row |
| P1.9-09 | Non-promotion (§3.5) asserted in every positive test | assertion in every PASS test |
| P1.9-10 | Deterministic JSON-Pointer diagnostics into `comparison_protocols[i]`, `comparisons[i].arms[j]`, `…outcomes[k]`, `evaluation_records[i]` | snapshot tests |
| P1.9-11 | New codes in a P1.9 `DIAGNOSTIC_EXTENSION.json` and `RULE_COVERAGE.json` with Morphology references | file diff |
| P1.9-12 | Independent oracle for C-01…C-20, transcribed before execution | `oracles/independent_c01_c20.json` |
| P1.9-13 | Local MCP and G5 Remote return identical reports for C-01…C-20 | adapter parity test |
| P1.9-14 | **Observable deploy:** `cube_discover_surface` gains a `p19_comparison` descriptor and the remote version is bumped (`P3-MCP-REMOTE/0.3.0-proof` or later) | live discover check |
| P1.9-15 | Four golden comparisons materialised from archived sources, each with pinned code and result witnesses: EXP-002B (ADM vs. MPC, scoped outcomes incl. a ranking flip), EXP-003 (three methods, per-metric outcomes, `aggregation: none`), EXP-007 (four strategies vs. direct, `result_equivalence` parity), EXP-009-D (seven strategies × three rates, `coverage` parity, holdout split, 009 baseline as `replay_of`) | `fixtures/golden_exp002b.json`, `golden_exp003.json`, `golden_exp007.json`, `golden_exp009d.json`, all PASS live |

`PASS` in this matrix means the listed test ran successfully. It does not mean that an outcome is true, that a comparison was fair, or that any arm should be adopted.

## 5. Alignment vectors (exit check)

Expected statuses fixed **before** implementation. Base case C-01: two `simulation` arms (control, treatment) with identical `units_ref`, shared `{seed_set, split}`, varied `{strategy}`, one metric `cost` (lower_better), one outcome `a_preferred` with `declared_value < 0`, annotation and witness present.

| ID | Case | Expected overall |
|---|---|---|
| C-01 | Base case | PASS |
| C-02 | C-01 with one arm only | FAIL · `COMPARISON_ARMS` |
| C-03 | C-01 with both arms `treatment` | FAIL · `COMPARISON_ARMS` |
| C-04 | C-01 with `units_ref` missing from the treatment world | FAIL · `COMPARISON_PAIRING` |
| C-05 | C-01 with `seed_set` different between arms | FAIL · `COMPARISON_CONFOUNDED` |
| C-06 | C-01 with an extra undeclared parameter differing (`horizon`) | FAIL · `COMPARISON_CONFOUNDED` |
| C-07 | C-06 with `horizon` added to `varied_parameters` | PASS |
| C-08 | C-01 with `outcome = "winner"` | FAIL · `COMPARISON_OUTCOME_INVALID` |
| C-09 | C-01 with `equivalent_under_criteria` and no margin | FAIL · `COMPARISON_OUTCOME_INVALID` |
| C-10 | C-01 with `declared_value > 0` | FAIL · `COMPARISON_OUTCOME_INCONSISTENT` |
| C-11 | Outcome over two metrics with `aggregation: none` | FAIL · `COMPARISON_AGGREGATION_UNDECLARED` |
| C-12 | Two outcomes, same arms and metric, scopes `depth=4` and `depth=20`, opposite values | PASS (ranking flip) |
| C-13 | C-12 with identical scope | FAIL · `COMPARISON_OUTCOME_CONFLICT` |
| C-14 | Splits declared, outcome without `split` | FAIL · `COMPARISON_SPLIT_MIXED` |
| C-15 | `annotation_ref` typed `X:endpoint:conclusion` | FAIL · `COMPARISON_OUTCOME_TYPE` |
| C-16 | `replay` arm whose record has `replay_of` with equal method, evaluator, input and output digests | PASS |
| C-17 | C-16 with different `input_digest` | FAIL · `REPLAY_RECORD_MISMATCH` |
| C-18 | C-16 with different `output_digest`, `status: declared` | FAIL · `REPLAY_DIVERGENT` |
| C-19 | C-18 with `status: unresolved` | UNRESOLVED · `REPLAY_DIVERGENT` |
| C-20 | `comparisons` inside a /3 context | MCP error · `P1_MCP_CONFIG_INVALID` |

Not expected to change, stated explicitly: any statistic, interval or significance; whether parity actually held; whether a control was really equally safe; the MILE-075 product-value disposition; the external gates of EXP-017/018/022.

## 6. Decisions (open)

| Decision | Options | Proposal | Consequence of the proposal |
|---|---|---|---|
| D-1 Context version | (a) new `/4` superset · (b) optional fields in `/3` | **(a) /4** | /3 stays frozen as deployed with P1.8; G5 needs one new profile, not a changed one. |
| D-2 Outcome vocabulary | (a) §5.16 five values, profile-local · (b) free text · (c) Morphology enum | **(a)** | Machine-checkable without adopting an enum in v9.4; a later Morphology version may adopt or rename it. |
| D-3 Sign check | (a) Cube checks only the sign of a declared number against outcome and direction · (b) structure only | **(a)** | Catches the most common declaration error (claim and number disagree) without any computation. |
| D-4 More than two arms | (a) pairwise outcomes only · (b) declared ranking objects | **(a)** | No implicit total order (§5.16); EXP-009-D's seven strategies become pairwise outcomes against the control. |
| D-5 Replay divergence | (a) FAIL for `declared`, UNRESOLVED for `unresolved` · (b) always UNRESOLVED | **(a)** | A record cannot claim a reproduction it does not have, and a real divergence stays visible. |
| D-6 Protocol location | (a) in the context, optional `library_ref` as in P1.8 D-3 · (b) Functions Library only | **(a)** | Comparisons work before protocols become library entries; a pinned protocol is possible from day one. |
