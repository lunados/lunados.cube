# TASK-040 — VP-10.1 Nachweise

- **Datum:** 2026-11-02
- **Code:** `vpcells` `P2-VP-CELLS/0.10.1` (opt-in `axis_order`), Branch `feature/mile006-remote-and-order`; Laufprotokoll mit Commit in [../task040-run.json](../task040-run.json).
- **Eingabe:** synthetische Vektoren O-01, O-02, O-04, O-08 und O-09 aus `P2/visual-printer-cells-v1/fixtures/o01_o10_materialized.json` (MILE-003-Plan R-1 als binding-context/8, Paarerklärung `m:printer → m:parser`, Prädikat `references`). Keine Kundendaten.
- **Aufruf:** `scripts/run_vectors_o.py` (`from_plan` → `render_cells(..., axis_order=…)`), lokal.
- **Ausgabe:** je Vektor `*.svg` und `*.report.json`.
- **Aussagegrenze:** Darstellung einer deklarierten Reihenfolge. „feedback“/„Rückkopplung“ folgt nur aus der Reihenfolge, die der Aufrufer angibt; es ist kein Befund über das System und keine Prüfsemantik.

| Datei | Zeigt |
|---|---|
| `O-01` | Reihenfolge parser, resolver, validator, printer: eine Marke (`m:parser|m:validator`) |
| `O-02` | umgekehrte Reihenfolge: drei Marken |
| `O-04` | Teilreihenfolge: resolver und printer „unordered“, Warnung `VP10_ORDER_PARTIAL` |
| `O-08` | zusätzliche `recovers-via`-Abhängigkeit über der Diagonale: keine Marke (Q-6) |
| `O-09` | wie O-04, deutsch: „Rückkopplung“, „nicht geordnet“ |
