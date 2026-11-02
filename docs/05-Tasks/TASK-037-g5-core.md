# TASK-037 — G5-Kern mit P1.12

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/deliver-remote-and-ordered-cells/tasks.md).

Story: [US-021](../04-US/US-021-remote-v8.md) · Mile: MILE-006-A · Aufwand: 0,5 PT

## Ziel und Arbeit

P1.12 (`cube_p112`) in `assemble_core.py` aufnehmen; Discovery-Abschnitt `p112_coverage_instance` im Kern; Version `0.7.0-proof`; Assembly-Prüfung mit K-01–K-21; Parität G4/G5 offline; Erwartungen für die Live-Abnahme vorab festlegen.

## Ergebnis und Akzeptanz

- Offline-Prüfung `verify_g5.py` PASS; Parität G4/G5 für alle K-Vektoren.
- Erwartungsdatei für die Host-Abnahme vor der Bereitstellung committet.

## Abhängigkeiten und Grenze

MILE-005 (P1.12, Adapter G4)

Umfang gemäß [MILE-006](../02-Milestones/MILE-006-remote-and-order.md). Keine neue Prüfsemantik; P0, P1.1–P1.12, VP-07, VP-09 und VP-10 0.10.0 bleiben byte-gleich.
