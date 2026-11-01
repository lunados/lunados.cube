# TASK-022 — Agenten-Vorprüfung nach Protokoll

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/check-visual-distinctions/tasks.md).

Story: [US-014](../04-US/US-014-agent-precheck-handover.md) · Mile: MILE-003-C · Aufwand: 2 h

## Ziel und Arbeit

Jedes Paar nach den Kriterien des Prüfprotokolls prüfen und die Fallfrage allein aus der Darstellung beantworten; Antworten als Agenten-Proxy kennzeichnen.

## Ergebnis und Akzeptanz

- Prüfbericht je Paar mit Kriterium, Ergebnis, Begründung; keine Aussage über menschliche Verständlichkeit.

## Eingaben / betroffene Ablagen

[Lückenbilanz §6](../09-Research/grammar-sampling/GAP-LEDGER.md), [Fallberichte](../09-Research/grammar-sampling/README.md), [Prüfprotokoll](../09-Research/visual-check/README.md). Neue Ergebnisse unter `docs/09-Research/visual-check/`, Rohnachweise und SVGs unter `docs/10-Evidence/MILE-003/`.

## Abhängigkeiten und Grenze

[TASK-021](TASK-021-mockups.md)

Umfang gemäß [MILE-003](../02-Milestones/MILE-003-visual-check.md). Keine Printer-, Morphologie- oder VG-Ankeränderung. Mockups sind Kandidaten, kein Printer-Output. Die Agenten-Vorprüfung ist kein menschlicher Lesbarkeitsnachweis. Ausführungsnachweis siehe Ergebnis.

## Ergebnis

Erledigt am 2026-11-01. Prüfplan mit Antwortschlüssel vor der Bewertung committet (`1f329ef`); neun Prüfeinheiten (P-01, P-09, R-1 als Ausgangslage, sechs Mockups) nach C1–C6 bewertet, Fallfragen als Agenten-Proxy beantwortet, nicht blind. Nur M-01A erfüllt alle Kriterien. Befunde: Die DAG-Zyklus-Variante hat zwei Zyklen, und jede Kante liegt auf einem (P-09, M-09A/B markieren nur einen); M-05A/B behaupten Vollständigkeit je Zeile statt je Zelle; M-12A zeigt die behauptete Paarung nicht und legt eine Ausführung von ship nahe. Die vier offenen Fragen aus TASK-021 sind beantwortet. Bericht: [PRECHECK.md](../09-Research/visual-check/PRECHECK.md). Kein Lesbarkeitsnachweis; keine Printer-, Anker- oder Morphologieänderung.
