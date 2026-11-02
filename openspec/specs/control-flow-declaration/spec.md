# Control flow declaration

Status: implemented · 2026-11-02. Konsolidiert aus `check-control-flow` (MILE-008); Nachweis [C-RESULT](../../../docs/10-Evidence/MILE-008/C-RESULT.md).

## Purpose

P1.13 (`binding-context/9`) deklariert exklusive und parallele Gateways mit Flüssen, Bedingungsreihenfolge und Default und bindet Spur-Aussagen an deklarierte Flüsse; `/8` bleibt unverändert.

## Requirements


### Requirement: Control flow declaration

A binding context SHALL be able to declare exclusive and parallel gateways with their incoming and outgoing flows and, for exclusive gateways, the condition order and at most one default flow; P1 SHALL reject malformed declarations and trace statements that name an undeclared flow, and SHALL leave `binding-context/8` unchanged.

#### Scenario: Routing to an undeclared flow

- **GIVEN** ein exklusives Gateway mit den Flüssen f-manual und f-auto
- **WHEN** eine Spur-Aussage den Token an einen nicht deklarierten Fluss leitet
- **THEN** meldet P1 einen Diagnosecode für die fehlende Flussbindung.

#### Scenario: Merge with a single unconditional outgoing flow

- **GIVEN** ein exklusives Merge-Gateway mit genau einem ausgehenden Fluss ohne `order`, `condition_ref` und `default`
- **WHEN** P1.13 die Deklaration prüft
- **THEN** ist sie gültig (CF-2a); ein Default-Fluss trägt dagegen weder `order` noch `condition_ref` (CF-2b).
