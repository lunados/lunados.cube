# VP-07.4 — Partition by method and methods line in `cube.flow` · Acceptance specification

**Status:** DRAFT 2026-10-27 — decisions D-1…D-8 open, no code.
**Profile (proposed):** `P2-VP-MIGRATION/0.7.4`, follow-up to `0.7.3` (VP-07.3, PR #23) in the same package `vpmigration` (profile dispatch as VP-07.1 PD-1…PD-4).
**Requirement:** follow-up to C-11 (2026-10-27): two items that VP-07.3 §7 left out — `--partition method` and methods in `cube.flow` panels. Methods in VP-08, colours or hatches per method, and any statement on whether a method fits its transition stay out (§7).
**Basis:** `VP07_ACCEPTANCE_SPEC.md` (PE-1…PE-6 panels and coverage, Path F flow panels per step), `VP07_1_ACCEPTANCE_SPEC.md` (NP-1…NP-5 nested partition, TM-1 codes), `VP07_2_ACCEPTANCE_SPEC.md` (LS-5 partition `layer`, LD-2 flow caption by post-processing), `VP07_3_ACCEPTANCE_SPEC.md` (MT-1…MT-3, MD-1…MD-4, D-3 short names, D-4 catalog order); `VP09_1_ACCEPTANCE_SPEC.md` D-3 (step of a dependency binding); P1.11 MP-5 (no order or rank from methods); VP-02 frozen (`cube.flow` printer unchanged).
**Motivation:** With 0.7.3 the methods are visible in `cube.phases`, but (1) there is no way to see all bars of one method together (e.g. every `rewrite` of the cut) with proven coverage, and (2) `cube.flow` panels, which show the state of one step, say nothing about the transitions that lead into that step.

| Finding in 0.7.3 | Effect |
|---|---|
| Partition keys `subject`, `object`, `step`, `track`, `layer` | "All rewrites" needs a hand-made `--subjects` list; coverage is then proven per slice only |
| `cube.flow` panels show nodes and edges of one step | The panel for p2 does not say that T1 (import, retire) and T3 (retire) take effect there |
| Bars carry `method`, flow edges do not | Opening the flow panel of p0 shows `shop → legacy-mail` without the declared `rewrite` |

## 0. Scope

| In scope | Out of scope |
|---|---|
| Partition key `method` for `cube.phases` and `cube.flow`, single and nested | Colour, hatch or glyph per method; methods as a rank or order |
| Methods line in `cube.flow` panels (post-processing, as the VP-07.2 layer caption) | Changes to VP-02 (edge labels in the frozen flow printer) |
| Edge metadata and title for dependency methods in `cube.flow` | Methods in VP-08 sequence views |
| Ledger: methods per flow panel; `check-panels` re-verifies | Fit of a method to its transition (P1.11 MP-1…MP-4) |
| 0.7.0…0.7.3 outputs byte-identical | MCP tool; G4/G5 |

## 1. Design summary

1. **Profile.** Per D-1. Partition `method` changes no existing output and works on 0.7.3 sources as well; the flow methods line needs 0.7.4.
2. **Partition key `method`.** The key of a bar is the `method_id` of its own declared binding (`cell.method`); bars without a method form the reserved group `none` (D-2, D-3). Groups follow catalog order, then local methods in first appearance, `none` last. A group is never merged with another; a group over budget is split by subject, as `layer` (LS-5) (D-4). Nested: `method,subject`, `track,method`, `method,step` (phases) etc. under NP-1. Coverage unit stays `(cell_id, step)`; the outer ledger proves every method group.
3. **Methods line in `cube.flow`.** A flow panel shows one step `s`. Its methods line lists the transitions at `s` that concern the panel (D-5), each as `T1 t-mail · import, retire` (VP-07.3 short names, catalog order). The line sits under the layer caption, or in its place without layers (D-7). Panels without such a transition get no line.
4. **Dependency methods in `cube.flow`.** The edge of a bar with a method gets `data-vp07-method` and the method in its title; the panel ledger lists it (D-6). Nothing is drawn on the edge itself.
5. **Ledger.** The flow panel result gets `methods`: transitions listed in the line (with code and full IDs) and edges with a method; `check-panels` re-renders as before (MD-4).

### 1.1 Shape (illustrative, synthetic)

```
print-panels --view cube.phases --partition method --granularity standard
panel-01  method: migrate.rewrite/v1    rows shop, support         bars d1, d5
panel-02  method: none                  rows shop, crm-sync, …     bars d2, d3, d4, d6, d7, d8
index: coverage COMPLETE 20/20 units; outer groups rewrite, none
```

```
cube.flow · step p2 · subject: shop, crm-sync
LAYERS (declared, left to right) · provider · account · system
TRANSITIONS AT p2 (declared) · T1 t-mail · import, retire · T3 t-box · retire
```

## 2. Status and diagnostic rules (proposed)

| Situation | Result | Diagnostic |
|---|---|---|
| `--partition method` (or nested with `method`) on a source below 0.7.3 | FAIL | `VP07_PANEL_PARTITION` (existing) |
| A method group alone exceeds the panel budget even after the split by subject | FAIL | `VP07_PANEL_PARTITION` (existing) |
| Methods line longer than the line budget | Wrapped, then `+n more`; full list in title and ledger (D-7) | — |
| Flow panel input, line or edge metadata differs from a deterministic re-render | FAIL | `VP07_PANEL_COVERAGE` (existing) |
| Methods line would overlap the drawn graph | FAIL (audit, never silently moved) | `VP07_AUDIT` (existing) |
| All other rows | as 0.7.0…0.7.3 | |

No new diagnostic code is proposed.

## 3. Rules in detail

### 3.1 Partition (PM)

- PM-1: `key(bar) = bar.method.method_id` if declared, else `none`. Transition methods never decide the group of a bar (D-2).
- PM-2: Group order: catalog order (import, rebuild, retire, rewrite, reconfigure), then local methods in order of first appearance in the cell list, then `none`. The order carries no rank (MP-5).
- PM-3: Packing per group as PE-2; a group over budget is split by subject in declared order; panels never mix groups (as LS-5).
- PM-4: Panels of `cube.phases` show the transitions that touch their rows and objects (existing rule) with their methods in the legend — also in the `none` group; a transition is not a bar and is not partitioned.
- PM-5: Subtitles read `method: rewrite` (short name, VP-07.3 D-3); the index and the ledger give the full ID.

### 3.2 Methods line (FL)

- FL-1: A transition `t` with `t.at = s` is listed in a flow panel of step `s` if a retired or introduced item of `t` is (i) a node of the panel, or (ii) the object of a source cell of a panel row that holds in the step directly before `s` (D-5). Both are declared facts; nothing is inferred.
- FL-2: Order: transition code order (TM-1). Per transition: code, ID, methods in catalog order (VP-07.3 D-4). Transitions without methods are listed with their code and ID only, so the line never suggests that a step has no transition.
- FL-3: Text ≥ 11 px, no colour, prefixed `TRANSITIONS AT <step> (declared)`; at most two lines of 150 characters, then `+n more`; the full list is in the `<title>` and the ledger (D-7).
- FL-4: Post-processing only: the VP-06/VP-02 result is kept as the inner result (as the VP-07.2 layered result); the nested VP-05 audit stays PASS.

### 3.3 Edges (FE)

- FE-1: The edge whose `declaration_ref` is that of a bar with a method gets `data-vp07-method` (full ID) and the short name appended to its title. Geometry, stroke and arrow are unchanged.
- FE-2: Per D-6 the dependency method is not repeated in the methods line.

## 4. Acceptance criteria (draft)

| AC | Requirement | Evidence |
|---|---|---|
| VP074-01 | 0.7.0, 0.7.1, 0.7.2 and 0.7.3 outputs byte-identical (0.7.3 digests pinned before code) | regression run |
| VP074-02 | Partition PM-1…PM-5, single and nested, coverage | N-01…N-06 |
| VP074-03 | Methods line FL-1…FL-4 | N-07…N-11 |
| VP074-04 | Edge metadata FE-1, FE-2 | N-12 |
| VP074-05 | `check-panels` detects tampering; layers and methods line together | N-13, N-14 |
| VP074-06 | Every row in §2 yields exactly the stated result and code | one test per row |
| VP074-07 | Synthetic golden: GM-pos, `cube.phases --partition method` (groups `rewrite`, `none`) and `cube.flow` p1/p2 panels with T1…T4 listed | fixture |
| VP074-08 | No client data in fixtures, examples or previews | review |

## 5. Alignment vectors (draft)

| ID | Case | Expected |
|---|---|---|
| N-01 | `cube.phases --partition method`, bars with `rewrite`, a local method and none | PASS, groups `rewrite`, local, `none` in that order |
| N-02 | Same | PASS, no panel mixes groups; coverage COMPLETE |
| N-03 | 30 `rewrite` bars at standard | PASS, group split by subject, every panel subtitle `method: rewrite` |
| N-04 | `--partition track,method` | PASS, outer ledger COMPLETE per track |
| N-05 | `--partition method,subject` on `cube.flow` | PASS, per step, groups never mixed |
| N-06 | `--partition method` on a 0.7.2 source | FAIL · `VP07_PANEL_PARTITION` |
| N-07 | Flow panel of p2 with `shop` (new-mail node) | PASS, line lists `T1 t-mail · import, retire` |
| N-08 | Flow panel of p2 with `crm-sync`; `t-box` retires mailbox-x held by crm-sync at p1 | PASS, line lists `T3 t-box · retire` (FL-1 ii) |
| N-09 | Flow panels of p0, p1 and p3 (the plan declares transitions only at p2) | PASS, no line where FL-1 selects nothing |
| N-10 | Transition without methods at the step | PASS, listed with code and ID only |
| N-11 | Twelve transitions at one step | PASS, two lines, `+n more`, full list in title and ledger |
| N-12 | Edge `shop → legacy-mail` at p0 | PASS, `data-vp07-method = migrate.rewrite/v1`; edge geometry identical to 0.7.3 |
| N-13 | `check-panels` after editing the line in a panel input | FAIL · `VP07_PANEL_COVERAGE` |
| N-14 | Layers and methods line together | PASS, both lines present, no overlap with node cards |

## 6. Decisions (open)

| Decision | Options | Proposal | Consequence |
|---|---|---|---|
| D-1 Profile | (a) new profile 0.7.4 only via `from-plan --profile P2-VP-MIGRATION/0.7.4`; a /7 context still yields 0.7.3 by default; `--partition method` also works on 0.7.3 sources · (b) a /7 context yields 0.7.4 by default, 0.7.3 via `--profile` · (c) no new profile; methods line behind a `print-panels` flag | **(a)** | The same command line keeps producing the same bytes (as VP-09.1 D-1). The partition key changes no existing output, so it needs no new profile. The default can move to 0.7.4 later as its own step. |
| D-2 Key of a bar | (a) the bar's own declared method only · (b) also the methods of transitions that retire or introduce the bar's object | **(a)** | (b) would assign a method to a bar that did not declare one — an inference. |
| D-3 Bars without method | (a) reserved group `none`, last · (b) `none` first · (c) leave them out | **(a)** | Coverage stays complete (PE-3); method IDs contain `/`, so `none` cannot collide with a method. |
| D-4 Large groups | (a) never merge groups; split a large group by subject (as `layer`) · (b) FAIL | **(a)** | The field test has 16+ `rewrite` bars in one cut; (b) would make the key unusable. |
| D-5 Transitions in a flow panel | (a) FL-1 (i) node of the panel or (ii) object of a panel row at the step before · (b) every transition at the step in every panel of that step · (c) (i) only | **(a)** | (c) loses every retire-only transition (its object is gone at `s`); (b) repeats unrelated transitions in every panel. |
| D-6 Dependency methods in `cube.flow` | (a) edge metadata, title and ledger only · (b) also in the methods line of the successor's first step (as VP-09.1 D-3) · (c) in the line of every panel where the edge is drawn | **(a)** | The edge already shows where the dependency holds; a line entry at p0 would read as "rewrite happens at p0". (b) is possible later. |
| D-7 Line placement and overflow | (a) under the layer caption (or in its place), two lines, then `+n more`; audit FAILs on overlap · (b) footer above `DISPLAY-ONLY` · (c) no limit | **(a)** | Read together with the step header; space between header and graph is measured in the 0.7.3 panels (caption at y 178, first node text at y 220); if the audit shows overlap at implementation, D-7 is reopened, not silently moved. |
| D-8 Golden | (a) GM-pos (P1.11 golden) · (b) new synthetic plan | **(a)** | Same plan as VP-07.3 and VP-09.1; three views of one plan stay comparable. |

## 7. Not part of VP-07.4

- Methods in VP-08 sequence views (VP-08 reads its own sequence sources, not migration plans; needs a separate bridge).
- Colour, hatch or glyph per method (colour carries no meaning in VP-07; hatches already mean declared conflicts).
- Showing whether a binding fits its plan (P1.11 MP-1…MP-4); a P1 report overlay would be a separate decision.
- Partition by transition; methods as an order or rank.
