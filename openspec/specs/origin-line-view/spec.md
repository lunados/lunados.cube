# Origin line view

Status: implemented · 2026-11-02. Konsolidiert aus `declare-relation-origin` (MILE-011); Nachweis [C-RESULT](../../../docs/10-Evidence/MILE-011/C-RESULT.md).

## Purpose

`cube.flow` mit Profil `P2-VP-MIGRATION/0.7.6` zeichnet jede Kante nach ihrer gebundenen Herkunft (durchgezogen, gestrichelt, gepunktet) und schreibt sie als Text an die Kante; liest dafür auch Aussagenmengen und Verdichtungen. 0.7.0–0.7.5 bleiben byte-gleich. Remote gilt die CPU-Grenze des G5-Workers.

## Requirements


### Requirement: Origin line in cube.flow

With profile `P2-VP-MIGRATION/0.7.6`, `cube.flow` SHALL draw each edge by its bound origin (solid declared, dashed derived, dotted unknown or unbound), SHALL always print the origin as text, SHALL keep the arrowhead neutral, SHALL never draw an edge without bound origin solid, and SHALL accept a statement set instead of a migration plan; profiles 0.7.0–0.7.5 SHALL stay byte-identical.

#### Scenario: Declared and condensed edge side by side

- **GIVEN** eine Aussagenmenge mit `api → db` einmal deklariert und einmal abgeleitet mit Grundlage
- **WHEN** `cube.flow` 0.7.6 sie zeichnet
- **THEN** ist die deklarierte Kante durchgezogen, die abgeleitete gestrichelt, beide tragen ihre Herkunft als Text, und die Legende nennt die drei Linienarten.
