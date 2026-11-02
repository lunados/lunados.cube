# TASK-052 — Prüfung der Fremdumsetzung TASK-050 und TASK-051

Stand: 2026-11-02 · Prüfer: Claude (TASK-052) · Umsetzung: TASK-050 durch ChatGPT „SOL“, TASK-051 durch ChatGPT „Astra“ (laut Nutzer)

## Geprüfter Stand

| Repo | Branch | Commits |
|---|---|---|
| lunados.cube | `feature/mile008-control-flow` | `d33f22c` Orakel KF-01–KF-09 · `9222424` P1.13 · `6291655`, `82846fe` Nachweis TASK-051 |
| lunados.lib | `codex/task-051-trace-conformance` | `ebb3110` Fälle, Schema, Orakel · `d823a4a` Evaluator, Eintrag, INDEX · `5511574` Korrektur Merge ohne `order` |

## Ergebnis

**Bestanden, mit sechs Befunden ohne Blocker.** Alle Läufe am 2026-11-02 auf dem Gerät des Nutzers wiederholt.

| Prüfung | Ergebnis |
|---|---|
| Orakel KF-01–KF-09 vor dem Profilcode (`d33f22c` vor `9222424`); Orakel nennt die SHA-256 von CHECK-CASES.json und der Spezifikation nach Q-Auflösung (`1874b7b`), beide stimmen | erfüllt |
| `run_vectors.py` P1.13: 9/9; `test_p113.py`: 18/18 | erfüllt |
| Alle früheren P1-Suiten (10 Testdateien, 6 weitere Vektorläufe) grün; P0 und P1.1–P1.12 seit `main` unverändert; alle P0/P1-SHA256SUMS halten | erfüllt |
| Eigene Proben außerhalb der Vektoren: `control_flow` bzw. `at_gateway` in `/8` → Konfigurationsfehler; Fluss als Ausgang zweier Gateways → FAIL `CONTROL_FLOW_INVALID`; Leitung von einem parallelen Gateway → FAIL `FLOW_UNDECLARED`; bedingter Ausgang ohne `order` → FAIL; Prädikat aus fremdem Scope → P1.1 lehnt ab | wie Spezifikation |
| LIB: Fälle, Schema und Orakel vor dem Evaluator (`ebb3110` vor `d823a4a`); `preregistered_expected` aller 18 Fälle gleich `expected_with_profile` aus CHECK-CASES.json; Erwartungen seit `ebb3110` unverändert | erfüllt |
| `verify.py --cube`: 13 Einträge, 159/159 (Cube-Referenzfall PASS); `differential_trace.py`: 471 Vergleiche, 18 Projektionen, 9 Ablehnungen; bestehende LIB-Einträge unverändert | erfüllt |

## Befunde

1. **Lücke in meiner Spezifikation (CF-2).** Wörtlich verlangt CF-2 ein `order` für jeden Nicht-Default-Ausgang eines exklusiven Gateways. Das Merge-Gateway der Prüffälle hat genau einen unbedingten Ausgang ohne `order`; KF-01 und CF-29 erwarten PASS. Beide Umsetzungen lassen einen einzelnen unbedingten Ausgang ohne `order` zu — konsistent mit den Fällen. Wird als Präzisierung in §8 der Spezifikation nachgetragen.
2. **Strenger als die Spezifikation:** P1.13 und LIB lehnen `condition_ref` am Default ab (die Spezifikation verbietet dort nur `order`). Konsistent in beiden; wird als Präzisierung nachgetragen.
3. **Orakel nach dem Evaluator geändert (LIB, `5511574`).** Eine Zeile Sortierschlüssel in Orakel und Evaluator sowie das künstliche `order` am Merge-Ausgang in allen 18 Falleingaben wurden nach dem Evaluator korrigiert. Die Erwartungen blieben unverändert, die Änderung ist in `TASK-051-LIB.md` offengelegt. Abweichung vom Ablauf „Orakel vor Code, danach unverändert“, ohne Einfluss auf das Ergebnis.
4. **Zeitabstand Orakel → Code (P1.13):** 31 Sekunden zwischen `d33f22c` und `9222424`. Die Reihenfolge ist formal eingehalten; die Unabhängigkeit ist aus der Historie nicht belegbar.
5. **Dokumentationslücken:** TASK-050 ohne Ergebnisabschnitt und ohne Laufprotokoll unter `docs/10-Evidence/MILE-008/`; Milestone-Nachverfolgung ohne TASK-050/051; lunados.lib-README ohne Zeile für den neuen Eintrag; `TASK-051-LIB.md` nennt einen absoluten lokalen Pfad. Werden in TASK-052 nachgezogen.
6. **Commits ohne Co-Author-Zeile:** Die Fremdcommits tragen die Nutzeridentität, aber keine Angabe zum ausführenden Agenten. Nur zur Nachvollziehbarkeit festgehalten.

## Offen in TASK-052

`/9` im lokalen `cube_validate` und Discovery; Wiederholung der BPMN-Fälle mit vorab committeter Erwartung; Abschlussprüfung, C-RESULT, Specs, Archiv.
