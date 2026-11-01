# EPIC-002 — Verlässliche lokale Selbstauskunft

Status: done · Milestone: [MILE-001](../02-Milestones/MILE-001-analysis-readiness.md)

## Ergebnis und Umfang

Die lokale MCP-Oberfläche nennt tatsächlich unterstützte Operationen und Binding-/Profilversionen mit ihren Grenzen. Die gefundene Beschreibungsabweichung wird quellengebunden eingegrenzt und additiv behoben.

## Akzeptanz

- Inventar und lokale Discovery stimmen mit Registrierung/Dispatch überein.
- Geschützte Legacy-P2- und G4-Ausgaben bleiben unverändert; keine G5-Parität wird behauptet.
- Die Ergänzung ist durch gezielte Kompatibilitätskontrollen und einen echten lokalen stdio-Aufruf belegt.

## Stories

- [US-002](../04-US/US-002-capability-discovery.md)

## Aufgaben

- [TASK-001 — Lokale Fähigkeiten und Kompatibilitätsgrenzen erfassen](../05-Tasks/TASK-001-capability-baseline.md)
- [TASK-002 — Lokale Discovery gezielt präzisieren](../05-Tasks/TASK-002-discovery-accuracy.md)

## Aufwand / Nutzen / Komplexität

2–4 h, erwarteter Nutzen sehr hoch, Komplexität niedrig–mittel. Annahmen und Grenzen stehen im Milestone. Führende Checkliste: [tasks.md](../../openspec/changes/archive/2026-11-01-prepare-grammar-comparison/tasks.md).


Ergebnis: [Charge A](../10-Evidence/MILE-001/A-RESULT.md), 2026-11-01.
