# TASK-054 — Prüffälle, Orakel und Pins

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/show-instance-view/tasks.md).

Story: [US-028](../04-US/US-028-instance-path-view.md), [US-029](../04-US/US-029-join-input-view.md) · Mile: MILE-009-A · Aufwand: 0,25–0,5 PT

## Ziel und Arbeit

Prüffälle aus BPMN-01/02/03 und den MILE-008-Fällen, je mit und ohne LIB-Ergebnis, plus Eingabefehler; unabhängiges Orakel (erwartete Texte, Zustände, Ledger-Einträge, Diagnosen je Fall); Pins der vorhandenen Printer (Digests).

## Ergebnis und Akzeptanz

- Fälle, Orakel und Pins committet, bevor Printer-Code entsteht; synthetisch, ohne Kundendaten.

## Abhängigkeiten und Grenze

[TASK-053](TASK-053-vp11-spec.md)

Umfang gemäß [MILE-009](../02-Milestones/MILE-009-instance-view.md). Keine neue Prüfsemantik; P0, P1, VP-07–VP-10 und lunados.lib-Einträge bleiben byte-gleich.
