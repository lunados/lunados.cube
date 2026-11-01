# TASK-012 — Drei ArchiMate-Fälle untersuchen

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/sample-five-grammars/tasks.md).

Story: [US-007](../04-US/US-007-archimate-learning.md) · Mile: MILE-002-B · Aufwand: 2–3 h

## Ziel und Arbeit

ARC-01 bis ARC-03 konkretisieren: typisierte Relation, abgegrenzte Zielbelegung und fehlende Referenz bei partieller Modellabdeckung. Normative Regeln und lokale Versuchskardinalitäten getrennt kennzeichnen.

## Ergebnis und Akzeptanz

- Version und Regelstelle der typisierten Relation sind belegt; ähnlich benannte Cube-Konzepte werden nicht ungeprüft gleichgesetzt.
- Jede Zählregel nennt Zielidentität, Rolle, Scope, Zeitpunkt und Vollständigkeit; ihr normativer oder lokaler Ursprung ist eindeutig.
- Das Gegenbeispiel trennt unbekannte Belegung von tatsächlicher Unterbelegung. Fehlende Populationsprüfung wird nicht durch vorhandene Slot-Arity als gelöst ausgegeben.

## Eingaben / betroffene Ablagen

[Fallmatrix](../09-Research/grammar-sampling/CASE-MATRIX.md), [Quellenplan](../09-Research/grammar-sampling/SOURCE-PLAN.md), [bestehender Fallvertrag](../09-Research/analysis-readiness/README.md). Neue Fallberichte unter `docs/09-Research/grammar-sampling/`; neue Rohprotokolle unter `docs/10-Evidence/MILE-002/`. TASK-010 betrifft zusätzlich den vorhandenen kleinen Runner und dessen Tests.

## Gezielte Verifikation

Regel-/Typbindung manuell gegen die gewählte Referenz kontrollieren, danach mögliche lokale Proben ausführen. Fehlt die notwendige Referenz, bleiben betroffene Kriterien offen.

## Abhängigkeiten und Grenze

[TASK-009](TASK-009-source-baselines.md), [TASK-010](TASK-010-authored-case-provenance.md)

Umfang gemäß [MILE-002](../02-Milestones/MILE-002-grammar-sampling.md). Keine neuen kanonischen Kategorien, Envelopes, produktiven Adapter oder Analysebibliotheken implementieren. Begrenzte Versuchsprofile bleiben Kandidaten. Noch kein Ausführungsnachweis vorhanden.
