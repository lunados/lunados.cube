# TASK-065 — Profil P1.14 und G4

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/archive/2026-11-02-declare-relation-origin/tasks.md).

Story: [US-032](../04-US/US-032-relation-origin-profile.md) · Mile: MILE-011-B · Aufwand: 1–1,5 PT

## Ziel und Arbeit

Profil `P1/relation-origin-profile-v1` (P1.14): Schema `binding-context/10`, Parametervertrag `origin`, Grundlage (Quellaussagen oder `project.aggregate-relations/v1`-Datensatz, gelesen), Diagnosen, Regelabdeckung, materialisierte Vektoren, Tests, Golden; lokaler Adapter G4 mit `/10` und Discovery.

## Ergebnis und Akzeptanz

- Alle Prüffälle wie das Orakel; P1.1–P1.13 und ihre Paritäten unverändert.

## Ergebnis (2026-11-02)

P1.14 ist lokal umgesetzt: `/10`-Kontextschema, Herkunft und Grundlagenvertrag, additive Diagnosen, Regelabdeckung, zwölf HO-Vektoren gegen das unabhängige Orakel, synthetisches Golden und `statement-set/2`-Schema. G4 akzeptiert `/10`; die lokale Discovery nennt das Profil und die drei neuen Diagnosen.

HO-12 wurde im Materialisierungsskript korrigiert: Das P1.10-Profil wird für diesen Vektor als gleichwertige lokale Verträge materialisiert, damit `sends-via` ausdrücklich `origin_binding` tragen kann. Das vor Code festgelegte Orakel und die P1.13-Baseline-Ergebnisse bleiben unverändert.

Prüfung: P1.14 11/11, P1.13 18/18 und vollständige lokale MCP-Adapter-Suite 250/250 Tests bestanden. G5 und Printer sind Gegenstand von TASK-066/067.

## Abhängigkeiten und Grenze

[TASK-064](TASK-064-origin-cases.md)

Umfang gemäß [MILE-011](../02-Milestones/MILE-011-relation-origin.md). P0, P1.1–P1.13, VP-07 0.7.0–0.7.5, VP-10, VP-11 und vorhandene lunados.lib-Einträge bleiben byte-gleich.
