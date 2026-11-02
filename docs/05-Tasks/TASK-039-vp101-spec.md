# TASK-039 — Spezifikation VP-10.1 und Orakel

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/deliver-remote-and-ordered-cells/tasks.md).

Story: [US-022](../04-US/US-022-declared-order.md) · Mile: MILE-006-B · Aufwand: 0,25 PT

## Ziel und Arbeit

Abnahmespezifikation VP-10.1 (`P2-VP-CELLS/0.10.1`): `axis_order`, Kennzeichnung nicht aufgeführter Referenten, Rückkopplungsmarke (D-4, D-5), Detailfragen mit Vorschlag; unabhängiges Orakel vor Code.

## Ergebnis und Akzeptanz

- Spezifikation mit aufgelösten Detailfragen; Orakel committet, bevor Code entsteht.

## Abhängigkeiten und Grenze

MILE-005 (VP-10 0.10.0)

Umfang gemäß [MILE-006](../02-Milestones/MILE-006-remote-and-order.md). Keine neue Prüfsemantik; P0, P1.1–P1.12, VP-07, VP-09 und VP-10 0.10.0 bleiben byte-gleich.

## Ergebnis (2026-11-02)

- [Spezifikation VP-10.1](../../P2/visual-printer-cells-v1/VP10_1_ACCEPTANCE_SPEC.md): Entwurf `1c21dce`; Detailfragen Q-1–Q-6 nach Vorschlag entschieden (`ec147e5`). O-08 und O-09 sind so präzisiert, dass sie Q-6 und „nicht geordnet“ tatsächlich prüfen.
- Orakel O-01–O-10 und Pins von 16 Ausgaben aus 0.10.0 vor jedem Code committet. Ohne `axis_order` muss alles byte-gleich bleiben.
