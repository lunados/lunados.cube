# MILE-013 — Modulkörper im Migrations-Printer

Status: lokal umgesetzt und in `main`; G5 (R8) vorbereitet, Bereitstellung ausstehend · Stand: 2026-11-05 · Voraussetzung: MILE-011 ([Abschluss](../10-Evidence/MILE-011/C-RESULT.md)), MILE-012

## Ergebnis

Der Migrations-Printer zeichnet mit dem neuen Profil `P2-VP-MIGRATION/0.7.7` auch Pläne, deren Referenten die Modulkörper Core, Connector, Toolbox oder Adapter, eine Grant-Grenze oder die Ressourcenobjekte Evidence und Content sind. Alle sieben Konzepte haben in P0 v9.4 bereits einen VG-Anker und eine vorgeschlagene Form; es fehlte nur die Zeile in der geschlossenen Tabelle des Adapters.

## Anlass

Pilot F02 in lunados.explorer (2026-11-05): Ein Funktionsablauf einer echten Migration (Relay-Metriken) wurde als `binding-context/10` exportiert und von P1.14 mit PASS geprüft, VP-07.6 konnte davon aber nur 5 von 42 Abhängigkeiten drucken. Mit 0.7.7 sind es alle 42 ([Nachweis](../10-Evidence/MILE-013/README.md)).

## Rahmenbedingungen

- Neues Profil statt Änderung: `0.7.0…0.7.6` bleiben byte-identisch; die 0.7.6-Ausgaben werden vor dem Code festgehalten.
- Keine Änderung an P0, P1, an den VP-04-Budgets und an den Diagnosecodes.
- X-Endpunkte (Admission, Result) sind nicht Teil dieser Mile; ihre Darstellung als Knoten ist eine eigene Frage.
- G5 nach D-4: Core `0.9.1-proof` mit VP-07.7 und CPU-Grenze von Workers Paid; Bereitstellung durch den Nutzer.

## Entscheidungen (2026-11-05, Nutzer)

| ID | Frage | Entscheidung |
|---|---|---|
| **D-1** | Vorgehen | Eine Task ohne Epic, Story oder OpenSpec-Change; als Mile aufgehängt, damit es nachvollziehbar bleibt |
| **D-2** | Umfang | Core, Connector, Toolbox, Adapter, Grant, Evidence, Content; X-Endpunkte ausgeklammert |
| **D-3** | G5 | Nicht in dieser Mile (abgelöst durch D-4) |
| **D-4** | G5 nach Upgrade auf Workers Paid (2026-11-05) | Doch in MILE-013: Core neu bauen, `limits.cpu_ms` setzen, R8-Live-Lauf inklusive der bisher abgebrochenen schweren Aufrufe |

## Tasks und Aufwand

| Task | Aufwand |
|---|---|
| [TASK-073 — Profil VP-07.7](../05-Tasks/TASK-073-vp077-module-bodies.md) | 0,5 PT |
| [TASK-074 — G5 R8: Core 0.9.1-proof und CPU-Budget](../05-Tasks/TASK-074-g5-r8.md) | 0,25–0,5 PT |

## Nicht Teil von MILE-013

- X-Endpunkte als Knoten in `cube.flow` oder `cube.phases`.
- Größere Panel-Budgets oder ein Teilen eines Subjekts über mehrere Flow-Panels.
- Gateway-Änderungen, OAuth, Rate-Limits und übriger Produktionsbetrieb (R7).
