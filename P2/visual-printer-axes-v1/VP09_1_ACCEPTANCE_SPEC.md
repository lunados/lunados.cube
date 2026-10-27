# VP-09.1 — F axes from P1.11 bindings, complete · Acceptance specification

**Status:** IMPLEMENTED 2026-10-27 (B-01…B-20 20/20; 22 pinned 0.9.0 outputs byte-identical); decisions D-1…D-9 resolved 2026-10-27 (all as proposed).
**Profile:** `P2-VP-AXES/0.9.1`, follow-up to `0.9.0` (VP-09, PR #21) in the same package `vpaxes`.
**Requirement:** C-11 from the running migration field test (2026-10-27; an inventory of about 37 referents, 56 dependencies, 3 transitions and 32 method bindings, all PASS under P1.11; client details withheld). Items 1 and 2 of C-11 (F × Z, F × T); item 3 (VP-07) is VP-07.3.
**Basis:** `VP09_ACCEPTANCE_SPEC.md` (AX-1…AX-3, AQ-1…AQ-6, CM table, D-2, D-7, D-9); `P1/migration-methods-v1/P1_11_ACCEPTANCE_SPEC.md` (catalog MC-1…MC-4, MI-3 local method contracts, MP-3 rewrite needs `successor_ref`, MP-5 no order from methods, `P1_MIGRATION_METHOD_UNKNOWN` = UNRESOLVED); Morphology v9.4 §3.7 (F is a qualifier over qualified referents), `core.json` `never_infer` (X/Y/Z/F/M are not a numeric vector).
**Motivation:** VP-09 0.9.0 already reads F from `binding-context/7`. Run against the synthetic P1.11 golden (GM-pos: 23 bindings, 41 arguments), F × T passes and F × Z covers all 41 arguments over 4 panels. The field test still needs a hand-written Markdown table, because of the gaps below.

| Finding in 0.9.0 | Effect |
|---|---|
| F × Y is not in the pair list (D-2) | `import`, `rebuild`, `retire`, `rewrite`, `reconfigure` all admit `Y:resource-object:resource`; accounts and mailboxes have no F view |
| In F × Z an argument whose referent has a Y home falls out silently (`proj` → no column) | The table looks complete but is not; the report does not say so |
| `from-plan` silently drops bindings whose owner is outside the plan slice, and arguments whose ref is not in the slice | Same: nothing in the report |
| A `method_id` outside the catalog is appended after the catalog rows (AQ-3) | A typo in a method ID becomes a row of its own; P1.11 would report `P1_MIGRATION_METHOD_UNKNOWN` |
| F × T places a dependency binding in the **last** step of the dependency itself | In GM-pos all 16 `rewrite` bindings land in p1, while the cut transitions they belong to are at p2 |
| F axis on a /5 or /6 context FAILs `VP09_AXIS_EMPTY` (A-04) | "No method declared yet" is a normal state of a plan; C-11 asks for a notice, not FAIL |
| Entry text `t2 (source)` | Other pairs use `·` (`<dependency> · <predicate>`); C-11 asks for `t2 · source` |

## 0. Scope

| In scope | Out of scope |
|---|---|
| Profile `0.9.1` next to `0.9.0`; all 0.9.0 outputs byte-identical (A-01…A-20) | Changes to VP-07 (VP-07.3), P1.11 or the catalog |
| New pair F × Y (Y referents or kinds) | Mixed Y/Z argument axis beyond D-2 |
| Binding ledger: every argument of every transcribed binding is accounted for (drawn, off-axis, out of slice) | Checking bindings — P1.11 does that; VP-09 stays DISPLAY-ONLY |
| Method IDs checked against the catalog and the context's local `method_contracts` (MI-3) | Ranking, ordering or grouping derived from methods (MP-5) |
| F × T step rule for dependency bindings from the declared `successor_ref` (D-3) | Inferring F from predicates, kinds or names |
| F axis without bindings: empty table with a notice (D-4) | M and O axes |
| GM-pos as vector; synthetic Y-argument golden | MCP tool |

## 1. Design summary

1. **Profile dispatch.** `0.9.0` stays the default; `--profile 0.9.1` (CLI) / `profile=` (API) selects the new rules (D-1). The axes input carries the profile, so a panel input re-renders under the profile it was printed with.
2. **Transcription.** `from-plan` 0.9.1 transcribes per binding its `declaration_ref` (JSON pointer into the context, e.g. `decl:ctx#/migration_plans/0/transitions/1/methods/0`), `witness_ref` if declared, and every argument, also those outside the slice (marked `in_slice: false`). It copies the IDs of local `method_contracts` into `local_methods`.
3. **Method check.** A `method_id` that is neither a catalog ID nor in `local_methods` FAILs (D-5). Rows: catalog order, then local methods in first-appearance order.
4. **Pairs.** F × Z (unchanged membership), new F × Y with the same rule on the Y home, F × T with the step rule D-3.
5. **Binding ledger.** Unit = `(binding, role)`. Each unit is `drawn` (cell of the chosen pair), `off_axis` (the referent's home is not the column axis) or `out_of_slice`. The report states the counts and lists off-axis and out-of-slice units; coverage is COMPLETE when every unit has exactly one state. Panels prove the union as in 0.9.0.
6. **Entry text.** `<owner> · <role>` in F × Y / F × Z, `<owner>` in F × T (D-6).

### 1.1 Shape (illustrative, synthetic)

```json
{
  "format": "aiaeao.cube.vp09-axes-input/1",
  "profile": "P2-VP-AXES/0.9.1",
  "source": { "...": "VP-07 migration source 0.7.1 / 0.7.2, unchanged" },
  "local_methods": [],
  "method_bindings": [
    {"owner_kind": "transition", "owner": "t-mail", "method_id": "migrate.import/v1",
     "arguments": {"source": "legacy-mail", "target": "new-mail"},
     "declaration_ref": "decl:ctx#/migration_plans/0/transitions/0/methods/0"},
    {"owner_kind": "dependency", "owner": "d1", "method_id": "migrate.rewrite/v1",
     "arguments": {"dependant": "shop", "new_object": "new-mail"}, "step": "p2", "step_rule": "successor_first",
     "declaration_ref": "decl:ctx#/migration_plans/0/dependencies/0/method"}
  ],
  "dropped_arguments": [
    {"owner": "t-archive", "role": "retired", "ref": "acme:archive-share", "reason": "out_of_slice",
     "declaration_ref": "decl:ctx#/migration_plans/0/transitions/2/methods/0"}
  ]
}
```

```
F × Z (standard)      shop            crm-sync        new-mail             legacy-mail
migrate.import/v1     –               –               t-mail · target      t-mail · source
migrate.retire/v1     –               –               –                    t-mail · retired
migrate.rewrite/v1    d1 · dependant  –               d1 · new_object      –
off axis (Y): t-box · retired → mailbox-x (see F × Y)
```

## 2. Status and diagnostic rules (0.9.1 only)

| Situation | Result | Diagnostic |
|---|---|---|
| `method_id` neither in the catalog nor in `local_methods` | FAIL, message names `method_id` and `declaration_ref` | `VP09_METHOD_UNKNOWN` (new) |
| `method_profile_refs` names a profile other than `P1.11/migration-methods-v1` | FAIL | `VP09_ADAPTER_INPUT` (existing) |
| F axis, input declares no bindings | PASS, header row and notice, no cells | `VP09_METHODS_NONE` (new, warning) |
| Argument whose referent has a home other than the column axis | PASS, not drawn, listed in the binding ledger | `VP09_ARGUMENT_OFF_AXIS` (new, warning) |
| Binding or argument outside the plan slice | PASS, listed in `dropped_arguments` | `VP09_ARGUMENT_OUT_OF_SLICE` (new, warning) |
| Binding ledger does not account for every `(binding, role)` exactly once | FAIL | `VP09_PANEL_COVERAGE` (existing) |
| Dependency binding without `successor_ref` (local method on a dependency) | PASS, step by fallback rule D-3, `step_rule` in ledger | — |
| All other rows | as 0.9.0 §2 | |

## 3. Rules in detail

### 3.1 Methods (FM)

- FM-1: Catalog IDs are the five IDs of the pinned P1.11 catalog (sha `5e317bce…`). VP-09 keeps them as a constant; a test compares the constant with the pinned P1.11 file (D-5).
- FM-2: `local_methods` lists the `method_id` of every `method_contracts` entry of the context, in declared order. A hand-written axes input may declare it; absent means empty.
- FM-3: Row order of F: catalog order (import, rebuild, retire, rewrite, reconfigure), then local methods in order of first appearance in the bindings. Only declared bindings make a row. No other order (MP-5).
- FM-4: F is never derived: a dependency without `method` does not appear on F, whatever its predicate or kind.

### 3.2 Pairs (FP)

| Pair | Rows × columns | Cell (r, c) holds |
|---|---|---|
| F × Z | methods × Z referents or kinds | `(binding, role)` units with method r whose argument is c (unchanged from 0.9.0) |
| F × Y | methods × Y referents or kinds | the same rule on the Y home (new) |
| F × T | methods × steps | transition bindings with `at_phase` = c; dependency bindings at the step of D-3 |

- FP-1: F × Y joins the D-2 pair list after F × T (field-test priority unchanged for the others); swapped orientation allowed as for every pair.
- FP-2: Empty cell = nothing declared. Overflow `+n more` as D-7.

### 3.3 Binding ledger (FL)

- FL-1: Units are `(binding index, role)` over all transcribed bindings, including arguments outside the slice.
- FL-2: For one rendering, every unit has exactly one state: `drawn` (cell key listed), `off_axis` (home of the referent, e.g. `Y`), `out_of_slice`. In F × T every in-slice binding counts once (unit `(binding, *)`).
- FL-3: Report fields: `binding_ledger` (units with state), `binding_coverage` `{units_total, drawn, off_axis, out_of_slice, status}`; SVG embeds the same ledger. `check-panels` recomputes it.

## 4. Acceptance criteria

| AC | Requirement | Evidence |
|---|---|---|
| VP091-01 | 0.9.0 outputs byte-identical: digests of A-01…A-20 and the 0.9.0 golden pinned before code | regression run |
| VP091-02 | Method check FM-1…FM-4, unknown ID with code and path | B-01…B-05 |
| VP091-03 | Pairs FP-1…FP-2 incl. F × Y | B-06…B-10 |
| VP091-04 | F × T step rule D-3 | B-11…B-13 |
| VP091-05 | Binding ledger FL-1…FL-3 over render and panels | B-14…B-18 |
| VP091-06 | GM-pos (P1.11 golden) as vector: F × Z and F × T complete over panels, 41 / 23 units | B-19, B-20 |
| VP091-07 | Every row in §2 yields exactly the stated result and code | one test per row |
| VP091-08 | No client data in fixtures, examples or previews | review |

## 5. Alignment vectors (exit check)

| ID | Case | Expected |
|---|---|---|
| B-01 | /7 context, catalog methods only, F × Z | PASS, rows in catalog order |
| B-02 | Binding with `migrate.imprt/v1` (typo) | FAIL · `VP09_METHOD_UNKNOWN`, message holds the `declaration_ref` |
| B-03 | Local method contract `acme.archive/v1`, bound once | PASS, row after the catalog rows |
| B-04 | Context declares bindings in reverse catalog order | PASS, rows still in catalog order |
| B-05 | Dependency without `method` but with predicate `sends-via` | PASS, not on F |
| B-06 | F × Y on a context with `import` source/target = two resources | PASS, both Y columns filled |
| B-07 | F × Z on the same context | PASS · `VP09_ARGUMENT_OFF_AXIS`, both arguments listed off-axis (home Y) |
| B-08 | F × Y:kind | PASS, column `Resource` |
| B-09 | F axis on a /5 context | PASS · `VP09_METHODS_NONE`, no cells (D-4) |
| B-10 | Entry text F × Z | `t-mail · source` |
| B-11 | F × T, `rewrite` on d1 (holds p0–p1), successor d2 (holds p2–p3) | PASS, entry `d1` in column p2, `step_rule: successor_first` |
| B-12 | F × T, local method on a dependency without `successor_ref` | PASS, fallback step, `step_rule` per D-3 |
| B-13 | F × T, transition binding at p2 | PASS, column p2 |
| B-14 | Binding owner outside the `--track` slice | PASS · `VP09_ARGUMENT_OUT_OF_SLICE`, ledger lists it |
| B-15 | Render F × Z, ledger counts drawn + off_axis + out_of_slice = units_total | PASS, `binding_coverage.status` COMPLETE |
| B-16 | `print-panels` F × Z over 22 columns | PASS, union of panel ledgers COMPLETE |
| B-17 | `check-panels` after removing one unit from a panel ledger | FAIL · `VP09_PANEL_COVERAGE` |
| B-18 | Same input, `--profile 0.9.0` | byte-identical to the 0.9.0 output |
| B-19 | GM-pos, F × Z, standard, panels | PASS, 41/41 units, 0 off-axis |
| B-20 | GM-pos, F × T, standard | PASS, 23 units; all 16 `rewrite` entries at p2 |

## 6. Decisions (resolved 2026-10-27, all as proposed)

| Decision | Options | Resolution | Consequence |
|---|---|---|---|
| D-1 Profile selection | (a) default stays 0.9.0, `--profile 0.9.1` explicit · (b) default 0.9.1, A-vectors pinned under `--profile 0.9.0` · (c) automatic | **(a)** | The same command line keeps producing the same bytes; there is no input feature that could select automatically (A-vectors already use /7). Switching the default can follow later as its own step. |
| D-2 Y arguments | (a) new pair F × Y; F × Z lists Y arguments as off-axis · (b) F × Z gets a second column group for Y referents · (c) both | **(a)** | Every VP-09 axis keeps one home (AX-2); the ledger makes the missing half visible and points to F × Y. (b) mixes two homes on one axis. |
| D-3 Step of a dependency binding in F × T | (a) 0.9.0: last step of the dependency · (b) C-11: first `holds_in` step of `successor_ref`; without successor: last step of the dependency, `step_rule` recorded · (c) (b) without successor: FAIL | **(b)** | `rewrite` then sits in the column of the cut it belongs to (GM-pos: p2 instead of p1). Both values are declared; nothing is derived. P1.11 MP-3 guarantees a successor for `rewrite`; the fallback only affects local methods. |
| D-4 F axis without bindings | (a) keep FAIL `VP09_AXIS_EMPTY` · (b) PASS with header row, notice and warning `VP09_METHODS_NONE` | **(b)** | A /5 or /6 plan simply has no methods yet; other empty axes stay FAIL (they indicate a wrong axis choice). |
| D-5 Method check | (a) catalog IDs as a VP-09 constant + local `method_contracts`, test against the pinned P1.11 file · (b) VP-09 loads the P1.11 catalog file at run time · (c) no check, as 0.9.0 | **(a)** | No run-time coupling to the P1 package; the pinned catalog cannot change within `migration-methods-v1`. FAIL (not UNRESOLVED as in P1.11), because a printer cannot draw an unknown row honestly; the message points to P1.11. |
| D-6 Entry text | (a) `<owner> · <role>` in 0.9.1 · (b) keep `<owner> (<role>)` | **(a)** | Same separator as Y × Z; 0.9.0 keeps its text. |
| D-7 Arguments outside the slice | (a) transcribed with `in_slice: false`, listed, warning · (b) dropped as 0.9.0 | **(a)** | C-11: no silent omission. |
| D-8 GM-pos in the vectors | (a) materialize copies the GM-pos context and records the sha of the P1.11 golden · (b) vectors read the P1 file at run time | **(a)** | The P2 vectors stay self-contained; a change of the P1 golden shows up as a sha mismatch. |
| D-9 P1.11 README ("VP-09 F axes" listed as not part) | (a) leave P1.11 byte-identical, note the status in the VP-09 README · (b) correct the line, refresh the P1.11 SHA sums | **(a)** | No change to an accepted profile for a documentation detail. |

## 7. Not part of VP-09.1

- Methods in VP-07 views (VP-07.3).
- F × X, F × M, three-way tables; grouping rows by primitive (`transition_supersession`, `derivation`).
- Any statement whether a binding fits the plan — that is P1.11 (MP-1…MP-4).
- MCP tool (as VP-09).
