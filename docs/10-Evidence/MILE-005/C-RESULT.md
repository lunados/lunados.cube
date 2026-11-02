# MILE-005 — Abschlussnachweis (TASK-036)

Stand: 2026-11-02 · Branch `feature/mile005-completeness-instances` (lunados.cube), `feature/analyze-population` (lunados.lib) · Prüfung: [verification.json](verification.json), Skript [verify_mile005.py](verify_mile005.py) · Hashes: [MANIFEST.json](MANIFEST.json)

## Prüfung

| Kriterium | Ergebnis |
|---|---|
| Prüffälle vor der Spezifikation (`52cc773` vor `26c32b6`), P1.12-Orakel vor dem Profilcode (`8297b82` vor `4c05b5b`), VP-10-Orakel vor dem Printercode (`2316f45` vor `639e6c0`), LIB-Orakel und Fälle vor dem Evaluator (`33ce6c3` vor `c649931`), Wiederholungserwartung vor dem `/8`-Adapter (`1250feb` vor `bede236`) | erfüllt |
| Erwartungen seitdem unverändert; VP-10 J-12 nur in der Aufrufbeschreibung vor dem Code korrigiert, die erwarteten Zustände sind gleich | erfüllt |
| P1.12 K-01–K-21 21/21, 29 Tests; P1.11 F-Vektoren 16/16; alle P1-Testsuiten grün | erfüllt |
| lunados.lib `verify.py --cube`: 127/127, CC-01–CC-16 16/16 | erfüllt |
| VP-10 J-01–J-14 14/14, 24 Tests; Adapter-Tests (P1.12 über `cube_validate`, Discovery, G6 `cube.cells`) grün; gesamte Adapter-Suite 226 | erfüllt |
| Wiederholung der MILE-002-Fälle über lokales MCP stdio: 7/7 wie erwartet, zwei frische Verbindungen, Readiness bestanden | erfüllt |
| P0, P1.1–P1.11, P2 (außer dem neuen VP-10) seit `main` unverändert; alle Prüfsummenlisten halten (P3 Charge-3-Schnappschuss historisch, schon vorher veraltet) | erfüllt |
| Relative Links in docs/, openspec/ und den neuen Paketen | keine kaputten |

## Chargen

| Mile | Abschlusskriterium | Nachweis |
|---|---|---|
| MILE-005-A | Prüffälle mit Erwartung vor Code; Spezifikation und Entscheidungen | [CHECK-CASES](../../09-Research/completeness-instances/CHECK-CASES.md), [Baseline](task030-baseline-check.json), [P1.12-Spezifikation](../../../P1/coverage-instance-profile-v1/P1_12_ACCEPTANCE_SPEC.md) |
| MILE-005-B | Orakel vor Code; alle Vektoren und Prüffälle wie erwartet; P0/P1.1–P1.11 unverändert | [P1.12](../../../P1/coverage-instance-profile-v1/README.md), [Lauf TASK-033](task033-run.json), [Lauf TASK-034](task034-run.json) |
| MILE-005-C | Printer-Abnahme nach Spezifikation; ARC-03, DSM-03, BPMN-03 mit neuem, vorab erwartetem Ergebnis | [VP-10](../../../P2/visual-printer-cells-v1/README.md), [Lauf TASK-035](task035-run.json), [Wiederholung](task036-rerun/report.json), [Übergabe](../../09-Research/completeness-instances/HANDOVER.md) |

## Ergebnis

| Fall | Baseline (TASK-030) | Jetzt (`/8`) |
|---|---|---|
| ARC-03 Abwesenheit, Service-Sicht | nicht ausführbar | UNRESOLVED · `P1_COVERAGE_UNDECLARED` |
| ARC-03 Vollsicht, Regel abgedeckt | nicht ausführbar | PASS |
| DSM-03 Paar erklärt | nicht ausführbar | PASS |
| DSM-03 Paar außerhalb der Erklärung | nicht ausführbar | UNRESOLVED · `P1_COVERAGE_UNDECLARED` |
| BPMN-03 gemeinsamer Scope | **PASS** | **FAIL · `P1_INSTANCE_MISMATCH`** |
| BPMN-03 Scope je Instanz | FAIL · `P1_REFERENT_MISMATCH`, `P1_SCOPE_CONFLICT` | unverändert |
| BPMN-02 gleiche Instanz | PASS | PASS |

Die Auswertung über Aussagenmengen liefert lunados.lib: absent_checked, absence_contradicted, within_bounds, out_of_bounds, join_enabled, join_not_enabled und coverage_undeclared, jeweils typisiert als `aiaeao.population-result/v1`. VP-10 zeigt die vier Zellzustände.

## Grenzen

- Alles lokal. G5 und Host-Abnahme sind nach D-5 ein eigener Folgeschritt.
- Kein Menschentest der Darstellung.
- Orakel, Evaluator und Printer stammen vom selben Autor; die Übereinstimmung ist eine Kontrolle auf Implementierungsunterschiede.
- Alle Fälle sind synthetisch, ohne Kundendaten.
