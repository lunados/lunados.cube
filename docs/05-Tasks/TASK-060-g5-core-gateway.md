# TASK-060 — Kern und Gateway

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/deliver-remote-plan-views/tasks.md).

Story: [US-030](../04-US/US-030-remote-control-flow.md), [US-031](../04-US/US-031-remote-plan-views.md) · Mile: MILE-010-B · Aufwand: 1,25–2 PT

## Ziel und Arbeit

G5-Kern `0.8.0-proof`: P1.13 und die Plan-Printer stufen (`assemble_core.py`, Laufzeit-Assets), Dispatch für `/9` und die drei Plan-Tools; Gateway: drei Tools mit Schemas; Discovery. Offline-Prüfung: Remote = lokal für alle Vektoren, Laufzeitmessung nach D-6, Asset- und Prüfsummenprüfung, Parität G4/G5.

## Ergebnis und Akzeptanz

- Offline alles grün; Messung dokumentiert; bei Überschreitung Umfang nach D-6 begrenzt.

## Abhängigkeiten und Grenze

[TASK-059](TASK-059-g5-r5-expectations.md)

Umfang gemäß [MILE-010](../02-Milestones/MILE-010-remote-plan-views.md). Keine neue Prüfsemantik; P0, P1, P2, lokaler Adapter und lunados.lib-Einträge bleiben byte-gleich; geändert wird nur `P3/remote-mcp-g5`.
