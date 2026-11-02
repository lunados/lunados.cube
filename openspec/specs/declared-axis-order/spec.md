# Declared axis order

Status: implemented · 2026-11-02. Konsolidiert aus `deliver-remote-and-ordered-cells` (MILE-006); Nachweis [C-RESULT](../../../docs/10-Evidence/MILE-006/C-RESULT.md).

## Purpose

VP-10 ordnet die Y × Y-Matrix nach einer deklarierten `axis_order` und kennzeichnet Einträge über der Diagonale farbfrei als Rückkopplung (`P2-VP-CELLS/0.10.1`, opt-in).

## Requirements


### Requirement: Declared axis order

A cell-state matrix SHALL order rows and columns by a declared `axis_order` when given, SHALL mark referents outside that order, and SHALL label entries above the diagonal as feedback only when an order is declared; without `axis_order` the output SHALL stay byte-identical to 0.10.0.

#### Scenario: Feedback above the diagonal

- **GIVEN** die Reihenfolge parser, resolver, validator, printer und die Abhängigkeit parser → validator
- **WHEN** die Matrix gedruckt wird
- **THEN** steht der Eintrag über der Diagonale und trägt farbfrei „Rückkopplung“.
