# TASK-066 — Printer VP-07.6 und G6

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/archive/2026-11-02-declare-relation-origin/tasks.md).

Story: [US-033](../04-US/US-033-origin-line-view.md) · Mile: MILE-011-C · Aufwand: 0,75–1 PT

## Ziel und Arbeit

`P2-VP-MIGRATION/0.7.6` (opt-in): Linienart nach gebundener Herkunft mit Text und fester Legende, `cube.flow` aus Aussagenmengen (`statements` statt `plan_id`), Kopfzeile nach PO-1; CLI und G6 (`cube_plan_source`, `cube_plan_views`, `cube_plan_check`).

## Ergebnis und Akzeptanz

- Vektoren wie das Orakel; VP-07 0.7.0–0.7.5 byte-gleich (Pins); G6 = CLI.

## Abhängigkeiten und Grenze

[TASK-065](TASK-065-p114-profile.md)

Umfang gemäß [MILE-011](../02-Milestones/MILE-011-relation-origin.md). P0, P1.1–P1.13, VP-07 0.7.0–0.7.5, VP-10, VP-11 und vorhandene lunados.lib-Einträge bleiben byte-gleich.
