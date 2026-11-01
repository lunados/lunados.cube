# TASK-009 — Quellen und Regelbasis fixieren

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/sample-five-grammars/tasks.md).

Story: [US-005](../04-US/US-005-source-bound-cases.md) · Mile: MILE-002-A · Aufwand: 1–2 h

## Ziel und Arbeit

Je Ansatz eine konkrete Referenzversion oder einen datierten Quellenstand, relevante Regelstellen und die betrachtete Aufgabe festlegen. C4-Methode und Structurizr-Ableitungsstrategie getrennt erfassen. ArchiMate-Normzugang und Version zuerst klären; DSM/MDM und DAG sind keine einzelnen Produkte.

## Ergebnis und Akzeptanz

- Ein Quellenregister deckt alle fünf Ansätze ab; jede verwendete Regel hat Fundstelle und Status (normativ, dokumentarisch, eigene Arbeitsannahme).
- Lokale Quellen-/Modellhashes sind erfasst; frei zugängliche Einstiegsseiten werden nicht als vollständig gelesene Normen bezeichnet.
- Fehlender Zugang bleibt offen. Insbesondere wird eine eigene Kardinalitätsregel nicht nachträglich ArchiMate zugeschrieben.

## Eingaben / betroffene Ablagen

[Fallmatrix](../09-Research/grammar-sampling/CASE-MATRIX.md), [Quellenplan](../09-Research/grammar-sampling/SOURCE-PLAN.md), [bestehender Fallvertrag](../09-Research/analysis-readiness/README.md). Neue Fallberichte unter `docs/09-Research/grammar-sampling/`; neue Rohprotokolle unter `docs/10-Evidence/MILE-002/`. TASK-010 betrifft zusätzlich den vorhandenen kleinen Runner und dessen Tests.

## Gezielte Verifikation

Quellenregister mit den 15 geplanten Fall-IDs abgleichen. Strittige Regelstellen nicht anhand von Cube-Ergebnissen umdeuten.

## Abhängigkeiten und Grenze

[MILE-001 abgeschlossen](../02-Milestones/MILE-001-analysis-readiness.md)

Umfang gemäß [MILE-002](../02-Milestones/MILE-002-grammar-sampling.md). Keine neuen kanonischen Kategorien, Envelopes, produktiven Adapter oder Analysebibliotheken implementieren. Begrenzte Versuchsprofile bleiben Kandidaten. Noch kein Ausführungsnachweis vorhanden.

## Ergebnis

Abgeschlossen am 2026-11-01. [Quellen- und Regelregister](../09-Research/grammar-sampling/SOURCE-REGISTER.md) mit 15 Quellen, 21 Regeln und Zuordnung aller 15 Fall-IDs; maschinenlesbar in [SOURCE-LOCK.json](../10-Evidence/MILE-002/SOURCE-LOCK.json). ArchiMate: vollständige Spezifikation 3.2 nicht verfügbar und per Entscheidung vom 2026-11-01 ausgelassen; Bindung an Reference Cards N221 und Herstellerbeispiele, normative Endpunkt-Zulässigkeit ungeprüft. BPMN: Fundstellen gebunden, Regelwortlaut wird in TASK-014 gelesen. Keine Cube-Prüfung ausgeführt.
