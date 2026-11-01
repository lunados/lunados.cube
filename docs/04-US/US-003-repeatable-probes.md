# US-003 — Vergleichsfälle reproduzierbar prüfen

Status: done · Epic: [EPIC-003](../03-Epics/EPIC-003-reproducible-comparison.md) · Milestone: [MILE-001](../02-Milestones/MILE-001-analysis-readiness.md)

Als Analyst möchte ich vorhandene Erfolgs-, Fehler- und ungelöste Fälle mit denselben Eingaben erneut prüfen, damit Ergebnisse vergleichbar sind und Ausfälle keine falschen fachlichen Urteile erzeugen.

## Akzeptanz

- Drei vorab fixierte Fälle laufen über den lokalen MCP-Pfad; Rohantworten bleiben erhalten.
- Wiederholungen stimmen fachlich überein; Run-ID und Zeit werden separat behandelt.
- Toolfehler, Konfigurationsfehler, fachliches FAIL und UNRESOLVED bleiben unterscheidbar.
- Ausdruck, Bindung, Prüfung, Darstellung und Nutzen werden getrennt beurteilt.

## Aufgaben und Anforderungen

- [TASK-003 — Minimales Fall- und Berichtsformat festlegen](../05-Tasks/TASK-003-comparison-case-contract.md)
- [TASK-004 — Vorhandene Prüfungen wiederholbar aufrufen](../05-Tasks/TASK-004-repeatable-probe-runner.md)
- [TASK-006 — Fehler- und Unsicherheitsgrenzen absichern](../05-Tasks/TASK-006-diagnostic-boundaries.md)

Requirements: Reproducible comparison case; Separate evidence dimensions; Preserve failure and uncertainty. Exakte Zuordnung mit Spec-Links: [TRACEABILITY.md](../../openspec/changes/archive/2026-11-01-prepare-grammar-comparison/TRACEABILITY.md).

Führender Aufgabenstatus: [tasks.md](../../openspec/changes/archive/2026-11-01-prepare-grammar-comparison/tasks.md). Abgeschlossen; [Nachweis B](../10-Evidence/MILE-001/B-RESULT.md).
