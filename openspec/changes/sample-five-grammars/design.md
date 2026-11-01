# Design — Grammatikabtastung

Status: planned

## Context

Der vorhandene Runner akzeptiert nur exakt aus historischen Proben extrahierte Eingaben. Seine fünf Ergebnisdimensionen und Fehlergrenzen sind erprobt. Neue Vergleichsfälle dürfen diese Herkunftsprüfung nicht durch eine falsche Archivbehauptung umgehen. Die bestehenden konsolidierten Specs bleiben bis tatsächlicher Umsetzung unverändert.

## Goals / Non-Goals

Kleine quellengebundene Gegenbeispiele sollen Fähigkeiten und Grenzen sichtbar machen. Es entstehen keine vollständigen Sprachadapter, keine allgemeinen Engine- oder Solverfunktionen und keine neue kanonische Morphologie.

## Decisions

Vorgeschlagener Ablauf:

1. Quellen und Regelstellen vor Cube-Experimenten fixieren; datierte Webdokumentation nur innerhalb ihres Geltungsanspruchs verwenden.
2. Für selbst erstellte synthetische Fälle eine explizite versionierte Herkunftsart definieren. Historischer v1-Modus behält Exaktextraktion und Hashprüfungen. Konkrete Feldnamen/Version in TASK-010 am kleinsten Fall festlegen.
3. Pro Fall Ausgangsmodell, Erwartung und entscheidende Unterscheidung dokumentieren. Bestehenden Cube-Stand zuerst untersuchen; zusätzliche Bindungsprofile separat identifizieren.
4. Quellenanalyse, manuelle semantische Beurteilung, lokales MCP und gegebenenfalls externer LIB-Evaluator werden als unterschiedliche Nachweisarten aufgezeichnet. Nicht alles muss ausführbar sein, aber keine Ausführung wird erfunden.
5. Pro Lücke die kleinste Eingriffsebene benennen. „Fehlender Prüfer“ und „nicht ausdrückbar“ sind verschiedene Ergebnisse. Vorschläge bleiben Vorschläge.

## Risks / Trade-offs

Der Aufwand wächst besonders durch Normzugang und Prozesssemantik. Die Fälle bleiben klein. Eigene Kardinalitäten dürfen nicht als ArchiMate-Norm ausgegeben werden; ein erfolgreiches Token-/Join-Beschreibungsmodell ist noch keine BPMN-Ausführung. Ein Graphalgorithmus hat einen anderen Anspruch als morphologische Darstellbarkeit. Die Stichprobe kann Lücken finden, keine universelle Vollständigkeit beweisen.

## Open Questions

- Welche zugängliche ArchiMate-Version und welche konkrete Relationsregel bilden die begrenzte Baseline?
- Welche exakte lokale Herkunftserweiterung genügt für eigene Fälle, ohne ein allgemeines Framework zu bauen?
- Welche Fälle lassen sich bereits ausführen, welche liefern zunächst einen belegten fehlenden Vertrag oder Prüfer?

Diese Fragen sind Aufgaben der Charge A/B, keine ungefragten Implementierungsannahmen. Fehlende zwingende Quellen bleiben als offene Abschlusskriterien sichtbar.
