# Remote plan views

Status: planned.

## ADDED Requirements

### Requirement: Remote plan views

The remote connector SHALL offer `cube_plan_source`, `cube_plan_views` and `cube_plan_check` with the same arguments, limits and error codes as the local G6 tools, SHALL return byte-identical SVGs, reports and diagnostics for the same inputs, and SHALL never truncate an output over a limit.

#### Scenario: Instance view remote equals local

- **GIVEN** the VP-11 vector I-22 (BPMN-02, two instances, six records)
- **WHEN** it is printed through the remote connector with view `cube.instances`
- **THEN** the SVG digest equals the local G6 digest and `cube_plan_check` returns PASS.
