# Completeness declaration

Status: implemented · 2026-11-02.

## ADDED Requirements

### Requirement: Declared completeness scope

A context SHALL be able to declare for which scope (per decision D-2: referent × relation type × direction, or a single pair) the statements of a relation type are completely surveyed, and validation SHALL treat absence as "checked empty" only inside a declared scope.

#### Scenario: Absence outside the declared scope

- **GIVEN** eine Erklärung, die das Paar (printer, parser) als erhoben ausweist, aber nicht (printer, resolver)
- **WHEN** nach einer Abhängigkeit printer → resolver gefragt wird
- **THEN** lautet das Ergebnis unbekannt (UNRESOLVED nach D-3), nicht „keine“.

### Requirement: Population check over declared scope

The study SHALL count statements only over a declared scope and SHALL NOT report FAIL when the declaration is incomplete.

#### Scenario: Count rule with incomplete declaration

- **GIVEN** eine Zählregel „genau einer je Aktivierung“ und eine unvollständige Erklärung
- **WHEN** die Population geprüft wird
- **THEN** ist das Ergebnis UNRESOLVED (D-3) mit benanntem fehlenden Umfang.
