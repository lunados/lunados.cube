# Instance view

Status: planned.

## ADDED Requirements

### Requirement: Instance view

An instance view SHALL draw each declared instance of a `binding-context/9` as a named frame, SHALL show per exclusive gateway activation the taken and not taken paths and per parallel join each expected input with its status, SHALL take every verdict from a `aiaeao.trace-conformance-result/v1` record without recomputing it, SHALL show "not checked" when no record is given, and SHALL distinguish all states without colour.

#### Scenario: Two paths for one activation

- **GIVEN** BPMN-01 mit Instanz i1, deren Token am exklusiven Gateway an zwei Flüsse geleitet wurde, und das LIB-Ergebnis FAIL `exclusive_two_paths`
- **WHEN** `cube.instances` die Spur zeichnet
- **THEN** stehen beide Pfade im Rahmen von i1 als „genommen“, die Aktivierung trägt „Regelverstoß“ mit Schraffurmarke, und ohne LIB-Ergebnis trägt sie stattdessen „nicht geprüft“.

#### Scenario: Join still waiting

- **GIVEN** BPMN-02 mit Instanz i2, deren Join den Eingang f-stock-done nicht hat, kein Token hinter dem Join, und das LIB-Ergebnis PASS `join_waiting`
- **WHEN** `cube.instances` die Spur zeichnet
- **THEN** listet der Join f-credit-done als „angekommen“ und f-stock-done als „fehlt“, nennt „wartet“, und ship erscheint nur im Feld „Prozessmodell · keine Spur“.
