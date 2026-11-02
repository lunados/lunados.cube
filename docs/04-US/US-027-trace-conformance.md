# US-027 — Spur gegen das Modell prüfen

Status: done · Epic: [EPIC-008](../03-Epics/EPIC-008-control-flow.md) · Mile: [MILE-008-A, -B, -C](../02-Milestones/MILE-008-control-flow.md)

Als Betreiber möchte ich je Instanz wissen, ob ein Gateway genau einen Pfad nahm, ob der Default berechtigt war und warum ein Join wartet, damit „Welche Instanz ging welchen Weg?“ und „Warum wartet diese Instanz?“ beantwortbar sind (BPMN-01, BPMN-02).

## Akzeptanz

- LIB `analyze.trace-conformance/v1` mit typisiertem Ergebnis, Orakel und Fällen vor dem Evaluator (D-4).
- Statuslogik nach D-5/D-6: FAIL nur bei belegtem Verstoß, UNRESOLVED bei fehlender Abdeckung oder fehlenden Bedingungsergebnissen; Überschuss gezählt.
- BPMN-01/02 über lokales MCP mit vorab erwartetem Ergebnis.
- Die in den verlinkten Tasks benannten Abschlusskriterien sind erfüllt oder konkret offen ausgewiesen; offene Pflichtkriterien verhindern den Story-Abschluss.

## Aufgaben

- [TASK-048 — Prüffälle und Baseline](../05-Tasks/TASK-048-control-flow-cases.md)
- [TASK-049 — Spezifikation und Detailfragen](../05-Tasks/TASK-049-control-flow-spec.md)
- [TASK-051 — LIB `analyze.trace-conformance/v1`](../05-Tasks/TASK-051-trace-conformance-lib.md)
- [TASK-052 — Adapter, Wiederholung und Abschluss](../05-Tasks/TASK-052-mile008-adapter-rerun.md)

[Requirement-Zuordnung](../../openspec/changes/archive/2026-11-02-check-control-flow/TRACEABILITY.md) · [Führender Aufgabenstatus](../../openspec/changes/archive/2026-11-02-check-control-flow/tasks.md).
