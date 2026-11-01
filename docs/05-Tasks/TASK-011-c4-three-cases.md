# TASK-011 — Drei C4-/Structurizr-Fälle untersuchen

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/sample-five-grammars/tasks.md).

Story: [US-006](../04-US/US-006-c4-learning.md) · Mile: MILE-002-B · Aufwand: 2–3 h

## Ziel und Arbeit

C4-01 bis C4-03 konkretisieren: Hierarchie, nachvollziehbare Verdichtung und Verwechslung direkter/abgeleiteter Beziehung. Vorhandene Cube-Ausdrücke und mögliche deklarative Profile getrennt prüfen.

## Ergebnis und Akzeptanz

- Drei Fallberichte mit konkreten Eingaben, benannter Ableitungsstrategie und unterscheidbaren Ergebnissen liegen vor.
- Quellbeziehungen bleiben bei Verdichtung referenzierbar; Artifact-Ablage allein zählt nicht als semantische Abdeckung.
- Ein fehlender Aggregator wird als LIB-/Projektionsbedarf eingeordnet, sofern kein Ausdrucksverlust nachgewiesen ist.

## Eingaben / betroffene Ablagen

[Fallmatrix](../09-Research/grammar-sampling/CASE-MATRIX.md), [Quellenplan](../09-Research/grammar-sampling/SOURCE-PLAN.md), [bestehender Fallvertrag](../09-Research/analysis-readiness/README.md). Neue Fallberichte unter `docs/09-Research/grammar-sampling/`; neue Rohprotokolle unter `docs/10-Evidence/MILE-002/`. TASK-010 betrifft zusätzlich den vorhandenen kleinen Runner und dessen Tests.

## Gezielte Verifikation

Erwartung aus Quellen vor dem Cube-Aufruf festhalten. Bestehende deklarative Prüfbarkeit nutzen; manuelle Ableitungsbeurteilung ausdrücklich davon trennen.

## Abhängigkeiten und Grenze

[TASK-009](TASK-009-source-baselines.md), [TASK-010](TASK-010-authored-case-provenance.md)

Umfang gemäß [MILE-002](../02-Milestones/MILE-002-grammar-sampling.md). Keine neuen kanonischen Kategorien, Envelopes, produktiven Adapter oder Analysebibliotheken implementieren. Begrenzte Versuchsprofile bleiben Kandidaten. Noch kein Ausführungsnachweis vorhanden.
