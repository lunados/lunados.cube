# TASK-052 — Adapter, Wiederholung und Abschluss

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/archive/2026-11-02-check-control-flow/tasks.md).

Story: [US-026](../04-US/US-026-control-flow-profile.md), [US-027](../04-US/US-027-trace-conformance.md) · Mile: MILE-008-C · Aufwand: 0,75–1,25 PT

## Ziel und Arbeit

`/9` im lokalen `cube_validate` (G4) mit Discovery; Wiederholung der BPMN-Fälle als `/9` über lokales MCP mit vorab erwarteter Antwort; Abschlussprüfung, C-RESULT, Specs konsolidieren, Change archivieren, Übergabe.

## Ergebnis und Akzeptanz

- BPMN-01/02 ausführbar mit vorab erwartetem Ergebnis; Adapter-Tests grün; Abschlussprüfung `all_ok`.

## Abhängigkeiten und Grenze

[TASK-050](TASK-050-p113-profile.md), [TASK-051](TASK-051-trace-conformance-lib.md)

Umfang gemäß [MILE-008](../02-Milestones/MILE-008-control-flow.md). Keine Änderung an P0, P1.1–P1.12, P2 oder lunados.lib-Einträgen; neue Fähigkeiten als eigenes Profil und eigener LIB-Eintrag.

## Ergebnis (2026-11-02)

- [Prüfung](../10-Evidence/MILE-008/TASK-052-REVIEW.md) der Fremdumsetzung von TASK-050 und TASK-051: bestanden, sechs Befunde ohne Blocker; Befunde 1 und 2 als Präzisierung CF-2a/2b in §8 der [Spezifikation](../../P1/control-flow-profile-v1/P1_13_ACCEPTANCE_SPEC.md), Befund 5 nachgezogen.
- Erwartung der Wiederholung (`76e5ac1`) vor dem Adapter: `/9` in `cube_validate` und Discovery (`70d0469`), 6 neue Adapter-Tests, G5 unverändert (`/9` dort geschlossen).
- [Wiederholung](../10-Evidence/MILE-008/task052-rerun/README.md): 7/7 über lokales MCP in zwei Verbindungen, LIB-Teil 3/3; die falsche Leitung an Ship und der unbekannte Fluss sind jetzt FAIL, zwei Pfade einer Aktivierung FAIL in LIB.
- Abschluss: [C-RESULT](../10-Evidence/MILE-008/C-RESULT.md), [verification.json](../10-Evidence/MILE-008/verification.json) `all_ok`; Specs konsolidiert, Change archiviert.
