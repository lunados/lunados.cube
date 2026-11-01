# Grammar sampling — research protocol

Status: done · konsolidiert in [specs/grammar-sampling](../../../../../specs/grammar-sampling/spec.md).

## ADDED Requirements

### Requirement: Source-qualified sampling scope

The study SHALL bind each used rule to an explicit source/version and SHALL distinguish normative rules, documentary descriptions and local assumptions.

#### Scenario: Unavailable normative rule

- **GIVEN** eine für den Fall erforderliche, nicht zugängliche normative Regel
- **WHEN** der Fall ausgewertet wird
- **THEN** bleibt der entsprechende Nachweis offen; eine eigene Annahme wird nicht als Normbestätigung bezeichnet.

### Requirement: Fifteen differentiated cases

The study SHALL document two normal cases and one counterexample for each of C4/Structurizr, ArchiMate, DSM/MDM, BPMN and DAG, preserving concrete inputs, prior expectations and the distinction under examination.

#### Scenario: Missing validator for a concrete distinction

- **GIVEN** ein ausgearbeiteter Fall mit belegter Regel und einer heute nicht automatisiert prüfbaren Unterscheidung
- **WHEN** das Ergebnis berichtet wird
- **THEN** wird die fehlende Prüfung als konkrete Lücke mit Bezug auf Ausdruck und Bindung ausgewiesen
- **AND** weder ein Toolaufruf noch ein fachliches PASS werden erfunden.

### Requirement: Independent baseline and evidence scope

The study SHALL separate the unchanged Cube baseline from proposed profiles and SHALL distinguish documentary analysis, declared validation, external evaluation and visual/utility evidence.

#### Scenario: Candidate profile allows a declared expression

- **GIVEN** ein Ausgangsfall und eine eigene Profilvariante
- **WHEN** die Variante einen deklarativen PASS erhält
- **THEN** bleiben der Ausgangsbefund und das zusätzliche Profil getrennt referenzierbar
- **AND** daraus folgt keine vollständige Fremdsprachen-, Ausführungs- oder visuelle Konformität.

### Requirement: Traceable learning and gap ledger

The study SHALL trace its findings to the fifteen cases and seven user questions and SHALL state the smallest justified intervention, expected utility, effort, complexity and remaining uncertainty.

#### Scenario: Candidate library method

- **GIVEN** eine wiederkehrende Analyseaufgabe in konkreten Fällen
- **WHEN** sie als LIB-Kandidat vorgeschlagen wird
- **THEN** werden Aufgabe, benötigte Bindung und erwarteter Nutzen mit Fallbezug beschrieben
- **AND** der Vorschlag wird nicht als bereits implementierte Methode bezeichnet.

### Requirement: Honest sampling completion

The milestone SHALL close only when all required case reports and source bindings exist; concrete unsupported behavior may be a finding, while missing work or necessary sources SHALL remain open.

#### Scenario: Incomplete case or source coverage

- **GIVEN** ein fehlender Fallbericht oder eine fehlende notwendige Quelle
- **WHEN** die Übergabe erstellt wird
- **THEN** bleibt das zugehörige Abschlusskriterium offen
- **AND** Darstellungsanforderungen und vorläufige Maßnahmen werden mit diesen Grenzen an MILE-003/004 übergeben.
