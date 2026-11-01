# TASK-016 — Kompatibilitätslücken und Lerngewinn bündeln

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/sample-five-grammars/tasks.md).

Story: [US-011](../04-US/US-011-grammar-gap-ledger.md) · Mile: MILE-002-C · Aufwand: 2–3 h

## Ziel und Arbeit

Die 15 Fallberichte auf die sieben Nutzerfragen zurückführen. Für jede belegte Lücke die kleinste Eingriffsebene, Wiederverwendung, erwarteten Nutzen, Aufwand und Komplexität benennen. Kandidaten für MILE-003/MILE-004 übergeben.

## Ergebnis und Akzeptanz

- Ein Lückenregister verweist pro Eintrag auf Fall, Quelle, konkrete verlorene Unterscheidung und Nachweisgrad.
- Die sieben Leitfragen haben je eine begrenzte Antwort oder eine präzise offene Frage; aus 15 Fällen folgt keine universelle Vollständigkeit.
- Vorschläge sind in Dokumentation, Komposition, Profil, LIB, visuelle Regel und erst bei belegtem Bedarf Morphologie eingeordnet.
- Wichtige konkrete Nutzeraufgaben und erwarteter Nutzen sind benannt; keine gemessene Nutzenevidenz ohne Messung.

## Eingaben / betroffene Ablagen

[Fallmatrix](../09-Research/grammar-sampling/CASE-MATRIX.md), [Quellenplan](../09-Research/grammar-sampling/SOURCE-PLAN.md), [bestehender Fallvertrag](../09-Research/analysis-readiness/README.md). Neue Fallberichte unter `docs/09-Research/grammar-sampling/`; neue Rohprotokolle unter `docs/10-Evidence/MILE-002/`. TASK-010 betrifft zusätzlich den vorhandenen kleinen Runner und dessen Tests.

## Gezielte Verifikation

Jede Schlussfolgerung auf Fallberichte rückverfolgen. Diagnosen, semantische Lücken und bloße Implementierungsgrenzen gegeneinander kontrollieren.

## Abhängigkeiten und Grenze

[TASK-011](TASK-011-c4-three-cases.md), [TASK-012](TASK-012-archimate-three-cases.md), [TASK-013](TASK-013-dsm-mdm-three-cases.md), [TASK-014](TASK-014-bpmn-three-cases.md), [TASK-015](TASK-015-dag-three-cases.md)

Umfang gemäß [MILE-002](../02-Milestones/MILE-002-grammar-sampling.md). Keine neuen kanonischen Kategorien, Envelopes, produktiven Adapter oder Analysebibliotheken implementieren. Begrenzte Versuchsprofile bleiben Kandidaten. Noch kein Ausführungsnachweis vorhanden.
