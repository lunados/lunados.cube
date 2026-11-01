# DAG-01 — Azyklischer Graph mit beliebigen IDs und numerisch rückwärts gerichteter Kante

Status: ausgeführt 2026-11-01 · Normalfall · Matrix: [DAG-01](../CASE-MATRIX.md) · Läufe: [P1](../../../10-Evidence/MILE-002/task015-dag-p1-report.json), [LIB](../../../10-Evidence/MILE-002/task015-dag-lib-calls.json) · Bewertung: **teilweise; konkrete Lücke im LIB-Vertrag**

## Aufgabe und Fremdreferenz

**Nutzeraufgabe:** „Welche Arbeitspakete sind betroffen, wenn sich *b* ändert?“ Nummerierung von Zyklizität unterscheiden; die bekannte `i < j`-Grenze des vorhandenen Evaluators nicht als Grammatikgrenze ausgeben.

**Regeln:** R-DAG-1 (DAG = gerichteter Graph ohne gerichteten Zyklus; Nummerierung ist keine Grapheigenschaft, A), R-DAG-4 (lokal: `impact.propagate/v1` lehnt `1 → 0` ab).

**Modell:** [dag-workitems.json](../models/dag-workitems.json): Raute a → {b, c} → d, Abhängigkeit „X dependsOn Y“ heißt Y vor X.

## Ausdruck, Vertrag und Läufe

**Cube (P1):** Work Items → `Y:identified-object:work-item`; `rel("dependsOn", X, Y)`.

**LIB (direkter Evaluatoraufruf, eigene Nachweisart):** `lunados.lib` `impact.propagate/v1`, Evaluator-Hash `c98411f9…c668`, LIB `4d07650`, Python 3.13.16. Aufrufe und Erwartungen vor der Ausführung committet (`b45ac11`) unter [lib-calls/](../lib-calls/).

| Lauf | Art | Erwartung | Ergebnis |
|---|---|---|---|
| DAG-01-statement | P1: `rel("dependsOn", WorkItem[wi:d], WorkItem[wi:b])` | PASS | PASS |
| DAG-01-lib-topological-numbering | LIB, Nummerierung N1 (a, b, c, d) | assessed; betroffen b, d; d: 7 → 10 | wie erwartet |
| DAG-01-lib-backward-numbering | LIB, **derselbe azyklische Graph**, Nummerierung N2 (d, a, b, c) | refused „cycle / reverse DAG edge rejected“ | wie erwartet |

## Zuordnung der Evaluatorgrenze (Quellenanalyse des Codes)

- `dependents()` aus EXP-013 lehnt jede Kante mit `i >= j` ab; `eval_full()` rechnet in **einem** Durchlauf in Indexreihenfolge. Die Grenze ist also eine echte algorithmische **Vorbedingung: Knotennummerierung muss topologisch sein** — keine Zyklusprüfung und keine Grammatikgrenze.
- [entry.json](../../../../../lunados.lib/entries/impact.propagate/v1/entry.json) deklariert diese Vorbedingung **nicht**, obwohl der [Library-Vertrag](../../../../../lunados.lib/LIBRARY_CONTRACT.md) Vorbedingungen als Vertragsteil nennt. Die Meldung „cycle“ ist für eine azyklische Rückwärtskante irreführend.
- **Kantenorientierung:** Eine LIB-Kante `[i, j, w, "dependsOn"]` bedeutet „j hängt von i ab“ (`value[j]` nutzt `inbound i`) — umgekehrt zur natürlichen Lesart von `rel("dependsOn", X, Y)`. Die Abbildung steht im Modell (`lib_mapping.edge_orientation`), aber nicht im LIB-Vertrag.

## Befunde

| Dimension | Befund |
|---|---|
| **Ausdruck** | Belegt: Abhängigkeiten mit beliebigen IDs sind ausdrückbar; die Aussage kennt keine Nummerierung. |
| **Vertragsbindung** | **Konkrete Lücke (LIB):** Vorbedingung „topologische Nummerierung“ und Kantenorientierung fehlen im Eintrag. |
| **Prüfung** | Teilweise: Der Evaluator lehnt sicher ab (kein falsches Ergebnis), aber mit falschem Grund. P1 prüft keine Graphstruktur über mehrere Aussagen. |
| **Darstellungsbedarf** | Abhängigkeitsrichtung eindeutig („Y vor X“); bei Ablehnung den tatsächlichen Grund zeigen. → MILE-003 |
| **Nutzen** | Hoch: Impact-Fragen sind ein Hauptanwendungsfall. Messbar: Anteil azyklischer Eingaben, die ohne manuelle Umnummerierung bewertet werden. |

## Kleinster Eingriff und Unsicherheit

**LIB, kein Morphologiebedarf:** (1) Vorbedingung und Kantenorientierung in `entry.json` deklarieren; (2) entweder ein vorgeschalteter, reiner Normalisierungsschritt (topologische Umnummerierung mit Rückabbildung auf die Original-IDs) oder eine präzise Ablehnung („nicht topologisch nummeriert“ vs. „Zyklus“). Bestehende v1-Einträge werden laut LIB-Grundsatz nicht still verändert — also neue Revision.

Unsicherheit: Die Werte stammen aus einem Evaluator desselben Autors; geprüft ist nur dieses Eingabepaar.
