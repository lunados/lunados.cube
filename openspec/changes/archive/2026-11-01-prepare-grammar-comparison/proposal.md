# Prepare grammar comparison

Status: done · Stand: 2026-11-01 · [MILE-001](../../../../docs/02-Milestones/MILE-001-analysis-readiness.md)

Zwei Epics, vier Stories und acht Tasks umgesetzt; [Nachweise](../../../../docs/10-Evidence/MILE-001/C-RESULT.md). Keine fachliche Vollständigkeit der fünf Ansätze behauptet.

## Why

Die fünf Vergleiche sollen konkrete Vertrags- und Darstellungslücken sichtbar machen. Unterschiedliche Fallformate und unpräzise Discovery-Angaben erschweren derzeit die Unterscheidung zwischen vorhandener Fähigkeit und bloßer Beschreibung.

## What Changes

- Gemeinsame Vergleichsfälle mit Quellen, Eingaben, Erwartung und getrennten Ergebnissen.
- Kleiner wiederholbarer Prüflauf mit bestehenden Cube-/LIB-Werkzeugen.
- Begrenzte Präzisierung der lokalen MCP-Selbstauskunft nach Abgleich mit der Implementierung.

## Capabilities

### New Capabilities

- `comparison-evidence`: wiederholbare Vergleichsfälle mit nachvollziehbarer Quellen- und Ergebnisbindung.
- `local-discovery-accuracy`: neuer Spezifikationsbereich für die additive Präzisierung einer bereits vorhandenen lokalen Discovery; keine neue Validierungsoperation.

### Modified Capabilities

Noch keine bestehende Discovery-Spezifikation nach OpenSpec migriert. Daher wird der eng begrenzte neue Spezifikationsbereich als ADDED geführt. TASK-001 fixiert die genaue Metadatenform und Kompatibilitätsbasis; die bestehenden P3-Verträge bleiben gültig.

## Impact

Research-Fälle und Protokolle unter `docs/`; ein kleiner Runner und gegebenenfalls eine begrenzte P3-Dokumentations-/Discovery-Korrektur. Discovery-Ziel ist der lokale Pfad `discover_surface_local()` mit passender Toolbeschreibung; der kleine Runner ist unter `scripts/research/` vorgesehen. Bestehende Legacy-/G4-Ausgaben bleiben geschützt. Keine neue Morphologie, kein neuer Envelope-Typ, keine Fremdtool-Adapter und keine Prozessengine. Grobe Schätzung: 1–2 PT, teilweise Ersatz manueller Analysearbeit. Alle Aufgaben sind mit begrenzten Nachweisen abgeschlossen.
