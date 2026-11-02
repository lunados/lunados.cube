# TASK-071 — Live-Ausgangswert R5 und R6

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/record-current-state/tasks.md).

Story: [US-034](../04-US/US-034-current-state-recorded.md) · Mile: MILE-012 · Aufwand: 0,25 PT

## Ziel und Arbeit

Der Nutzer lässt die vorhandenen Abnahmeskripte `r5_remote_acceptance.py` und `r6_remote_acceptance.py` einmal gegen den bereitgestellten Kern laufen; die Ergebnisse werden als Ausgangswert committet und in der Grenzen-Seite eingeordnet. Optional, nach Entscheidung des Nutzers: Rotation des Bearer-Tokens nach `DEPLOYMENT.md`, danach derselbe Lauf.

## Ergebnis und Akzeptanz

- Ein Lauf R5 und R6 committet; Abweichungen ausschließlich als benannte Grenzen; Entscheidung zur Rotation festgehalten.

## Abhängigkeiten und Grenze

[TASK-069](TASK-069-g5-ledger-limits.md).

Umfang gemäß [MILE-012](../02-Milestones/MILE-012-record-current-state.md). Keine Änderung an Code oder Payloads.
