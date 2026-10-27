# VP-07.3 — Declared methods at transitions and bars · Acceptance specification

**Status:** SPECIFIED, decisions D-1…D-8 resolved 2026-10-27 (all as proposed) — ready for oracle transcription and implementation.
**Profile:** `P2-VP-MIGRATION/0.7.3`, follow-up to `0.7.2` (VP-07.2) in the same package `vpmigration` (profile dispatch as VP-07.1 PD-1…PD-4).
**Requirement:** C-11 item 3 (optional) from the running migration field test (2026-10-27; client details withheld). Items 1 and 2 are VP-09.1.
**Basis:** `VP07_ACCEPTANCE_SPEC.md` (PV-4 transition markers, MS-1 source, AD-1…AD-9 adapter), `VP07_1_ACCEPTANCE_SPEC.md` (TM-1…TM-5 coded markers and transition legend, PD-1…PD-4), `VP07_2_ACCEPTANCE_SPEC.md` (LS-1…LS-5); `P1/migration-methods-v1/P1_11_ACCEPTANCE_SPEC.md` (bindings on transitions `methods[]` and on dependencies `method`, MP-5, MI-3); `P2/visual-printer-axes-v1/VP09_1_ACCEPTANCE_SPEC.md` (method check FM-1…FM-3, shared with this spec).
**Motivation:** In `cube.phases` the reader sees *that* a transition retires or introduces something and *which* bars end or start, but not *how* the step is done (import, rebuild, rewrite …). The P1.11 bindings carry exactly that, and VP-07 refuses a `binding-context/7` today (`VP07_ADAPTER_INPUT`).

| Finding in 0.7.2 | Effect |
|---|---|
| `from-plan` accepts /5 and /6 only | A /7 context must be stripped by hand before printing |
| Transition legend (TM-5) lists code, ID, step, objects | No method; the field test adds it by hand |
| Bar label `object · predicate` | A `rewrite` on the dependency is invisible |

## 0. Scope

| In scope | Out of scope |
|---|---|
| `from-plan` reads `binding-context/7` and writes a 0.7.3 source with declared methods | Checking bindings (P1.11) |
| Transition legend: methods per code; marker carries them as metadata | Changing marker glyphs, stacking or code width (TM-2…TM-4) |
| Bar label suffix with the method of the dependency | Methods in `cube.flow` panels (VP-02 frozen) |
| Ledger (embedded and report) lists methods per shown transition and cell | Ordering, colouring or grouping by method (MP-5) |
| 0.7.0, 0.7.1, 0.7.2 outputs byte-identical | Layer-map or partition changes; MCP tool |

## 1. Design summary

1. **Adapter.** A /7 context is read through its /6 view (as VP-09 AQ-1) plus the bindings. The source gets profile `0.7.3`; layers (`--layers`) work as in 0.7.2, since 0.7.3 includes 0.7.2.
2. **Source.** `transitions[].methods` and `cells[].method` with `method_id`, `arguments` (role → display ID), `declaration_ref`, `witness_ref?`. Validation like VP-09.1 FM-1…FM-2 (catalog or local method).
3. **Short name.** Catalog IDs `migrate.<verb>/v1` show `<verb>`; local methods show the full ID (D-3).
4. **Transition legend.** TM-5 line per code gets the methods: `T2 · t-mail-cut · p2 · import, retire`. The marker group carries `data-vp07-methods`.
5. **Bars.** Label `object · predicate · rewrite`; when the label is shortened, object and predicate are shortened first, the method stays (D-5). Full text in `<title>`.
6. **Ledger.** The embedded ledger and `report.json` add `methods` to every shown transition and cell; panel ledgers carry them; coverage unit stays `(cell_id, step)`.

### 1.1 Shape (illustrative, synthetic)

```json
{
  "format": "aiaeao.cube.vp07-migration-source/1",
  "profile": "P2-VP-MIGRATION/0.7.3",
  "transitions": [
    {"id": "t-mail-cut", "at": "p2", "retires": ["legacy-mail"], "introduces": ["new-mail"],
     "methods": [
       {"method_id": "migrate.import/v1", "arguments": {"source": "legacy-mail", "target": "new-mail"},
        "declaration_ref": "decl:ctx#/migration_plans/0/transitions/1/methods/0"},
       {"method_id": "migrate.retire/v1", "arguments": {"retired": "legacy-mail"},
        "declaration_ref": "decl:ctx#/migration_plans/0/transitions/1/methods/1"}]}
  ],
  "cells": [
    {"id": "d1", "row": "shop", "object": "legacy-mail", "predicate": "sends-via", "steps": ["p0", "p1"], "successor": "d2",
     "method": {"method_id": "migrate.rewrite/v1", "arguments": {"dependant": "shop", "new_object": "new-mail"},
                "declaration_ref": "decl:ctx#/migration_plans/0/dependencies/0/method"}}
  ]
}
```

```
TRANSITIONS
T1  t-intro-files      p1   introduces new-files            rebuild
T2  t-mail-cut         p2   retires legacy-mail · new-mail  import, retire
bar: legacy-mail · sends-via · rewrite
```

## 2. Status and diagnostic rules (0.7.3 only)

| Situation | Result | Diagnostic |
|---|---|---|
| /7 context with `method_profile_refs` other than `P1.11/migration-methods-v1` | FAIL | `VP07_ADAPTER_INPUT` (existing) |
| `method_id` neither in the catalog nor a local `method_contracts` entry | FAIL, message names ID and `declaration_ref` | `VP07_METHOD_UNKNOWN` (new) |
| Method fields in a source with profile below 0.7.3 | FAIL | `VP07_SOURCE_INVALID` (existing) |
| Binding argument outside the slice (`--track`, `--subject`) | PASS, argument kept as declared ref, ledger marks it | `VP07_METHOD_ARGUMENT_HIDDEN` (new, warning) |
| /7 context without any binding | PASS, 0.7.3 source without method fields | — |
| All other rows | as 0.7.0–0.7.2 | |

## 3. Rules in detail

### 3.1 Transcription (MT)

- MT-1: `from-plan` on /5 or /6 behaves as 0.7.2 (byte-identical). On /7 it writes profile 0.7.3 (D-1).
- MT-2: Method lists keep their declared content; order inside a transition per D-4.
- MT-3: Arguments map refs to display IDs as rows and objects do (AD-3); a ref not in the slice keeps its ref text and is marked hidden.

### 3.2 Drawing (MD)

- MD-1: Markers unchanged in shape, stack and code (TM-1…TM-4); methods appear in the transition legend line and in `data-vp07-methods`.
- MD-2: Bar label: `object · predicate · <short name>`; the short name is never cut; shortening applies to object and predicate first.
- MD-3: No colour, hatch or glyph for methods; the legend gets one line "method · declared P1.11 binding, display only, not checked here".
- MD-4: Panel plans keep the methods of the transitions and cells they show; `check-panels` re-renders as before.

## 4. Acceptance criteria

| AC | Requirement | Evidence |
|---|---|---|
| VP073-01 | 0.7.0, 0.7.1 and 0.7.2 outputs byte-identical (pinned digests extended by the 0.7.2 golden before code) | regression run |
| VP073-02 | Adapter and source MT-1…MT-3 | M-01…M-05 |
| VP073-03 | Drawing MD-1…MD-4 | M-06…M-10 |
| VP073-04 | Panels and ledger | M-11, M-12 |
| VP073-05 | Every row in §2 yields exactly the stated result and code | one test per row |
| VP073-06 | Synthetic golden: GM-pos context, `cube.phases` with all 4 transitions and 16 `rewrite` bars labelled | fixture |
| VP073-07 | No client data in fixtures, examples or previews | review |

## 5. Alignment vectors (exit check)

| ID | Case | Expected |
|---|---|---|
| M-01 | /7 context with bindings | PASS, source profile 0.7.3, methods transcribed with `declaration_ref` |
| M-02 | /6 context | PASS, byte-identical to 0.7.2 output |
| M-03 | Unknown `method_id` | FAIL · `VP07_METHOD_UNKNOWN` |
| M-04 | Local method contract bound to a transition | PASS, full ID in the legend |
| M-05 | Method fields in a 0.7.2 source | FAIL · `VP07_SOURCE_INVALID` |
| M-06 | Transition with import and retire | PASS, legend line `… import, retire` (catalog order, D-4) |
| M-07 | Dependency with `rewrite` | PASS, bar label ends `· rewrite` |
| M-08 | Long object label with `rewrite` | PASS, object shortened, `rewrite` intact; full text in `<title>` |
| M-09 | `data-vp07-methods` on marker groups; no new fill colour | PASS |
| M-10 | /7 context with `--layers` | PASS, layer bands as 0.7.2 plus methods |
| M-11 | `print-panels --partition track` | PASS, panel ledgers carry methods, coverage COMPLETE |
| M-12 | `--track` slice hides one argument | PASS · `VP07_METHOD_ARGUMENT_HIDDEN` |

## 6. Decisions (resolved 2026-10-27, all as proposed)

| Decision | Options | Resolution | Consequence |
|---|---|---|---|
| D-1 Profile selection | (a) a /7 context yields 0.7.3 automatically; /5, /6 unchanged · (b) explicit `--profile 0.7.3` | **(a)** | /7 is refused today, so no existing output changes; same pattern as VP-07.2 (layers select 0.7.2). |
| D-2 Where methods appear at transitions | (a) transition legend line + metadata, marker unchanged · (b) text next to the marker code · (c) both | **(a)** | Markers stack at fixed pitch with codes ≤ 4 characters (TM-3, TM-4); text at the marker would collide in stacks. The legend line already has the form C-11 asks for (`T2 · …`). |
| D-3 Short name | (a) `<verb>` for catalog IDs, full ID for local methods · (b) full ID always · (c) declared label from the contract | **(a)** | Readable and unambiguous; the full ID stays in `<title>` and ledger. |
| D-4 Order of methods inside one transition | (a) catalog order, then local in declared order · (b) declared order of the binding list · (c) alphabetical | **(a)** | Same order as the F rows in VP-09; a declared order could be read as an execution order (MP-5). Note: C-11's example `import, reconfigure, retire` is alphabetical; under (a) it reads `import, retire, reconfigure`. |
| D-5 Bar label | (a) suffix `· <verb>`, method never cut · (b) separate tag at the bar end · (c) legend/ledger only | **(a)** | No new shape; the reader sees the method on the bar itself. |
| D-6 Method check | (a) same rule and constant as VP-09.1 D-5 (shared helper in `vpmigration`, VP-09 imports it) · (b) separate copies | **(a)** | One catalog constant on P2; the VP-09.1 test against the pinned P1.11 file covers both. Order of work: VP-07.3 introduces the helper only if it ships first. |
| D-7 Hidden arguments | (a) keep ref text, mark hidden, warning · (b) drop the argument | **(a)** | No silent omission (C-11). |
| D-8 Golden | (a) GM-pos context (synthetic, from P1.11) · (b) new synthetic plan | **(a)** | Same data as VP-09.1 B-19/B-20; both views of one plan can be compared. |

## 7. Not part of VP-07.3

- Methods in `cube.flow` panels and in VP-08 sequence views.
- Partitioning by method (`--partition method`), colours or hatches for methods.
- Any statement whether a method fits its transition (P1.11 MP-1…MP-4).
