# TASK-064 — Prüffälle, Orakel und Pins vor Code

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/declare-relation-origin/tasks.md).

Story: [US-032](../04-US/US-032-relation-origin-profile.md), [US-033](../04-US/US-033-origin-line-view.md) · Mile: MILE-011-A · Aufwand: 0,25 PT

## Ziel und Arbeit

Prüffälle für P1.14 (C4-02, C4-03, MILE-007-Verdichtung, Gegenproben je Diagnose) und VP-07.6 (Herkunftsklassen, Aussagenmengen, Text ohne Linienart lesbar); unabhängiges Orakel; Pins der Ausgaben von VP-07 0.7.0–0.7.5. Alles vor Profil- und Printer-Code committet.

## Ergebnis und Akzeptanz

- Prüffälle, Orakel und Pins committet, bevor Code entsteht; Reihenfolge per git prüfbar.

## Abhängigkeiten und Grenze

[TASK-063](TASK-063-origin-spec.md)

Umfang gemäß [MILE-011](../02-Milestones/MILE-011-relation-origin.md). P0, P1.1–P1.13, VP-07 0.7.0–0.7.5, VP-10, VP-11 und vorhandene lunados.lib-Einträge bleiben byte-gleich.
