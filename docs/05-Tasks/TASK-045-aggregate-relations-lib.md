# TASK-045 — LIB `project.aggregate-relations/v1`

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/project-statement-sets/tasks.md).

Story: [US-025](../04-US/US-025-relation-aggregation.md) · Mile: MILE-007-B · Aufwand: 0,75–1 PT

## Ziel und Arbeit

Eintrag in lunados.lib (`candidate-authored`): Vertrag, Ergebnisschema, Cube-Methodenvertrag und Referenzfall, Orakel und Fälle aus TASK-044 vor dem Evaluator, Evaluator, INDEX.

## Ergebnis und Akzeptanz

- `scripts/verify.py --cube` grün; alle Fälle gleich dem Orakel; Ergebnis validiert gegen das Schema.

## Abhängigkeiten und Grenze

[TASK-044](TASK-044-statement-set-cases.md)

Umfang gemäß [MILE-007](../02-Milestones/MILE-007-statement-sets.md). Keine neue Prüfsemantik; P0, P1.1–P1.12, VP-07, VP-09 und VP-10 0.10.0/0.10.1 bleiben byte-gleich.
