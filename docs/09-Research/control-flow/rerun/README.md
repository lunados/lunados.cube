# MILE-008 TASK-052 — Wiederholung der BPMN-Fälle als `binding-context/9`

Sieben Fälle im Runner-Format `aiaeao.cube.research-case/2`, erzeugt mit `build_rerun_cases.py`, dazu drei LIB-Prüfungen. Alle Erwartungen sind festgelegt, bevor der lokale Adapter `/9` annimmt und bevor ein Lauf stattfindet.

- **Kontexte:** aus den P1.13-Vektoren KF-01, KF-06, KF-07, KF-08, KF-09 und dem P1.12-Vektor K-17 (als `/9` ohne Kontrollfluss).
- **Erwartung:** aus dem P1.13-Orakel (`d33f22c`), dem P1.12-Orakel (`8297b82`) oder, für die Leitung an approve-auto, von Hand nach TB-1.

| Fall | Früher (MILE-002 / Baseline TASK-048) | Erwartet über `cube_validate` |
|---|---|---|
| BPMN-01-routed-v9 | PASS (Einzelaussage) | PASS (Leitung an ein Ziel des XOR) |
| BPMN-01-ctrl-other-branch-v9 | PASS | PASS (Einzelaussage gültig; zwei Pfade sind Sache der LIB) |
| BPMN-01-routed-to-ship-v9 | **PASS** (Probe) | **FAIL · `P1_FLOW_UNDECLARED`** |
| BPMN-01-token-position-v9 | PASS | UNRESOLVED · `P1_TOKEN_POSITION_UNDECLARED` |
| BPMN-02-onflow-undeclared-v9 | **PASS** (Probe) | **FAIL · `P1_FLOW_UNDECLARED`** |
| BPMN-02-join-same-instance-v8 | PASS | PASS (Regressionsschutz `/8`) |
| BPMN-03-join-cross-instance-shared-v9 | PASS bis MILE-005 | FAIL · `P1_INSTANCE_MISMATCH` (P1.12 unter `/9`) |

**LIB-Teil** (kein `cube_validate`; lunados.lib `analyze.trace-conformance/v1`, Erwartung aus CHECK-CASES.json, `aefe6aa`):

| Frage | Früher | Erwartet |
|---|---|---|
| BPMN-01-exclusivity: Nahm i1 zwei Pfade? (CF-12) | nicht ausführbar | FAIL · `exclusive_two_paths` |
| BPMN-02-sync-condition: Startete Ship für i2 ohne Lagerprüfung? (CF-22) | nicht ausführbar | FAIL · `join_incomplete`, fehlt f-stock-done |
| BPMN-02-sync-condition: Warum wartet i2? (CF-23) | nicht ausführbar | PASS · `join_waiting`, fehlt f-stock-done |

Den Lauf hält `docs/10-Evidence/MILE-008/task052-rerun/` fest.
