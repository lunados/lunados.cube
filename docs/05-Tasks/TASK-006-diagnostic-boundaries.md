# TASK-006 — Fehler- und Unsicherheitsgrenzen absichern

Planungsstand: umgesetzt und verifiziert. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/archive/2026-11-01-prepare-grammar-comparison/tasks.md).

Story: [US-003](../04-US/US-003-repeatable-probes.md) · Mile: MILE-001-B · Aufwand: 0,5–1,5 h

## Ziel und Arbeit

Toolausfall, ungültige Konfiguration, fachliches FAIL und UNRESOLVED in wenigen gezielten Kontrollen unterscheiden. Erwartete Rohdiagnosen und nicht bewertete Dimensionen erhalten.

## Eingaben / betroffene Bereiche

Runner aus TASK-004; bestehende P1-/MCP-Fehlerbehandlung und ausgewählte Test-Fixtures.

Die genannten Ablagen wurden im beschriebenen Umfang umgesetzt; konkrete Nachweise siehe Ergebnisverweis.

## Ergebnis

Begrenzte Negativkontrollen mit berichteten Aufruf-/Fachstatusgrenzen.

## Akzeptanz

- Unerreichbares Tool bzw. fehlgeschlagener Prozess erzeugt einen Aufruffehler, kein erfundenes fachliches FAIL oder PASS.
- Konfigurationsfehler bleiben von regulären fachlichen Ergebnissen unterscheidbar.
- Fehlende Darstellungs- oder Nutzenbeobachtung bleibt ungeprüft; Rohantworten werden nicht normalisiert überschrieben.

## Gezielte Verifikation

Kontrollierter unerreichbarer Aufruf bzw. Stub plus eine ungültige Konfiguration; simulierte Fehler ausdrücklich als Testsimulation kennzeichnen.

## Abhängigkeiten und Grenze

[TASK-004](TASK-004-repeatable-probe-runner.md)

Umfangsgrenze: [MILE-001](../02-Milestones/MILE-001-analysis-readiness.md). Keine Veränderung an Morphologie oder Envelope-Semantik. Der konkrete Nachweis ist unten verlinkt; daraus folgt keine fachliche Gesamtvalidierung.


## Abschlussnachweis

Abgeschlossen am 2026-11-01. [Charge B: Ausführung und Nachweis](../10-Evidence/MILE-001/B-RESULT.md).
