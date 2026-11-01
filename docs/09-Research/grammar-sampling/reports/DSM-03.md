# DSM-03 — Leere, unbekannte und ausgeblendete Zelle fallen zusammen

Status: ausgeführt 2026-11-01 (ein Lauf ausführbar, zwei begründet nicht ausführbar) · Gegenfall · Matrix: [DSM-03](../CASE-MATRIX.md) · Lauf: [task013-dsm-report.json](../../../10-Evidence/MILE-002/task013-dsm-report.json) · Bewertung: **konkrete Lücke (Ausdruck/Bindung)**

## Aufgabe und Fremdreferenz

**Nutzeraufgabe:** „Hat *printer* keine Abhängigkeit zu *parser* — oder wissen wir es nur nicht?“ Die drei Zustände semantisch unterscheiden und den Darstellungsbedarf für MILE-003 festhalten.

**Regel:** R-DSM-2 — die Basis-DSM ist binär (markiert/nicht markiert), numerische DSMs ergänzen Stärke oder Anzahl. **Die Quelle kennt keinen eigenen Zustand für „unbekannt“ oder „ausgeblendet“.** Die Dreiteilung ist eine Arbeitsannahme (A).

**Modell:** [dsm-modules.json](../models/dsm-modules.json) deklariert je Zelle einen Zustand: markiert (printer, validator), leer-bekannt (printer, parser), unbekannt (validator, printer), ausgeblendet (resolver, printer); nicht aufgeführte Zellen sind unbekannt.

## Cube-Ausdruck und Vertrag

| Zellzustand | Cube heute | Lauf | Erwartung (vorab, `fa50ee9`) | Ergebnis |
|---|---|---|---|---|
| markiert | positive Aussage | DSM-03-marked | PASS | PASS |
| leer-bekannt | nicht ausdrückbar (keine Negation, keine Vollständigkeit je Zeile und Relationstyp) | DSM-03-empty-known · `not_executable` | kein Fachstatus | `NOT_EXECUTED` |
| unbekannt | keine Aussage (offene Welt, Normalzustand) | — (Quellenanalyse) | — | — |
| ausgeblendet | keine Sicht-/Sichtbarkeitsbindung in P1; Sache der P2-Projektion | DSM-03-hidden · `not_executable` | kein Fachstatus | `NOT_EXECUTED` |

**Vorhandene P2-Fähigkeit (Quellenanalyse):** Die Achsenansicht VP-09.2 blendet mit `--hide-empty rows|cols|both` Werte ohne Eintrag aus und hält `hidden_rows`/`hidden_cols` mit Anzahl im Bericht fest ([Spezifikation](../../../../P2/visual-printer-axes-v1/VP09_2_ACCEPTANCE_SPEC.md) §4). „Ausgeblendet“ bleibt dort also nachvollziehbar. „Leer nach Projektion“ fasst aber „nachweislich leer“ und „unbekannt“ zusammen.

## Befunde

| Dimension | Befund |
|---|---|
| **Ausdruck** | **Konkrete Lücke:** Auf Aussageebene fallen leer-bekannt und unbekannt zusammen (beide = keine Aussage). Nur „markiert“ existiert als Aussage. |
| **Vertragsbindung** | **Konkrete Lücke:** keine Vollständigkeitserklärung (z. B. „Zeile printer ist für dependsOn vollständig analysiert“). Dieselbe Lücke wie [ARC-03](ARC-03.md). |
| **Prüfung** | Ungeprüft und heute nicht prüfbar: die Unterscheidung leer/unbekannt. Ausgeblendet ist auf P2-Ebene nachvollziehbar, aber in MILE-003 zu prüfen. |
| **Darstellungsbedarf** | Vier unterscheidbare Zellzustände: markiert, leer (geprüft), unbekannt, ausgeblendet (mit Zähler). Unbekannt darf nicht wie leer aussehen. → MILE-003 (Schwerpunkt) |
| **Nutzen** | Hoch: Eine DSM, in der „nicht analysiert“ wie „keine Abhängigkeit“ aussieht, führt zu falschen Modularisierungsentscheidungen. Messbar: Anteil der leeren Zellen mit belegter Vollständigkeit. |

## Kleinster Eingriff und Unsicherheit

**Profil:** dieselbe Vollständigkeitserklärung wie für ARC-02/ARC-03 (Referent oder Zeile, Relationstyp, Scope, Witness). Damit wird „leer-bekannt“ ableitbar, ohne Negation in die Grammatik einzuführen. **Visuelle Regel:** vier Zellzustände in der Matrixdarstellung, inklusive der Unterscheidung in VP-09.2 zwischen „leer nach Projektion“ und „unbekannt“. Keine Morphologieänderung.

Unsicherheit: Ob die vier Zustände für Nutzer tatsächlich unterscheidbar und hilfreich sind, ist eine Lesbarkeitsfrage für MILE-003.
