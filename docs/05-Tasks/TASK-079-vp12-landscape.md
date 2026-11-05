# TASK-079 — VP-12: Landschaftssicht `cube.landscape`

Mile: [MILE-016](../02-Milestones/MILE-016-axis-pair-views.md) (B6, B10) · Aufwand: 1–1,5 PT · Status: erledigt, 2026-11-05

Spezifikation: [VP12_ACCEPTANCE_SPEC.md](../../P2/visual-printer-landscape-v1/VP12_ACCEPTANCE_SPEC.md). Reihenfolge: Entscheidungen D-1…D-8, Vektoren L-01…L-14 und Oracle vor dem Code, Regression VP-07…VP-11, dann Laufzeit, G6, Explorer-Abnahme und Cockpit.

## Stand 2026-11-05

- Spezifikation SPECIFIED, D-1…D-8 wie vorgeschlagen bestätigt; Ebenen über die VP-07.2-Layer-Map (keine zweite Form).
- Oracle `oracles/independent_l01_l14.json` vor dem Code committet (Commit 0514d14, §1.6 in 568873f präzisiert, Erwartungen unverändert).
- Paket `vplandscape` (CLI, `api`, Locales de/en), `tests/test_vp12.py` 18 Tests grün; keine Datei anderer P2-Pakete geändert (VP12-02).
- VP12-03: lunados.explorer druckt die Landschaft für alle 11 Blätter (Plan `<id>-full`, Spalten aus `mappings/landscape-layers.json` nach deklariertem Konzept, Schritte current/beta), `check-panels` PASS; F02 und F05 abgenommen; Cockpit-Sicht „Landschaft“.
- Geometrie: leere Spalten schmal, Breite wächst ab 5 belegten Spalten über 1200 px; Brücken in derselben Spalte links, parallele Wege versetzt (nur Darstellung, Oracle unverändert).
- VP12-04: G6 lokal und G5 R10 live erledigt (58/58, [TASK-080](TASK-080-g5-r10.md)).
- VG-Anker für die Schichtspalte: nach [MILE-018](../02-Milestones/MILE-018-axis-pairs-follow-up.md) (B13) verschoben.
