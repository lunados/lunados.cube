# TASK-061 — Bereitstellung und Host-Abnahme

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/archive/2026-11-02-deliver-remote-plan-views/tasks.md).

Story: [US-030](../04-US/US-030-remote-control-flow.md), [US-031](../04-US/US-031-remote-plan-views.md) · Mile: MILE-010-C · Aufwand: 0,25–0,5 PT

## Ziel und Arbeit

Bereitstellung durch den Nutzer nach `DEPLOYMENT.md` (kurze Anleitung); Host-Abnahme live über den G5-Connector mit den vorab festgelegten Erwartungen; Bericht R5.

## Ergebnis und Akzeptanz

- Alle Stichproben wie erwartet oder Abweichung benannt; Bericht committet.

## Abhängigkeiten und Grenze

[TASK-060](TASK-060-g5-core-gateway.md)

Umfang gemäß [MILE-010](../02-Milestones/MILE-010-remote-plan-views.md). Keine neue Prüfsemantik; P0, P1, P2, lokaler Adapter und lunados.lib-Einträge bleiben byte-gleich; geändert wird nur `P3/remote-mcp-g5`.

## Ergebnis (2026-11-02)

- Bereitstellung durch den Nutzer (Kern `0.8.0-proof`, Gateway `0.2.0-proof`). Vier Skript-Läufe live: 87/88, 87/88, 86/88, 87/88; jede Abweichung ein Abbruch `G5_CORE_UNAVAILABLE` durch `exceededCpu` des Kerns (größte Plansicht, K-07 Check, und der Folgeaufruf), nie ein anderes Ergebnis ([Läufe](../../P3/remote-mcp-g5/evidence/G5_R5_LIVE_SCRIPT_RUN4.json), [CPU-Ereignis](../../P3/remote-mcp-g5/evidence/G5_R5_CORE_CPU_EVENT.json)). D-6 revidiert: alle Sichten bleiben remote, die Grenze ist dokumentiert ([Spezifikation §10](../../P3/remote-mcp-g5/G5_R5_ACCEPTANCE_SPEC.md)).
- Host-Abnahme über den Connector: Teilmenge 7/7 wie erwartet (Discovery, drei `cube_validate`, drei Plan-Ketten), Payload-Digests nachgerechnet, Kontexte unverändert übertragen ([Host-Bericht R5](../../P3/remote-mcp-g5/evidence/G5_R5_HOST_REPORT.md)).
