# TASK-032 — Entscheidungen auflösen

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/archive/2026-11-02-declare-completeness-and-instances/tasks.md).

Story: [US-018](../04-US/US-018-completeness.md) · Mile: MILE-005-A · Aufwand: 0,25 PT

## Ziel und Arbeit

Die Entscheidungen O-1 bis O-6 mit dem Nutzer klären und als eigenen Docs-Commit festhalten; Spezifikation auf „decided“ setzen.

## Ergebnis und Akzeptanz

- Entscheidungs-Commit vor jeder Implementierung.
- Jede Entscheidung mit Grund; abgelehnte Optionen bleiben dokumentiert.

## Eingaben

[Lernbilanz](../09-Research/learning-balance/LERNBILANZ.md), [Lückenbilanz](../09-Research/grammar-sampling/GAP-LEDGER.md) (G-01, G-08), [Darstellungsübergabe](../09-Research/visual-check/HANDOVER.md) (VR-05), [Probeergebnisse](../09-Research/learning-balance/PROBE-RESULTS.md).

## Abhängigkeiten und Grenze

[TASK-031](TASK-031-acceptance-spec.md)

Umfang gemäß [MILE-005](../02-Milestones/MILE-005-completeness-instances.md). P0, P1.1–P1.9 und P2 bleiben byte-gleich; neue Fähigkeiten als eigenes Profil bzw. eigener Printer-Stand. Ausführungsnachweis siehe Ergebnis.

## Ergebnis

Vorgezogen und erledigt am 2026-11-01, vor TASK-030/031 und vor jeder Implementierung, als eigener Docs-Commit. Der Nutzer hat nach Erörterung alle Empfehlungen übernommen: D-1 ein Profil (P1.12, `binding-context/8`), D-2 Umfang Referent × Relationstyp × Richtung plus je Paar, D-3 UNRESOLVED mit eigenem Diagnosecode, D-4 typisierte `instance_ref` mit „gleiche Instanz verlangt“, D-5 lokal, G5 später, D-6 Profil erklärt, LIB zählt. Tabelle mit Gründen und nicht gewählten Optionen im [Milestone](../02-Milestones/MILE-005-completeness-instances.md). TASK-031 übernimmt die Entscheidungen als „decided“.

Ergänzung 2026-11-01: Die Detailfragen Q-1–Q-6 der [Abnahmespezifikation P1.12](../../P1/coverage-instance-profile-v1/P1_12_ACCEPTANCE_SPEC.md) wurden vom Nutzer nach Vorschlag entschieden und in einem eigenen Docs-Commit festgehalten; die Spezifikation steht auf SPECIFIED, bereit für die Implementierung.
