# Instance binding

Status: planned.

## ADDED Requirements

### Requirement: Typed instance membership

Trace statements SHALL carry a typed instance membership (per decision D-4: typed `instance_ref`), and a join SHALL be rejected when its inputs belong to different instances, also within a shared scope.

#### Scenario: Cross-instance join in a shared scope

- **GIVEN** ein gemeinsamer Scope für die ganze Spur und ein Join, der i1/tok-stock mit i2/tok-credit paart
- **WHEN** die Aussage geprüft wird
- **THEN** wird der instanzübergreifende Join erkannt (BPMN-03 shared, bisher PASS).
