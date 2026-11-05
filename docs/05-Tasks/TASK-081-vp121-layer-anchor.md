# TASK-081 — VP-12.1: VG-Anker der Schichtspalte

Mile: [MILE-018](../02-Milestones/MILE-018-axis-pairs-follow-up.md) (E18-1, B13) · Aufwand: 0,25–0,5 PT · Status: erledigt (lokal, G6), 2026-11-05

## Entscheidung (Nutzer, 2026-11-05)

D-1: Die Schichtspalte trägt den UI-Anker `skeleton-shell.section` (◲). Die Spalte ist eine deklarierte Anordnung (VP-07.2-Layer-Map, „presentation input only“) oder eine Ankerfamilie; ein UI-Anker trifft keine Cube-Aussage. `resource-zones.*` (Z:zone) hätte behauptet, jede Schicht sei eine Ressourcenzone.

## Ergebnis

- Spezifikation [VP12_1_ACCEPTANCE_SPEC.md](../../P2/visual-printer-landscape-v1/VP12_1_ACCEPTANCE_SPEC.md), Oracle LA-01…LA-06 und 24 Regressionsdigests von 0.12.0 vor dem Code.
- Profil `P2-VP-LANDSCAPE/0.12.1` (opt-in): Spaltenköpfe mit Anker, Ledger `column_anchor`, Audit `COLUMN_ANCHOR_EACH_COLUMN`; 0.12.0 byte-identisch. Tests: `test_vp121` 7, `test_vp12` 19 grün.
- G6: `cube_plan_source` nimmt `profile` für `vplandscape`; Discovery listet beide Profile. P3-Test `test_mile016_landscape` 4 grün.
- lunados.explorer druckt alle 11 Landschaften mit 0.12.1, `check-panels` PASS.

## Offen

G5-Auslieferung mit E18-7 (R11).
