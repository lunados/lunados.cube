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

## Ergebnis (2026-11-02)

- [27 Prüffälle](../09-Research/control-flow/CHECK-CASES.md) vor der Spezifikation (`aefe6aa`): 9 auf P1-Schicht (Deklaration, Flussbindung, Regressionsschutz `/8`), 18 auf LIB-Schicht (exklusiv 4, Bedingungsreihenfolge 5, Join 6, Split 2, Merge 1); je Prüfart PASS und FAIL, wo sinnvoll UNRESOLVED.
- Modellergänzung offen benannt: Flussnamen und Merge-Gateway aus der Modellnotiz; Varianten als `variant_of_model` gekennzeichnet.
- [Baseline-Lauf](../10-Evidence/MILE-008/task048-baseline-report.json) der sechs MILE-002-Fälle mit dem unveränderten Runner (Readiness bestanden) und eine Probe für CF-06/CF-07 mit dem unveränderten P1.12-Adapter: [27/27 Erwartungen für heute bestätigt](../10-Evidence/MILE-008/task048-baseline-check.json). Heute bestehen die falsche Leitung an Ship, der unbekannte Fluss und zwei widersprüchliche Leitungen je einzeln mit PASS; 22 Fälle sind nicht ausführbar.
