# MILE-005 — Nachweise

Stand: 2026-11-02 · abgeschlossen ([C-RESULT](C-RESULT.md)).

| Datei | Inhalt |
|---|---|
| [task030-baseline-report.json](task030-baseline-report.json) | TASK-030: Baseline-Lauf der neun zugehörigen MILE-002-Fälle mit dem unveränderten Runner (2 Verbindungen, Readiness bestanden) |
| [task030-baseline-check.json](task030-baseline-check.json) | Abgleich: Erwartung „heute“ aller 21 Prüffälle gegen den Baseline-Lauf (21/21) |
| [task033-run.json](task033-run.json) | TASK-033: P1.12-Lauf (K-01–K-21 21/21 gegen Orakel `8297b82`), Testsuiten P1.1–P1.12, P1.11-Vektoren 16/16; `all_ok` |
| [task034-run.json](task034-run.json) | TASK-034: lunados.lib `analyze.population/v1`, CC-01–CC-16 16/16 (Evaluator, Orakel, Ergebnisschema), `verify --cube`, Differenzprüfung; `all_ok` |
| [task034_differential.py](task034_differential.py) | TASK-034: Differenzprüfung Evaluator gegen Orakel über abgeleitete Varianten |
| [task035-run.json](task035-run.json) | TASK-035: VP-10, J-01–J-14 14/14, 24 Tests, VP-07/VP-09 unverändert, Render-Hashes; `all_ok` |
| [task035/](task035/) | TASK-035: Renderings und Berichte (Golden en/de, J-07, J-08 de, J-12) |
| [task036-rerun/report.json](task036-rerun/report.json) | TASK-036: Wiederholung von ARC-03, DSM-03, BPMN-03 (plus Kontrolle BPMN-02) als `/8` über lokales MCP stdio, 7/7 wie erwartet, zwei Verbindungen |
| [verify_mile005.py](verify_mile005.py), [verification.json](verification.json) | Abschlussprüfung (Reihenfolge, Läufe, Wiederholung, Schichten, Prüfsummen, Links); `all_ok` |
| [C-RESULT.md](C-RESULT.md), [MANIFEST.json](MANIFEST.json) | Abschlussnachweis und Hashes |
