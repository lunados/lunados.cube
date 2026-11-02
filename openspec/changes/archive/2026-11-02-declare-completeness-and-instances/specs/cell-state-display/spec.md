# Cell state display

Status: implemented · 2026-11-02.

## ADDED Requirements

### Requirement: Four cell states

A matrix view SHALL distinguish marked, checked empty (only within a declared scope), unknown and hidden cells without relying on colour, and SHALL name hidden elements; the existing VP-09 printer SHALL remain byte-identical.

#### Scenario: Unknown cell next to a checked-empty cell

- **GIVEN** eine Zeile mit einer erklärten leeren Zelle und einer nicht erhobenen Zelle
- **WHEN** die Matrix gedruckt wird
- **THEN** sind beide Zellen farbfrei unterscheidbar, und nur die erklärte Zelle trägt „geprüft“.
