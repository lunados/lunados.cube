# DAG-03 — Echter gerichteter Zyklus

Status: ausgeführt 2026-11-01 · Gegenfall · Matrix: [DAG-03](../CASE-MATRIX.md) · Läufe: [P1](../../../10-Evidence/MILE-002/task015-dag-p1-report.json), [LIB](../../../10-Evidence/MILE-002/task015-dag-lib-calls.json) · Bewertung: **konkrete Lücke (Prüfvertrag/Diagnose)**

## Aufgabe und Fremdreferenz

**Nutzeraufgabe:** „Ist dieser Abhängigkeitsplan überhaupt abarbeitbar — und wenn nicht, wo liegt der Zyklus?“ Zyklus gegenüber bloßer Umnummerierung unterscheiden; ausdrückbaren Graph und für DAG-Analyse unzulässige Eingabe getrennt bewerten.

**Regeln:** R-DAG-1, R-DAG-2 (bei Zyklus `NetworkXUnfeasible`, D), R-DAG-3, R-DAG-4. **Modell:** [dag-workitems.json](../models/dag-workitems.json), `cycle_variant`: zusätzlich *a dependsOn d* → Zyklus a → b → d → a.

## Läufe

| Lauf | Art | Erwartung (vorab, `b45ac11`) | Ergebnis |
|---|---|---|---|
| DAG-03-cycle-edge | P1: `rel("dependsOn", WorkItem[wi:a], WorkItem[wi:d])` | PASS | PASS |
| DAG-03-lib-true-cycle | LIB, N1 + Zykluskante | refused „cycle / reverse DAG edge rejected“ | wie erwartet |
| (Vergleich) DAG-01-lib-backward-numbering | LIB, azyklisch, N2 | refused, **gleiche Meldung** | wie erwartet |

## Befunde

| Dimension | Befund |
|---|---|
| **Ausdruck** | Belegt und richtig so: Der Cube-Graph darf Zyklen enthalten; jede Kante ist für sich eine gültige Aussage. Ungültig ist erst die DAG-Projektion. |
| **Vertragsbindung** | Teilweise: Dass eine Analyse einen azyklischen Teilgraphen verlangt, ist nirgends als Vorbedingung gebunden (siehe [DAG-01](DAG-01.md)). |
| **Prüfung** | **Konkrete Lücke:** Der Evaluator unterscheidet echten Zyklus und bloße Rückwärtsnummerierung nicht — gleiche Ablehnung, gleiche Meldung, kein Zyklusnachweis. P1 prüft keine Zyklenfreiheit über mehrere Aussagen (und soll es als Einzelaussagenprüfung auch nicht). |
| **Darstellungsbedarf** | Zyklus als hervorgehobene Kantenfolge mit Quellaussagen; Unterschied „Plan nicht abarbeitbar“ vs. „Eingabe falsch nummeriert“. → MILE-003 |
| **Nutzen** | Hoch: Zyklen in Abhängigkeitsplänen sind ein häufiger, teurer Fehler. Messbar: Jede Ablehnung nennt mindestens einen konkreten Zyklus mit seinen Aussagen. |

## Analysefunktions-Kandidat (nicht implementiert)

| Kandidat | Eingabe | Ausgabe | Nicht-Implikation |
|---|---|---|---|
| `analyze.cycle-gate/v1` | gefilterte Abhängigkeitsaussagen (Teilgraph) | `acyclic` ja/nein; bei nein ein Zeugenzyklus mit Original-IDs und Quellaussagen; bei ja eine topologische Nummerierung | Zyklenfreiheit sagt nichts über fachliche Richtigkeit der Kanten; Erreichbarkeit ≠ Kausalität |

Mit diesem Gate vor `impact.propagate` würden DAG-01 (umnummerieren und bewerten) und DAG-03 (ablehnen mit Zeugenzyklus) korrekt getrennt.

## Kleinster Eingriff und Unsicherheit

**LIB:** `analyze.cycle-gate/v1` als vorgeschalteter, reiner Schritt; neue Revision von `impact.propagate` mit präziser Ablehnung. Keine Morphologieänderung — eine Evaluatorablehnung ist keine morphologische Unmöglichkeit.

Unsicherheit: Kein unabhängiger Algorithmus (z. B. NetworkX) wurde ausgeführt; der Zyklus ist von Hand belegt.
