# TASK-005 — Ausgangsstand und Profilvariante vergleichen

Planungsstand: umgesetzt und verifiziert. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/archive/2026-11-01-prepare-grammar-comparison/tasks.md).

Story: [US-001](../04-US/US-001-reproducible-comparison.md) · Mile: MILE-001-C · Aufwand: 1–2 h

## Ziel und Arbeit

Einen bereits geeigneten Fall mit fehlender Profilbindung und seine explizit gebundene Variante paaren. Unterschiede in Eingaben/Profilen und Ergebnissen nachvollziehbar ausweisen.

## Eingaben / betroffene Bereiche

Fall-/Berichtsformat aus TASK-003 und Runner aus TASK-004; vorhandene MODE-Proben mit/ohne Darstellungsprofil als bevorzugte Ausgangsbasis.

Die genannten Ablagen wurden im beschriebenen Umfang umgesetzt; konkrete Nachweise siehe Ergebnisverweis.

## Ergebnis

Ein reproduzierbarer Variantenvergleich mit identifizierbarem Ausgangsstand und minimaler Änderungsbeschreibung.

## Akzeptanz

- Beide Eingaben und Profilrevisionen sind unabhängig erhalten und gehasht; die Baseline wird nicht nachträglich überschrieben.
- Der Bericht zeigt die tatsächlich beobachtete Änderung, ohne zusätzliche Fähigkeiten oder vollständige Kompatibilität zu behaupten.
- Keine neue Envelope-/Morphologieänderung nötig; eine vorhandene Profilvariation genügt für den Nachweis.

## Gezielte Verifikation

Beide Varianten ausführen, explizite Eingabedifferenz und getrennte Diagnosen prüfen. Nutzenaussage bleibt begründete Hypothese, sofern kein Nutzertest stattfand.

## Abhängigkeiten und Grenze

[TASK-003](TASK-003-comparison-case-contract.md), [TASK-004](TASK-004-repeatable-probe-runner.md)

Umfangsgrenze: [MILE-001](../02-Milestones/MILE-001-analysis-readiness.md). Keine Veränderung an Morphologie oder Envelope-Semantik. Der konkrete Nachweis ist unten verlinkt; daraus folgt keine fachliche Gesamtvalidierung.


## Abschlussnachweis

Abgeschlossen am 2026-11-01. [Charge C: Ausführung und Nachweis](../10-Evidence/MILE-001/C-RESULT.md).
