# Local discovery accuracy

Status: implemented · 2026-11-01. Consolidated from the completed preparation change.

## Purpose

Additive local-only domains.P1.validation_contexts, format aiaeao.cube.local-validation-discovery/1. It records explicit dispatch profiles and file presence; runtime_load_verified remains false. Legacy/G4 responses remain unchanged.

## Requirements

### Requirement: Accurate local validation discovery

The local discovery surface SHALL describe supported validation context/profile versions consistently with the implemented local dispatch, distinguish documentary and operational roles, and preserve explicit limits on truth, execution and authority claims.

#### Scenario: Local analysis session discovers validation support

- **GIVEN** eine frische lokale stdio-MCP-Verbindung mit dokumentiertem Code-/Adapterstand
- **WHEN** Discovery und Toolbeschreibung gelesen werden
- **THEN** lassen sich die tatsächlich unterstützten lokalen Kontexte mit der Implementierung abgleichen
- **AND** die öffentliche Lesereferenz ist keine Quelle für behauptete Validatorausführung.

### Requirement: Preserve legacy discovery compatibility

The local metadata extension SHALL preserve the protected legacy printer capability response and G4 discovery response and SHALL NOT assert deployment or parity of remote G5 changes.

#### Scenario: Additive local metadata extension

- **GIVEN** vor der Änderung fixierte geschützte Legacy-/G4-Ausgaben
- **WHEN** die lokale Discovery präzisiert wird
- **THEN** bleiben diese Alt-Ausgaben unverändert
- **AND** neue lokale Angaben sind auf den lokalen Discovery-Pfad begrenzt.


## Verification

[Milestone evidence](../../../docs/10-Evidence/MILE-001/C-RESULT.md). Scope and untested claims remain explicit.
