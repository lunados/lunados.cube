# TASK-061 — Bereitstellung und Host-Abnahme

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/deliver-remote-plan-views/tasks.md).

Story: [US-030](../04-US/US-030-remote-control-flow.md), [US-031](../04-US/US-031-remote-plan-views.md) · Mile: MILE-010-C · Aufwand: 0,25–0,5 PT

## Ziel und Arbeit

Bereitstellung durch den Nutzer nach `DEPLOYMENT.md` (kurze Anleitung); Host-Abnahme live über den G5-Connector mit den vorab festgelegten Erwartungen; Bericht R5.

## Ergebnis und Akzeptanz

- Alle Stichproben wie erwartet oder Abweichung benannt; Bericht committet.

## Abhängigkeiten und Grenze

[TASK-060](TASK-060-g5-core-gateway.md)

Umfang gemäß [MILE-010](../02-Milestones/MILE-010-remote-plan-views.md). Keine neue Prüfsemantik; P0, P1, P2, lokaler Adapter und lunados.lib-Einträge bleiben byte-gleich; geändert wird nur `P3/remote-mcp-g5`.
