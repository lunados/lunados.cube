# Statement set display

Status: implemented · 2026-11-02.

## ADDED Requirements

### Requirement: Statement set display

A cell matrix SHALL read a declared statement set for a binding context without a migration plan, SHALL resolve every referent and predicate against that context and reject unresolved ones, SHALL read rows as subjects and columns as objects, and SHALL leave the 0.10.x outputs byte-identical.

#### Scenario: DSM without a plan

- **GIVEN** die Module aus DSM-01 als Referenten und ihre `dependsOn`-Aussagen als Aussagenmenge
- **WHEN** `cube.cells` 0.11.0 die Menge druckt
- **THEN** stehen die Einträge in den Zellen Subjekt × Objekt mit dem Prädikat `dependsOn`, ohne Migrationsvokabular in Titel oder Legende.
