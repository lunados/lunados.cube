# MILE-010 — Kontrollfluss und Plansichten remote

Status: in_progress · Stand: 2026-11-02 · Voraussetzung: MILE-008 ([Abschluss](../10-Evidence/MILE-008/C-RESULT.md)), MILE-009 ([Abschluss](../10-Evidence/MILE-009/C-RESULT.md))

## Ergebnis

Auslieferung ohne neue Prüfsemantik. Was lokal (G4/G6) geht, geht danach auch über den G5-Remote-Connector:

1. **`/9` remote:** `cube_validate` im G5-Kern nimmt `binding-context/9` an (P1.13); die Remote-Discovery nennt `/9`.
2. **Plansichten remote:** die drei Plan-Tools `cube_plan_source`, `cube_plan_views` und `cube_plan_check` im G5-Gateway, mit den Printern VP-07 bis VP-11 und denselben Argumenten, Grenzen und Ergebnissen wie lokal.
3. **Host-Abnahme:** Bereitstellung durch den Nutzer, Live-Abnahme mit vorab festgelegten Erwartungen.

Heute: G5 (`P3-MCP-REMOTE/0.7.0-proof`, MILE-006) prüft bis `/8`; `/9` endet remote geschlossen. Die Plansichten laufen nur lokal; G5 bündelt die Plan-Printer nicht (`remote_available: false`).

## Rahmenbedingungen

- P0, P1 (einschließlich P1.13), P2 (einschließlich VP-11), der lokale Adapter und die lunados.lib-Einträge bleiben byte-gleich. Geändert werden nur G5-Kern, Gateway, Zusammenbau, Prüfskripte und Nachweise unter `P3/remote-mcp-g5`.
- Ablauf wie MILE-006: Spezifikation mit Entscheidungen → Entscheidungen auflösen (eigener Docs-Commit) → Erwartungen vor Code → Kern und Gateway → Offline-Prüfung → Bereitstellung → Host-Abnahme → Abschluss.
- G5 bleibt ein Proof (`G5_PROOF_NOT_PRODUCTION_AUTHORIZED`); keine Änderung an Authentifizierung, Herkunftsregeln oder `cube.lunados.net`.
- Keine Kundendaten in Repo, Prüfunterlagen oder auf cube.lunados.net.

## Entscheidungen (2026-11-02, Nutzer)

D-1 bis D-8 hat der Nutzer wie vorgeschlagen freigegeben („Ja“).

| ID | Frage | Entscheidung | Grund | Nicht gewählt |
|---|---|---|---|---|
| **D-1** | Rahmen | **Schlanke Mile wie MILE-006:** drei Chargen, Epic, zwei Stories, fünf Tasks, OpenSpec-Change | reine Auslieferung | zwei getrennte Miles |
| **D-2** | Umfang `/9` | `cube_validate` mit **`/9` (P1.13)** und Discovery, wie lokal; neue Kernversion `P3-MCP-REMOTE/0.8.0-proof` | gleicher Weg wie `/8` in MILE-006 | nur Discovery |
| **D-3** | Umfang Plansichten | **alle drei Plan-Tools mit allen fünf Plan-Printern** (VP-07 `cube.phases`/`cube.flow`, VP-08 `cube.sequence`, VP-09 `cube.axes`, VP-10 `cube.cells`, VP-11 `cube.instances`), Argumente wie lokal | ein Remote-Weg für alle Sichten; die Printer sind klein (zusammen rund 1,4 MB) | nur VP-10 und VP-11 |
| **D-4** | Ergebnisgleichheit | **Remote = lokal, byte-gleich:** dieselben Eingaben ergeben dieselben SVGs, Berichte und Fehlercodes wie G6; offline am Kern über alle vorhandenen Vektoren geprüft (K-01–K-18, O-, S-, I-Vektoren), live stichprobenweise | keine zweite Darstellungslogik | eigene Remote-Ausgabe |
| **D-5** | Grenzen | **wie lokal:** 2 MiB Anfrage, 512 KiB je SVG, 2 MiB Antwort; über einer Grenze ein Fehler, nie gekürzt. Reicht der Platz im Gateway-Rahmen nicht, wird die Grenze der Plan-Tools so gesetzt, dass derselbe Fehlercode wie lokal kommt | gleiche Zusagen wie G6 (D-5, D-6) | Remote-eigene Grenzen |
| **D-6** | Laufzeitrisiko | **zuerst offline messen** (Paketgröße, Rechenzeit je Aufruf der größten Vektoren); überschreitet ein Teil die Grenzen der Cloudflare-Python-Laufzeit, wird der Umfang **auf VP-10 und VP-11 begrenzt** und der Rest als offen benannt | Rechenzeit in Pyodide ist die größte Unbekannte | ohne Messung bereitstellen |
| **D-7** | Bereitstellung und Abnahme | wie MILE-006 D-3: **Agent** baut Kern und Gateway, prüft offline und legt die Erwartungen vorab fest; **Nutzer** stellt nach `DEPLOYMENT.md` bereit; **Agent** nimmt live über den G5-Connector ab und schreibt den Bericht | bewährte Rollen | Abnahme durch den Nutzer allein |
| **D-8** | Abnahmeumfang | live: die sieben BPMN-Fälle als `/9` (MILE-008) und KF-01–KF-09; je Sicht mindestens ein Vektor mit SVG-Digest gleich lokal, dazu `cube_plan_check` und ein Grenzfall; **keine neue Sichtprüfung** (Ausgabe byte-gleich zur geprüften lokalen) | deckt beide Teile mit vorab festgelegten Erwartungen ab | Sichtprüfung remote |

## Drei Chargen

| Mile | Ergebnis | Abschlusskriterium | Aufgaben |
|---|---|---|---|
| **MILE-010-A — Spezifikation und Erwartungen** | Abnahmespezifikation G5 R5 mit Detailfragen; Erwartungen für Offline- und Live-Abnahme | Entscheidungen aufgelöst; Erwartungen vor Code committet | TASK-058, TASK-059 |
| **MILE-010-B — Kern und Gateway** | G5-Kern `0.8.0-proof` mit P1.13 und den Plan-Printern; drei neue Tools im Gateway; Discovery | Offline-Prüfung grün, Remote = lokal für alle Vektoren, Laufzeitmessung nach D-6, G5-Prüfsummen und Asset-Prüfung | TASK-060 |
| **MILE-010-C — Bereitstellung und Abnahme** | Bereitstellung durch den Nutzer; Host-Abnahme; Abschluss | Live-Abnahme wie erwartet; Bericht R5; Abschlussprüfung `all_ok` | TASK-061, TASK-062 |

## Epics, Stories und Aufwand

[EPIC-010](../03-Epics/EPIC-010-remote-plan-views.md). US-030–031, TASK-058–062.

**Aufwand: 2,25–3,5 PT**, ohne die Zeit des Nutzers für die Bereitstellung. Unsicher ist vor allem die Rechenzeit der Plan-Printer in der Python-Laufzeit von Cloudflare (D-6).

| Charge | Aufwand |
|---|---|
| A | 0,5–0,75 PT |
| B | 1,25–2 PT |
| C | 0,5–0,75 PT |

## Nicht Teil von MILE-010

- Produktionsfreigabe von G5 (OAuth, Mandantentrennung, Rate-Limits, Kostenkontrolle); `cube.lunados.net` bleibt unverändert.
- Neue Prüfsemantik oder neue Darstellungen; lunados.lib remote.
- VR-01 (Herkunftslinie): eigener Milestone.

## Nachverfolgung

[OpenSpec-Change](../../openspec/changes/deliver-remote-plan-views/proposal.md) · [Aufgabenstatus](../../openspec/changes/deliver-remote-plan-views/tasks.md) · [Abdeckung](../../openspec/changes/deliver-remote-plan-views/TRACEABILITY.md).
