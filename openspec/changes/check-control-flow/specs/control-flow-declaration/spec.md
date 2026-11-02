# Control flow declaration

Status: planned.

## ADDED Requirements

### Requirement: Control flow declaration

A binding context SHALL be able to declare exclusive and parallel gateways with their incoming and outgoing flows and, for exclusive gateways, the condition order and at most one default flow; P1 SHALL reject malformed declarations and trace statements that name an undeclared flow, and SHALL leave `binding-context/8` unchanged.

#### Scenario: Routing to an undeclared flow

- **GIVEN** ein exklusives Gateway mit den Flüssen f-manual und f-auto
- **WHEN** eine Spur-Aussage den Token an einen nicht deklarierten Fluss leitet
- **THEN** meldet P1 einen Diagnosecode für die fehlende Flussbindung.
