# Readability check

Status: planned.

## ADDED Requirements

### Requirement: Readability check with people

A readability check SHALL fix its questions and expected answers before it is run, SHALL use synthetic material only, and SHALL report results per cell state with the limits of a small sample.

#### Scenario: Unknown versus checked empty

- **GIVEN** eine Matrix mit einer geprüft leeren und einer unbekannten Zelle in derselben Zeile
- **WHEN** Testpersonen gefragt werden, ob dort eine Abhängigkeit „sicher nicht“ besteht
- **THEN** wird die Antwort je Zelle gegen die vorab festgelegte Antwort gewertet.
