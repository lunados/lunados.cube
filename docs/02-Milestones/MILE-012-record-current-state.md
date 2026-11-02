# MILE-012 — Aktuellen Entwicklungsstand festhalten

Status: planned · Stand: 2026-11-02 · Voraussetzung: MILE-010 ([Abschluss](../10-Evidence/MILE-010/C-RESULT.md)), MILE-011 ([Abschluss](../10-Evidence/MILE-011/C-RESULT.md))

## Ergebnis

Der Stand nach MILE-011 ist nachvollziehbar festgehalten, ohne Code an Gateway, Kern oder Printern zu ändern:

1. **G5-Ledger bereinigt:** `G5_ACCEPTANCE.md` nennt R5 und R6 mit ihren tatsächlichen Ergebnissen; das bisherige Gate „R6 Production operations“ heißt künftig R7 und steht als offen, nicht geplant.
2. **Bekannte Grenzen auf einer Seite:** was remote zuverlässig geht und was nicht (CPU-Grenze bei den größten Plansichten, sporadischer Abbruch ohne Ursache, fester Bearer-Token), der Ausweg für schwere Aufgaben (lokal über G4/G6) und die Optionen für später.
3. **Gesamtüberblick aktuell:** `RELEASE_INDEX.md` beschreibt den heutigen Stand aller Schichten statt des VP-06-Stands vom 2026-10-24.
4. **Live-Ausgangswert:** ein Lauf der vorhandenen Skripte R5 und R6 gegen den bereitgestellten Kern `0.9.0-proof`, als Messpunkt für den aktuellen Stand; optional eine Rotation des Bearer-Tokens.
5. **Integration:** MILE-010, MILE-011 und MILE-012 in `main`, der Stand mit einem Tag markiert.

## Rahmenbedingungen

- Keine Änderung an P0, P1, P2, dem lokalen Adapter, Gateway- oder Kern-Code und an keinem Payload. Geändert werden nur Dokumente; `RELEASE_INDEX.md` wird bewusst aktualisiert (bisher als unverändert geprüft).
- Die CPU-Grenze und der Bearer-Token werden in Kauf genommen und dokumentiert, nicht behoben.
- Bereitstellung, Secrets, Merges und Tag macht der Nutzer.

## Entscheidungen (2026-11-02, Nutzer)

| ID | Frage | Entscheidung |
|---|---|---|
| **D-1** | Umfang | Kurze Mile zum Festhalten des Stands (fünf Punkte oben), etwa 1 PT; keine Codeänderung |
| **D-2** | CPU-Budget | In Kauf genommen; bei Bedarf später Workers Paid oder ein anderer Weg für schwere Aufgaben |
| **D-3** | Anmeldung | Bearer-Token bleibt; OAuth erst nach dem Test des aktuellen Stands |
| **D-4** | Produktion | CPU-Budget, OAuth, Rate-Limits, Betrieb und Freigabe als ungeplanter Kandidat in der Roadmap |

Offen und in den Tasks zu entscheiden: Rotation des Bearer-Tokens (TASK-071), Name des Tags (TASK-072).

## Tasks und Aufwand

[EPIC-012](../03-Epics/EPIC-012-record-current-state.md) · [US-034](../04-US/US-034-current-state-recorded.md) · TASK-069–072.

| Task | Aufwand |
|---|---|
| [TASK-069 — G5-Ledger und bekannte Grenzen](../05-Tasks/TASK-069-g5-ledger-limits.md) | 0,25 PT |
| [TASK-070 — Gesamtüberblick RELEASE_INDEX](../05-Tasks/TASK-070-release-index.md) | 0,25 PT |
| [TASK-071 — Live-Ausgangswert R5 und R6](../05-Tasks/TASK-071-live-baseline.md) | 0,25 PT |
| [TASK-072 — Abschluss, Integration und Tag](../05-Tasks/TASK-072-mile012-close.md) | 0,25 PT |

**Aufwand: etwa 1 PT**, ohne die Zeit des Nutzers für Live-Lauf, Merges und Tag.

## Nicht Teil von MILE-012

- Produktionsfreigabe von G5 (CPU-Budget, OAuth, Rate-Limits, Betrieb).
- Quellenabgleich mit Fremdmodellen (getrennt, durch den Nutzer); Host-Vergleich (nicht nötig).

## Nachverfolgung

[OpenSpec-Change](../../openspec/changes/record-current-state/proposal.md) · [Aufgabenstatus](../../openspec/changes/record-current-state/tasks.md).
