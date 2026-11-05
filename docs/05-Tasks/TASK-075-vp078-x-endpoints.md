# TASK-075 — Profil VP-07.8: X-Endpunkte, Source, Cache und Revision

Mile: [MILE-014](../02-Milestones/MILE-014-printer-x-endpoints.md) · Aufwand: 0,25–0,5 PT · Status: erledigt (lokal), 2026-11-05

## Ziel und Arbeit

`P2-VP-MIGRATION/0.7.8` als Opt-in-Folgeprofil von 0.7.7: geschlossene Konzepttabelle um dreizehn Zeilen erweitert (Spezifikation [VP07_8_ACCEPTANCE_SPEC.md](../../P2/visual-printer-migration-v1/VP07_8_ACCEPTANCE_SPEC.md)); alles andere wie 0.7.7. CLI und G6.

## Ergebnis und Akzeptanz

- 0.7.7-Ausgaben vor dem Code festgehalten (`scripts/pin_077_digests.py`, 3 Szenarien) und danach byte-identisch; 0.7.0–0.7.6 ebenso.
- `tests/test_vp078.py` (8 Tests, VP078-01…07) grün; P2 `visual-printer-migration-v1` 131 Tests, P3 `mcp-local` 250 Tests grün; G5-Offline-Gate unverändert PASS.
- Abnahmefälle aus lunados.explorer: F01 24/24, F02 42/42, F03a 61/61, F04a 39/39, F05 28/28 Abhängigkeiten gedruckt; P1.14 für alle Pläne PASS ([Nachweis](../10-Evidence/MILE-014/README.md)).

## Abhängigkeiten und Grenze

MILE-013 (Profil 0.7.7). Keine Änderung an P0, P1, VP-04-Budgets und Diagnosecodes. G5 nicht ausgeliefert.
