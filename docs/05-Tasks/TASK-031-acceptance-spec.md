# TASK-031 — Abnahmespezifikation mit Entscheidungen

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/archive/2026-11-02-declare-completeness-and-instances/tasks.md).

Story: [US-018](../04-US/US-018-completeness.md), [US-019](../04-US/US-019-instance-binding.md) · Mile: MILE-005-A · Aufwand: 0,5 PT

## Ziel und Arbeit

Abnahmespezifikation für das neue P1-Profil (Vollständigkeitserklärung, Population, Instanzbindung) im Stil P1.9/P1.10.1: Umfang, Nicht-Ziele, Diagnosen, Vektoren, Entscheidungen D-1 bis D-6 (2026-11-01 getroffen, TASK-032 vorgezogen) als „decided“ übernommen.

## Ergebnis und Akzeptanz

- Spezifikation unter P1/<neues Profil>/ als Entwurf; Entscheidungen D-1 bis D-6 eingetragen, neu auftretende Detailfragen offen ausgewiesen.
- Bezug jedes Vektors auf einen Prüffall aus TASK-030.

## Eingaben

[Lernbilanz](../09-Research/learning-balance/LERNBILANZ.md), [Lückenbilanz](../09-Research/grammar-sampling/GAP-LEDGER.md) (G-01, G-08), [Darstellungsübergabe](../09-Research/visual-check/HANDOVER.md) (VR-05), [Probeergebnisse](../09-Research/learning-balance/PROBE-RESULTS.md).

## Abhängigkeiten und Grenze

[TASK-030](TASK-030-executable-cases.md)

Umfang gemäß [MILE-005](../02-Milestones/MILE-005-completeness-instances.md). P0, P1.1–P1.9 und P2 bleiben byte-gleich; neue Fähigkeiten als eigenes Profil bzw. eigener Printer-Stand. Ausführungsnachweis siehe Ergebnis.

## Ergebnis

Erledigt am 2026-11-01. [Abnahmespezifikation P1.12](../../P1/coverage-instance-profile-v1/P1_12_ACCEPTANCE_SPEC.md) (Entwurf, nicht implementiert) im Stil von P1.10.1: `binding-context/8` als strikte Obermenge von `/7`; Regeln CV (Abdeckung), PR (Populationsregeln, nur Deklaration und Abdeckungsprüfung in P1) und IN (Instanzbindung); drei neue Diagnosecodes; zehn Abnahmekriterien; 21 Vektoren K-01–K-21 als Übersetzung der Prüffälle CC-01–CC-16 und CI-01–CI-05 ohne Änderung von Status oder Schicht; LIB-Gegenstück `analyze.population/v1` mit typisiertem Ergebnis; D-1–D-6 als entschieden. Sechs Detailfragen Q-1–Q-6 mit Vorschlag offen; sie werden vor der Implementierung in einem eigenen Docs-Commit aufgelöst.
