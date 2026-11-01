# TASK-004 — Vorhandene Prüfungen wiederholbar aufrufen

Planungsstand: umgesetzt und verifiziert. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/archive/2026-11-01-prepare-grammar-comparison/tasks.md).

Story: [US-003](../04-US/US-003-repeatable-probes.md) · Mile: MILE-001-B · Aufwand: 2–3 h

## Ziel und Arbeit

Einen kleinen lokalen Runner mit vorhandenen SDK-/Adapteraufrufen verbinden. Aufrufart und aktueller Stand werden protokolliert. Mindestens der lokale stdio-MCP-Pfad ist für die drei ausgewählten Proben nachzuweisen.

## Eingaben / betroffene Bereiche

Vorhandene SDK-Smokes unter `P3/adapters/mcp-local/scripts/`; geplanter kleiner Runner unter `scripts/research/` mit Fixtures unter `docs/09-Research/analysis-readiness/` (neu bei Umsetzung).

Die genannten Ablagen wurden im beschriebenen Umfang umgesetzt; konkrete Nachweise siehe Ergebnisverweis.

## Ergebnis

Ein dokumentierter Aufruf erzeugt je Fall Rohantwort und strukturierten Ergebnisbericht; Ergebnisablage ist explizit.

## Akzeptanz

- PASS, FAIL und UNRESOLVED werden tatsächlich ausgeführt und mit vorab fixierten Erwartungen abgeglichen.
- Erwartetes fachliches FAIL kann eine bestandene Probe sein; Fachstatus und Übereinstimmung mit Erwartung bleiben getrennte Felder.
- Ausgabe enthält Revision/Hash und Aufrufart; direkte Python-Aufrufe werden nicht als MCP-Nachweis beschriftet.
- Keine Semantik nachbauen und keine neue externe Abhängigkeit voraussetzen, solange vorhandene Laufzeit/SDK genügen.

## Gezielte Verifikation

Drei Proben zweimal ausführen; fachliche Ergebnisse und Diagnosecodes vergleichen, Laufzeit/Run-ID getrennt behandeln. Frische stdio-Verbindung wird von historischem Chat-Toolbestand unterschieden.

## Abhängigkeiten und Grenze

[TASK-003](TASK-003-comparison-case-contract.md)

Umfangsgrenze: [MILE-001](../02-Milestones/MILE-001-analysis-readiness.md). Keine Veränderung an Morphologie oder Envelope-Semantik. Der konkrete Nachweis ist unten verlinkt; daraus folgt keine fachliche Gesamtvalidierung.


## Abschlussnachweis

Abgeschlossen am 2026-11-01. [Charge B: Ausführung und Nachweis](../10-Evidence/MILE-001/B-RESULT.md).
