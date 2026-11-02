# TASK-058 — Spezifikation und Detailfragen

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/archive/2026-11-02-deliver-remote-plan-views/tasks.md).

Story: [US-030](../04-US/US-030-remote-control-flow.md), [US-031](../04-US/US-031-remote-plan-views.md) · Mile: MILE-010-A · Aufwand: 0,25 PT

## Ziel und Arbeit

Abnahmespezifikation G5 R5 (`P3-MCP-REMOTE/0.8.0-proof`): Tools und Schemas im Gateway, Dispatch im Kern, gestufte Pakete, Grenzen und Fehlercodes, Discovery, Laufzeitmessung, Live-Abnahme. Detailfragen werden benannt und vom Nutzer entschieden; eigener Commit.

## Ergebnis und Akzeptanz

- Spezifikation mit aufgelösten Detailfragen, bevor Erwartungen und Code entstehen.

## Abhängigkeiten und Grenze

Entscheidungen D-1–D-8

Umfang gemäß [MILE-010](../02-Milestones/MILE-010-remote-plan-views.md). Keine neue Prüfsemantik; P0, P1, P2, lokaler Adapter und lunados.lib-Einträge bleiben byte-gleich; geändert wird nur `P3/remote-mcp-g5`.

## Ergebnis (2026-11-02)

- [Spezifikation G5 R5](../../P3/remote-mcp-g5/G5_R5_ACCEPTANCE_SPEC.md): Operationen und Wire (RW-1–RW-3), Grenzen, Paketumfang und Assets (ST-1–ST-3), Laufzeitmessung (RM-1–RM-3), Abnahmekriterien R5-01–R5-06. Entwurf `7cc8505`; Q-1–Q-10 nach Vorschlag entschieden.
- Befund: G5 übernimmt den lokalen Adapter bereits unverändert; `/9` und die Plansichten brauchen nur die zusätzlichen Pakete, drei Kernoperationen und drei Gateway-Tools. Das Gateway muss diesmal neu bereitgestellt werden.
