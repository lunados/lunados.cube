# MILE-008 — Nachweise

Stand: 2026-11-02 · abgeschlossen ([C-RESULT](C-RESULT.md)).

| Datei | Inhalt |
|---|---|
| [Prüffälle](../../09-Research/control-flow/CHECK-CASES.md) | TASK-048: 27 Fälle CF-01–CF-29 mit Erwartung „heute“ und „nach Umsetzung“, je Schicht |
| [task048-baseline-report.json](task048-baseline-report.json), [task048_baseline_check.py](task048_baseline_check.py), [task048-baseline-check.json](task048-baseline-check.json) | TASK-048: Baseline-Lauf und Abgleich 27/27 |
| [TASK-051-LIB.md](TASK-051-LIB.md) | TASK-051: Nachweis lunados.lib `analyze.trace-conformance/v1` (extern umgesetzt) |
| [TASK-052-REVIEW.md](TASK-052-REVIEW.md) | TASK-052: Prüfung von TASK-050 und TASK-051, sechs Befunde ohne Blocker |
| [task052-rerun/](task052-rerun/README.md) | TASK-052: Wiederholung als `/9`, 7/7 × 2 über lokales MCP, LIB-Teil 3/3 |
| [verify_mile008.py](verify_mile008.py), [lib-verify.json](lib-verify.json), [verification.json](verification.json) | Abschlussprüfung in zwei Schritten (`--lib` für lunados.lib `verify --cube` 159/159 und Differenzprüfung 471, dann Reihenfolge Cube und LIB, P1- und Adapter-Läufe, Wiederholung, Schichten, Prüfsummen, Links); `all_ok` |
| [C-RESULT.md](C-RESULT.md), [MANIFEST.json](MANIFEST.json) | Abschlussnachweis und Hashes |
