# Trace conformance

Status: implemented · 2026-11-02. Konsolidiert aus `check-control-flow` (MILE-008); Nachweis [C-RESULT](../../../docs/10-Evidence/MILE-008/C-RESULT.md).

## Purpose

lunados.lib `analyze.trace-conformance/v1` prüft deklarierte Spuren je Instanz gegen den deklarierten Kontrollfluss; Bedingungen werden nur als aufgezeichnete Ergebnisse gelesen, nie ausgewertet.

## Requirements


### Requirement: Trace conformance

A trace check SHALL evaluate, per instance and outside the Cube, that each activation of an exclusive gateway took exactly one path, that the default was taken only when no recorded condition was true, and that a parallel join had a token on every incoming flow of the same instance; it SHALL return UNRESOLVED when trace coverage or condition outcomes are missing, and SHALL never evaluate conditions itself.

#### Scenario: Two paths for one activation

- **GIVEN** Instanz i1 mit einem Token am exklusiven Gateway, der an zwei ausgehende Flüsse geleitet wurde
- **WHEN** die Spur geprüft wird
- **THEN** ist das Ergebnis FAIL für diese Aktivierung, mit beiden Flüssen benannt.

#### Scenario: Join still waiting

- **GIVEN** ein paralleler Join, dem in Instanz i2 der Token auf f-stock-done fehlt, und kein Token hinter dem Join
- **WHEN** die Spur geprüft wird
- **THEN** ist das Ergebnis PASS mit `join_waiting` und dem fehlenden Eingang benannt; liegt schon ein Token hinter dem Join (Ship gestartet), ist es FAIL mit `join_incomplete`.
