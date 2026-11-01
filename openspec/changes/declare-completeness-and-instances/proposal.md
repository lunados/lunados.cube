# Declare completeness and instances

Status: decided · 2026-11-01 · [MILE-005](../../../docs/02-Milestones/MILE-005-completeness-instances.md) · noch nicht umgesetzt

## Why

Die [Lernbilanz](../../../docs/09-Research/learning-balance/LERNBILANZ.md) stellt Vollständigkeit mit Populationsprüfung samt Darstellung (G-01 → VR-05) und typisierte Instanzbindung (G-08) auf Rang 1 und 2 für Architektursichten und Prozessspuren. Heute fallen „unbekannt“ und „geprüft leer“ zusammen, und ein instanzübergreifender Join besteht im gemeinsamen Scope.

## What Changes

- Ausführbare Prüffälle für die bisher nicht ausgeführten MILE-002-Fälle, Erwartung vorab.
- Ein neues P1-Profil für Vollständigkeitserklärung, Populationsprüfung und Instanzbindung.
- Ein LIB-Eintrag für die Populationsprüfung mit typisiertem Ergebnisschema (D-6).
- Ein neuer Printer-Stand für vier Zellzustände; VP-09 bleibt unverändert.

## Capabilities

### New Capabilities

- `completeness-declaration`: erklärter Erhebungsumfang, Population, Status bei Unvollständigkeit.
- `instance-binding`: typisierte Instanzzugehörigkeit und Regel „gleiche Instanz“.
- `cell-state-display`: vier farbfrei unterscheidbare Zellzustände.

## Impact

Neues P1-Profil, ggf. LIB-Eintrag, neuer Printer-Stand, Adapter. Keine Änderung an P0, P1.1–P1.9, P2 oder der Morphologie. Grobe Planung: 5–7 PT.
