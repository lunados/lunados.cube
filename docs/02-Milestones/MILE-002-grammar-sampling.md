# MILE-002 — Fünf Grammatiken gezielt abtasten

Status: done · Stand: 2026-11-01 · Voraussetzung: MILE-001 abgeschlossen

## Ergebnis

15 konkrete Vergleichsfälle zeigen, was Cube von Structurizr/C4, ArchiMate, DSM/MDM, BPMN und DAG lernen kann. Je Fall werden Ausdruck, Vertragsbindung und heutige Prüfbarkeit getrennt beurteilt; Darstellungsbedarf und Nutzen werden erfasst. Das Ergebnis ist ein quellengebundenes Lückenregister und eine begrenzte Antwort auf die sieben Leitfragen.

**Abgeschlossen** mit [Quellenregister](../09-Research/grammar-sampling/SOURCE-REGISTER.md), 15 [Fallberichten](../09-Research/grammar-sampling/README.md), [Lückenbilanz](../09-Research/grammar-sampling/GAP-LEDGER.md) und [Abschlussnachweis](../10-Evidence/MILE-002/C-RESULT.md). Vollständige Interoperabilität, eine Erweiterung der Morphologie sowie Implementierung neuer LIB-Methoden oder einer Prozessengine gehören nicht zu diesem Milestone.

## Drei Miles / Chargen

| Mile | Ergebnis | Abschlusskriterium | Aufgaben |
|---|---|---|---|
| **MILE-002-A — Quellen und Fallbasis** | Fünf abgegrenzte Referenzstände; neue Fälle mit expliziter Herkunft verwendbar | Quellen-/Regelregister und kleine versionierte Herkunftserweiterung; alte v1-Proben weiter gültig | TASK-009–010 |
| **MILE-002-B — 15 Vergleiche** | Je Ansatz zwei Normalfälle und ein Gegenfall | Konkrete Modelle, Erwartungen, Cube-Ausdruck/Bindung, Beobachtungen oder belegte Prüfgrenzen für alle 15 Fälle | TASK-011–015 |
| **MILE-002-C — Lückenbilanz und Übergabe** | Rückführung auf sieben Leitfragen; kleinste sinnvolle Eingriffe | Verknüpftes Lückenregister, vorläufige Nutzen-/Aufwandseinschätzung und Übergabe an MILE-003/004 | TASK-016–017 |

A geht B voraus; die fünf Untersuchungen in B sind anschließend fachlich unabhängig. C verwendet alle fünf Ergebnisse. Die Statusliste steht ausschließlich im [OpenSpec-Change](../../openspec/changes/archive/2026-11-01-sample-five-grammars/tasks.md).

## Umfang und Prüflogik

- [15-Fälle-Matrix](../09-Research/grammar-sampling/CASE-MATRIX.md) mit stabilen lokalen Fall-IDs.
- Quellen-/Normversion und konkrete Regelstelle vor der Durchführung festlegen. Eigene Modellannahmen und normative Regeln getrennt markieren.
- Erst unveränderten Cube-Stand prüfen; ein zusätzliches Versuchsprofil erhält einen eigenen Stand. Ein Artefakt mit Freitext ist kein ausreichender Abdeckungsbeleg.
- Fachstatus aus Werkzeugen bleibt unverändert. Forschungsbewertung trennt belegt, teilweise, konkrete Lücke und ungeprüft. Nicht ausführbare Fälle erhalten keinen erfundenen MCP-Nachweis.
- Fehlende Prüfmöglichkeit ist ein zulässiger Erkenntnisbefund, wenn der konkrete Fall und seine notwendige Unterscheidung ausgearbeitet sind. Fehlende Quelle oder fehlender Fallbericht verhindert das betreffende Abschlusskriterium.
- Die visuelle Grammatik wird hier auf benötigte Unterscheidungen befragt. Rendering und Lesbarkeit werden in MILE-003 geprüft; endgültige Maßnahmenpriorisierung folgt in MILE-004.

## Epics, Stories und Aufwand

[EPIC-004 — Quellengebundene Vergleichsfälle](../03-Epics/EPIC-004-source-bound-comparison-cases.md) trägt A. Der bestehende [EPIC-001 — Grammatikvergleich als Lerninstrument](../03-Epics/EPIC-001-grammar-learning.md) trägt B/C und bleibt bis MILE-004 offen. Zugehörig: US-005–011 und TASK-009–017.

**16–24 Engineering-/Review-Stunden, grob 2–3 PT à 8 h.** A: 3–5 h; B: 10–15 h; C: 3–4 h. Erwarteter Nutzen sehr hoch; Komplexität mittel–hoch, insbesondere bei ArchiMate-Regelbindung und BPMN-Zuständen. Die Schätzung setzt zugängliche Referenzen, kleine synthetische Modelle und vorhandene lokale Werkzeuge voraus. Fehlender Normzugang oder ein wachsender Infrastrukturbedarf führt zu einer sichtbaren Umfangs-/Schätzkorrektur, nicht automatisch zu einem Integrationsprojekt.

## Sieben Leitfragen

1. Reicht der Envelope-Rahmen für die erforderlichen Pflichtunterscheidungen?
2. Welche wiederkehrenden Analysemethoden eignen sich für LIB?
3. Welche Referenz- und Kardinalitätsregeln gehören in Profile?
4. Welche Bindungen benötigen LENS, MODE und Achsen für hilfreiche Sichten?
5. Welche konkreten visuellen Unterscheidungen sind noch ungesichert?
6. Wo fehlen Ausdrucksmöglichkeiten trotz vorhandener Konzepte/Anker — und wo fehlt lediglich ein Vertrag oder Prüfer?
7. Welche Aufgaben der fünf Ansätze stiften den höchsten erwarteten Nutzen für Cube?

Die 129 visuellen Anker und 80 Konzeptindexeinträge aus der Bestandsaufnahme bleiben unterschiedliche Zählbasen. Dieser Milestone ist eine Stichprobe und kein Vollständigkeitsbeweis.

## Nachverfolgung

[Anforderungen und Abdeckung](../../openspec/changes/archive/2026-11-01-sample-five-grammars/TRACEABILITY.md) · [Voraussetzung: Nachweise MILE-001](../10-Evidence/MILE-001/C-RESULT.md). Alle Abschlusskriterien der drei Chargen sind mit Nachweisen erfüllt ([C-RESULT](../10-Evidence/MILE-002/C-RESULT.md)). Übergaben: Darstellungsanforderungen an MILE-003, vorläufige Maßnahmenliste an MILE-004 ([Lückenbilanz §6–7](../09-Research/grammar-sampling/GAP-LEDGER.md)).
