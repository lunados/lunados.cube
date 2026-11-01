# TASK-030 — Ausführbare Prüffälle mit Erwartung vorab

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/declare-completeness-and-instances/tasks.md).

Story: [US-018](../04-US/US-018-completeness.md), [US-019](../04-US/US-019-instance-binding.md) · Mile: MILE-005-A · Aufwand: 0,5 PT

## Ziel und Arbeit

Die MILE-002-Fälle ARC-02, ARC-03, DSM-03, BPMN-01, BPMN-02 (bisher NE) und BPMN-03 (scoped/shared) als ausführbare Prüffälle formulieren: Eingabe, erwarteter Status heute (Baseline) und erwarteter Status mit dem neuen Profil, jeweils vor jeder Spezifikation committet.

## Ergebnis und Akzeptanz

- Prüffälle im Format research-case/2 mit gepinnter Herkunft; Baseline-Lauf gegen den heutigen Stand mit Bericht.
- Erwartung „mit Profil“ je Fall begründet; Grundlage für das Orakel in TASK-033.

## Eingaben

[Lernbilanz](../09-Research/learning-balance/LERNBILANZ.md), [Lückenbilanz](../09-Research/grammar-sampling/GAP-LEDGER.md) (G-01, G-08), [Darstellungsübergabe](../09-Research/visual-check/HANDOVER.md) (VR-05), [Probeergebnisse](../09-Research/learning-balance/PROBE-RESULTS.md).

## Abhängigkeiten und Grenze

[MILE-004](../02-Milestones/MILE-004-learning-balance.md) abgeschlossen

Umfang gemäß [MILE-005](../02-Milestones/MILE-005-completeness-instances.md). P0, P1.1–P1.9 und P2 bleiben byte-gleich; neue Fähigkeiten als eigenes Profil bzw. eigener Printer-Stand. Ausführungsnachweis siehe Ergebnis.

## Ergebnis

Erledigt am 2026-11-01. 21 formatneutrale [Prüffälle](../09-Research/completeness-instances/CHECK-CASES.md) (16 Vollständigkeit auf LIB-Schicht: Abwesenheit, Zählung, Join-Aktivierung; 5 Instanzbindung auf P1-Schicht), je Regelart PASS, FAIL und UNRESOLVED, Erwartung heute und mit Profil; vor Spezifikation und Code committet (`52cc773`). Baseline-Lauf der neun MILE-002-Fälle: alle 21 Erwartungen für heute bestätigt ([Abgleich](../10-Evidence/MILE-005/task030-baseline-check.json)); 16 Fälle bleiben heute nicht ausführbar, BPMN-03 im gemeinsamen Scope liefert weiterhin PASS.

Abweichung von der Planformulierung: Die Fälle liegen nicht als research-case/2 vor, sondern formatneutral, weil das Eingabeformat des neuen Profils erst TASK-031 festlegt; TASK-031 übersetzt sie in Vektoren.
