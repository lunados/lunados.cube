# TASK-059 — Erwartungen vor Code

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/deliver-remote-plan-views/tasks.md).

Story: [US-030](../04-US/US-030-remote-control-flow.md), [US-031](../04-US/US-031-remote-plan-views.md) · Mile: MILE-010-A · Aufwand: 0,25–0,5 PT

## Ziel und Arbeit

Erwartungen vorab: für die Offline-Parität die lokalen G4/G6-Ergebnisse aller vorhandenen Vektoren als Digests; für die Live-Abnahme die Stichproben (`/9`-Fälle, je Sicht ein Vektor, `cube_plan_check`, Grenzfall) mit erwarteten Status, Codes und SVG-Digests.

## Ergebnis und Akzeptanz

- Erwartungen committet, bevor Kern- und Gateway-Code entstehen; synthetisch, ohne Kundendaten.

## Abhängigkeiten und Grenze

[TASK-058](TASK-058-g5-r5-spec.md)

Umfang gemäß [MILE-010](../02-Milestones/MILE-010-remote-plan-views.md). Keine neue Prüfsemantik; P0, P1, P2, lokaler Adapter und lunados.lib-Einträge bleiben byte-gleich; geändert wird nur `P3/remote-mcp-g5`.
