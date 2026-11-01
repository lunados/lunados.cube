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

## Ergebnis

Abgeschlossen am 2026-11-01. Drei Fallberichte: [DAG-01](../09-Research/grammar-sampling/reports/DAG-01.md), [DAG-02](../09-Research/grammar-sampling/reports/DAG-02.md), [DAG-03](../09-Research/grammar-sampling/reports/DAG-03.md). Zwei Nachweisarten getrennt: zwei P1-Fälle über den Runner ([Bericht](../10-Evidence/MILE-002/task015-dag-p1-report.json)) und vier direkte Aufrufe von `lunados.lib` `impact.propagate/v1` ([Protokoll](../10-Evidence/MILE-002/task015-dag-lib-calls.json)); alle Erwartungen vor der Ausführung committet (`b45ac11`) und getroffen. Zuordnung der bekannten Grenze: `i < j` ist eine echte, aber im Eintrag nicht deklarierte Vorbedingung (topologische Nummerierung für die Einpass-Auswertung), keine Grammatik- oder Morphologiegrenze; die Meldung „cycle“ ist für die azyklische Rückwärtskante irreführend; echter Zyklus und Umnummerierung ergeben dieselbe Ablehnung. Kantenorientierung im Evaluator umgekehrt zur Cube-Lesart. Zwei topologische Nummerierungen liefern je ID identische Ergebnisse. Kandidaten `analyze.cycle-gate`, `analyze.topological-generations`, `analyze.topological-orders` beschrieben, nicht implementiert. NetworkX nicht ausgeführt.

