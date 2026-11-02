# TASK-067 — G5 und Host-Abnahme

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/archive/2026-11-02-declare-relation-origin/tasks.md).

Story: [US-032](../04-US/US-032-relation-origin-profile.md), [US-033](../04-US/US-033-origin-line-view.md) · Mile: MILE-011-C · Aufwand: 0,5–0,75 PT

## Ziel und Arbeit

G5-Kern `0.9.0-proof`: P1.14 und VP-07.6 gestuft, Erwartungen vor Code, Offline-Parität, Bereitstellung durch den Nutzer nach `DEPLOYMENT.md`, Host-Abnahme über den Connector mit vorab festgelegter Teilmenge (wie MILE-010).

## Ergebnis und Akzeptanz

- Remote = lokal für alle neuen Aufrufe; Host-Bericht committet; CPU-Grenze des Workers beachtet und Abweichungen benannt.

## Abhängigkeiten und Grenze

[TASK-066](TASK-066-vp076-printer.md)

Umfang gemäß [MILE-011](../02-Milestones/MILE-011-relation-origin.md). P0, P1.1–P1.13, VP-07 0.7.0–0.7.5, VP-10, VP-11 und vorhandene lunados.lib-Einträge bleiben byte-gleich.

## Ergebnis (2026-11-02)

- Core `0.9.0-proof` durch den Nutzer bereitgestellt; Gateway `0.2.0-proof`. Discovery, zehn Tools und allgemeiner Remote-Smoke-Test (Auth, P0, P1, VP-06) bestanden.
- Drei vollständige R6-Live-Läufe: jeweils 25/26 wie erwartet; `G5_CORE_UNAVAILABLE` bei P-OL-07 (Views bzw. Check) oder V-HO-11. Für einen P-OL-07-Abbruch belegt der Core-Tail `CpuLimitExceeded` bei 522 ms. P-OL-07 traf bei gezielten Wiederholungen vollständig die fixierten Digests. Kein vollständiger 26/26-Lauf wird behauptet.
- Host-Abnahme über den G5-Connector: die neun fixierten Fälle nach Wiederholung von P-OL-02 wie erwartet, 16 Payload-Digests und SVG-Digests gleich. Die sporadische Core-Nichtverfügbarkeit bleibt als Abweichung benannt ([Host-Bericht](../../P3/remote-mcp-g5/evidence/G5_R6_HOST_REPORT.md), [CPU-Ereignis](../../P3/remote-mcp-g5/evidence/G5_R6_CORE_CPU_EVENT.json)).
