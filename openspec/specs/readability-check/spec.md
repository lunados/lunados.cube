# Readability check

Status: implemented · 2026-11-02. Konsolidiert aus `deliver-remote-and-ordered-cells` (MILE-006); Nachweis [C-RESULT](../../../docs/10-Evidence/MILE-006/C-RESULT.md).

## Purpose

Darstellungsänderungen werden mit einer kurzen, angeleiteten Sichtprüfung gesichtet; jedes „nein“ wird behoben oder als offen benannt.

## Requirements


### Requirement: Short guided visual check

The visual check SHALL use synthetic renders only, SHALL give the reviewer a short guide with yes/no check points, and SHALL resolve every "no" by a fix or by naming it as open. It SHALL NOT claim a statistical finding.

#### Scenario: Unknown versus checked empty

- **GIVEN** a matrix with a checked-empty and an unknown cell in the same row
- **WHEN** the reviewer answers the check point "hatching reads as not surveyed, the bold border as checked and none found"
- **THEN** a "no" leads to a fix of the render or legend, or to an open item in the task result.
