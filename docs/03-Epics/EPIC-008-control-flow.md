# EPIC-008 — Kontrollfluss und Spurkonformität

Status: planned · Milestone: [MILE-008](../02-Milestones/MILE-008-control-flow.md) · Voraussetzung: [EPIC-005](EPIC-005-completeness-and-instances.md)

## Ergebnis

Exklusive und parallele Gateways lassen sich mit Flüssen, Bedingungsreihenfolge und Default deklarieren. Eine beobachtete Spur wird je Instanz gegen dieses Modell geprüft: ein Pfad je Aktivierung, Default nur ohne wahre Bedingung, Join mit allen Eingängen der eigenen Instanz.

## Umfang

- Profil P1.13 (`binding-context/9`) mit Kontrollfluss-Deklaration;
- LIB `analyze.trace-conformance/v1`;
- lokaler Adapter und Wiederholung der BPMN-Fälle.

Keine Prozess-Engine, keine Bedingungsauswertung, keine Änderung an P0, P1.1–P1.12, P2 oder vorhandenen LIB-Einträgen.

## Akzeptanz

- BPMN-01 und BPMN-02 sind ausführbar und liefern das vorab erwartete Ergebnis.
- Fehlende Spur-Abdeckung oder fehlende Bedingungsergebnisse führen zu UNRESOLVED, nie zu FAIL.
- P0, P1.1–P1.12 und P2 byte-gleich.

## Stories

- [US-026 — Kontrollfluss deklarieren](../04-US/US-026-control-flow-profile.md)
- [US-027 — Spur gegen das Modell prüfen](../04-US/US-027-trace-conformance.md)
