# TASK-058 — Spezifikation und Detailfragen

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/deliver-remote-plan-views/tasks.md).

Story: [US-030](../04-US/US-030-remote-control-flow.md), [US-031](../04-US/US-031-remote-plan-views.md) · Mile: MILE-010-A · Aufwand: 0,25 PT

## Ziel und Arbeit

Abnahmespezifikation G5 R5 (`P3-MCP-REMOTE/0.8.0-proof`): Tools und Schemas im Gateway, Dispatch im Kern, gestufte Pakete, Grenzen und Fehlercodes, Discovery, Laufzeitmessung, Live-Abnahme. Detailfragen werden benannt und vom Nutzer entschieden; eigener Commit.

## Ergebnis und Akzeptanz

- Spezifikation mit aufgelösten Detailfragen, bevor Erwartungen und Code entstehen.

## Abhängigkeiten und Grenze

Entscheidungen D-1–D-8

Umfang gemäß [MILE-010](../02-Milestones/MILE-010-remote-plan-views.md). Keine neue Prüfsemantik; P0, P1, P2, lokaler Adapter und lunados.lib-Einträge bleiben byte-gleich; geändert wird nur `P3/remote-mcp-g5`.
