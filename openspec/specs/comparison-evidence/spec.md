# Comparison evidence

Status: implemented · 2026-11-01. Consolidated from the completed preparation change (MILE-001) and extended by `sample-five-grammars` (MILE-002, TASK-010).

## Purpose

The runner accepts exactly sourced historical cube_validate fixtures (case format v1) and authored synthetic cases with pinned provenance and pre-fixed expectations (case format v2), opens fresh local stdio connections, and compares observed validation. Non-executable authored cases are recorded without a tool call. It does not implement foreign-language semantics or infer unassessed evidence dimensions.

## Requirements

### Requirement: Reproducible comparison case

The comparison tooling SHALL retain case identity, source and model versions, exact inputs, bound profile revisions, invocation kind and raw response for each executed case. It SHALL distinguish unchanged historical exact-extraction cases from explicitly versioned authored cases with pinned provenance and expectations fixed before execution.

#### Scenario: Existing local validation probe

- **GIVEN** ein vorhandener Fall mit fixierter Eingabe und Erwartung
- **WHEN** die lokale Prüfung ausgeführt wird
- **THEN** enthält der Bericht die tatsächlich aufgerufene Operation, die verfügbare Versionsinformation und die unveränderte Rohantwort
- **AND** dokumentarische Quellen und tatsächlich ausgeführte Prüfungen sind unterscheidbar.

#### Scenario: Authored synthetic case

- **GIVEN** ein neuer Fall mit expliziter Herkunftsart, Modell-/Argumenthashes, Quellen-/Regelverweisen und vorab definierter Erwartung
- **WHEN** der Fall lokal ausgeführt wird
- **THEN** bleibt er als neu erstellter synthetischer Fall erkennbar
- **AND** historische Proben werden dafür weder umgeschrieben noch als Herkunft vorgetäuscht.

#### Scenario: Missing provenance or changed input

- **GIVEN** fehlende Herkunftsbindung oder eine vom fixierten Hash abweichende Eingabe
- **WHEN** der Fall geladen wird
- **THEN** wird er vor dem Toolaufruf zurückgewiesen und kein fachlicher Erfolg ausgegeben.

#### Scenario: Documented non-executable case

- **GIVEN** ein ausgearbeiteter Fall, dessen Unterscheidung heute nicht als einzelner Ausdruck prüfbar ist
- **WHEN** der Runner ihn verarbeitet
- **THEN** wird er mit Begründung als NOT_EXECUTED protokolliert, ohne Toolaufruf und ohne Fachstatus.

### Requirement: Separate evidence dimensions

The report SHALL distinguish expression, contract binding, implemented validation, visualization and utility; an unobserved dimension SHALL remain explicitly unassessed.

#### Scenario: Validation without visual or semantic evidence

- **GIVEN** ein deklarativer PASS ohne Darstellungs- oder Nutzennachweis
- **WHEN** der Bericht erzeugt wird
- **THEN** bleibt PASS auf die betreffende deklarative Prüfung begrenzt
- **AND** die übrigen Dimensionen werden nicht als erfolgreich ausgegeben.

### Requirement: Preserve failure and uncertainty

The tooling SHALL preserve FAIL and UNRESOLVED diagnostics and SHALL distinguish invocation unavailability from a domain result.

#### Scenario: Missing profile

- **GIVEN** eine Antwort mit UNRESOLVED wegen fehlender Profilbindung
- **WHEN** der Bericht erzeugt wird
- **THEN** bleiben Status und Diagnose erhalten und werden nicht durch einen allgemeinen Erfolg ersetzt.

#### Scenario: Tool invocation fails

- **GIVEN** ein nicht erreichbares lokales Werkzeug
- **WHEN** der Fall nicht ausgeführt werden kann
- **THEN** wird der Aufruffehler berichtet und kein fachliches PASS oder FAIL erfunden.

#### Scenario: Expected failure remains a domain failure

- **GIVEN** ein vorab definierter Fall mit erwarteter fachlicher FAIL-Diagnose
- **WHEN** diese Diagnose tatsächlich eintritt
- **THEN** bleibt der Fachstatus FAIL und die separate Erwartungsprüfung meldet Übereinstimmung
- **AND** die Rohantwort bleibt unverändert erhalten.

#### Scenario: Repeated probe with different run metadata

- **GIVEN** dieselbe fixierte Eingabe und derselbe Prüfstand
- **WHEN** zwei Läufe unterschiedliche Zeitstempel oder Run-IDs erhalten
- **THEN** werden Fachstatus und Diagnose getrennt von diesen Laufmetadaten verglichen.

### Requirement: Baseline and variant remain distinguishable

The tooling SHALL retain baseline and variant identity and SHALL identify changed inputs or profile revisions before comparing results.

#### Scenario: Proposed profile addition

- **GIVEN** ein Ausgangsfall und eine Variante mit zusätzlichem Profil
- **WHEN** ihre Ergebnisse verglichen werden
- **THEN** bleibt erkennbar, welche Fähigkeit im Ausgangsstand vorhanden war und welche erst durch die Variante geprüft wurde.

### Requirement: Readiness evidence and handover

The readiness handover SHALL map milestone criteria to actual recorded evidence or explicit gaps and SHALL provide a reproducible local invocation for the subsequent analysis.

#### Scenario: Incomplete readiness evidence

- **GIVEN** ein Vorbereitungskriterium ohne aktuellen Nachweis
- **WHEN** der Abschlussbericht erstellt wird
- **THEN** bleibt das Kriterium offen und der Milestone wird nicht vollständig abgeschlossen
- **AND** historische Protokolle werden nicht als neue Ausführung ausgegeben.


## Verification

[MILE-001 evidence](../../../docs/10-Evidence/MILE-001/C-RESULT.md) · [MILE-002 evidence](../../../docs/10-Evidence/MILE-002/C-RESULT.md). Scope and untested claims remain explicit.
