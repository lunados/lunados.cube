# TASK-038 — Bereitstellung und Host-Abnahme

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/deliver-remote-and-ordered-cells/tasks.md).

Story: [US-021](../04-US/US-021-remote-v8.md) · Mile: MILE-006-A · Aufwand: 0,25–0,5 PT (plus Bereitstellung durch den Nutzer)

## Ziel und Arbeit

Der Nutzer stellt den Kern nach `DEPLOYMENT.md` bereit. Der Agent führt die Abnahme live über den G5-Connector mit den vorab festgelegten Erwartungen durch und schreibt `G5_R4_P112_HOST_REPORT.md`.

## Ergebnis und Akzeptanz

- Discovery und Vektoren wie erwartet; Regressionen `/7` und `/1` unverändert.
- Bericht mit Version, Quelle und Abweichungen.

## Abhängigkeiten und Grenze

[TASK-037](TASK-037-g5-core.md)

Umfang gemäß [MILE-006](../02-Milestones/MILE-006-remote-and-order.md). Keine neue Prüfsemantik; P0, P1.1–P1.12, VP-07, VP-09 und VP-10 0.10.0 bleiben byte-gleich.
