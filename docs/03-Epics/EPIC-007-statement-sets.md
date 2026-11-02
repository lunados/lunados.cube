# EPIC-007 — Aussagenmengen darstellen und verdichten

Status: planned · Milestone: [MILE-007](../02-Milestones/MILE-007-statement-sets.md) · Voraussetzung: [EPIC-006](EPIC-006-remote-and-readability.md)

## Ergebnis

Cube-Aussagen lassen sich ohne Migrationsplan als Matrix zeigen. Verdichtete Beziehungen nennen ihre Quellen und den Verlust, und die Matrix unterscheidet abgeleitete von deklarierten Einträgen.

## Umfang

- Format für Aussagenmengen und Lesen in `cube.cells` (VP-10 0.11.0);
- LIB `project.aggregate-relations/v1` mit Quellenspur und Verlustbericht;
- kurze Sichtprüfung.

Keine neue Prüfsemantik, keine Änderung an P0, P1.1–P1.12, VP-07, VP-09 oder VP-10 0.10.x.

## Akzeptanz

- C4-02 und DSM-01 laufen ohne Umbiegen in einen Migrationsplan, mit vorab festgelegter Erwartung.
- Jede abgeleitete Beziehung nennt alle Quellen; Verlust und Strategie stehen im Ergebnis und in der Darstellung.
- VP-10 0.10.0 und 0.10.1 byte-gleich.

## Stories

- [US-024 — Aussagenmenge ohne Plan darstellen](../04-US/US-024-statement-set-view.md)
- [US-025 — Beziehungen mit Quellenspur verdichten](../04-US/US-025-relation-aggregation.md)
