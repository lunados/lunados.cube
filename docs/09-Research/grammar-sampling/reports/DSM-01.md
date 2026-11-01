# DSM-01 — Gerichtete Abhängigkeiten in einer Domäne

Status: ausgeführt 2026-11-01 · Normalfall · Matrix: [DSM-01](../CASE-MATRIX.md) · Lauf: [task013-dsm-report.json](../../../10-Evidence/MILE-002/task013-dsm-report.json) · Bewertung: **teilweise**

## Aufgabe und Fremdreferenz

**Nutzeraufgabe:** „Wovon hängt *resolver* ab, und wo gibt es Rückkopplungen?“ Zeilen-/Spaltenrichtung, Zellbedeutung und Identitäten binden; eine transponierte Lesart darf nicht still dasselbe bedeuten.

**Regeln:** R-DSM-1, R-DSM-2 (S-DSM-1, Stand 2026-03-03). Präzisiert am selben Tag aus S-DSM-1: Unter **IR/FAD** bedeutet eine Markierung in Zelle (Zeile i, Spalte j), dass i einen Input von j erhält; unter **IC/FBD** liefert i an j. Beide Konventionen tragen dieselbe Information **nur bei bekannter Konvention**; verwechselt kehrt sich jede Kante um.

**Modell:** [dsm-modules.json](../models/dsm-modules.json), synthetisch, Konvention IR/FAD deklariert, vier Module, eine Rückkopplungsmarke über der Diagonale.

## Cube-Ausdruck und Vertrag

**Versuchsabbildung (A):** Module → `Y:resource-object:artifact`; Zelle → `rel("dependsOn", Zeile, Spalte)` (IR/FAD). Eine Aussage pro markierter Zelle.

| Lauf | Ausdruck (gekürzt) | Erwartung (vorab, `fa50ee9`) | Ergebnis |
|---|---|---|---|
| DSM-01-cell-irfad | `rel("dependsOn", Artifact[resolver], Artifact[parser])` | PASS | PASS |
| DSM-01-ctrl-transposed-reading | `rel("dependsOn", Artifact[parser], Artifact[resolver])` | PASS | PASS — Lesefehler nicht erkennbar |
| DSM-01-ctrl-diagonal | `rel("dependsOn", Artifact[parser], Artifact[parser])` | PASS | PASS — keine Irreflexivität |

## Befunde

| Dimension | Befund |
|---|---|
| **Ausdruck** | **Belegt und eine Stärke:** Eine Cube-Relation trägt die Richtung explizit (Subjekt → Objekt). Nach dem Import gibt es keine Konventionsmehrdeutigkeit mehr. |
| **Vertragsbindung** | Teilweise: Die Konvention selbst ist nirgends gebunden. Sie entscheidet nur beim Import aus und beim Export in eine Matrix. |
| **Prüfung** | **Konkrete Lücke:** Eine transponiert gelesene Zelle und eine Diagonale als Selbstabhängigkeit bestehen P1. Der Vertrag hat kein Feld für Irreflexivität; die Lesekonvention ist keiner Aussage anhaftend. |
| **Darstellungsbedarf** | Matrix mit deklarierter Konvention in der Legende; Rückkopplungen (bei IR/FAD über der Diagonale) hervorheben; Zelle auf ihre Quellaussage zurückführbar. → MILE-003 |
| **Nutzen** | Hoch für Refactoring: kompakte Kopplungsübersicht und Rückkopplungsfindung. Messbar: Anteil der Zellen, die eindeutig auf genau eine Aussage zurückgehen. |

## Analysefunktions-Kandidaten (nicht implementiert)

| Kandidat | Eingabe | Ausgabe | Nicht-Implikation |
|---|---|---|---|
| `project.dsm/v1` | deklarierte Aussagen, Prädikatfilter, Domäne (Konzeptmenge), Konvention IR/FAD oder IC/FBD, Reihenfolge | Matrix mit Zellzustand und Quellaussage je Zelle | Darstellung, keine neue Aussage |
| `analyze.scc/v1` | gerichteter Teilgraph aus gefilterten Aussagen | Komponentenmengen mit den beteiligten Quellkanten | Strukturelle Rückkopplung ≠ fachliche Kausalität |
| `analyze.partition/v1` | wie oben | Reihenfolge der Komponenten, Rückkopplungsmarken | Keine Ausführungsreihenfolge |

Im Modell bilden parser, resolver und validator eine solche Komponente (resolver → parser, validator → resolver, parser → validator). Nachweis der Analyse: erst mit Implementierung.

## Kleinster Eingriff und Unsicherheit

**LIB** für Projektion und Analyse (oben), mit der Konvention als Pflichtparameter. **Profil:** optionales Merkmal „irreflexiv“ im Prädikatvertrag. Keine Morphologieänderung.

Unsicherheit: Die Präzisierung der Zellrichtung stammt aus S-DSM-1, ist aber noch nicht als eigene Regel im Register (Register bleibt unverändert, um die Fall-Pins nicht erneut zu brechen — siehe Lückenbilanz).
