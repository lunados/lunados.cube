# Declare relation origin

Status: done · 2026-11-02 · archiviert · [MILE-011](../../../../docs/02-Milestones/MILE-011-relation-origin.md) · [Nachweis](../../../../docs/10-Evidence/MILE-011/C-RESULT.md)

## Why

Eine nur verdichtete Beziehung besteht P1 wie eine deklarierte ([C4-03](../../../../docs/09-Research/grammar-sampling/reports/C4-03.md)); die in `relations.json` vorgesehene Form `origin=` hat keinen Vertrag. `cube.flow` unterscheidet Linien nur nach Prädikat und liest nur Migrationspläne. Eine Übersicht kann so als festgelegte Architekturentscheidung gelesen werden (G-02, VR-01).

## What Changes

- Profil P1.14 (`binding-context/10`): typisierter Parameter `origin ∈ {declared, derived, unknown}`; fehlende Herkunft und Ableitung ohne Grundlage → UNRESOLVED.
- VP-07 0.7.6: `cube.flow` mit Linienart nach Herkunft und Text, auch aus Aussagenmengen.
- G4, G6 und G5; kurze Sichtprüfung.

## Capabilities

### New Capabilities

- `relation-origin`: gebundene Herkunft einer Beziehung mit Grundlage für Ableitungen.
- `origin-line-view`: Herkunftslinie in `cube.flow`, farbfrei und mit Text.

## Impact

Neues P1-Profil, neues opt-in-Profil in `vpmigration`, Adapter G4/G6, G5-Kern. Keine Änderung an P0, P1.1–P1.13, VP-07 0.7.0–0.7.5, VP-10, VP-11 oder vorhandenen lunados.lib-Einträgen. Grobe Planung: 3–4,5 PT.
