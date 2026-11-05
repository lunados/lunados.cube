# MILE-014 — X-Endpunkte im Migrations-Printer

Status: umgesetzt (lokal, G4/G6) · Stand: 2026-11-05 · Voraussetzung: MILE-013

## Ergebnis

Mit dem Profil `P2-VP-MIGRATION/0.7.8` zeichnet der Migrations-Printer auch die zehn X-Endpunkte (Perception … Result) als Vertragsanker und die Ressourcenobjekte Source, Cache und Revision. Damit sind in den fünf ausgearbeiteten Fällen von lunados.explorer alle nicht internen Abhängigkeiten druckbar.

## Anlass

Nach MILE-013 blieben in lunados.explorer nur Abhängigkeiten ungedruckt, deren Objekt ein X-Endpunkt (meist Admission) oder eine Quelle ist. VP-07.7 hatte die X-Endpunkte als offene Darstellungsfrage ausgeklammert; ein Prototyp auf Fall F05 zeigte, dass `cube.flow` und `cube.phases` einen `form.contract-anchor` als Karte mit Vertragsglyphe zeichnen und `check-panels` besteht.

## Rahmenbedingungen

- Neues Profil, `0.7.0…0.7.7` byte-identisch (0.7.7 vor dem Code gepinnt).
- Keine Änderung an P0, P1, VP-04-Budgets und Diagnosecodes; X-Scopes bleiben ungemappt (kein VG-Anker).
- Der Druck sagt nichts über die P1.6-Bindung eines X-Endpunkts (Instanzprofil, Scope, Slots).
- G5 nicht in dieser Mile.

## Entscheidungen (2026-11-05, Nutzer)

| ID | Frage | Entscheidung |
|---|---|---|
| **D-1** | Vorgehen | Wie MILE-013: eine Task, als Mile aufgehängt |
| **D-2** | Umfang | Alle zehn X-Endpunkte sowie Source, Cache, Revision |

## Tasks und Aufwand

| Task | Aufwand |
|---|---|
| [TASK-075 — Profil VP-07.8](../05-Tasks/TASK-075-vp078-x-endpoints.md) | 0,25–0,5 PT |

## Nicht Teil von MILE-014

- X-Scopes als Knoten; Farbakzente der Vertragsanker.
- P1.6-Bindung der X-Referenten in den Explorer-Fällen (Instanzprofile mit Slots).
- G5-Auslieferung.
