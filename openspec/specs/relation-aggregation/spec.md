# Relation aggregation

Status: implemented · 2026-11-02. Konsolidiert aus `project-statement-sets` (MILE-007); Nachweis [C-RESULT](../../../docs/10-Evidence/MILE-007/C-RESULT.md).

## Purpose

lunados.lib `project.aggregate-relations/v1` verdichtet mit Pflichtstrategie, vollständiger Quellenspur und Verlustbericht; der Cube liest das Ergebnis als Datensatz und rechnet nicht nach.

## Requirements


### Requirement: Relation aggregation with source trace

An aggregation SHALL take its strategy as a required parameter, SHALL list every source statement of each derived statement, SHALL report suppressed and internal sources and the loss counts, and SHALL be computed outside the Cube; the Cube SHALL only read and display the typed result.

#### Scenario: Two sources to one container relation

- **GIVEN** Order Controller → Database und Order Repository → Database, beide Komponenten im Container API, und die Strategie `all`
- **WHEN** auf Container verdichtet wird
- **THEN** entsteht eine abgeleitete Aussage API → Database mit beiden Quellen, die Matrix zeigt „abgeleitet · 2 Quellen“, und die interne Beziehung Order Controller → Order Repository ist als intern ausgewiesen.
