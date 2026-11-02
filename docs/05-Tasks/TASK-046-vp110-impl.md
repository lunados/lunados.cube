# TASK-046 — VP-10 0.11.0 und G6

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/project-statement-sets/tasks.md).

Story: [US-024](../04-US/US-024-statement-set-view.md), [US-025](../04-US/US-025-relation-aggregation.md) · Mile: MILE-007-C · Aufwand: 0,75–1,5 PT (eigener Zeichner, Q-3)

## Ziel und Arbeit

`vpcells` liest Aussagenmengen und Projektionsergebnisse (`from-statements`), Profil 0.11.0; abgeleitete Einträge mit Quellenzahl, Verlust in Legende und Ledger; CLI und G6.

## Ergebnis und Akzeptanz

- Vektoren wie Orakel; 0.10.0/0.10.1 byte-gleich (Pins); VP-07/VP-09 unverändert; Adapter-Tests grün.

## Abhängigkeiten und Grenze

[TASK-044](TASK-044-statement-set-cases.md), für abgeleitete Einträge [TASK-045](TASK-045-aggregate-relations-lib.md)

Umfang gemäß [MILE-007](../02-Milestones/MILE-007-statement-sets.md). Keine neue Prüfsemantik; P0, P1.1–P1.12, VP-07, VP-09 und VP-10 0.10.0/0.10.1 bleiben byte-gleich.
