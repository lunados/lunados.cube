# TASK-065 — Profil P1.14 und G4

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/declare-relation-origin/tasks.md).

Story: [US-032](../04-US/US-032-relation-origin-profile.md) · Mile: MILE-011-B · Aufwand: 1–1,5 PT

## Ziel und Arbeit

Profil `P1/relation-origin-profile-v1` (P1.14): Schema `binding-context/10`, Parametervertrag `origin`, Grundlage (Quellaussagen oder `project.aggregate-relations/v1`-Datensatz, gelesen), Diagnosen, Regelabdeckung, materialisierte Vektoren, Tests, Golden; lokaler Adapter G4 mit `/10` und Discovery.

## Ergebnis und Akzeptanz

- Alle Prüffälle wie das Orakel; P1.1–P1.13 und ihre Paritäten unverändert.

## Abhängigkeiten und Grenze

[TASK-064](TASK-064-origin-cases.md)

Umfang gemäß [MILE-011](../02-Milestones/MILE-011-relation-origin.md). P0, P1.1–P1.13, VP-07 0.7.0–0.7.5, VP-10, VP-11 und vorhandene lunados.lib-Einträge bleiben byte-gleich.
