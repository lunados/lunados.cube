# EPIC-003 — Reproduzierbare Vergleichsprüfung

Status: done · Milestone: [MILE-001](../02-Milestones/MILE-001-analysis-readiness.md)

## Ergebnis und Umfang

Vorhandene Fälle werden mit fixierter Erwartung reproduziert, Fehlergrenzen erhalten und eine minimale Profilvariante gegen ihren Ausgangsstand verglichen.

## Akzeptanz

- PASS, FAIL und UNRESOLVED sind reproduzierbar; Fachstatus und Übereinstimmung mit Erwartung sind getrennt.
- Herkunft, Eingaben, Versionen und Rohantwort sind nachvollziehbar; nicht geprüfte Dimensionen bleiben offen.
- Ausgangsfall und Profilvariante bleiben getrennt; ein gemeinsamer Bereitschaftsnachweis ermöglicht die Folgeanalyse.

## Stories

- [US-003](../04-US/US-003-repeatable-probes.md)
- [US-001](../04-US/US-001-reproducible-comparison.md)
- [US-004](../04-US/US-004-analysis-handover.md)

## Aufgaben

- [TASK-003 — Minimales Fall- und Berichtsformat festlegen](../05-Tasks/TASK-003-comparison-case-contract.md)
- [TASK-004 — Vorhandene Prüfungen wiederholbar aufrufen](../05-Tasks/TASK-004-repeatable-probe-runner.md)
- [TASK-005 — Ausgangsstand und Profilvariante vergleichen](../05-Tasks/TASK-005-baseline-variant-comparison.md)
- [TASK-006 — Fehler- und Unsicherheitsgrenzen absichern](../05-Tasks/TASK-006-diagnostic-boundaries.md)
- [TASK-007 — Gemeinsamen Bereitschaftsnachweis erstellen](../05-Tasks/TASK-007-readiness-evidence.md)
- [TASK-008 — Spezifikation und Analyseübergabe abschließen](../05-Tasks/TASK-008-readiness-handover.md)

## Aufwand / Nutzen / Komplexität

6–12 h, erwarteter Nutzen sehr hoch, Komplexität niedrig–mittel. Annahmen und Grenzen stehen im Milestone. Führende Checkliste: [tasks.md](../../openspec/changes/archive/2026-11-01-prepare-grammar-comparison/tasks.md).


Ergebnis und Grenzen: [Charge C](../10-Evidence/MILE-001/C-RESULT.md), 2026-11-01.
