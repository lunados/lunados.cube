# TASK-014 — Drei BPMN-Fälle untersuchen

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/sample-five-grammars/tasks.md).

Story: [US-009](../04-US/US-009-bpmn-learning.md) · Mile: MILE-002-B · Aufwand: 3–4 h

## Ziel und Arbeit

BPMN-01 bis BPMN-03 konkretisieren: XOR, korrelierter AND-Join und instanzübergreifend vermischte Eingänge. Kleine Spuren und ihre Voraussetzungen aus der gewählten Referenz ableiten.

## Ergebnis und Akzeptanz

- Zustand, Prozessinstanz, Eingangsbedeutung und Aktivierungsbedingung sind ausdrücklich gebunden.
- Der Gegenfall unterscheidet zwei Signale aus verschiedenen Instanzen von zwei passenden Eingängen derselben Instanz.
- Ein P1-PASS bleibt Deklarationsprüfung. Fehlende operative Transition-/Join-Prüfung ist eine explizite Lücke.
- Zusätzliche Envelope-Anforderungen werden nur aus verlorenen Pflichtunterscheidungen begründet; keine Engine oder neue kanonische Kategorie wird gebaut.

## Eingaben / betroffene Ablagen

[Fallmatrix](../09-Research/grammar-sampling/CASE-MATRIX.md), [Quellenplan](../09-Research/grammar-sampling/SOURCE-PLAN.md), [bestehender Fallvertrag](../09-Research/analysis-readiness/README.md). Neue Fallberichte unter `docs/09-Research/grammar-sampling/`; neue Rohprotokolle unter `docs/10-Evidence/MILE-002/`. TASK-010 betrifft zusätzlich den vorhandenen kleinen Runner und dessen Tests.

## Gezielte Verifikation

Vorab definierte Normal-/Gegenspuren fachlich gegen die Quelle abgleichen; ausführbare Deklarationen separat lokal prüfen. Eine manuelle Spurprüfung ist kein BPMN-Engine-Nachweis.

## Abhängigkeiten und Grenze

[TASK-009](TASK-009-source-baselines.md), [TASK-010](TASK-010-authored-case-provenance.md)

Umfang gemäß [MILE-002](../02-Milestones/MILE-002-grammar-sampling.md). Keine neuen kanonischen Kategorien, Envelopes, produktiven Adapter oder Analysebibliotheken implementieren. Begrenzte Versuchsprofile bleiben Kandidaten. Noch kein Ausführungsnachweis vorhanden.
