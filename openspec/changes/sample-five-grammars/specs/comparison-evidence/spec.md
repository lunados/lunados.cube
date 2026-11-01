# Comparison evidence — authored case extension

Status: planned. Bestehender Ist-Vertrag wird nicht durch diesen Entwurf ersetzt.

## MODIFIED Requirements

### Requirement: Reproducible comparison case

The comparison tooling SHALL retain case identity, source and model versions, exact inputs, bound profile revisions, invocation kind and raw response for each executed case. It SHALL distinguish unchanged historical exact-extraction cases from explicitly versioned authored cases with pinned provenance and expectations fixed before execution.

#### Scenario: Existing local validation probe

- **GIVEN** ein vorhandener historischer v1-Fall mit fixierter Eingabe und Erwartung
- **WHEN** die lokale Prüfung ausgeführt wird
- **THEN** gelten weiterhin Exaktextraktion und ursprüngliche Hashprüfungen
- **AND** Operation, Versionsinformation und unveränderte Rohantwort bleiben im Bericht enthalten.

#### Scenario: Authored synthetic case

- **GIVEN** ein neuer Fall mit expliziter Herkunftsart, Modell-/Argumenthashes, Quellen-/Regelverweisen und vorab definierter Erwartung
- **WHEN** der Fall lokal ausgeführt wird
- **THEN** bleibt er als neu erstellter synthetischer Fall erkennbar
- **AND** historische Proben werden dafür weder umgeschrieben noch als Herkunft vorgetäuscht.

#### Scenario: Missing provenance or changed input

- **GIVEN** fehlende Herkunftsbindung oder eine vom fixierten Hash abweichende Eingabe
- **WHEN** der Fall geladen wird
- **THEN** wird er vor dem Toolaufruf zurückgewiesen und kein fachlicher Erfolg ausgegeben.
