# TASK-064 — Prüffälle, Orakel und Pins vor Code

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/archive/2026-11-02-declare-relation-origin/tasks.md).

Story: [US-032](../04-US/US-032-relation-origin-profile.md), [US-033](../04-US/US-033-origin-line-view.md) · Mile: MILE-011-A · Aufwand: 0,25 PT

## Ziel und Arbeit

Prüffälle für P1.14 (C4-02, C4-03, MILE-007-Verdichtung, Gegenproben je Diagnose) und VP-07.6 (Herkunftsklassen, Aussagenmengen, Text ohne Linienart lesbar); unabhängiges Orakel; Pins der Ausgaben von VP-07 0.7.0–0.7.5. Alles vor Profil- und Printer-Code committet.

## Ergebnis und Akzeptanz

- Prüffälle, Orakel und Pins committet, bevor Code entsteht; Reihenfolge per git prüfbar.

## Abhängigkeiten und Grenze

[TASK-063](TASK-063-origin-spec.md)

Umfang gemäß [MILE-011](../02-Milestones/MILE-011-relation-origin.md). P0, P1.1–P1.13, VP-07 0.7.0–0.7.5, VP-10, VP-11 und vorhandene lunados.lib-Einträge bleiben byte-gleich.

## Ergebnis (2026-11-02)

- P1.14: [Orakel](../../P1/relation-origin-profile-v1/oracles/independent_ho01_ho12.json) von Hand aus der Spezifikation, [Vektoren HO-01–HO-12](../../P1/relation-origin-profile-v1/fixtures/ho01_ho12_materialized.json) aus dem MILE-007-C4-Kontext, dem Projektionsdatensatz S-04, KF-01 und GM-pos. [Vorher-Lauf](../../P1/relation-origin-profile-v1/fixtures/baseline_p113.json) mit P1.13: HO-01 (`api → db` ohne Herkunft) PASS, jede Herkunftsangabe `PREDICATE_PROFILE_MISSING`.
- VP-07.6: [Orakel](../../P2/visual-printer-migration-v1/oracles/independent_ol01_ol12.json) mit Herkunft, Linienart und Text je Kante, [Vektoren](../../P2/visual-printer-migration-v1/fixtures/ol01_ol12_materialized.json) in G6-Form (13 Fälle, OL-03 a/b). [Pins 0.7.5](../../P2/visual-printer-migration-v1/fixtures/regression_075_digests.json): 16 Szenarien, auf dem Mac gepinnt und 16/16 reproduziert; 0.7.0–0.7.4 behalten ihre Pins.
- Präzisierungen HO-1–HO-3 und OL-A–OL-E in §8 beider Spezifikationen. Charge A abgeschlossen.

