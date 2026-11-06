# US-041 — Gepinnte Nachbarn über den Cube entdecken

Status: abgeschlossen lokal und live G5 ([CLOSURE](../10-Evidence/MILE-020/CLOSURE.md)) · Epic: [EPIC-014](../03-Epics/EPIC-014-module-capability-descriptors.md) · Mile: [MILE-020](../02-Milestones/MILE-020-module-capability-descriptors.md)

Als Cube-Nutzer möchte ich über neighbors dieselben gepinnten Modulverweise lokal und in G5 sehen, damit ich anschließend selbst die passende Quelle auswählen kann.

## Akzeptanz

Der neue neighbors-Inhalt ist bytegleich bei festgelegter Serialisierung; alle bisherigen Felder bleiben je Oberfläche unverändert. Discovery lädt und ruft keine Nachbarn auf. Eine Abnahmematrix belegt alle sechs Mile-Kriterien und trennt Offline-Parität von tatsächlicher Host-Bereitstellung.

## Aufgaben und Abhängigkeiten

- [TASK-093 — Gepinnte neighbors additiv in G4 und G5 aufnehmen](../05-Tasks/TASK-093-neighbors-discovery.md)
- [TASK-094 — Mile-Abnahme und Übergabe an Verbraucher](../05-Tasks/TASK-094-descriptor-acceptance.md)

Die Task-Voraussetzungen und [Reihenfolge](../../openspec/changes/archive/2026-11-06-declare-module-capabilities/tasks.md) sind verbindlich; diese Story begründet keine Ausführungs-, Admission- oder Host-Freigabe.

Szenarien: [Deskriptor-Verhalten](../../openspec/changes/archive/2026-11-06-declare-module-capabilities/specs/module-capabilities/spec.md).
