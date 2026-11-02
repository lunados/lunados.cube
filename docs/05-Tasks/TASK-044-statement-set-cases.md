# TASK-044 — Prüffälle und Orakel

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/project-statement-sets/tasks.md).

Story: [US-024](../04-US/US-024-statement-set-view.md), [US-025](../04-US/US-025-relation-aggregation.md) · Mile: MILE-007-A · Aufwand: 0,25 PT

## Ziel und Arbeit

Prüffälle aus C4-02 (Strategien `all`, `unless_same`, `unless_any`; interne Beziehung; zwei Quellen zum selben Elternpaar) und DSM-01 (Module mit `dependsOn`), dazu Fehlerfälle (unbekannter Referent, unbekanntes Prädikat, fehlende Strategie). Unabhängiges Orakel für Projektionsergebnis und Matrixzellen, Pins der 0.10.x-Ausgaben.

## Ergebnis und Akzeptanz

- Fälle, Orakel und Pins committet, bevor Evaluator oder Printercode entstehen; synthetisch, ohne Kundendaten.

## Abhängigkeiten und Grenze

[TASK-043](TASK-043-statement-set-spec.md)

Umfang gemäß [MILE-007](../02-Milestones/MILE-007-statement-sets.md). Keine neue Prüfsemantik; P0, P1.1–P1.12, VP-07, VP-09 und VP-10 0.10.0/0.10.1 bleiben byte-gleich.

## Ergebnis (2026-11-02)

- [Prüffälle](../09-Research/statement-sets/README.md): Kontexte `/8` für DSM und C4 (P1.12 PASS), zehn Aussagenmengen; A-01–A-10 für die LIB-Verdichtung; S-01–S-16 für VP-10 0.11.0. Alle Erwartungen von Hand, vor jedem Code.
- Pins: 0.10.1-Ausgaben O-01–O-09 (9) neu, 0.10.0 weiter 16/16.
- Beim Festlegen geschlossene Lücken der Spezifikation (§8, ohne Entscheidung zu ändern): Endpunkte müssen in `referents` stehen; Prüfreihenfolge; durchgereichte Aussagen und Verlustschlüssel; Nummerierung `d-n`; Projektionssicht zeigt Quell- und abgeleitetes Prädikat; Verlustzeile exakt, ohne Pluralformen.
