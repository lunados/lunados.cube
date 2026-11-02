# TASK-049 — Spezifikation und Detailfragen

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/check-control-flow/tasks.md).

Story: [US-026](../04-US/US-026-control-flow-profile.md), [US-027](../04-US/US-027-trace-conformance.md) · Mile: MILE-008-A · Aufwand: 0,25–0,5 PT

## Ziel und Arbeit

Abnahmespezifikation P1.13 (`binding-context/9`: `control_flow`, Diagnosen, Statusregeln) und Vertrag `analyze.trace-conformance/v1` (Eingaben, Ergebnisschema, Regeln). Detailfragen werden benannt und vom Nutzer entschieden; eigener Commit.

## Ergebnis und Akzeptanz

- Spezifikation mit aufgelösten Detailfragen, bevor Orakel und Code entstehen.

## Abhängigkeiten und Grenze

[TASK-048](TASK-048-control-flow-cases.md)

Umfang gemäß [MILE-008](../02-Milestones/MILE-008-control-flow.md). Keine Änderung an P0, P1.1–P1.12, P2 oder lunados.lib-Einträgen; neue Fähigkeiten als eigenes Profil und eigener LIB-Eintrag.

## Ergebnis (2026-11-02)

- [Spezifikation P1.13](../../P1/control-flow-profile-v1/P1_13_ACCEPTANCE_SPEC.md): `binding-context/9`, Regeln CF-1–CF-5 und TB-1–TB-3, Diagnosen, Vektoren KF-01–KF-09; LIB-Vertrag `analyze.trace-conformance/v1` mit TC-1–TC-6. Entwurf `ff31bd5`; Q-1–Q-10 nach Vorschlag entschieden.
