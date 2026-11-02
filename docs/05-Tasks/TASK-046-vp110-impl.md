# TASK-046 — VP-10 0.11.0 und G6

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/project-statement-sets/tasks.md).

Story: [US-024](../04-US/US-024-statement-set-view.md), [US-025](../04-US/US-025-relation-aggregation.md) · Mile: MILE-007-C · Aufwand: 0,75–1,5 PT (eigener Zeichner, Q-3)

## Ziel und Arbeit

`vpcells` liest Aussagenmengen und Projektionsergebnisse (`from-statements`), Profil 0.11.0; abgeleitete Einträge mit Quellenzahl, Verlust in Legende und Ledger; CLI und G6.

## Ergebnis und Akzeptanz

- Vektoren wie Orakel; 0.10.0/0.10.1 byte-gleich (Pins); VP-07/VP-09 unverändert; Adapter-Tests grün.

## Abhängigkeiten und Grenze

[TASK-044](TASK-044-statement-set-cases.md), für abgeleitete Einträge [TASK-045](TASK-045-aggregate-relations-lib.md)

Umfang gemäß [MILE-007](../02-Milestones/MILE-007-statement-sets.md). Keine neue Prüfsemantik; P0, P1.1–P1.12, VP-07, VP-09 und VP-10 0.10.0/0.10.1 bleiben byte-gleich.

## Ergebnis (2026-11-02)

- Umsetzung `310b522`: `from-statements` prüft nur die Auflösung (SS-1–SS-4) und liest einen Projektionsdatensatz aus lunados.lib, ohne nachzurechnen (PR-3, PR-6). Ein eigener Matrix-Zeichner zeichnet Y × Y und Z × Z mit den Zuständen und dem Farbaudit von 0.10.x; Zeile = Subjekt.
- Abgeleitete Einträge tragen „derived · n sources“ / „abgeleitet · n Quellen“; die Legende trägt die exakte Verlustzeile, das Ledger alle Quellen, Beschreibungen, internen und unterdrückten Quellen. Deutsche Texte in `de-0110.json`, eigener Pin.
- CLI `from-statements`; G6 `cube_plan_source` mit `statements`/`projection` statt `plan_id`. Discovery: das Profil-Feld von MILE-005 bleibt `[0.10.0]`, die Opt-in-Profile 0.10.1 und 0.11.0 stehen in einem neuen Feld.
- S-01–S-16 16/16; 0.10.0 16/16 und 0.10.1 9/9 byte-gleich; J 14/14, O 10/10; 17 + 6 neue Tests; alle Adapter-Suiten grün, G6-Parität 201/201; VP-07/VP-09 unverändert.
- Lesart des Orakels: `svg_must_not_contain` als ganze Wörter geprüft, weil „p1“ als Teilzeichenfolge auch das Attributpräfix `data-vp10-` trifft. Im Runner dokumentiert.
- [Lauf](../10-Evidence/MILE-007/task046-run.json) · [Renderings](../10-Evidence/MILE-007/task046/README.md).
