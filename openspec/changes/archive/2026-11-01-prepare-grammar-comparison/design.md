# Design — Analysevorbereitung

Status: implemented · Abschluss am 2026-11-01

## Context

Die [interne Bestandsanalyse](../../../../docs/09-Research/cube-grammar-2026-11-01/ANALYSE.md) enthält echte lokale MCP-Proben und beschreibt eine Abweichung zwischen Discovery-Detailtiefe und unterstützten Binding-Kontexten. Die importierten Ergebnisse sind historische Eingaben, keine neuen Läufe.

## Goals / Non-Goals

Ein kleiner lokaler Ablauf soll vorhandene Fälle wiederholen und begrenzte Varianten vergleichen. Universelle Interoperabilität, eine neue Validierungsengine und Änderungen an kanonischen Kategorien sind nicht vorgesehen.

## Decisions

Umgesetzter Ansatz im Umfang von MILE-001; keine zusätzliche ADR erforderlich:

1. Bestehende Fixtures wiederverwenden; minimale Metadaten für Fall-ID, Referenzversion, Eingabe, Profile und vorab definierte Erwartung ergänzen.
2. Werkzeuge direkt und explizit anbinden. MCP-Transport und direkte lokale Validatoraufrufe im Bericht unterscheiden. Keine neue allgemeine Pluginplattform.
3. Rohantwort erhalten. Ausdruck, Vertragsbindung, Prüfung, Darstellung und Nutzen separat berichten; fehlende Beobachtung bleibt offen.
4. Ausgangsstand und Varianten versionieren. Hashes/Revisionen und Aufrufparameter erlauben den Vergleich.
5. Discovery gegen tatsächlich implementierte Operationen und Kontextversionen prüfen. Nur belegte Angaben ergänzen; fachliche Fähigkeiten nicht aus Versionsnummern ableiten.

## Risks / Trade-offs

Ein selbst geschriebenes Prüfskript könnte nur eigene Erwartungen bestätigen. Deshalb vorhandene negative und unresolved Fixtures verwenden, Erwartungen vor dem Lauf fixieren und fachliche Abdeckung getrennt prüfen. Toolausfälle sind Infrastrukturprobleme und keine semantische Widerlegung. Ein Report ist keine Ausführungs- oder Wahrheitsentscheidung.

## Konkrete Umsetzungskorridore

Der aktuelle Code trennt `surface.discover_surface()` (historische G4-Card, auch Grundlage für G5) und `surface.discover_surface_local()` (lokale Erweiterung). Ergänzungen gehören in den lokalen Pfad. `server.py` beschreibt `cube_validate` noch über context/1 und context/2; der Dispatch in `p1_adapter.py` berücksichtigt weitere Formate. TASK-001 pinnt diese Quellen und die geschützten Ausgaben vor einer Änderung. Eine Versionsliste allein ist kein Nachweis aller Kombinationen.

Die Vergleichsprüfung nutzt vorhandene SDK-Smokes/Fixtures. Ein kleiner Runner unter `scripts/research/` und getrennte Fallartefakte unter `docs/09-Research/analysis-readiness/` wurden im beschriebenen Umfang implementiert. Der lokale stdio-Pfad muss mindestens einmal über eine frische Verbindung nachgewiesen werden; direkte lokale Funktionsaufrufe allein reichen für diesen Nachweis nicht.

Laufmetadaten und Rohantwort werden erhalten. Ein Vergleich betrachtet Fachstatus/Diagnose und Erwartungsübereinstimmung getrennt; Zeitstempel oder Run-IDs sind keine fachliche Abweichung. Ein erwartetes FAIL darf als erfolgreiche Probe gelten, ohne den Fachstatus umzuschreiben.

## Open Questions

- Welche Discovery-Felder können ohne Vertragsbruch präzisiert werden?
- Welcher vorhandene Runner bietet den kleinsten Anknüpfungspunkt?
- Welches minimale Fallformat trägt sowohl Matrix- als auch Prozessgegenfälle?

Diese Fragen werden in der ersten Aufgabe am Code geklärt; neue Schnittstellen werden hier noch nicht als festgelegt behauptet.


## Resolution and delivered limits

Die drei offenen Designfragen sind im gelieferten Umfang beantwortet: Ein separates versioniertes Metadatenfeld ergänzt `discover_surface_local`, der vorhandene SDK-stdio-Client trägt den kleinen Runner, und drei exakt extrahierte Fälle definieren das minimale Format. Die G4- und Legacy-Ausgaben bleiben unverändert. Der Runner implementiert keine allgemeine Fallherkunft und keine fachliche Fremdmodellabbildung; neue Fälle benötigen eine explizite Herkunftserweiterung. Wiederholungen vergleichen Diagnose/Fachstatus unabhängig von Run-Metadaten.

[Nachweise und verbleibende Grenzen](../../../../docs/10-Evidence/MILE-001/C-RESULT.md).
