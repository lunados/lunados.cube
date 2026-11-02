# VP-10 against mockup M-05C (VP10-07)

**Compared:**
- **Printer output:** `docs/10-Evidence/MILE-005/task035/J-08-de.svg`. This is vector J-08 (pair declaration m:printer → m:parser, `--hide-empty cols`, `--locale de`).
- **Mockup:** `docs/09-Research/visual-check/mockups/M-05C.svg` (MILE-003, corrected after TASK-022).

Both show the DSM-03 situation. The comparison is a desk check of cells and texts; no human reading test was run.

## Same cells, same states

| Cell (row → column) | M-05C | VP-10 (J-08, de) |
|---|---|---|
| parser → resolver | hatched (unknown) | hatched (unknown) |
| parser → validator | `d-fb · dependsOn` | `d-fb · verweist auf` (marked) |
| resolver → parser | `d-rp · dependsOn` | `d-rp · verweist auf` (marked) |
| resolver → validator | hatched | hatched |
| validator → parser | hatched | hatched |
| validator → resolver | `d-vr · dependsOn` | `d-vr · verweist auf` (marked) |
| printer → parser | `keine · geprüft`, „erklärt: nur diese Zelle“ | `keine · geprüft (Paar)`, bold border |
| printer → resolver | hatched | hatched |
| printer → validator | `d-pv · dependsOn` | `d-pv · verweist auf` (marked) |
| column printer | hidden, named in a strip on the right | hidden, named in the legend: „ausgeblendete Spalten: m:printer (ihre Zellen, auch unbekannte, sind nicht gezeigt)“ |
| diagonal | „Element“ on grey | „Element“ as text, no fill |

All twelve visible cells, the hidden column and its naming match M-05C. As in the mockup, "checked" applies only to the declared cell and not to the row printer.

## Differences, and why

| Difference | Reason |
|---|---|
| Predicate `references` / „verweist auf“ instead of `dependsOn` | The R-1 mapping: VP-09 reads P1.10 plans, and `references` is the catalog's Y → Y predicate |
| Order resolver, validator, printer, parser instead of the declared DSM order | VP-09 orders by first appearance (PO-5, not part of VP-10) |
| Horizontal hatch instead of diagonal | D-5: no collision with VP-07 hatches A (`/`) and B (`\`) |
| Hidden column in the legend, not a strip | The legend already carries the hidden names (PO-6); a strip would need a new layout element |
| Scope as `(Paar)` instead of „erklärt: nur diese Zelle“ | One word per scope (Paar, Zeile, Spalte); the legend explains it |
| Diagonal without grey fill | Fill carries no state (CS-6) |
| No „Rückkopplung“ note on d-fb | A feedback reading needs the declared order (PO-5) |

## Restbefund

The pre-check found that the M-05C footer still says „Vollständigkeitserklärung“. VP-10 uses „erklärter Erhebungsumfang“ instead, which is closer to CV-5 (a survey scope, not proof).
