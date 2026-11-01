# TASK-002 — Lokale Discovery gezielt präzisieren

Planungsstand: umgesetzt und verifiziert. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/archive/2026-11-01-prepare-grammar-comparison/tasks.md).

Story: [US-002](../04-US/US-002-capability-discovery.md) · Mile: MILE-001-A · Aufwand: 1–2 h

## Ziel und Arbeit

Die in TASK-001 belegte Lücke im lokalen Discovery-Pfad und in der Toolbeschreibung schließen. Die Änderung bleibt Metadaten über vorhandene Fähigkeiten; keine zusätzliche Validierungs- oder Ausführungssemantik.

## Eingaben / betroffene Bereiche

`P3/adapters/mcp-local/aiaeao_mcp_local/surface.py` (`discover_surface_local`), `server.py` (`cube_validate`-Beschreibung), gegebenenfalls ergänzendes lokales Schema; `tests/test_g4_surface.py`, `tests/test_g6_plan_views.py`.

Die genannten Ablagen wurden im beschriebenen Umfang umgesetzt; konkrete Nachweise siehe Ergebnisverweis.

## Ergebnis

Präzise lokale Capability-Angaben mit passender Dokumentation und gezieltem Regressionstest.

## Akzeptanz

- Unterstützte Kontext-/Profilversionen und Nachweisgrenzen entsprechen der in TASK-001 belegten Implementierung.
- `cube_get_capabilities` und `surface.discover_surface()` bleiben in ihren geschützten Ausgaben unverändert; die lokale Ergänzung erfolgt separat.
- Die reale lokale Discovery und Toolbeschreibung sind konsistent; keine Remote-Parität oder fachliche Wahrheit wird daraus abgeleitet.

## Gezielte Verifikation

Gezielte G4-/G6-Kompatibilitätsprüfungen, Alt-Ausgabenvergleich und lokale stdio-Discovery-Probe. Golden-Dateien nicht nur zur Anpassung an einen Fehler überschreiben.

## Abhängigkeiten und Grenze

[TASK-001](TASK-001-capability-baseline.md)

Umfangsgrenze: [MILE-001](../02-Milestones/MILE-001-analysis-readiness.md). Keine Veränderung an Morphologie oder Envelope-Semantik. Der konkrete Nachweis ist unten verlinkt; daraus folgt keine fachliche Gesamtvalidierung.


## Abschlussnachweis

Abgeschlossen am 2026-11-01. [Charge A: Ausführung und Nachweis](../10-Evidence/MILE-001/A-RESULT.md).
