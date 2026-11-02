# MILE-005 TASK-036 — Wiederholung der MILE-002-Fälle als `binding-context/8`

Sieben Fälle im Runner-Format `aiaeao.cube.research-case/2`, erzeugt mit `build_rerun_cases.py`. Sie decken ARC-03, DSM-03, BPMN-03 und zur Kontrolle BPMN-02 ab.

- **Kontexte:** aus den P1.12-Vektoren K-01, K-02, K-04, K-05, K-17, K-18 und K-19.
- **Herkunft:** Matrixfall, Modell-Hash und Regeln stammen aus den ursprünglichen MILE-002-Fällen, ergänzt um die P1.12-Spezifikation.
- **Erwartung:** vor jedem Lauf festgelegt, und zwar bevor der lokale Adapter `/8` annimmt. Sie folgt dem unabhängigen Orakel (`8297b82`).

| Fall | Früher (MILE-002 / Baseline TASK-030) | Erwartet als `/8` |
|---|---|---|
| ARC-03-absence-claim-v8 | nicht ausführbar | UNRESOLVED · `P1_COVERAGE_UNDECLARED` |
| ARC-03-ctrl-full-view-v8 | PASS (Einzelaussage) | PASS (Regel abgedeckt) |
| DSM-03-empty-known-v8 | nicht ausführbar | PASS (Paar erklärt) |
| DSM-03-unknown-v8 | nicht ausführbar | UNRESOLVED · `P1_COVERAGE_UNDECLARED` |
| BPMN-03-join-cross-instance-shared-v8 | **PASS** (Instanz nur im Namen) | **FAIL · `P1_INSTANCE_MISMATCH`** |
| BPMN-03-join-cross-instance-scoped-v8 | FAIL · `P1_REFERENT_MISMATCH`, `P1_SCOPE_CONFLICT` | unverändert |
| BPMN-02-join-same-instance-v8 | PASS | PASS |

Den Lauf und seine Nachweise hält `docs/10-Evidence/MILE-005/task036-rerun/` fest.
