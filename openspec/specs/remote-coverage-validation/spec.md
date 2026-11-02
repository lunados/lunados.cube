# Remote coverage validation

Status: implemented · 2026-11-02. Konsolidiert aus `deliver-remote-and-ordered-cells` (MILE-006); Nachweis [C-RESULT](../../../docs/10-Evidence/MILE-006/C-RESULT.md).

## Purpose

`cube_validate` im G5-Remote-Connector prüft `binding-context/8` mit dem unveränderten P1.12-Profil (`P3-MCP-REMOTE/0.7.0-proof`).

## Requirements


### Requirement: Remote validation of binding-context/8

The remote connector SHALL validate `binding-context/8` with the unchanged P1.12 profile and SHALL return the same status and diagnostics as the local adapter.

#### Scenario: Cross-instance join remotely

- **GIVEN** der Vektor K-17 (gemeinsamer Scope, `requires_same_instance`, Instanzen i1 und i2)
- **WHEN** er über den Remote-Connector geprüft wird
- **THEN** lautet das Ergebnis FAIL mit `P1_INSTANCE_MISMATCH`, wie lokal.
