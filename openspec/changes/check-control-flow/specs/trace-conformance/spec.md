# Trace conformance

Status: planned.

## ADDED Requirements

### Requirement: Trace conformance

A trace check SHALL evaluate, per instance and outside the Cube, that each activation of an exclusive gateway took exactly one path, that the default was taken only when no recorded condition was true, and that a parallel join had a token on every incoming flow of the same instance; it SHALL return UNRESOLVED when trace coverage or condition outcomes are missing, and SHALL never evaluate conditions itself.

#### Scenario: Two paths for one activation

- **GIVEN** Instanz i1 mit einem Token am exklusiven Gateway, der an zwei ausgehende Flüsse geleitet wurde
- **WHEN** die Spur geprüft wird
- **THEN** ist das Ergebnis FAIL für diese Aktivierung, mit beiden Flüssen benannt.
