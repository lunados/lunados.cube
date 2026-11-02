# Remote coverage validation

Status: planned.

## MODIFIED Requirements

### Requirement: Remote validation of binding-context/9

The remote `cube_validate` SHALL accept `aiaeao.cube.binding-context/9` through P1.13 with the same results as local G4, and the remote discovery SHALL list `/9` with entry profile `P1.13/control-flow-profile-v1`.

#### Scenario: Routing to an undeclared flow, remote

- **GIVEN** the re-run case BPMN-01-routed-to-ship-v9 (MILE-008)
- **WHEN** it is validated through the remote connector
- **THEN** the result is FAIL with `P1_FLOW_UNDECLARED`, as locally.
