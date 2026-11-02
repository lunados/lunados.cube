# MILE-007 — Prüffälle für Aussagenmengen und Verdichtung

Stand: 2026-11-02 · TASK-044 · Grundlage: [Spezifikation VP-10 0.11.0](../../../P2/visual-printer-cells-v1/VP110_ACCEPTANCE_SPEC.md) (Q-1–Q-10 entschieden)

Alle Erwartungen sind von Hand aus der Spezifikation abgeleitet und vor jedem Code committet. Alles synthetisch, ohne Kundendaten.

| Datei | Inhalt |
|---|---|
| [build_check_cases.py](build_check_cases.py) | schreibt Eingaben und Erwartungen; berechnet nur Eingabe-Hashes |
| [inputs/](inputs/) | Kontexte `binding-context/8` (DSM aus DSM-01, C4 aus C4-02, je mit und ohne Abdeckung; P1.12 PASS) und zehn Aussagenmengen |
| [CHECK-CASES.json](CHECK-CASES.json) | A-01–A-10 für lunados.lib `project.aggregate-relations/v1`: drei Strategien mit und ohne deklarierte Container-Beziehung, drei Fehlerfälle |
| [S-Orakel](../../../P2/visual-printer-cells-v1/oracles/independent_s01_s16.json) | S-01–S-16 für VP-10 0.11.0: DSM ohne Plan, Abdeckung, Reihenfolge, C4 verdichtet, Fehler und Warnungen, deutsch, G6 |

## Kernerwartungen

| Fall | Erwartung |
|---|---|
| A-01 (C4-02, `all`) | `d-1` API → DB `uses.derived` aus s-1 und s-2, Beschreibung „Writes orders to“, eine verworfen; s-3 intern |
| A-05 (`unless_same` neben s-4 API uses DB) | keine Ableitung; s-1 und s-2 unterdrückt durch s-4; s-4 durchgereicht |
| A-07 (`unless_any` neben s-5 API monitors DB) | keine Ableitung; s-1 und s-2 unterdrückt durch s-5; Zelle API × DB unbekannt |
| S-01 (DSM-01) | vier `dependsOn`-Einträge Zeile = Subjekt; keine Plan-Begriffe im SVG |
| S-04 (C4-02 verdichtet) | Zelle API × DB „d-1 · uses.derived · derived · 2 sources“; Verlustzeile exakt |
