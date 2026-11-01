# DAG-02 — Mehrere zulässige topologische Reihenfolgen

Status: ausgeführt 2026-11-01 · Normalfall · Matrix: [DAG-02](../CASE-MATRIX.md) · Lauf: [LIB](../../../10-Evidence/MILE-002/task015-dag-lib-calls.json) · Bewertung: **teilweise**

## Aufgabe und Fremdreferenz

**Nutzeraufgabe:** „In welcher Reihenfolge können die Arbeitspakete erledigt werden?“ Partielle Ordnung, ausgewählte Abhängigkeitstypen und mehrere Lösungen festhalten; keine Ressourcenparallelität aus der Ordnung folgern.

**Regeln:** R-DAG-2 (`topological_generations` schichtet einen DAG, NetworkX 3.7, D), R-DAG-3 (`all_topological_sorts` liefert alle Ordnungen, Bestand 2.3), R-DAG-4. **NetworkX wurde nicht ausgeführt** (nicht installiert); die Ordnungen sind von Hand bestimmt.

**Modell:** [dag-workitems.json](../models/dag-workitems.json). Von Hand: zwei topologische Ordnungen (a, b, c, d) und (a, c, b, d); Generationen {a}, {b, c}, {d}.

## Läufe

| Lauf | Art | Erwartung (vorab, `b45ac11`) | Ergebnis |
|---|---|---|---|
| DAG-01-lib-topological-numbering | LIB, N1 (a, b, c, d) | betroffen {b, d}; Werte je ID a=1, b 3→6, c=4, d 7→10 | wie erwartet |
| DAG-02-lib-other-topological-numbering | LIB, N3 (a, c, b, d) | dieselben Werte je ID | wie erwartet: Indizes [2, 3] = {b, d}, Werte je ID identisch |

## Befunde

| Dimension | Befund |
|---|---|
| **Ausdruck** | Belegt: Die Abhängigkeiten legen eine partielle Ordnung fest; Cube braucht keine Reihenfolge, um sie auszudrücken. |
| **Vertragsbindung** | Teilweise: Welche Prädikate eine Reihenfolge begründen („dependsOn“ ja, „references“ nein), ist nur im Fixture-Vertrag notiert. Der LIB-Evaluator kennt eine eigene, kleine Prädikatliste (`dependsOn`, `references`). |
| **Prüfung** | Belegt für das Ergebnis: Zwei verschiedene topologische Nummerierungen liefern dasselbe Ergebnis je ID. Die ID-Reihenfolge ist also *eine* zulässige Ordnung, keine allgemeingültige. **Nicht vorhanden:** eine Funktion, die alle Ordnungen oder die Generationen liefert. |
| **Darstellungsbedarf** | Generationen als Spalten (b und c nebeneinander) mit dem Hinweis „strukturell unabhängig, nicht zwingend parallel ausführbar“. → MILE-003 |
| **Nutzen** | Hoch für Planung (Migrations-/Refactoring-Reihenfolgen). Messbar: alle zulässigen Ordnungen bzw. Generationen werden angezeigt, nicht nur eine. |

## Analysefunktions-Kandidaten (nicht implementiert)

| Kandidat | Eingabe | Ausgabe | Nicht-Implikation |
|---|---|---|---|
| `analyze.topological-generations/v1` | gefilterte Abhängigkeitsaussagen | Generationen mit Original-IDs | Strukturelle Unabhängigkeit ≠ Ressourcenparallelität |
| `analyze.topological-orders/v1` (begrenzt) | wie oben, Obergrenze für Anzahl | Liste zulässiger Ordnungen oder deren Anzahl | Keine Empfehlung einer Ordnung |

## Kleinster Eingriff und Unsicherheit

**LIB** (oben) mit Prädikatfilter als Pflichtparameter; Referenz-Implementierung z. B. NetworkX ≥ 3.x, Version bei Ausführung festhalten. Keine Morphologieänderung.

Unsicherheit: Die zweite Ordnung ist von Hand bestimmt; ein unabhängiger Algorithmus wurde nicht ausgeführt.
