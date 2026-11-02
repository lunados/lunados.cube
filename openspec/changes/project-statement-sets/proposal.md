# Project statement sets

Status: proposed · 2026-11-02 · [MILE-007](../../../docs/02-Milestones/MILE-007-statement-sets.md) · Entscheidungen D-1–D-8 offen

## Why

Die Plansichten lesen nur P1.10-Migrationspläne; anderes Material muss umgebogen werden (PO-7, [RENDER-RESULTS](../../../docs/09-Research/visual-check/RENDER-RESULTS.md)). Verdichtungen wie in C4-02 verlieren Quellen still; es gibt keine Projektion mit Quellenspur und Verlustbericht (G-03).

## What Changes

- Format `aiaeao.cube.statement-set/1` für deklarierte Aussagenmengen zu einem `binding-context/8`.
- LIB `project.aggregate-relations/v1`: Verdichtung mit Pflichtstrategie, Quellenspur und Verlustbericht (`aiaeao.projection-result/v1`).
- VP-10 0.11.0: `cube.cells` liest Aussagenmengen und Projektionsergebnisse; abgeleitete Einträge mit Quellenzahl.
- Kurze Sichtprüfung.

## Capabilities

### New Capabilities

- `statement-set-display`: Matrix aus einer Aussagenmenge ohne Migrationsplan.
- `relation-aggregation`: Verdichtung mit Quellenspur und Verlustbericht, in LIB berechnet und im Cube nur gelesen.

## Impact

Neues Profil in `vpcells` (P2), neuer LIB-Eintrag (lunados.lib), G6-Option (P3 lokal). Keine Änderung an P0, P1.1–P1.12, VP-07, VP-09, VP-10 0.10.x oder der Morphologie. Grobe Planung: 2–3 PT.
