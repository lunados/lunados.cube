# TASK-024 — Probeplan mit Erwartungen festlegen

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/archive/2026-11-01-prioritize-learning-balance/tasks.md).

Story: [US-015](../04-US/US-015-open-guiding-questions.md) · Mile: MILE-004-A · Aufwand: 1–1,5 h

## Ziel und Arbeit

Für E-1, E-2, L-1 und L-2 Quelle und Version pinnen (Envelope-Vertrag, VP-03-Linsengrammatik, VP-07/VP-09-Bindungen, MODE in P0 v9.4), Eingaben aus dem MILE-002-Material wählen und je Probe die Erwartung samt Prüfkriterium festhalten. Nicht ausführbare Proben vorab als NE begründen.

## Ergebnis und Akzeptanz

- Probeplan unter `docs/09-Research/learning-balance/probes/` committet, bevor eine Probe läuft.
- Je Probe: Frage, Quelle mit Hash, Eingabe, Werkzeug (Schema-Prüfung, `cube_validate`, Printer), erwartetes Ergebnis, Entscheidungsregel.

## Eingaben / betroffene Ablagen

[Lernvergleich](../09-Research/cube-grammar-2026-11-01/LERNVERGLEICH.md), [Lückenbilanz](../09-Research/grammar-sampling/GAP-LEDGER.md), [Darstellungsübergabe](../09-Research/visual-check/HANDOVER.md). Neue Ergebnisse unter `docs/09-Research/learning-balance/`, Rohnachweise unter `docs/10-Evidence/MILE-004/`.

## Abhängigkeiten und Grenze

MILE-002 und MILE-003 abgeschlossen

Umfang gemäß [MILE-004](../02-Milestones/MILE-004-learning-balance.md). Keine Implementierung, keine Morphologie-, Envelope-, Printer- oder VG-Ankeränderung. Nutzen ist erwartet, nicht gemessen. Ausführungsnachweis siehe Ergebnis.

## Ergebnis

Erledigt am 2026-11-01. [Probeplan](../09-Research/learning-balance/probes/PROBE-PLAN.md) mit vier Proben (E-1, E-2, L-1, L-2) und einer begründeten Nichtausführbarkeit (MODE), zwölf gepinnten Quellen, je sechs Pflichtunterscheidungen mit erwartetem Träger für E-1/E-2, Erwartungen und Entscheidungsregeln. Maschinenlesbar und deterministisch erzeugt: [PROBE-PLAN.json](../09-Research/learning-balance/probes/PROBE-PLAN.json), [build_probes.py](../09-Research/learning-balance/probes/build_probes.py). Committet vor jedem Lauf.
