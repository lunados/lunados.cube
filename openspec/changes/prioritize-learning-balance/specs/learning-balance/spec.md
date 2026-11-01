# Learning balance — research protocol

Status: planned. Priorisierung von Maßnahmen, keine Umsetzung.

## ADDED Requirements

### Requirement: Probed guiding questions

The study SHALL probe each open guiding question with at least one architecture case and one process case whose source, input and expected outcome are committed before execution, and SHALL answer the question or state precisely what evidence is missing.

#### Scenario: Probe not executable

- **GIVEN** eine Probe, für die kein ausführbares Werkzeug oder keine versionierte Quelle vorliegt
- **WHEN** der Probeplan erstellt wird
- **THEN** wird sie vorab als nicht ausführbar begründet, und die Leitfrage bleibt mit diesem fehlenden Nachweis offen.

### Requirement: Framed prioritization

The study SHALL rank all measures with a scoring frame (benefit per declared use case, effort, complexity, uncertainty, dependencies) committed before any measure is scored.

#### Scenario: Frame changed after scoring started

- **GIVEN** eine Änderung am Bewertungsrahmen nach Beginn der Bewertung
- **WHEN** die Lernbilanz erstellt wird
- **THEN** wird die Änderung als Nachtrag mit Grund ausgewiesen und die Bewertung vollständig neu durchgeführt.

### Requirement: Evidence-bound extension candidates

The study SHALL name an envelope or morphology change only as a candidate backed by a probe in which two required distinctions become indistinguishable or a required binding fits only into untyped free text.

#### Scenario: Probe expressible in existing contract

- **GIVEN** eine Probe, deren Pflichtunterscheidungen im vorhandenen Vertrag typisiert ausdrückbar sind
- **WHEN** die Leitfrage beantwortet wird
- **THEN** wird keine Erweiterung vorgeschlagen.

### Requirement: Planned follow-up without implementation

The milestone SHALL plan the follow-up milestone for the top measures with measurable acceptance criteria and SHALL NOT implement any measure.

#### Scenario: Top measure depends on an open decision

- **GIVEN** eine oberste Maßnahme, die eine offene Nutzerentscheidung voraussetzt
- **WHEN** MILE-005 ausgeplant wird
- **THEN** wird die Entscheidung als offene Frage im Plan benannt und nicht vorweggenommen.
