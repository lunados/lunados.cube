# Relation origin

Status: implemented · 2026-11-02. Konsolidiert aus `declare-relation-origin` (MILE-011); Nachweis [C-RESULT](../../../docs/10-Evidence/MILE-011/C-RESULT.md).

## Purpose

P1.14 (`binding-context/10`) bindet die Herkunft einer Beziehung für Prädikate mit `origin_binding: required`: `declared`, `derived` (mit Grundlage aus Quellaussagen oder einem lunados.lib-Projektionsdatensatz) oder `unknown`. P1 prüft die Deklaration; es berechnet keine Herkunft und gleicht nicht mit einem Fremdmodell ab. Lokal (G4) und remote (G5 `0.9.0-proof`).

## Requirements


### Requirement: Bound relation origin

In a `binding-context/10` a relation SHALL carry a typed `origin` of `declared`, `derived` or `unknown`; a missing origin SHALL yield UNRESOLVED, never PASS; `derived` SHALL name its basis (source statements or a lunados.lib `project.aggregate-relations/v1` record, read and never recomputed), otherwise UNRESOLVED; any other value SHALL yield FAIL.

#### Scenario: Condensed relation without origin

- **GIVEN** C4-03 als `/10`-Kontext: `rel("uses", Boundary[api], Boundary[db])` ohne `origin`
- **WHEN** die Aussage geprüft wird
- **THEN** lautet das Ergebnis UNRESOLVED mit `P1_ORIGIN_UNDECLARED`, und mit `origin="derived"` samt Grundlage lautet es PASS.
