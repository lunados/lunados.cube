# MILE-013 — Modulkörper im Migrations-Printer

Status: umgesetzt (lokal, G4/G6) · Stand: 2026-11-05 · Voraussetzung: MILE-011 ([Abschluss](../10-Evidence/MILE-011/C-RESULT.md)), MILE-012

## Ergebnis

Der Migrations-Printer zeichnet mit dem neuen Profil `P2-VP-MIGRATION/0.7.7` auch Pläne, deren Referenten die Modulkörper Core, Connector, Toolbox oder Adapter, eine Grant-Grenze oder die Ressourcenobjekte Evidence und Content sind. Alle sieben Konzepte haben in P0 v9.4 bereits einen VG-Anker und eine vorgeschlagene Form; es fehlte nur die Zeile in der geschlossenen Tabelle des Adapters.

## Anlass

Pilot F02 in lunados.explorer (2026-11-05): Ein Funktionsablauf einer echten Migration (Relay-Metriken) wurde als `binding-context/10` exportiert und von P1.14 mit PASS geprüft, VP-07.6 konnte davon aber nur 5 von 42 Abhängigkeiten drucken. Mit 0.7.7 sind es alle 42 ([Nachweis](../10-Evidence/MILE-013/README.md)).

## Rahmenbedingungen

- Neues Profil statt Änderung: `0.7.0…0.7.6` bleiben byte-identisch; die 0.7.6-Ausgaben werden vor dem Code festgehalten.
- Keine Änderung an P0, P1, an den VP-04-Budgets und an den Diagnosecodes.
- X-Endpunkte (Admission, Result) sind nicht Teil dieser Mile; ihre Darstellung als Knoten ist eine eigene Frage.
- G5 wird nicht ausgeliefert (Bereitstellung durch den Nutzer, getrennt).

## Entscheidungen (2026-11-05, Nutzer)

| ID | Frage | Entscheidung |
|---|---|---|
| **D-1** | Vorgehen | Eine Task ohne Epic, Story oder OpenSpec-Change; als Mile aufgehängt, damit es nachvollziehbar bleibt |
| **D-2** | Umfang | Core, Connector, Toolbox, Adapter, Grant, Evidence, Content; X-Endpunkte ausgeklammert |
| **D-3** | G5 | Nicht in dieser Mile |

## Tasks und Aufwand

| Task | Aufwand |
|---|---|
| [TASK-073 — Profil VP-07.7](../05-Tasks/TASK-073-vp077-module-bodies.md) | 0,5 PT |

## Nicht Teil von MILE-013

- X-Endpunkte als Knoten in `cube.flow` oder `cube.phases`.
- Größere Panel-Budgets oder ein Teilen eines Subjekts über mehrere Flow-Panels.
- G5-Auslieferung und Host-Abnahme.
