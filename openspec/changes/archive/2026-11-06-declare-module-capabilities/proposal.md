# Modul-Fähigkeiten quellengebunden beschreiben

Status: abgeschlossen für den benannten lokalen Owner-/live G5-Stand ([CLOSURE](../../../../docs/10-Evidence/MILE-020/CLOSURE.md)) · 2026-11-06 · [MILE-020](../../../../docs/02-Milestones/MILE-020-module-capability-descriptors.md) · [EPIC-014](../../../../docs/03-Epics/EPIC-014-module-capability-descriptors.md)

## Why

Der Cube beschreibt bisher seine eigene Oberfläche. Gepinnte Nachbarverweise fehlen; Verbraucher können Modulgrenzen und vorhandene Fähigkeiten nicht konsistent auffinden. MILE-020 soll die modul-eigene Beschreibung zugänglich machen, ohne eine zentrale zweite Fähigkeitswahrheit zu schaffen.

## What Changes

- D-1-abhängiges Deskriptorformat mit Schema, Offline-Prüfung und expliziten Quellenpins.
- Owner-lokale Deskriptoren, vollständige Modulmatrix und 13 Lib-Zuordnungen nach D-2.
- D-3-ADR, eindeutige Connector-Namen nach D-4 und additive neighbors-Verweise in G4/G5.

## Capabilities

### New Capabilities

- `module-capabilities`: dokumentarische, versionierte Modulbeschreibung und rein beschreibende Nachbardiscovery.

### Modified Capabilities

Bestehende Discovery erhält nur das additive Feld neighbors; vorhandene Felder und ihre oberflächenspezifischen Aussagen bleiben erhalten.

## Impact

Planung und gemeinsamer Formatvertrag im Cube; Lib-, Toolbox- und Connector-Owner-Deskriptoren sind mit TASK-088/089 erstellt. TASK-090 ergänzt den Cube-Deskriptor sowie drei logische Relay-Rollen und den gesonderten Connector-Paketbestand in einem isolierten lokalen Relay-Worktree. TASK-086 hat D-1 entschieden: eigenes dokumentarisches Format und gezielter v2-Verweis. TASK-087 hat Schema und Offline-Prüfung geliefert. TASK-088 hat D-2 entschieden und 13 Lib-Zuordnungen belegt. TASK-092 hat D-4 entschieden: `translator/` liegt intern im gemeinsamen Connector-Ziel-Repo; aktuelle Space-Erklärtexte sind angepasst. D-3 ist in [ADR-001](../../../../docs/07-ADR/ADR-001-lib-snapshot-host-path.md) festgehalten. TASK-093 hat additive neighbors lokal und im G5-Quellartefakt geliefert; [TASK-094](../../../../docs/10-Evidence/MILE-020/TASK-094-RESULT.md) belegt alle sechs Kriterien und die tatsächlichen Aufrufe über den lokalen Codex-Host und den ausgelieferten G5-Stand. Nach [CLOSURE](../../../../docs/10-Evidence/MILE-020/CLOSURE.md) ist Relay-Integration in `main` kein Mile-Gate, aber vor einer späteren dauerhaften Verbraucher-Bindung erforderlich. Kein normativer v2-Eingriff, keine Ausführung, neue Toolbox-Fähigkeit oder automatische Bindung.

[EPIC-014](../../../../docs/03-Epics/EPIC-014-module-capability-descriptors.md) · [Design](design.md) · [führender Status](tasks.md)
