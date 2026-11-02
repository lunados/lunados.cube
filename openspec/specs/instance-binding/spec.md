# Instance binding

Status: implemented · 2026-11-02. Konsolidiert aus `declare-completeness-and-instances` (MILE-005); Nachweis [C-RESULT](../../../docs/10-Evidence/MILE-005/C-RESULT.md).

## Purpose

Spur-Aussagen typisiert einer Instanz zuordnen (`instance_ref`, `requires_same_instance`), damit instanzübergreifende Paarungen auch im gemeinsamen Scope erkannt werden (P1.12).

## Requirements

### Requirement: Typed instance membership

Trace statements SHALL carry a typed instance membership (per decision D-4: typed `instance_ref`), and a join SHALL be rejected when its inputs belong to different instances, also within a shared scope.

#### Scenario: Cross-instance join in a shared scope

- **GIVEN** ein gemeinsamer Scope für die ganze Spur und ein Join, der i1/tok-stock mit i2/tok-credit paart
- **WHEN** die Aussage geprüft wird
- **THEN** wird der instanzübergreifende Join erkannt (BPMN-03 shared, bisher PASS).
