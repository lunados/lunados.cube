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

## Ergebnis (2026-11-02)

- lunados.lib, Branch `feature/aggregate-relations`: Orakel, Ergebnisschema `aiaeao.projection-result/v1` und Fälle A-01–A-10 (`cee4e36`) vor Evaluator, Eintrag, INDEX und Cube-Referenzfall (`a9b6dd6`). INDEX-Hash `a187a9e12915…`.
- A-01–A-10: Evaluator = Erwartung = Orakel, Schema gültig, keine Promotion. Differenzprüfung auf 150 abgeleiteten Varianten 150/150. `verify.py --cube` 139/139.
- Präzisierung PR-6: Der Evaluator kennt seinen eigenen INDEX-Hash nicht; der Cube liest deshalb einen Projektionsdatensatz mit `library_ref`, Aufruf und Ergebnis.
- [Lauf](../10-Evidence/MILE-007/task045-run.json).
