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

## Ergebnis

Abgeschlossen am 2026-11-01. Drei Fallberichte: [ARC-01](../09-Research/grammar-sampling/reports/ARC-01.md) (teilweise), [ARC-02](../09-Research/grammar-sampling/reports/ARC-02.md) (konkrete Lücke: Populationsprüfung), [ARC-03](../09-Research/grammar-sampling/reports/ARC-03.md) (unbekannt ≠ verletzt belegt; Abwesenheit nicht ausdrückbar). Sieben v2-Fälle, davon zwei begründet `not_executable`; Erwartungen vor dem Lauf committet (`3229dd3`); alle ausführbaren Fälle in 2/2 frischen Verbindungen erwartungsgemäß, C4-Regression stabil; [Bericht](../10-Evidence/MILE-002/task012-archimate-report.json). ArchiMate-Basis: Reference Cards N221 + Herstellerbeispiele; normative Endpunkt-Zulässigkeit ausgelassen. Die Zählregel min 2/max 3 ist ausdrücklich lokal (A). Die P1.6-Slot-Arity wird nicht als Populationsprüfung ausgegeben. Keine Morphologieänderung begründet.

