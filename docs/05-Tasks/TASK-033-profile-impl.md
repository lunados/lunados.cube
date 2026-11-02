# TASK-033 — P1-Profil implementieren

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/archive/2026-11-02-declare-completeness-and-instances/tasks.md).

Story: [US-018](../04-US/US-018-completeness.md), [US-019](../04-US/US-019-instance-binding.md) · Mile: MILE-005-B · Aufwand: 1,5–2,5 PT

## Ziel und Arbeit

Profil nach Spezifikation: Schema (`binding-context/8`, D-1), Diagnosen, Regelabdeckung, Orakel vor Code, materialisierte Vektoren, Tests, Golden. Erklärungsumfang nach D-2, Instanzbindung nach D-4, Status nach D-3.

## Ergebnis und Akzeptanz

- Alle Vektoren und Prüffälle aus TASK-030 wie erwartet; P0 und P1.1–P1.9 byte-gleich.
- Unvollständige Erklärung nie FAIL.

## Eingaben

[Lernbilanz](../09-Research/learning-balance/LERNBILANZ.md), [Lückenbilanz](../09-Research/grammar-sampling/GAP-LEDGER.md) (G-01, G-08), [Darstellungsübergabe](../09-Research/visual-check/HANDOVER.md) (VR-05), [Probeergebnisse](../09-Research/learning-balance/PROBE-RESULTS.md).

## Abhängigkeiten und Grenze

[TASK-032](TASK-032-resolve-decisions.md)

Umfang gemäß [MILE-005](../02-Milestones/MILE-005-completeness-instances.md). P0, P1.1–P1.9 und P2 bleiben byte-gleich; neue Fähigkeiten als eigenes Profil bzw. eigener Printer-Stand.

## Ergebnis (2026-11-01)

Umgesetzt in [`P1/coverage-instance-profile-v1/`](../../P1/coverage-instance-profile-v1/README.md), Commit `4c05b5b`; Orakel vorab `8297b82`.

- K-01–K-21: 21/21 gegen das unabhängige Orakel, im ersten Lauf. Die fünf Fälle ohne Abdeckung ergeben UNRESOLVED `P1_COVERAGE_UNDECLARED`, nie FAIL. BPMN-03 im gemeinsamen Scope ergibt jetzt FAIL `P1_INSTANCE_MISMATCH` (K-17). Der Scope-pro-Instanz-Fall bleibt unverändert (K-18).
- 28 Tests grün. Die Vektorsuiten M, C, G und F sowie das P1.11-Golden sind byte-gleich zu P1.11. Die Testsuiten P1.1–P1.11 laufen unverändert, `SHA256SUMS` P0/P1 halten.
- Abweichung von der Übersetzung: K-01 und K-09 haben im Prüffall keine Aussage und tragen deshalb eine neutrale `composedOf`-Aussage desselben Modells.
- Nachweis: [task033-run.json](../10-Evidence/MILE-005/task033-run.json).

Offen bleiben die LIB-Auswertung (TASK-034), die Darstellung (TASK-035) sowie Adapter und Discovery (TASK-036).
