# MILE-020 — Fähigkeits-Deskriptor je Modul

Status: **geplant (Entwurf)** · Stand: 2026-11-06 · Vorbedingung für [MILE-022](MILE-022-workflow-builder.md) und [MILE-023](MILE-023-playbook-library.md) · Betrifft: lunados.cube, lunados.lib, lunados.toolbox, lunados.connector, agent-relay-poc-v3

## Ziel und Entscheidung

Der Cube soll der Einstiegspunkt in die AIAEAO-Workspaces sein. Wer über den Cube einsteigt, soll sehen, welche Module es gibt und was jedes davon leisten kann. Dieses Wissen liegt **beim jeweiligen Modul**: Jedes Modul beschreibt seine Fähigkeiten selbst, versioniert und per Hash gepinnt. Der Cube verweist darauf; ein späterer Workflow Builder liest es nur. So entsteht keine zweite, veraltende Wahrheit an zentraler Stelle.

Ein Deskriptor ist dokumentarisch. Er gewährt keine Authority, keine Admission und keinen Aufruf und belegt nicht, dass eine Fähigkeit in einem Host läuft.

## Ausgangslage (2026-11-06)

- `cube_discover_surface` beschreibt nur P0–P3; `cross_domain.overall_status` ist `NOT_DEFINED`. lunados.lib erscheint nur im Text einzelner Drucker-Optionen; Lib-Index, Connector-Tabellen, Explorer-Format und Toolbox fehlen.
- Der Cube referenziert 3 von 13 Lib-Funktionen über `library_ref` (`analyze.population`, `project.aggregate-relations`, `analyze.trace-conformance`).
- Zwischen Cube und Toolbox gibt es in keiner Richtung Verweise; zwischen Cube und Core/Server keine Bindung (lunados.connector `docs/09-Research/MILE-002-RESPONSIBILITY-RECOMMENDATION.md`).
- Vorbild für eine saubere Bindung: Die Übersetzungstabellen in lunados.connector pinnen `cube.lunados.net/v9.4/...` mit SHA-256.
- Die Tabelle der sieben logischen Module in `agent-relay-poc-v3/docs/10-contracts/MILE-071-MODULE-CONTRACT-BASELINE.md` (Input, Output, Ausschlüsse) ist die fachliche Ausgangsfassung. Der Module-Contract-v2-Capability-Deskriptor im Relay-Repo hat feste Fähigkeitstypen; eine generische MCP-Tool-Deklaration ist kein gültiger v2-Deskriptor.

## Arbeitsumfang

1. **Format:** Arbeitstitel `aiaeao.module-capabilities/1`. Je Modul: Kennung, Version, Quellen mit Hash, Fähigkeiten mit Input/Output und Status (`implemented`, `candidate`, `unknown`), Ausschlüsse. Abgleich mit dem Module-Contract-v2-Deskriptor (D-1).
2. **Cube:** Abschnitt `neighbors` in `cube_discover_surface` mit Verweisen auf die Deskriptoren der Nachbarn (Version, Hash). Rein beschreibend: kein Laden, kein Aufruf, keine automatische Bindung. G4 und G5 liefern denselben Inhalt.
3. **Lib:** Deskriptor aus `INDEX.json`. Für jede der 13 Funktionen das Verhältnis zum Cube festhalten: `cube-profile` (über `library_ref`), `standalone` oder `deferred` (D-2).
4. **Toolbox:** erster Deskriptor nur für den Bestand `aiaeao-toolbox-dns==0.1.0`; keine neue Fähigkeit.
5. **Connector und Relay-Repo:** Deskriptoren für lunados.connector (Translator-Entwurf) und für Core/Server, App und `aiaeao-connector` aus vorhandenen Quellen (`adapters/registry.py`, Module Contract v2), nur dokumentarisch.
6. **ADR Host-Pfad:** Der Cube liest Lib-Snapshots heute direkt aus dem Nachbar-Checkout; MILE-071 sieht vor, dass er sie über den Host erhält. Entschieden ist „beides, Hash führend“ (D-3); die ADR hält das fest und nennt die Folgen für MILE-071.
7. **Namen:** `aiaeao-connector` (Transport, Relay-Repo) und lunados.connector (Translator) in Deskriptoren und auf lunados.space eindeutig benennen (D-4).

## Entscheidungen

| ID | Frage | Optionen |
|---|---|---|
| D-1 | Verhältnis zum Module-Contract-v2-Deskriptor | übernehmen · erweitern · getrennt halten und verweisen |
| D-2 | Status jeder ungenutzten Lib-Funktion | `cube-profile` · `standalone` · `deferred` |
| D-3 | Host-Pfad für Lib-Snapshots | **Entschieden (Nutzer, 2026-11-06): beides, Hash führend.** Direkt aus dem gepinnten Lib-Stand für Build und Tests, über den Host zur Laufzeit; maßgeblich ist in beiden Fällen der gepinnte `INDEX.json`-Hash. |
| D-4 | Bezeichnung der beiden Connector | Vorschlag offen |

## Abnahme

- [ ] Format `aiaeao.module-capabilities/1` mit Schema und Prüfskript; D-1 entschieden.
- [ ] Je ein Deskriptor für Cube, Lib, Toolbox, Connector und die Module im Relay-Repo, jeweils mit Version und Hash.
- [ ] `cube_discover_surface` enthält `neighbors`, lokal und G5 byte-gleich; bestehende Felder unverändert.
- [ ] Alle 13 Lib-Funktionen haben einen Status zum Cube.
- [ ] ADR zum Host-Pfad liegt vor und gibt D-3 wieder.
- [ ] Die beiden Connector sind eindeutig benannt.

## Nicht in MILE-020

Ausführung, Admission oder Authority; Verlagerung von Code zwischen Repos; neue Toolbox-Fähigkeiten; der Workflow Builder selbst.

## Aufwand

Schätzung 2–3 PT, unsicher vor allem bei D-1 und der Abstimmung mit dem Relay-Repo.
