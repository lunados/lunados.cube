# TASK-048 — Prüffälle und Baseline

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/check-control-flow/tasks.md).

Story: [US-026](../04-US/US-026-control-flow-profile.md), [US-027](../04-US/US-027-trace-conformance.md) · Mile: MILE-008-A · Aufwand: 0,5 PT

## Ziel und Arbeit

Prüffälle aus BPMN-01, -02, -03 und Varianten (XOR zwei Pfade, kein Pfad, Default trotz wahrer Bedingung, Bedingungsreihenfolge, Join mit fehlendem Eingang, Token aus fremder Instanz, Überschuss) mit Erwartung „heute“ und „nach Umsetzung“, je Schicht (P1 oder LIB). Baseline-Lauf der zugehörigen MILE-002-Fälle mit dem unveränderten Runner.

## Ergebnis und Akzeptanz

- Fälle und Erwartungen committet, bevor die Spezifikation entsteht; Baseline-Abgleich dokumentiert; synthetisch, ohne Kundendaten.

## Abhängigkeiten und Grenze

MILE-005 (P1.12), Entscheidungen D-1–D-8

Umfang gemäß [MILE-008](../02-Milestones/MILE-008-control-flow.md). Keine Änderung an P0, P1.1–P1.12, P2 oder lunados.lib-Einträgen; neue Fähigkeiten als eigenes Profil und eigener LIB-Eintrag.
