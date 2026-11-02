# TASK-052 — Wiederholung der BPMN-Fälle als `binding-context/9`

- **Datum:** 2026-11-02
- **Code:** lokaler Adapter mit `/9` (`70d0469`), P1.13 (`9222424`), lunados.lib `analyze.trace-conformance/v1` (`5511574`, README `f9dfb20`).
- **Eingabe:** sieben Fälle in `docs/09-Research/control-flow/rerun/cases`, Erwartung vor dem Adapter festgelegt (`76e5ac1`); drei LIB-Fälle CF-12, CF-22, CF-23 mit Erwartung aus CHECK-CASES.json (`aefe6aa`). Synthetisch, keine Kundendaten.
- **Aufruf:** `scripts/research/comparison_runner.py` über lokales MCP stdio, zwei frische Verbindungen; `lib_part.py` mit dem gepinnten LIB-Evaluator.
- **Aussagegrenze:** P1 prüft Deklaration und Einzelaussagen; die Spurprüfung je Instanz ist eine LIB-Auswertung über deklarierte Spuren, keine Prozessausführung.

| Fall | Früher | Jetzt | Wie erwartet |
|---|---|---|---|
| BPMN-01-routed-v9 | PASS | PASS | ja |
| BPMN-01-ctrl-other-branch-v9 | PASS | PASS (Einzelaussage gültig) | ja |
| BPMN-01-routed-to-ship-v9 | **PASS** | **FAIL · `P1_FLOW_UNDECLARED`** | ja |
| BPMN-01-token-position-v9 | PASS | UNRESOLVED · `P1_TOKEN_POSITION_UNDECLARED` | ja |
| BPMN-02-onflow-undeclared-v9 | **PASS** | **FAIL · `P1_FLOW_UNDECLARED`** | ja |
| BPMN-02-join-same-instance-v8 | PASS | PASS | ja |
| BPMN-03-join-cross-instance-shared-v9 | PASS bis MILE-005 | FAIL · `P1_INSTANCE_MISMATCH` | ja |
| BPMN-01-exclusivity (LIB, CF-12) | nicht ausführbar | **FAIL · `exclusive_two_paths`** | ja |
| BPMN-02-sync-condition (LIB, CF-22) | nicht ausführbar | **FAIL · `join_incomplete`**, fehlt f-stock-done | ja |
| BPMN-02-sync-condition (LIB, CF-23) | nicht ausführbar | **PASS · `join_waiting`**, fehlt f-stock-done | ja |

[report.json](report.json) (7 Fälle × 2 Verbindungen, Readiness bestanden) · [lib-part.json](lib-part.json) (3/3).
