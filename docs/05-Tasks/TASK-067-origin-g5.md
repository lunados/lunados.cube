# TASK-067 — G5 und Host-Abnahme

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/declare-relation-origin/tasks.md).

Story: [US-032](../04-US/US-032-relation-origin-profile.md), [US-033](../04-US/US-033-origin-line-view.md) · Mile: MILE-011-C · Aufwand: 0,5–0,75 PT

## Ziel und Arbeit

G5-Kern `0.9.0-proof`: P1.14 und VP-07.6 gestuft, Erwartungen vor Code, Offline-Parität, Bereitstellung durch den Nutzer nach `DEPLOYMENT.md`, Host-Abnahme über den Connector mit vorab festgelegter Teilmenge (wie MILE-010).

## Ergebnis und Akzeptanz

- Remote = lokal für alle neuen Aufrufe; Host-Bericht committet; CPU-Grenze des Workers beachtet und Abweichungen benannt.

## Abhängigkeiten und Grenze

[TASK-066](TASK-066-vp076-printer.md)

Umfang gemäß [MILE-011](../02-Milestones/MILE-011-relation-origin.md). P0, P1.1–P1.13, VP-07 0.7.0–0.7.5, VP-10, VP-11 und vorhandene lunados.lib-Einträge bleiben byte-gleich.
