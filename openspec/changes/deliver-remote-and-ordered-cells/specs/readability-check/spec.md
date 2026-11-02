# Readability check

Status: planned. Revised 2026-11-02 (D-6): a short guided visual check instead of a readability test with several people.

## ADDED Requirements

### Requirement: Short guided visual check

The visual check SHALL use synthetic renders only, SHALL give the reviewer a short guide with yes/no check points, and SHALL resolve every "no" by a fix or by naming it as open. It SHALL NOT claim a statistical finding.

#### Scenario: Unknown versus checked empty

- **GIVEN** a matrix with a checked-empty and an unknown cell in the same row
- **WHEN** the reviewer answers the check point "hatching reads as not surveyed, the bold border as checked and none found"
- **THEN** a "no" leads to a fix of the render or legend, or to an open item in the task result.
