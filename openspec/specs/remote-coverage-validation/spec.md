# Remote coverage validation

Status: implemented · 2026-11-02. Konsolidiert aus `deliver-remote-and-ordered-cells` (MILE-006) und `deliver-remote-plan-views` (MILE-010); Nachweise [C-RESULT MILE-006](../../../docs/10-Evidence/MILE-006/C-RESULT.md), [C-RESULT MILE-010](../../../docs/10-Evidence/MILE-010/C-RESULT.md).

## Purpose

`cube_validate` im G5-Remote-Connector prüft `binding-context/8` mit dem unveränderten P1.12-Profil (seit `P3-MCP-REMOTE/0.7.0-proof`) und `binding-context/9` mit dem unveränderten P1.13-Profil (seit `0.8.0-proof`); die Remote-Discovery nennt beide.

## Requirements


### Requirement: Remote validation of binding-context/8

The remote connector SHALL validate `binding-context/8` with the unchanged P1.12 profile and SHALL return the same status and diagnostics as the local adapter.

#### Scenario: Cross-instance join remotely

- **GIVEN** der Vektor K-17 (gemeinsamer Scope, `requires_same_instance`, Instanzen i1 und i2)
- **WHEN** er über den Remote-Connector geprüft wird
- **THEN** lautet das Ergebnis FAIL mit `P1_INSTANCE_MISMATCH`, wie lokal.

### Requirement: Remote validation of binding-context/9

The remote `cube_validate` SHALL accept `aiaeao.cube.binding-context/9` through P1.13 with the same results as local G4, and the remote discovery SHALL list `/9` with entry profile `P1.13/control-flow-profile-v1`.

#### Scenario: Routing to an undeclared flow, remote

- **GIVEN** der Wiederholungsfall BPMN-01-routed-to-ship-v9 (MILE-008)
- **WHEN** er über den Remote-Connector geprüft wird
- **THEN** lautet das Ergebnis FAIL mit `P1_FLOW_UNDECLARED`, wie lokal.
