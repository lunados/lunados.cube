# US-033 — Herkunftslinie sehen

Status: done · Epic: [EPIC-011](../03-Epics/EPIC-011-relation-origin.md) · Mile: [MILE-011-A, -C](../02-Milestones/MILE-011-relation-origin.md)

Als Leser einer Architektur- oder Migrationsübersicht möchte ich auf einen Blick sehen, welche Linien deklariert, abgeleitet oder in ihrer Herkunft unbekannt sind, damit ich eine Verdichtung nicht als Entscheidung lese.

## Akzeptanz

- `cube.flow` (VP-07 0.7.6) zeichnet durchgezogen = deklariert, gestrichelt = abgeleitet, gepunktet = unbekannt oder nicht gebunden; die Herkunft steht zusätzlich als Text; die Pfeilspitze ist neutral.
- `cube.flow` liest dafür auch Aussagenmengen ohne Migrationsplan.
- VP-07 0.7.0–0.7.5 bleiben byte-gleich; CLI = G6 = G5.
- Kurze Sichtprüfung durch den Nutzer beantwortet; jedes „nein“ bearbeitet.
- Die in den verlinkten Tasks benannten Abschlusskriterien sind erfüllt oder konkret offen ausgewiesen; offene Pflichtkriterien verhindern den Story-Abschluss.

## Aufgaben

- [TASK-063 — Spezifikation und Detailfragen](../05-Tasks/TASK-063-origin-spec.md)
- [TASK-064 — Prüffälle, Orakel und Pins vor Code](../05-Tasks/TASK-064-origin-cases.md)
- [TASK-066 — Printer VP-07.6 und G6](../05-Tasks/TASK-066-vp076-printer.md)
- [TASK-067 — G5 und Host-Abnahme](../05-Tasks/TASK-067-origin-g5.md)
- [TASK-068 — Sichtprüfung und Abschluss](../05-Tasks/TASK-068-mile011-close.md)

[Requirement-Zuordnung](../../openspec/changes/archive/2026-11-02-declare-relation-origin/TRACEABILITY.md) · [Führender Aufgabenstatus](../../openspec/changes/archive/2026-11-02-declare-relation-origin/tasks.md).
