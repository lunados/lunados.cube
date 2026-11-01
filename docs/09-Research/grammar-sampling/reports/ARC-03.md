# ARC-03 — Fehlender Partner in einem nur teilweise bekannten Modell

Status: ausgeführt 2026-11-01 (zwei Läufe ausführbar, einer begründet nicht ausführbar) · Gegenfall · Matrix: [ARC-03](../CASE-MATRIX.md) · Lauf: [task012-archimate-report.json](../../../10-Evidence/MILE-002/task012-archimate-report.json) · Bewertung: **teilweise belegt; konkrete Lücke für Abwesenheit**

## Aufgabe und Fremdreferenz

**Nutzeraufgabe:** „In der Service-Sicht realisiert nichts *Transaction Processing* — fehlt die Realisierung wirklich?“ „Nicht gefunden“ von „nachgewiesen nicht vorhanden“ unterscheiden; keine Verletzung aus einer unvollständigen Sicht erfinden.

**Regeln:** R-AM-1, R-AM-2. Das [Modell](../models/archimate-billing.json) hat zwei Sichten: `am:view/full` (vollständig, enthält `am:r1`) und `am:view/service` (nur der Service, ausdrücklich partiell). Die Unterscheidung selbst ist eine Cube-Scope-Frage (A).

## Cube-Ausdruck und Vertrag

Abbildung wie [ARC-01](ARC-01.md). Zwei Kontexte mit gleichem Scope und gleichen Verträgen: Vollsicht mit fünf Referenten, Teilsicht nur mit dem Service.

| Lauf | Kontext · Art | Erwartung (vorab, `3229dd3`) | Ergebnis |
|---|---|---|---|
| ARC-03-partner-undeclared | Teilsicht · `rel("realizes", Tool[accounting], Capability[transaction-processing])` | UNRESOLVED / P1_BINDING_CONTEXT_REQUIRED | wie erwartet: `/subject` „No exact declared referent binding available“; Prädikattypisierung PASS |
| ARC-03-ctrl-full-view | Vollsicht · gleicher Ausdruck | PASS | PASS |
| ARC-03-absence-claim | `not_executable` | kein Fachstatus | `NOT_EXECUTED`, kein Aufruf |

Begründung der Nichtausführbarkeit: „Von keinem Element realisiert“ bräuchte eine Negation oder eine Vollständigkeitserklärung der Sicht für einen Relationstyp. Die ACG-Grammatik hat keine Negation; binding-context/1 hat kein Feld für deklarierte Vollständigkeit, nur freie `profile_limitations`.

## Befunde

| Dimension | Befund |
|---|---|
| **Ausdruck** | Belegt für positive Aussagen. **Konkrete Lücke:** Abwesenheit („kein Partner“) ist nicht ausdrückbar. |
| **Vertragsbindung** | Teilweise: Die Teilsicht kann ihre Unvollständigkeit nur als Freitext erklären. |
| **Prüfung** | **Belegt:** Ein unbekannter Partner ergibt UNRESOLVED, nicht FAIL — P1 erfindet keine Verletzung. Dasselbe Ergebnis wechselt mit der Sicht (UNRESOLVED → PASS), nicht mit dem Ausdruck. Ungeprüft: echte Unterbelegung in einer vollständigen Sicht. |
| **Darstellungsbedarf** | Drei Zustände sichtbar halten: vorhanden, unbekannt (Sicht unvollständig), nachgewiesen fehlend (erst mit Vollständigkeitserklärung). Anschluss an DSM-03 (leer/unbekannt/ausgeblendet). → MILE-003 |
| **Nutzen** | Hoch: verhindert falsche Modellfehler-Meldungen aus Teilsichten — in EA-Repositories häufig. Messbar: keine FAIL-Meldung bei partieller Sicht ohne Vollständigkeitserklärung. |

## Kleinster Eingriff und Unsicherheit

**Profil:** eine deklarierte Vollständigkeit je Sicht und Relationstyp (z. B. `complete_for: [realizes]` mit Witness), auf der eine Populationsprüfung (siehe [ARC-02](ARC-02.md)) „nachgewiesen fehlend“ ableiten darf. Keine Negation in der Grammatik nötig: Abwesenheit folgt dann aus Vollständigkeit plus Zählung. Kein Morphologiebedarf belegt.

Unsicherheit: Das UNRESOLVED stammt aus der Referentenbindung, nicht aus einer eigenen Partnerprüfung; ein Fall mit deklariertem, aber unverbundenem Partner wurde nicht untersucht.
