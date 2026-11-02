# TASK-056 — G6-Anbindung

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/archive/2026-11-02-show-instance-view/tasks.md).

Story: [US-028](../04-US/US-028-instance-path-view.md) · Mile: MILE-009-C · Aufwand: 0,25–0,5 PT

## Ziel und Arbeit

Printer `vpinstances` in G6 (`cube_plan_source`, `cube_plan_views`, `cube_plan_check`) und Discovery; Ergebnis byte-gleich zur CLI; vorhandene Adapter-Tests grün; G5 unverändert.

## Ergebnis und Akzeptanz

- G6 = CLI für alle Vektoren; Discovery nennt den Printer.

## Abhängigkeiten und Grenze

[TASK-055](TASK-055-vp11-printer.md)

Umfang gemäß [MILE-009](../02-Milestones/MILE-009-instance-view.md). Keine neue Prüfsemantik; P0, P1, VP-07–VP-10 und lunados.lib-Einträge bleiben byte-gleich.

## Ergebnis (2026-11-02)

- `plan_views.py`: Printer `vpinstances` und Sicht `cube.instances`; `cube_plan_source` nimmt `plan_id` null, `statements` (Spur) und optional `records` (Q-10); `cube_plan_views` mit `locale`; `cube_plan_check`. `server.py`: neues optionales Argument `records`, Literale um `vpinstances` und `cube.instances` ergänzt. Discovery nennt `P2-VP-INSTANCES/0.12.0`.
- Neuer Test `test_mile009_instances.py`: alle 34 Vektoren über G6, die 26 gültigen byte-gleich zum Printer, die 8 Fehler mit Printer und Profil durchgereicht, `cube_plan_check` PASS; I-22 deutsch byte-gleich zu den CLI-Dateien.
- Vorhandene Adapter-Suiten grün (146 Tests; `test_g6_plan_views` mit K-17 im Container, weil K-17 allein die Zeitgrenze des Geräts überschreitet; auf dem Gerät K-01–K-16 und K-18 grün). VP-10 0.11.0 15/15 byte-gleich. G5 unverändert: `assemble_core`, G5-Vertrag, Prüfsummen, Parität G4/G5 21/21.
