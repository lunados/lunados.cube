# TASK-056 — G6-Anbindung

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/show-instance-view/tasks.md).

Story: [US-028](../04-US/US-028-instance-path-view.md) · Mile: MILE-009-C · Aufwand: 0,25–0,5 PT

## Ziel und Arbeit

Printer `vpinstances` in G6 (`cube_plan_source`, `cube_plan_views`, `cube_plan_check`) und Discovery; Ergebnis byte-gleich zur CLI; vorhandene Adapter-Tests grün; G5 unverändert.

## Ergebnis und Akzeptanz

- G6 = CLI für alle Vektoren; Discovery nennt den Printer.

## Abhängigkeiten und Grenze

[TASK-055](TASK-055-vp11-printer.md)

Umfang gemäß [MILE-009](../02-Milestones/MILE-009-instance-view.md). Keine neue Prüfsemantik; P0, P1, VP-07–VP-10 und lunados.lib-Einträge bleiben byte-gleich.
