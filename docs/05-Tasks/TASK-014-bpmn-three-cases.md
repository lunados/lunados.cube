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

## Ergebnis

Abgeschlossen am 2026-11-01. Regelwortlaut aus der bereitgestellten Spezifikation BPMN 2.0.2 (formal/13-12-09) gelesen: §10.6.2, §13.2, §13.3.1, §13.4.1, §13.4.2, Glossar „Token“; Hinweis auf den Nummerierungswiderspruch (Konformitätsklausel nennt „Clause 14“). Drei Fallberichte: [BPMN-01](../09-Research/grammar-sampling/reports/BPMN-01.md), [BPMN-02](../09-Research/grammar-sampling/reports/BPMN-02.md), [BPMN-03](../09-Research/grammar-sampling/reports/BPMN-03.md). Sieben v2-Fälle, davon zwei `not_executable`; Erwartungen vor dem Lauf committet (`66efa7b`); alle ausführbaren Fälle in 2/2 frischen Verbindungen erwartungsgemäß, Regression über 35 Fälle stabil; [Bericht](../10-Evidence/MILE-002/task014-bpmn-report.json). Kernbefunde: instanzgebundene Aufzeichnungen ausdrückbar; Exklusivität und Synchronisation sind Regeln über mehrere Aussagen ohne Übergangsvertrag; Instanz-als-Scope weist instanzübergreifende Joins ab, ein gemeinsamer Scope nicht. Keine Engine gebaut, keine Morphologieänderung begründet.

