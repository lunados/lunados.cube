# VP-07.5 — Locale, hidden ledger and method sets · Acceptance specification

**Status:** SPECIFIED, decisions D-1…D-9 resolved 2026-10-28 (all as proposed) — ready for oracle transcription and implementation.
**Profile:** `P2-VP-MIGRATION/0.7.5`, follow-up to `0.7.4` (VP-07.4, PR #24) in the same package `vpmigration`; opt-in via `from-plan --profile`.
**Requirement:** C-12 items (a), (b), (e), (h), (i) for VP-07 (field test 2026-10-28: 24 runs with VP-07.3/.4 and VP-09.1, all PASS, used for client sign-off, dependency clarification and runbooks; client details withheld). Items (c), (d), (f), (g) and the VP-09 parts of (a), (h), (i) are VP-09.2.
**Basis:** `VP07_ACCEPTANCE_SPEC.md` (PV-1a ledger, PE-1…PE-6), `VP07_1…VP07_4_ACCEPTANCE_SPEC.md` (codes TM-1, layers, methods MT/MD, partition PM-1…PM-5, D-2 of VP-07.4: a bar's group is only its own method), P1.10 predicate profile (predicate IDs), P1.11 (MP-5 no order from methods); VP-02/VP-06 frozen (texts of `cube.flow` panels).
**Motivation:**

| Finding in 0.7.4 | Effect in the field |
|---|---|
| All labels, legends and step roles are English; predicates show their IDs (`sends-via`) | Client sign-off documents need German |
| The DECLARATION LEDGER with `decl:` references fills the lower half of every panel | Clients read internal paths; the picture is twice as tall |
| `--partition method` puts every bar without its own method into `none` | Only the `rewrite` picture is useful; import / retire / rebuild bars land in `none` although the transition names their object |
| Every hint is one line in the report | Long lists (one line per hidden argument) |
| Diagnostics always say `profile: P2-VP-MIGRATION/0.7.0` | The profile of the actual input is not visible |

## 0. Scope

| In scope | Out of scope |
|---|---|
| Locale profile `aiaeao.cube.p2-locale/1` with `de` (and `en` as identity), `print-panels --locale` | Translating IDs, `decl:` references, method IDs or report keys |
| `--hide-ledger` for `cube.phases` (and `cube.flow` per D-3) | Removing the ledger from `report.json` or the embedded ledger |
| Method sets: per method the bars named by its bindings (D-5) | Changing `--partition method` of 0.7.4 |
| Grouped hints in the report; diagnostics name the input profile | Colours, ranks, inferred groups |
| 0.7.0…0.7.4 byte-identical | VP-08 |

## 1. Design summary

1. **Profile.** `from-plan --profile P2-VP-MIGRATION/0.7.5` (D-1). A 0.7.5 source adds `role` to each step (`current`, `intermediate`, `target`, from the plan) so that the printer can translate it; everything else as 0.7.4. The new print options are accepted only for 0.7.5 sources.
2. **Locale (a).** A locale profile is a pinned JSON file: UI strings by key (`legend.bar`, `header.phases`, …), step roles, and predicate display names (`sends-via` → `sendet über`). `--locale de` translates only display text; IDs, method IDs (short names stay `import`, D-4), `decl:` references and report keys stay. Unknown predicates show their ID; the report lists them. The report and the embedded ledger record `locale` and its SHA-256.
3. **Hidden ledger (b).** `--hide-ledger` leaves out the drawn DECLARATION LEDGER block (and its height); `report.json`, the embedded ledger and `check-panels` are unchanged; the report and the SVG root record `ledger_hidden: true`.
4. **Method sets (e).** `--method-sets` prints, per method in catalog order, one set of panels with every bar *named* by a binding of that method: a bar whose subject or object is an argument of the binding, or the bar that carries the binding. A bar can belong to several sets; each set proves its own coverage; bars named by no binding form the set `none`. This is a selection by declared arguments, not a partition, so `--partition method` (0.7.4) stays as it is (D-5, D-6).
5. **Grouped hints (h).** The report keeps `warnings` and adds `warning_summary`: per code `{code, count, items}` in first-appearance order; the CLI prints the summary (D-7).
6. **Diagnostics (i).** A 0.7.5 error names the profile of its input (`profile`) and the printer base profile (`printer_profile`) (D-8).

### 1.1 Shape (illustrative, synthetic)

```json
{"format": "aiaeao.cube.p2-locale/1", "locale": "de", "strings": {"header.phases": "CUBE.PHASES · DEKLARIERTE SCHRITTE UND ABHÄNGIGKEITEN · die Reihenfolge ist deklariert, keine Zeitachse"},
 "step_roles": {"current": "Ist", "intermediate": "Zwischenstand", "target": "Ziel"},
 "predicates": {"sends-via": "sendet über", "depends-on": "hängt ab von"}}
```

```
print-panels --view cube.phases --method-sets --locale de --hide-ledger
set migrate.import/v1   panels 01–02   bars d1, d2, d8 (named as source/target of t-mail)
set migrate.retire/v1   panel 03       bars d1, d7 (retired legacy-mail, mailbox-x)
set migrate.rewrite/v1  panel 04       bars d1, d5 (own binding)
set none                panel 05       bars d3, d4
```

## 2. Status and diagnostic rules (0.7.5 only)

| Situation | Result | Code |
|---|---|---|
| `--locale`, `--hide-ledger` or `--method-sets` on a source below 0.7.5 | FAIL | `VP07_PANEL_PARTITION` (existing) or `VP07_LOCALE_INVALID` (new) for the locale |
| Unknown locale, locale file not pinned or malformed | FAIL | `VP07_LOCALE_INVALID` (new) |
| Predicate without a display name in the locale | PASS, ID shown | `VP07_LOCALE_FALLBACK` (new, warning; grouped) |
| A method set alone exceeds the budget after splitting by subject | FAIL | `VP07_PANEL_PARTITION` (existing) |
| Any 0.7.5 FAIL | diagnostic names the input profile | — |

## 3. Rules in detail

- LC-1: Locale files live in `vpmigration/locales/<locale>.json`, pinned by SHA-256 in code; `en` reproduces today's strings exactly (so `--locale en` on 0.7.5 equals no locale).
- LC-2: Text length: translated strings follow the same budgets (`excerpt`, wrap); a string longer than its slot is shortened with `…`, full text in `<title>`.
- LC-3: `cube.flow` panels: per D-3.
- MS-1: A binding *names* a bar if the bar carries it (cell `method`) or the bar's subject or object is an argument value of a transition binding. Nothing else (no predicate, kind or layer) puts a bar into a set.
- MS-2: Sets in catalog order, local methods after, `none` last; within a set packing as PM-3 (split by subject).
- MS-3: The index lists per set its panels and coverage; the report adds `method_sets: {method: {panels, cells, status}}` and `memberships: {cell: [methods]}`; `check-panels` recomputes both.
- WS-1: `warning_summary` order: first appearance; `items` hold the existing warning objects without `code`.

## 4. Acceptance criteria

| AC | Requirement | Evidence |
|---|---|---|
| VP075-01 | 0.7.0…0.7.4 byte-identical (0.7.4 digests pinned before code) | regression run |
| VP075-02 | Locale LC-1…LC-3 | O-01…O-05 |
| VP075-03 | Hidden ledger | O-06…O-08 |
| VP075-04 | Method sets MS-1…MS-3 | O-09…O-13 |
| VP075-05 | Grouped hints, diagnostics with input profile | O-14, O-15 |
| VP075-06 | Every §2 row | one test per row |
| VP075-07 | Synthetic golden (GM-pos): `de`, hidden ledger, method sets import / rebuild / retire / rewrite / none | fixture |
| VP075-08 | No client data | review |

## 5. Alignment vectors (exit check)

| ID | Case | Expected |
|---|---|---|
| O-01 | `--locale de` on `cube.phases` | PASS, header, legend and roles German; IDs unchanged |
| O-02 | Predicate `sends-via` | bar label `legacy-mail · sendet über · rewrite` |
| O-03 | Predicate missing in the locale | PASS · `VP07_LOCALE_FALLBACK`, ID shown |
| O-04 | `--locale en` on 0.7.5 | equal bytes to no locale on 0.7.5 |
| O-05 | `--locale xx` | FAIL · `VP07_LOCALE_INVALID` |
| O-06 | `--hide-ledger` | PASS, no ledger text in the SVG; embedded ledger and report unchanged; `ledger_hidden` |
| O-07 | `check-panels` on a hidden-ledger directory | PASS |
| O-08 | `--hide-ledger` on a 0.7.4 source | FAIL |
| O-09 | `--method-sets` on the VP-07.3 plan | sets import, retire, rewrite, none with the bars of the shape above |
| O-10 | A bar named by two methods | in both sets; `memberships` lists both |
| O-11 | Bar named by no binding | only in `none` |
| O-12 | Every set COMPLETE; `check-panels` recomputes sets | PASS |
| O-13 | 30 bars named by one import | set split by subject |
| O-14 | 41 hidden arguments | one summary entry with count 41 |
| O-15 | Invalid input to a 0.7.5 call | diagnostic `profile: P2-VP-MIGRATION/0.7.5` |

## 6. Decisions (resolved 2026-10-28, all as proposed)

| Decision | Options | Resolution | Consequence |
|---|---|---|---|
| D-1 Profile | (a) 0.7.5 only via `--profile`, print options only for 0.7.5 sources · (b) options on any source, recorded in the panel input | **(a)** | C-12 rule: everything new is opt-in through a new profile; 0.7.4 bytes stay. |
| D-2 Where locales live | (a) pinned files in `vpmigration/locales/`, VP-09 reuses them · (b) a separate P2 locale package · (c) user-supplied locale files | **(a)**, (c) later | One source of strings for P2; pinned so a picture's text is reproducible. |
| D-3 `cube.flow` texts from the frozen VP-02/VP-06 printer (header, edge ledger, footer, VP-04 box) | (a) exact-string replacement in the finished SVG from a fixed table; every replacement must match exactly, otherwise FAIL · (b) translate only VP-07's own lines (layer caption, methods line); frozen texts stay English · (c) no locale for `cube.flow` | **(a)** | A client panel in one language; the frozen printers stay untouched; the audit catches a changed upstream text. Same for `--hide-ledger` in flow (remove the edge-ledger block by its exact header). |
| D-4 Method short names in German | (a) keep `import`, `retire`, … (IDs of P1.11) · (b) translate (`Übernahme`, `Abschaltung`) | **(a)** | Method names are vocabulary of the catalog; a translation table can follow. |
| D-5 Method assignment by arguments | (a) method sets (selection, a bar may appear in several sets) · (b) partition with the first matching method · (c) keep 0.7.4 only | **(a)** | (b) would rank methods by catalog position (MP-5) and hide a bar's second method. Note: VP-07.4 D-2 ruled out assigning transition methods to bars *within a partition*; sets are a separate mode and assign only by declared argument values. |
| D-6 Coverage of method sets | (a) each set COMPLETE for its members, union of all sets = all bars (including `none`) · (b) global coverage only | **(a)** | Every set can be handed out alone (runbook per method). |
| D-7 Grouped hints | (a) keep `warnings`, add `warning_summary`; CLI prints the summary · (b) replace `warnings` | **(a)** | Tools reading `warnings` keep working. |
| D-8 Diagnostics profile | (a) 0.7.5 inputs only: `profile` = input profile, `printer_profile` = base · (b) also for 0.7.1…0.7.4 inputs | **(a)** | Existing outputs, including error output, stay byte-identical. |
| D-9 Golden | (a) GM-pos with `de`, hidden ledger and method sets · (b) new plan | **(a)** | Same plan as VP-07.3/.4 and VP-09.1. |

## 7. Not part of VP-07.5

- VP-09 items of C-12 (VP-09.2), VP-08 locale.
- User-supplied locale files (D-2 c), translated method names (D-4 b).
- MCP exposure (comes through G6 with the new profile).
