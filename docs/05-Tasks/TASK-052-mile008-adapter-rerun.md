# TASK-052 — Adapter, Wiederholung und Abschluss

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/check-control-flow/tasks.md).

Story: [US-026](../04-US/US-026-control-flow-profile.md), [US-027](../04-US/US-027-trace-conformance.md) · Mile: MILE-008-C · Aufwand: 0,75–1,25 PT

## Ziel und Arbeit

`/9` im lokalen `cube_validate` (G4) mit Discovery; Wiederholung der BPMN-Fälle als `/9` über lokales MCP mit vorab erwarteter Antwort; Abschlussprüfung, C-RESULT, Specs konsolidieren, Change archivieren, Übergabe.

## Ergebnis und Akzeptanz

- BPMN-01/02 ausführbar mit vorab erwartetem Ergebnis; Adapter-Tests grün; Abschlussprüfung `all_ok`.

## Abhängigkeiten und Grenze

[TASK-050](TASK-050-p113-profile.md), [TASK-051](TASK-051-trace-conformance-lib.md)

Umfang gemäß [MILE-008](../02-Milestones/MILE-008-control-flow.md). Keine Änderung an P0, P1.1–P1.12, P2 oder lunados.lib-Einträgen; neue Fähigkeiten als eigenes Profil und eigener LIB-Eintrag.
