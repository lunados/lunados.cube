# TASK-001 — Lokale Fähigkeiten und Kompatibilitätsgrenzen erfassen

Planungsstand: umgesetzt und verifiziert. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/archive/2026-11-01-prepare-grammar-comparison/tasks.md).

Story: [US-002](../04-US/US-002-capability-discovery.md) · Mile: MILE-001-A · Aufwand: 1–2 h

## Ziel und Arbeit

Aktuelle lokale Toolregistrierung, Dispatch für Binding-Kontexte und Discovery-Angaben gegenüberstellen. Pro Angabe Quelle und Version erfassen; öffentliche Lesereferenz, lokales stdio und G5 unterscheiden. Die in der Baseline berichtete Lücke am aktuellen Code bestätigen oder korrigieren.

## Eingaben / betroffene Bereiche

`P3/adapters/mcp-local/aiaeao_mcp_local/server.py`, `p1_adapter.py`, `surface.py`; vorhandene G4-/G6-Nachweise und importierte MCP-Proben.

Die genannten Ablagen wurden im beschriebenen Umfang umgesetzt; konkrete Nachweise siehe Ergebnisverweis.

## Ergebnis

Quellengebundene Capability-Matrix und genaue Liste der additiv zu ergänzenden lokalen Angaben. Hashes der geschützten Alt-Ausgaben als Ausgangspunkt.

## Akzeptanz

- Jede behauptete lokale Operation und Kontextversion ist auf Registrierung bzw. Dispatch zurückführbar; nicht geprüfte Unterstützung bleibt gekennzeichnet.
- Legacy-P2-Card und G4-Card werden als gesonderte Kompatibilitätsflächen dokumentiert; G5 wird nicht als lokal geprüft ausgegeben.
- Die minimal nötige Änderung einschließlich Metadaten-/Schemaversion ist vor Implementierung beschrieben.

## Gezielte Verifikation

Statischer Abgleich plus tatsächlich protokollierte lokale Discovery-Abfrage; reine Dateilektüre wird nicht als MCP-Ausführung ausgegeben.

## Abhängigkeiten und Grenze

Keine; vorhandene Research-Basis verwenden.

Umfangsgrenze: [MILE-001](../02-Milestones/MILE-001-analysis-readiness.md). Keine Veränderung an Morphologie oder Envelope-Semantik. Der konkrete Nachweis ist unten verlinkt; daraus folgt keine fachliche Gesamtvalidierung.


## Abschlussnachweis

Abgeschlossen am 2026-11-01. [Charge A: Ausführung und Nachweis](../10-Evidence/MILE-001/A-RESULT.md).
