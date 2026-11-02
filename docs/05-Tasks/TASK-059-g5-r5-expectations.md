# TASK-059 — Erwartungen vor Code

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/deliver-remote-plan-views/tasks.md).

Story: [US-030](../04-US/US-030-remote-control-flow.md), [US-031](../04-US/US-031-remote-plan-views.md) · Mile: MILE-010-A · Aufwand: 0,25–0,5 PT

## Ziel und Arbeit

Erwartungen vorab: für die Offline-Parität die lokalen G4/G6-Ergebnisse aller vorhandenen Vektoren als Digests; für die Live-Abnahme die Stichproben (`/9`-Fälle, je Sicht ein Vektor, `cube_plan_check`, Grenzfall) mit erwarteten Status, Codes und SVG-Digests.

## Ergebnis und Akzeptanz

- Erwartungen committet, bevor Kern- und Gateway-Code entstehen; synthetisch, ohne Kundendaten.

## Abhängigkeiten und Grenze

[TASK-058](TASK-058-g5-r5-spec.md)

Umfang gemäß [MILE-010](../02-Milestones/MILE-010-remote-plan-views.md). Keine neue Prüfsemantik; P0, P1, P2, lokaler Adapter und lunados.lib-Einträge bleiben byte-gleich; geändert wird nur `P3/remote-mcp-g5`.

## Ergebnis (2026-11-02)

- [Aufrufliste](../../P3/remote-mcp-g5/scripts/r5_calls.py) und [Erwartungen](../../P3/remote-mcp-g5/evidence/G5_R5_EXPECTATIONS.json), erzeugt mit den lokalen Server-Funktionen: Discovery, 16 `/9`-Aufrufe (KF-01–KF-09, sieben BPMN-Fälle, wie in MILE-008), 71 Plan-Ketten (K-, O-, S-, I-Vektoren, SVG-Grenze, zwei Argumentfehler); 23 Ketten enden im erwarteten Fehler, darunter beide Größengrenzen.
- Präzisierung CL-3 (§8 der [Spezifikation](../../P3/remote-mcp-g5/G5_R5_ACCEPTANCE_SPEC.md)): live alle Aufrufe per Skript gegen das bereitgestellte Gateway, dazu eine Teilmenge von sieben Aufrufen durch den Agenten im Host; einige Argumente sind für die Eingabe im Host zu groß.
- Lokale Rechenzeit höchstens 0,98 s (P-K07-flow), unter der 2-s-Regel von Q-7.
