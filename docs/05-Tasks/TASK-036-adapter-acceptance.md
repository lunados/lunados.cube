# TASK-036 — Adapter, Wiederholung der MILE-002-Fälle und Übergabe

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/archive/2026-11-02-declare-completeness-and-instances/tasks.md).

Story: [US-020](../04-US/US-020-cell-states.md) · Mile: MILE-005-C · Aufwand: 0,75–1 PT

## Ziel und Arbeit

Profil und Printer im lokalen MCP (G4/G6) bereitstellen, G5 mit Host-Abnahme nach D-5 als eigener Folgeschritt; MILE-002-Fälle ARC-03, DSM-03, BPMN-03 erneut ausführen; Nachweise, Spec-Konsolidierung und Übergabe.

## Ergebnis und Akzeptanz

- Wiederholung mit vorab erwartetem neuem Ergebnis; Abschlussprüfung mit Hashes.
- Offene Punkte (z. B. VR-12, G-07) als Folgearbeit benannt.

## Eingaben

[Lernbilanz](../09-Research/learning-balance/LERNBILANZ.md), [Lückenbilanz](../09-Research/grammar-sampling/GAP-LEDGER.md) (G-01, G-08), [Darstellungsübergabe](../09-Research/visual-check/HANDOVER.md) (VR-05), [Probeergebnisse](../09-Research/learning-balance/PROBE-RESULTS.md).

## Abhängigkeiten und Grenze

[TASK-035](TASK-035-cell-state-printer.md)

Umfang gemäß [MILE-005](../02-Milestones/MILE-005-completeness-instances.md). P0, P1.1–P1.9 und P2 bleiben byte-gleich; neue Fähigkeiten als eigenes Profil bzw. eigener Printer-Stand.

## Ergebnis (2026-11-02)

- **Adapter (G4):** `cube_validate` leitet `binding-context/8` ausdrücklich an P1.12 weiter. Das Envelope enthält `coverage_profile` und `population_evaluation_by_cube: false`. Die lokale Discovery listet `/8` mit P1.12 (Q-6). K-01–K-21 ergeben über den Adapter dieselben Ergebnisse wie das Orakel (`bede236`).
- **Plan-Sichten (G6):** Drucker `vpcells` mit `predicate`, Sicht `cube.cells` und `cube_plan_check`. Die gesamte Adapter-Suite läuft grün (226 Tests). Die G5-Offline-Prüfung ist unverändert PASS; G5 selbst bleibt nach D-5 Folgeschritt.
- **Wiederholung der MILE-002-Fälle:** sieben Fälle (ARC-03, DSM-03, BPMN-03, Kontrolle BPMN-02) als `/8`, Erwartung vor dem Lauf (`1250feb`). Lauf über echtes lokales MCP stdio mit zwei frischen Verbindungen: 7/7 wie erwartet, Readiness bestanden. BPMN-03 im gemeinsamen Scope: Baseline PASS → jetzt FAIL `P1_INSTANCE_MISMATCH`. Der Scope-Fall ist unverändert. ARC-03 und DSM-03 sind jetzt ausführbar und unterscheiden „abgedeckt“ von „nicht abgedeckt“ ([Fälle](../09-Research/completeness-instances/rerun/README.md), [Lauf](../10-Evidence/MILE-005/task036-rerun/report.json)).
- **Abschlussprüfung:** [verify_mile005.py](../10-Evidence/MILE-005/verify_mile005.py) → [verification.json](../10-Evidence/MILE-005/verification.json), `all_ok`; Hashes in [MANIFEST.json](../10-Evidence/MILE-005/MANIFEST.json).
- **Übergabe und Folgearbeit:** [HANDOVER](../09-Research/completeness-instances/HANDOVER.md) mit G5 und Host-Abnahme, Menschentest, PO-5, PO-7, VR-12 und G-07.
