# TASK-034 — Populationsprüfung als LIB-Eintrag

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/declare-completeness-and-instances/tasks.md).

Story: [US-018](../04-US/US-018-completeness.md) · Mile: MILE-005-B · Aufwand: 0,75–1 PT

## Ziel und Arbeit

Reine Populations-/Zählprüfung über Aussagenmengen als lunados.lib-Eintrag (entry/v1: Rollen, Ausgabe, Nicht-Implikationen, Evaluator, Orakel, Fälle) nach D-6, mit typisiertem Ergebnisschema (erster Anwendungsfall für LR-1).

## Ergebnis und Akzeptanz

- Eintrag mit unabhängigem Orakel und Referenzfällen; alle Fälle wie erwartet.

## Eingaben

[Lernbilanz](../09-Research/learning-balance/LERNBILANZ.md), [Lückenbilanz](../09-Research/grammar-sampling/GAP-LEDGER.md) (G-01, G-08), [Darstellungsübergabe](../09-Research/visual-check/HANDOVER.md) (VR-05), [Probeergebnisse](../09-Research/learning-balance/PROBE-RESULTS.md).

## Abhängigkeiten und Grenze

[TASK-032](TASK-032-resolve-decisions.md)

Umfang gemäß [MILE-005](../02-Milestones/MILE-005-completeness-instances.md). P0, P1.1–P1.9 und P2 bleiben byte-gleich; neue Fähigkeiten als eigenes Profil bzw. eigener Printer-Stand.

## Ergebnis (2026-11-02)

Umgesetzt in lunados.lib auf Branch `feature/analyze-population`: Eintrag `entries/analyze.population/v1/`, Status `candidate-authored`, INDEX-Hash `f69963e0b0f5…`.

- **Reihenfolge:** Orakel, Ergebnisschema und Fälle wurden vor dem Evaluator committet (`33ce6c3`), der Eintrag danach (`c649931`). Die Eingaben der Fälle stammen aus den P1.12-Vektoren K-01–K-16. Status, Wert und Anzahl stammen aus dem Cube-Orakel `lib_expected`. `covered_by`, `per_flow` und `missing_scope` sind von Hand festgelegt.
- **Fälle:** CC-01–CC-16 16/16. Der Evaluator gibt genau die Erwartung aus, das unabhängige Programm-Orakel stimmt überein, jede Ausgabe ist gültig gegen `aiaeao.population-result/v1` (LR-1, erster Anwendungsfall). `verify.py --cube` ergibt 127/127 checks, einschließlich des Cube-Referenzfalls.
- **Differenzprüfung:** 105 abgeleitete Varianten ohne Abweichung zwischen Evaluator und Orakel; fehlerhafte Regeln werden abgewiesen (3/3). Skript und Ergebnis: [task034_differential.py](../10-Evidence/MILE-005/task034_differential.py), [task034-run.json](../10-Evidence/MILE-005/task034-run.json).
- **Bibliotheksvertrag:** Er ist um den Eintragstyp `authored` erweitert, also eine nativ verfasste Funktion ohne Ursprungsexperiment. `verify.py` prüft zusätzlich jede Ausgabe gegen das Ergebnisschema. Die bestehenden zehn Einträge sind unverändert.
- **Grenze:** Ein Fall ohne Abdeckung ergibt UNRESOLVED `coverage_undeclared`, nie FAIL. `absent_checked` bedeutet „keine Aussage im erklärten Umfang“, nicht „existiert nicht“.

lunados.lib ist noch nicht gepusht.
