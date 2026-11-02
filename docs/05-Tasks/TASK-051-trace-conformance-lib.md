# TASK-051 — LIB `analyze.trace-conformance/v1`

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/archive/2026-11-02-check-control-flow/tasks.md).

Story: [US-027](../04-US/US-027-trace-conformance.md) · Mile: MILE-008-B · Aufwand: 1–1,5 PT

## Ziel und Arbeit

Eintrag in lunados.lib (`candidate-authored`): Vertrag, Ergebnisschema, Cube-Methodenvertrag und Referenzfall, Orakel und Fälle aus TASK-048 vor dem Evaluator, Evaluator, Differenzprüfung, INDEX.

## Ergebnis und Akzeptanz

- `scripts/verify.py --cube` grün; alle Fälle gleich Erwartung und Orakel; Ergebnis validiert gegen das Schema.

## Abhängigkeiten und Grenze

[TASK-049](TASK-049-control-flow-spec.md)

Umfang gemäß [MILE-008](../02-Milestones/MILE-008-control-flow.md). Keine Änderung an P0, P1.1–P1.12, P2 oder lunados.lib-Einträgen; neue Fähigkeiten als eigenes Profil und eigener LIB-Eintrag.

## Ergebnis (2026-11-02)

- Umgesetzt durch ChatGPT „Astra“ (laut Nutzer) in lunados.lib, Branch `codex/task-051-trace-conformance`: [Nachweis](../10-Evidence/MILE-008/TASK-051-LIB.md).
- In TASK-052 geprüft: 18/18, Differenzprüfung 471, `verify --cube` 159/159; Orakeländerung nach dem Evaluator ohne Einfluss auf Erwartungen ([Prüfung](../10-Evidence/MILE-008/TASK-052-REVIEW.md)).
