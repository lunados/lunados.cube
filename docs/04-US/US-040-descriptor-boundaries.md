# US-040 — Host-Pfad und Connector-Namen verstehen

Status: abgeschlossen für den benannten Stand ([CLOSURE](../10-Evidence/MILE-020/CLOSURE.md)) · Epic: [EPIC-014](../03-Epics/EPIC-014-module-capability-descriptors.md) · Mile: [MILE-020](../02-Milestones/MILE-020-module-capability-descriptors.md)

Als Integrator möchte ich denselben Lib-Snapshot auf beiden erlaubten Pfaden identifizieren und Connector-Modul, internen Übersetzungsbereich und vorhandenes Paket auseinanderhalten, damit Herkunft und Verantwortung eindeutig bleiben.

## Akzeptanz

Die ADR übernimmt D-3 unverändert und benennt Folgen für MILE-071 ohne Laufzeitumbau. D-4 ordnet `translator/` dem Ziel-Repo `lunados.connector` zu und unterscheidet das vorhandene Paket `aiaeao-connector` in Deskriptoren und Space, ohne Paket-IDs oder bestehende Verträge umzubenennen.

## Aufgaben und Abhängigkeiten

- [TASK-091 — D-3 als Host-Pfad-ADR festhalten](../05-Tasks/TASK-091-lib-host-path-adr.md)
- [TASK-092 — Connector-Bezeichnungen entscheiden und konsistent verwenden](../05-Tasks/TASK-092-connector-names.md)

Die Task-Voraussetzungen und [Reihenfolge](../../openspec/changes/archive/2026-11-06-declare-module-capabilities/tasks.md) sind verbindlich; diese Story begründet keine Ausführungs-, Admission- oder Host-Freigabe.

Szenarien: [Deskriptor-Verhalten](../../openspec/changes/archive/2026-11-06-declare-module-capabilities/specs/module-capabilities/spec.md).
