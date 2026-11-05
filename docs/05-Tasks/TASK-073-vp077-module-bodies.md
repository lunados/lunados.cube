# TASK-073 — Profil VP-07.7: Modulkörper, Grant, Evidence und Content

Mile: [MILE-013](../02-Milestones/MILE-013-printer-module-bodies.md) · Aufwand: 0,5 PT · Status: erledigt (lokal), 2026-11-05

## Ziel und Arbeit

`P2-VP-MIGRATION/0.7.7` als Opt-in-Folgeprofil von 0.7.6: geschlossene Konzepttabelle um sieben Zeilen erweitert (Spezifikation [VP07_7_ACCEPTANCE_SPEC.md](../../P2/visual-printer-migration-v1/VP07_7_ACCEPTANCE_SPEC.md)); alles andere wie 0.7.6. CLI und G6 (`cube_plan_source`, `cube_plan_views`, `cube_plan_check`).

## Ergebnis und Akzeptanz

- 0.7.6-Ausgaben vor dem Code festgehalten (`scripts/pin_076_digests.py`, 10 Szenarien) und danach byte-identisch; 0.7.0–0.7.5 ebenso (Pins 14/16/13/14/16/16).
- `tests/test_vp077.py` (8 Tests, VP077-01…07) grün; P2 `visual-printer-migration-v1` 123 Tests, P3 `mcp-local` 250 Tests grün, bestätigt in der Adapter-venv auf dem Mac.
- Abnahmefall F02 aus lunados.explorer: P1.14 PASS für alle Pläne, 42 von 42 Abhängigkeiten gedruckt, `check-panels` PASS ([Nachweis](../10-Evidence/MILE-013/README.md)).

## Abhängigkeiten und Grenze

MILE-011 (Profil 0.7.6, P1.14). Keine Änderung an P0, P1, VP-04-Budgets und Diagnosecodes. G5 nicht ausgeliefert.
