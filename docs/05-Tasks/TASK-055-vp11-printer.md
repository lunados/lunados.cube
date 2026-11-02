# TASK-055 — Printer VP-11 `cube.instances`

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/show-instance-view/tasks.md).

Story: [US-028](../04-US/US-028-instance-path-view.md), [US-029](../04-US/US-029-join-input-view.md) · Mile: MILE-009-B · Aufwand: 1–1,5 PT

## Ziel und Arbeit

Paket `P2/visual-printer-instances-v1`: Eingabeprüfung, Zeichnung, Bericht und Ledger, CLI, materialisierte Vektoren, Tests; Invarianten wie VP-10 (ohne Farbe unterscheidbar, kein aktiver SVG-Inhalt, Ledger passt).

## Ergebnis und Akzeptanz

- Alle Vektoren wie Orakel; Pins der vorhandenen Printer halten; Tests grün.

## Abhängigkeiten und Grenze

[TASK-054](TASK-054-vp11-cases.md)

Umfang gemäß [MILE-009](../02-Milestones/MILE-009-instance-view.md). Keine neue Prüfsemantik; P0, P1, VP-07–VP-10 und lunados.lib-Einträge bleiben byte-gleich.
