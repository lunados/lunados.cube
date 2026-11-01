# Design — Vollständigkeit und Instanzbindung

Status: planned

## Context

P1.10.1 D-2 behandelt eine unvollständige Erklärung bereits als UNRESOLVED („incomplete, not contradictory“). MILE-002 zeigte, dass „geprüft leer“ ohne Vollständigkeitserklärung nicht ausdrückbar ist (DSM-03, ARC-03) und dass Instanzzugehörigkeit nur über Scope-Überladung gebunden ist (BPMN-03). MILE-003 zeigte, dass Zeilen-Vollständigkeit eine Überbehauptung wäre; MILE-004 (E-2, L-2) bestätigte die fehlende typisierte Instanz je Eingang.

## Goals / Non-Goals

Vollständigkeit erklärbar und prüfbar machen, Instanzen typisiert binden, vier Zellzustände darstellen. Keine Kontrollflusssemantik (G-07), keine Instanzdarstellung im Fluss (VR-12), keine Herkunftsbindung (G-02) — diese bleiben Folgearbeit.

## Decisions

Offen bis TASK-032: O-1 Profilschnitt/Nummer, O-2 Umfang der Erklärung, O-3 Status, O-4 Form der Instanzbindung, O-5 Auslieferung, O-6 Ort der Populationsprüfung. Siehe [MILE-005](../../../docs/02-Milestones/MILE-005-completeness-instances.md#offene-entscheidungen-vor-task-032-vom-nutzer-zu-treffen).

## Risks / Trade-offs

G-01 ist teils nur durch nicht ausgeführte Fälle belegt; TASK-030 macht sie zuerst ausführbar. Der Aufwand liegt mit Spezifikation und Adapter über der Quellenschätzung von 5,0 PT.
