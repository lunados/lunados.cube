# TASK-046 — VP-10 0.11.0 Nachweise

- **Datum:** 2026-11-02
- **Code:** `vpcells` `P2-VP-CELLS/0.11.0` (`from-statements`, eigener Matrix-Zeichner), Branch `feature/mile007-statement-sets`; Laufprotokoll mit Commit in [../task046-run.json](../task046-run.json).
- **Eingabe:** synthetische Vektoren aus `P2/visual-printer-cells-v1/fixtures/s01_s16_materialized.json`; Kontexte und Aussagenmengen aus `docs/09-Research/statement-sets/inputs`, Projektionsdatensätze aus dem gepinnten lunados.lib-Evaluator. Keine Kundendaten.
- **Aufruf:** `scripts/run_vectors_s.py` (`from_statements` → `render_cells`), lokal.
- **Ausgabe:** je Vektor `*.svg` und `*.report.json`.
- **Aussagegrenze:** Darstellung deklarierter Aussagen. Eine abgeleitete Aussage folgt nur aus ihren deklarierten Quellen unter der gewählten Strategie; der Cube rechnet die Verdichtung nicht nach.

| Datei | Zeigt |
|---|---|
| `S-01` | DSM-01 als Aussagenmenge: vier `dependsOn`-Einträge, Zeile = Subjekt, keine Plan-Begriffe |
| `S-02` | wie S-01 mit Abdeckung: printer × parser „keine · geprüft (Paar)“ |
| `S-03` | wie S-01 mit Reihenfolge: „feedback“ auf parser → validator |
| `S-04` | C4-02 verdichtet (`all`): API × DB „d-1 · uses.derived · derived · 2 sources“, Verlustzeile |
| `S-05` | `all` neben deklarierter API uses DB: durchgereichte und abgeleitete Aussage in einer Zelle |
| `S-06` | `unless_any` neben API monitors DB: keine Ableitung, zwei unterdrückte Quellen |
| `S-15` | wie S-04, deutsch: „abgeleitet · 2 Quellen“, „Verdichtung all: …“ |
