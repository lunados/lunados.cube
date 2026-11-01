# Design — Vollständigkeit und Instanzbindung

Status: decided · Umsetzung offen

## Context

P1.10.1 D-2 behandelt eine unvollständige Erklärung bereits als UNRESOLVED („incomplete, not contradictory“). MILE-002 zeigte, dass „geprüft leer“ ohne Vollständigkeitserklärung nicht ausdrückbar ist (DSM-03, ARC-03) und dass Instanzzugehörigkeit nur über Scope-Überladung gebunden ist (BPMN-03). MILE-003 zeigte, dass Zeilen-Vollständigkeit eine Überbehauptung wäre; MILE-004 (E-2, L-2) bestätigte die fehlende typisierte Instanz je Eingang.

## Goals / Non-Goals

Vollständigkeit erklärbar und prüfbar machen, Instanzen typisiert binden, vier Zellzustände darstellen. Keine Kontrollflusssemantik (G-07), keine Instanzdarstellung im Fluss (VR-12), keine Herkunftsbindung (G-02) — diese bleiben Folgearbeit.

## Decisions

Entschieden am 2026-11-01 (Nutzer, TASK-032 vorgezogen); Gründe und nicht gewählte Optionen im [Milestone](../../../docs/02-Milestones/MILE-005-completeness-instances.md).

1. **D-1:** ein gemeinsames Profil (Arbeitstitel P1.12, `binding-context/8`) mit getrennten Abschnitten Vollständigkeit und Instanzbindung.
2. **D-2:** Erklärungsumfang Referent × Relationstyp × Richtung, zusätzlich je Paar; keine Erklärung je Sicht.
3. **D-3:** unvollständige Erklärung → UNRESOLVED mit eigenem Diagnosecode (Arbeitstitel `P1_COVERAGE_UNDECLARED`).
4. **D-4:** typisierte, optionale `instance_ref`; Prädikatvertragseigenschaft „gleiche Instanz verlangt“.
5. **D-5:** Auslieferung lokal (G4/G6); G5 als eigener Folgeschritt.
6. **D-6:** Profil erklärt, P1-Validator prüft Wohlgeformtheit und Status, LIB-Eintrag zählt mit typisiertem Ergebnisschema.
7. **Q-1–Q-6** der [Abnahmespezifikation](../../../P1/coverage-instance-profile-v1/P1_12_ACCEPTANCE_SPEC.md) am 2026-11-01 nach Vorschlag entschieden.

## Risks / Trade-offs

G-01 ist teils nur durch nicht ausgeführte Fälle belegt; TASK-030 macht sie zuerst ausführbar. Der Aufwand liegt mit Spezifikation und Adapter über der Quellenschätzung von 5,0 PT.
