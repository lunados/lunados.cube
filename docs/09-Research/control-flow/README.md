# MILE-008 — Kontrollfluss und Spurkonformität (Research)

Stand: 2026-11-02 · [Milestone](../../02-Milestones/MILE-008-control-flow.md)

| Datei | Inhalt |
|---|---|
| [CHECK-CASES.md](CHECK-CASES.md), [CHECK-CASES.json](CHECK-CASES.json) | TASK-048: 27 formatneutrale Prüffälle (9 P1, 18 LIB), Erwartung heute und mit Profil, vor der Spezifikation (`aefe6aa`) |
| [build_check_cases.py](build_check_cases.py) | erzeugt beide Dateien deterministisch; alle Erwartungen von Hand |
| [Baseline-Lauf](../../10-Evidence/MILE-008/task048-baseline-report.json), [Abgleich](../../10-Evidence/MILE-008/task048-baseline-check.json) | sechs MILE-002-Fälle mit dem unveränderten Runner, zwei Verbindungen; Probe für CF-06/CF-07 mit dem unveränderten P1.12-Adapter; 27/27 Erwartungen für heute bestätigt |
