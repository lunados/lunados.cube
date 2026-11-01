# ARC-01 — Eine typisierte ArchiMate-Beziehung

Status: ausgeführt 2026-11-01 · Normalfall · Matrix: [ARC-01](../CASE-MATRIX.md) · Lauf: [task012-archimate-report.json](../../../10-Evidence/MILE-002/task012-archimate-report.json) · Bewertung: **teilweise**

## Aufgabe und Fremdreferenz

**Nutzeraufgabe:** „Welche Application Function realisiert den Service *Transaction Processing*?“ Endpunkttypen und Relation mit Regelstelle festhalten, Cube-Typbindung dagegen prüfen, ähnlich benannte Konzepte nicht ungeprüft gleichsetzen.

**Regeln:** R-AM-1 (elf Beziehungstypen, K), R-AM-2 (Realization-Definition, N221 S. 2, K), R-AM-3 (Beispiel *Application Function realizes Application Service*, Bizzdesign S. 5, H). **R-AM-6 (normative Endpunkt-Zulässigkeit) ausgelassen** — Entscheidung vom 2026-11-01.

**Modell:** [archimate-billing.json](../models/archimate-billing.json), synthetisch, kombiniert zwei Herstellerbeispiele; Beziehung `am:r1`.

## Cube-Ausdruck und Vertrag

Ausgangsstand P1-VC/1.0.0. **Versuchsabbildung (A):** Application Function → `Z:module-body:tool` („invocable operational capability“), Application Service → `Z:boundary:capability` („technically available ability, not Authority“). Prädikat `realizes` nur Tool → Capability.

| Lauf | Ausdruck (gekürzt) | Erwartung (vorab, `3229dd3`) | Ergebnis |
|---|---|---|---|
| ARC-01-realization | `rel("realizes", Tool[accounting], Capability[transaction-processing])` | PASS | PASS |
| ARC-01-ctrl-reversed | `rel("realizes", Capability[…], Tool[…])` | FAIL / P1_PREDICATE_SIGNATURE | wie erwartet |

Das FAIL gilt nur für den Versuchsvertrag; ob ArchiMate 3.2 die Gegenrichtung zulässt, ist ohne Spezifikation nicht bestimmbar.

## Namensgleiche Begriffe (Quellenanalyse, nicht ausgeführt)

| ArchiMate (N221) | Cube v9.4 (concepts.json) | Urteil |
|---|---|---|
| Outcome — Endergebnis, Wirkung oder Folge eines Zustands (Motivation) | `Y:identified-object:outcome` — Endzustand und Evidenzzusammenfassung *einer* begrenzten Ausführung | **verschieden** |
| Capability — Fähigkeit eines aktiven Strukturelements (Strategie) | `Z:boundary:capability` — technisch verfügbare Fähigkeit, keine Autorität | teilweise; Ebene verschieden (Geschäftsfähigkeit vs. technische Verfügbarkeit) |
| Constraint — Einschränkung der Architektur, Umsetzung oder Realisierung | `X:logic-relation:constraint` — Einschränkung zulässiger Zustände; **nicht instanziierbar** | teilweise; in Cube kein Referent |
| Artifact — Daten aus Softwareentwicklung oder Betrieb | `Y:resource-object:artifact` — dauerhafte Ausgabe/Referenz, nicht automatisch Evidenz | nächste Überlappung |
| Resource — Vermögenswert einer Person/Organisation (Strategie) | `Y:resource-object:resource` — adressierbares Objekt unter Eigentum, Rechten, Nutzungsgrenzen | teilweise |

Für *Realization* gibt es kein gleichnamiges Cube-Konzept; die technische Referenzart `fulfills` trägt laut relations.json die Nicht-Implikation „fulfills → completed Contract“ und ist daher kein Ersatz.

## Befunde

| Dimension | Befund |
|---|---|
| **Ausdruck** | Belegt: Eine gerichtete, typisierte Realisierung ist ausdrückbar und prüfbar. |
| **Vertragsbindung** | Teilweise: Endpunkttypen sind nur über eine Arbeitsabbildung gebunden. Keiner der fünf namensgleichen Begriffe ist bedeutungsgleich; eine Abbildung nach Namen wäre in drei Fällen falsch. |
| **Prüfung** | Belegt für den Versuchsvertrag (Richtung, Typen). Ungeprüft: normative ArchiMate-Zulässigkeit. P1 kann eine falsche, aber deklarierte Begriffsabbildung grundsätzlich nicht erkennen. |
| **Darstellungsbedarf** | Fremdtyp (ArchiMate-Elementtyp) und Cube-Konzept nebeneinander anzeigen; bei Namensgleichheit ausdrücklicher Hinweis. → MILE-003 |
| **Nutzen** | Mittel: Architekturbeziehungen in Cube prüfbar, solange ein Abbildungsprofil gepflegt wird. Messbar: Anteil der Elementtypen mit begründeter statt namensbasierter Abbildung. |

## Kleinster Eingriff und Unsicherheit

**Profil:** ein versioniertes ArchiMate-Abbildungsprofil mit begründeter Typabbildung und einer ausdrücklichen „nicht gleichsetzen“-Liste; die Endpunkt-Zulässigkeit ließe sich später als Prädikatverträge aus der Norm ableiten. **Dokumentation:** die Namensfallen-Tabelle in die Cube-Doku für Fremdsprachen übernehmen.

Unsicherheit: Ohne Spezifikation bleibt offen, ob die Versuchssignatur strenger oder lockerer ist als ArchiMate. Die Abbildung Function→Tool ist nur teilweise passend.
