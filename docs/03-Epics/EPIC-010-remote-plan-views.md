# EPIC-010 — Kontrollfluss und Plansichten remote

Status: done · Milestone: [MILE-010](../02-Milestones/MILE-010-remote-plan-views.md) · Voraussetzung: [EPIC-006](EPIC-006-remote-and-readability.md), [EPIC-008](EPIC-008-control-flow.md), [EPIC-009](EPIC-009-instance-view.md)

## Ergebnis

Der G5-Remote-Connector prüft `binding-context/9` und druckt die Plansichten VP-07 bis VP-11 mit denselben Ergebnissen wie lokal.

## Umfang

- G5-Kern `0.8.0-proof` mit P1.13 und den Plan-Printern;
- drei Plan-Tools im Gateway, Discovery;
- Bereitstellung und Host-Abnahme.

Keine neue Prüfsemantik und keine neue Darstellung; P0, P1, P2, lokaler Adapter und lunados.lib byte-gleich.

## Akzeptanz

- Remote = lokal für alle vorhandenen Vektoren (offline) und für die vorab festgelegten Stichproben (live).
- Grenzen und Fehlercodes wie lokal; nichts wird gekürzt.

## Stories

- [US-030 — Kontrollfluss remote prüfen](../04-US/US-030-remote-control-flow.md)
- [US-031 — Plansichten remote drucken](../04-US/US-031-remote-plan-views.md)
