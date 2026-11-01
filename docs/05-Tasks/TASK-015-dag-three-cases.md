# TASK-015 — Drei DAG-Fälle untersuchen

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/sample-five-grammars/tasks.md).

Story: [US-010](../04-US/US-010-dag-learning.md) · Mile: MILE-002-B · Aufwand: 1–2 h

## Ziel und Arbeit

DAG-01 bis DAG-03 konkretisieren: beliebige IDs, mehrere Reihenfolgen und echter Zyklus. Die bekannte Begrenzung von impact.propagate/v1 dem tatsächlichen Algorithmusvertrag zuordnen.

## Ergebnis und Akzeptanz

- Azyklische Rückwärtskante und echter Zyklus werden anhand desselben kleinen Modells/der minimalen Variation unterschieden.
- Mehrere zulässige Reihenfolgen bleiben zulässig; ID-Sortierung wird nicht als topologische Allgemeingültigkeit interpretiert.
- Erreichbarkeit, Kausalität und ressourcenbeschränkte Parallelität bleiben getrennt. Eine vorhandene Evaluatorablehnung wird nicht zur morphologischen Unmöglichkeit umgedeutet.

## Eingaben / betroffene Ablagen

[Fallmatrix](../09-Research/grammar-sampling/CASE-MATRIX.md), [Quellenplan](../09-Research/grammar-sampling/SOURCE-PLAN.md), [bestehender Fallvertrag](../09-Research/analysis-readiness/README.md). Neue Fallberichte unter `docs/09-Research/grammar-sampling/`; neue Rohprotokolle unter `docs/10-Evidence/MILE-002/`. TASK-010 betrifft zusätzlich den vorhandenen kleinen Runner und dessen Tests.

## Gezielte Verifikation

Kleine erwartete Ordnungen bzw. Zykluszeugen vorab festhalten. Falls ein vorhandener LIB-Evaluator ausgeführt wird, dessen Aufruf separat von MCP protokollieren; v1 unverändert lassen.

## Abhängigkeiten und Grenze

[TASK-009](TASK-009-source-baselines.md), [TASK-010](TASK-010-authored-case-provenance.md)

Umfang gemäß [MILE-002](../02-Milestones/MILE-002-grammar-sampling.md). Keine neuen kanonischen Kategorien, Envelopes, produktiven Adapter oder Analysebibliotheken implementieren. Begrenzte Versuchsprofile bleiben Kandidaten. Noch kein Ausführungsnachweis vorhanden.
