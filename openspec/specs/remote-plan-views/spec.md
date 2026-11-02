# Remote plan views

Status: implemented · 2026-11-02. Konsolidiert aus `deliver-remote-plan-views` (MILE-010); Nachweis [C-RESULT](../../../docs/10-Evidence/MILE-010/C-RESULT.md).

## Purpose

Der G5-Remote-Connector (`P3-MCP-REMOTE/0.8.0-proof`, Gateway `0.2.0-proof`) bietet `cube_plan_source`, `cube_plan_views` und `cube_plan_check` mit den Printern VP-07 bis VP-11, byte-gleich zu den lokalen G6-Tools. Grenze: ein Aufruf über der CPU-Grenze des Workers endet mit `G5_CORE_UNAVAILABLE` (`isError`), nie mit einem anderen oder gekürzten Ergebnis ([Spezifikation §10](../../../P3/remote-mcp-g5/G5_R5_ACCEPTANCE_SPEC.md)).

## Requirements


### Requirement: Remote plan views

The remote connector SHALL offer `cube_plan_source`, `cube_plan_views` and `cube_plan_check` with the same arguments, limits and error codes as the local G6 tools, SHALL return byte-identical SVGs, reports and diagnostics for the same inputs, and SHALL never truncate an output over a limit.

#### Scenario: Instance view remote equals local

- **GIVEN** der VP-11-Vektor I-22 (BPMN-02, zwei Instanzen, sechs Datensätze)
- **WHEN** er über den Remote-Connector mit der Sicht `cube.instances` gedruckt wird
- **THEN** gleicht der SVG-Digest dem lokalen G6-Digest, und `cube_plan_check` liefert PASS.
