# Visual distinction check — research protocol

Status: implemented · 2026-11-01. Research-Protokoll aus `check-visual-distinctions` (MILE-003); keine neue visuelle Grammatik, keine Printer- oder Ankeränderung.

## Purpose

Nachvollziehbare Prüfung, welche Darstellungsunterscheidungen vorhandene Sichten tragen: Inventur, Minimalpaare aus Printern oder markierte Handmockups, Agenten-Vorprüfung als Proxy. Gilt als Protokoll für weitere Darstellungsprüfungen.

## Requirements


### Requirement: Presentation inventory

The study SHALL record for each presentation requirement V-01 to V-12 the carrying view, printer or anchor, or a justified gap, together with the kind of evidence (documentation/code, render, not tested).

#### Scenario: No carrying view

- **GIVEN** eine Anforderung, für die keine Sicht die Unterscheidung trägt
- **WHEN** die Inventur erstellt wird
- **THEN** wird sie als Lücke mit Begründung geführt und nicht als vorhanden ausgegeben.

### Requirement: Minimal pairs

The study SHALL show each priority distinction as a minimal pair from existing printer output or as a visibly marked hand mockup using only existing visual-grammar anchors.

#### Scenario: Mockup instead of printer output

- **GIVEN** eine Unterscheidung, die kein vorhandener Printer trägt
- **WHEN** ein Kandidat gezeigt wird
- **THEN** ist er als Mockup gekennzeichnet, nennt Fall und Variante und verändert weder Printer noch Anker.

### Requirement: Agent pre-check is not human evidence

The pre-check SHALL apply the fixed criteria to every pair and SHALL mark agent answers as a proxy; it SHALL NOT claim human readability.

#### Scenario: Question answered from the picture

- **GIVEN** ein Paar und die zugehörige Fallfrage
- **WHEN** der Agent sie allein aus der Darstellung beantwortet
- **THEN** wird die Antwort als Agenten-Proxy protokolliert und keine Verständlichkeit für Menschen abgeleitet.

### Requirement: Honest visual completion

The milestone SHALL close only when inventory, pairs and pre-check exist; missing renders or untested distinctions SHALL remain open and be handed over to MILE-004.

#### Scenario: Untested distinction

- **GIVEN** eine nicht gerenderte oder nicht geprüfte Unterscheidung
- **WHEN** die Übergabe erstellt wird
- **THEN** bleibt sie offen ausgewiesen.
