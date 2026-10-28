# VP-09.2 — Y × Y, arguments in F × T and readable cells · Acceptance specification

**Status:** SPECIFIED, decisions D-1…D-9 resolved 2026-10-28 (all as proposed) — ready for oracle transcription and implementation.
**Profile:** `P2-VP-AXES/0.9.2`, follow-up to `0.9.1` (VP-09.1, PR #22) in `vpaxes`; opt-in via `from-plan --profile`.
**Requirement:** C-12 items (a), (c), (d), (f), (g), (h), (i) for VP-09 (field test 2026-10-28; client details withheld). Item (b) does not apply: VP-09 draws no ledger block (the ledger is embedded only). Items (b) and (e) and the VP-07 parts of (a), (h), (i) are VP-07.5.
**Basis:** `VP09_ACCEPTANCE_SPEC.md` (AX-1…AX-3, CM table, D-2 pair list, D-7 overflow), `VP09_1_ACCEPTANCE_SPEC.md` (FL binding ledger, D-3 step rule, D-6 entry text), `VP07_5_ACCEPTANCE_SPEC.md` (locale profile, D-2); Morphology v9.4 §3.3 (blank cells do not impose a relationship).
**Motivation:**

| Finding in 0.9.1 | Effect in the field |
|---|---|
| No Y × Y pair | Account → account dependencies (e.g. restoring a mailbox through another account) are visible only in Y × T |
| F × T shows only the owner (`t1`) | Runbooks need the arguments (`t1 · import: legacy-mail → new-mail`) |
| Rows and columns without any entry are drawn | Large blank areas in F × Z |
| `wrap_words` splits overlong words (`…-calenda / r · target`) | Unreadable cell text |
| One report line per hint | Up to 41 lines of `VP09_ARGUMENT_OUT_OF_SLICE` |
| Diagnostics say `profile: P2-VP-AXES/0.9.0` for a 0.9.1 input | Wrong profile in error output |

## 0. Scope

| In scope | Out of scope |
|---|---|
| Pair Y × Y (directed, declared dependencies between two Y referents) | Y × Y through transitive chains |
| F × T entries with arguments | Argument text in F × Z / F × Y (already role-based) |
| `--hide-empty rows|cols|both` | Hiding cells; reordering |
| Wrapping at separators, otherwise `…` with full text in `<title>` | Changes to 0.9.0 / 0.9.1 drawing |
| Locale (`--locale de`) with the VP-07.5 locale files | Translating IDs |
| Grouped hints; diagnostics with input profile | — |

## 1. Design summary

1. **Profile.** `from-plan --profile P2-VP-AXES/0.9.2`; includes all of 0.9.1. The new options are accepted only for 0.9.2 inputs (D-1).
2. **Y × Y (c).** Rows and columns are Y referents (or Y kinds). Cell (r, c) lists the declared dependencies with subject r and object c, as `<dependency> · <predicate>` (D-2: directed). The diagonal stays empty unless a dependency names the same referent twice.
3. **F × T arguments (d).** A transition entry reads `<owner> · <short>: <arg> → <arg>` for two-argument methods in the catalog's role order (`import: source → target`), `<owner> · <short>: <arg>` for one argument; local methods list `role=value` (D-3). Dependency entries add the dependant → new object of `rewrite`. Overflow `+n more` as before; full entries in ledger and `<title>`.
4. **Hide empty (f).** `--hide-empty rows|cols|both` leaves out values without any entry after projection; the report keeps `row_values_all` / `col_values_all` and `hidden_rows` / `hidden_cols` with counts (D-4).
5. **Wrapping (g).** Cell and header text wraps at spaces and after the separators `-`, `_`, `/`, `.`, `:`, `·`; a piece longer than a line is shortened with `…`; the full entry stays in `<title>` and the ledger (D-5).
6. **Locale (a).** As VP-07.5: header, legend, membership rules, step roles and predicate names; IDs unchanged (D-6).
7. **Grouped hints (h), diagnostics (i).** As VP-07.5 D-7, D-8: `warning_summary`; a 0.9.2 diagnostic names its input profile (D-7, D-8).

### 1.1 Shape (illustrative, synthetic)

```
F × T (0.9.2)          p1                              p2
migrate.import/v1      –                               t-mail · import: legacy-mail → new-mail
migrate.retire/v1      –                               t-mail · retire: legacy-mail
migrate.rewrite/v1     –                               d1 · rewrite: shop → new-mail

Y × Y (0.9.2)          admin-mailbox                   archive-box
support                d9 · restores-via               –
admin-mailbox          –                               d10 · depends-on
```

## 2. Status and diagnostic rules (0.9.2 only)

| Situation | Result | Code |
|---|---|---|
| Pair Y × Y on 0.9.0 / 0.9.1 | FAIL | `VP09_AXIS_INVALID` (existing) |
| `--hide-empty` / `--locale` on an input below 0.9.2 | FAIL | `VP09_SOURCE_INVALID` (existing) or `VP07_LOCALE_INVALID` mapped to `VP09_LOCALE_INVALID` (new) |
| Every row (or column) hidden | PASS, empty table with notice | `VP09_ALL_EMPTY` (new, warning) |
| Text shortened in a cell | PASS, `<title>` holds the full text | — |
| Any 0.9.2 FAIL | diagnostic names the input profile | — |

## 3. Rules in detail

- YY-1: Membership: dependencies whose subject and object both have home Y; row = subject, column = object.
- YY-2: Y × Y rows and columns follow AX-3 (identity anchors, then resource chain; layer order if declared).
- FA-1: Argument order: the catalog's role order (`import`: source, target; `rewrite`: dependant, new_object; others one role); local methods: declared role order.
- FA-2: Out-of-slice arguments show their declared ref with a trailing `*` and stay `out_of_slice` in the binding ledger.
- HE-1: Hiding happens after projection and before the budget check, so hidden values do not count against the budget (D-4); panels split the remaining values.
- WR-1: The wrap helper is new and used only by 0.9.2; 0.9.0 / 0.9.1 keep `wrap_words`.

## 4. Acceptance criteria

| AC | Requirement | Evidence |
|---|---|---|
| VP092-01 | 0.9.0 and 0.9.1 byte-identical (0.9.1 digests pinned before code) | regression run |
| VP092-02 | Y × Y YY-1, YY-2 | H-01…H-04 |
| VP092-03 | F × T arguments FA-1, FA-2 | H-05…H-08 |
| VP092-04 | Hide empty HE-1 | H-09…H-11 |
| VP092-05 | Wrapping WR-1 | H-12, H-13 |
| VP092-06 | Locale, grouped hints, diagnostics | H-14…H-16 |
| VP092-07 | Every §2 row | one test per row |
| VP092-08 | Synthetic golden: GM-pos with Y × Y additions, F × T with arguments, hidden empty columns, `de` | fixture |
| VP092-09 | No client data | review |

## 5. Alignment vectors (exit check)

| ID | Case | Expected |
|---|---|---|
| H-01 | Y × Y with `support → admin-mailbox` | PASS, entry in (support, admin-mailbox) only |
| H-02 | Y × Y:kind | PASS, (Actor, Resource) |
| H-03 | Y × Y on 0.9.1 | FAIL · `VP09_AXIS_INVALID` |
| H-04 | Y × Y without any Y → Y dependency | PASS, blank table (or `VP09_ALL_EMPTY` with `--hide-empty both`) |
| H-05 | F × T import | `t-mail · import: legacy-mail → new-mail` |
| H-06 | F × T rewrite on d1 | `d1 · rewrite: shop → new-mail` at p2 |
| H-07 | Local method with one argument | `t-box · acme.archive/v1: arg1=hosting` |
| H-08 | Argument outside the slice | ref with `*`, ledger `out_of_slice` |
| H-09 | `--hide-empty cols` on F × Z | blank columns gone; report counts them |
| H-10 | `--hide-empty both` keeps panels coverage COMPLETE | PASS |
| H-11 | Hidden values do not count against the budget | F × Z at standard fits after hiding |
| H-12 | Entry `a01a · new_object` with a 40-character ID | wrapped at `-` / `:`; no piece split inside a word |
| H-13 | 80-character ID without separators | shortened with `…`, full text in `<title>` |
| H-14 | `--locale de` | German header, legend and step roles; IDs unchanged |
| H-15 | 41 out-of-slice hints | one summary entry, count 41 |
| H-16 | Invalid axis on a 0.9.2 input | diagnostic `profile: P2-VP-AXES/0.9.2` |

## 6. Decisions (resolved 2026-10-28, all as proposed)

| Decision | Options | Resolution | Consequence |
|---|---|---|---|
| D-1 Profile | (a) 0.9.2 only via `--profile`; new options only for 0.9.2 inputs · (b) options on any input | **(a)** | C-12 rule; 0.9.0 / 0.9.1 bytes stay. |
| D-2 Y × Y direction | (a) directed: row = subject, column = object · (b) symmetric: both cells | **(a)** | The dependency has a direction; (b) would double every entry. |
| D-3 Argument text in F × T | (a) `owner · verb: a → b` for two catalog roles, `owner · verb: a` for one, `role=value` for local methods · (b) always `role=value` | **(a)** | Readable for runbooks; the ledger keeps role names. |
| D-4 Hidden values and the budget | (a) hide before the budget check (fewer panels) · (b) hide after (same panels, emptier) | **(a)** | The point of hiding is a compact picture; the report lists every hidden value. |
| D-5 Wrapping | (a) break at spaces and after `- _ / . : ·`, else `…` with full text in `<title>` · (b) only `…` | **(a)** | IDs like `acme:legacy-calendar` stay whole on two lines. |
| D-6 Locale source | (a) the VP-07.5 locale files (one set for P2) · (b) VP-09's own | **(a)** | One vocabulary across views. |
| D-7 Grouped hints | (a) keep `warnings`, add `warning_summary` · (b) replace | **(a)** | Same as VP-07.5 D-7. |
| D-8 Diagnostics profile | (a) 0.9.2 inputs only · (b) also correct 0.9.1 (known bug) | **(a)** | Error output of 0.9.1 stays byte-identical; the wrong profile in 0.9.1 errors is documented in the README. |
| D-9 Golden | (a) GM-pos plus two synthetic Y → Y dependencies · (b) new plan | **(a)** | Same plan as VP-07.3…5 and VP-09.1. |

## 7. Not part of VP-09.2

- Transitive Y × Y, F × Z argument text changes, M / O axes.
- VP-07 items of C-12 (VP-07.5); MCP exposure (through G6 with the new profile).
