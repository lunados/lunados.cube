# TASK-013 — Drei DSM-/MDM-Fälle untersuchen

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/sample-five-grammars/tasks.md).

Story: [US-008](../04-US/US-008-dsm-mdm-learning.md) · Mile: MILE-002-B · Aufwand: 2–3 h

## Ziel und Arbeit

DSM-01 bis DSM-03 konkretisieren: gerichtete Ein-Domänen-Matrix, Mehrdomänenzuordnung und Unterscheidung leer/unbekannt/ausgeblendet. Die benötigten Zustände und Relationstypen semantisch erfassen.

## Ergebnis und Akzeptanz

- Richtung, Domänen und Zellbedeutung sind eindeutig und auf Referenten/Relationen zurückführbar.
- Unbekannte und ausgeblendete Inhalte werden nicht automatisch als abwesend gewertet.
- Benötigte Analysefunktionen (etwa Erreichbarkeit, SCC oder Clustering) werden als Kandidaten mit Vertrag beschrieben, nicht im Rahmen dieser Task implementiert.

## Eingaben / betroffene Ablagen

[Fallmatrix](../09-Research/grammar-sampling/CASE-MATRIX.md), [Quellenplan](../09-Research/grammar-sampling/SOURCE-PLAN.md), [bestehender Fallvertrag](../09-Research/analysis-readiness/README.md). Neue Fallberichte unter `docs/09-Research/grammar-sampling/`; neue Rohprotokolle unter `docs/10-Evidence/MILE-002/`. TASK-010 betrifft zusätzlich den vorhandenen kleinen Runner und dessen Tests.

## Gezielte Verifikation

Kleine Matrix und ihre Beziehungsliste gegeneinander prüfen; vorhandene P1-Prüfungen nur für tatsächlich gebundene Regeln nutzen. Renderer-/Lesbarkeitstests an MILE-003 übergeben.

## Abhängigkeiten und Grenze

[TASK-009](TASK-009-source-baselines.md), [TASK-010](TASK-010-authored-case-provenance.md)

Umfang gemäß [MILE-002](../02-Milestones/MILE-002-grammar-sampling.md). Keine neuen kanonischen Kategorien, Envelopes, produktiven Adapter oder Analysebibliotheken implementieren. Begrenzte Versuchsprofile bleiben Kandidaten. Noch kein Ausführungsnachweis vorhanden.

## Ergebnis

Abgeschlossen am 2026-11-01. Drei Fallberichte: [DSM-01](../09-Research/grammar-sampling/reports/DSM-01.md) (teilweise: Richtung nach Import eindeutig, Konvention und Irreflexivität ungebunden), [DSM-02](../09-Research/grammar-sampling/reports/DSM-02.md) (teilweise: Domäne implizit über Konzepte, Abflachung nur durch Profildisziplin verhindert), [DSM-03](../09-Research/grammar-sampling/reports/DSM-03.md) (konkrete Lücke: leer-bekannt und unbekannt fallen zusammen). Neun v2-Fälle, davon zwei `not_executable`; Erwartungen vor dem Lauf committet (`fa50ee9`); alle ausführbaren Fälle in 2/2 frischen Verbindungen erwartungsgemäß, Regression über 26 Fälle stabil; [Bericht](../10-Evidence/MILE-002/task013-dsm-report.json). Analysefunktionen (`project.dsm`, `project.mdm`, `analyze.scc`, `analyze.partition`, `analyze.cross-domain-coupling`) als Kandidaten mit Ein-/Ausgabe und Nicht-Implikation beschrieben, nicht implementiert. Keine Morphologieänderung begründet.

