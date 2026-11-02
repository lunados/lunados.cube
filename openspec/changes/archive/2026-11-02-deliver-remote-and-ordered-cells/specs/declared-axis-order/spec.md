# Declared axis order

Status: implemented · 2026-11-02.

## ADDED Requirements

### Requirement: Declared axis order

A cell-state matrix SHALL order rows and columns by a declared `axis_order` when given, SHALL mark referents outside that order, and SHALL label entries above the diagonal as feedback only when an order is declared; without `axis_order` the output SHALL stay byte-identical to 0.10.0.

#### Scenario: Feedback above the diagonal

- **GIVEN** die Reihenfolge parser, resolver, validator, printer und die Abhängigkeit parser → validator
- **WHEN** die Matrix gedruckt wird
- **THEN** steht der Eintrag über der Diagonale und trägt farbfrei „Rückkopplung“.
