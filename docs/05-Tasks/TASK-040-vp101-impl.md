# TASK-040 — VP-10.1 umsetzen

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/deliver-remote-and-ordered-cells/tasks.md).

Story: [US-022](../04-US/US-022-declared-order.md) · Mile: MILE-006-B · Aufwand: 0,5–0,75 PT

## Ziel und Arbeit

VP-10 0.10.1 opt-in: Reihenfolge, Marke, Legende, Audit, Vektoren, Tests, G6-Option.

## Ergebnis und Akzeptanz

- Vektoren wie Orakel; VP-10 0.10.0, VP-09 und VP-07 byte-gleich; G6 nimmt `axis_order` an.

## Abhängigkeiten und Grenze

[TASK-039](TASK-039-vp101-spec.md)

Umfang gemäß [MILE-006](../02-Milestones/MILE-006-remote-and-order.md). Keine neue Prüfsemantik; P0, P1.1–P1.12, VP-07, VP-09 und VP-10 0.10.0 bleiben byte-gleich.

## Ergebnis (2026-11-02)

- Umsetzung `b2f75f5`: `axis_order` als Anzeigeoption (CLI `--axis-order`, G6 `cube_plan_views`). Nur damit gilt Profil `0.10.1`. Ohne die Option sind alle 16 gepinnten Ausgaben aus `0.10.0` byte-gleich, ebenso VP-07 und VP-09 (SHA256SUMS).
- Reihenfolge innerhalb der Art-Gruppe. Nicht gelistete Werte stehen am Ende ihrer Gruppe, mit „nicht geordnet“ im Kopf. Die Marke „Rückkopplung“ ist eine kursive Textzeile ohne Farbe; sie steht nur an markierten Zellen des gewählten Prädikats über der Diagonale. Legende und Ledger sagen, dass sie nur aus der deklarierten Reihenfolge folgt.
- Deutsche Texte für 0.10.1 stehen in einer eigenen gepinnten Datei `de-0101.json`; `de.json` bleibt unverändert.
- O-01–O-10 10/10 gegen das Orakel, O-10 über G6 gleich der CLI und Check PASS. Tests: 14 neue in `vpcells`, 5 im Adapter. Alle bisherigen Suiten bestehen, einschließlich der G6-Parität 201/201.
- [Laufprotokoll](../10-Evidence/MILE-006/task040-run.json) · [Renders](../10-Evidence/MILE-006/task040/README.md).

