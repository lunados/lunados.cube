# US-032 — Herkunft einer Beziehung deklarieren und prüfen

Status: planned · Epic: [EPIC-011](../03-Epics/EPIC-011-relation-origin.md) · Mile: [MILE-011-A, -B, -C](../02-Milestones/MILE-011-relation-origin.md)

Als Modellierer möchte ich für jede Beziehung festhalten, ob sie deklariert, abgeleitet oder in ihrer Herkunft unbekannt ist, damit eine verdichtete Beziehung nicht als festgelegte Tatsache durch die Prüfung geht.

## Akzeptanz

- In einem `/10`-Kontext ergibt eine Beziehung ohne `origin` UNRESOLVED; `derived` ohne Grundlage ebenso; ein unbekannter Wert FAIL.
- C4-03 (`api → db` ohne Herkunft) besteht nicht mehr stillschweigend; mit `origin="derived"` und Grundlage besteht es.
- Lokal (G4) und remote (G5) gleiche Ergebnisse; P1.1–P1.13 unverändert.
- Die in den verlinkten Tasks benannten Abschlusskriterien sind erfüllt oder konkret offen ausgewiesen; offene Pflichtkriterien verhindern den Story-Abschluss.

## Aufgaben

- [TASK-063 — Spezifikation und Detailfragen](../05-Tasks/TASK-063-origin-spec.md)
- [TASK-064 — Prüffälle, Orakel und Pins vor Code](../05-Tasks/TASK-064-origin-cases.md)
- [TASK-065 — Profil P1.14 und G4](../05-Tasks/TASK-065-p114-profile.md)
- [TASK-067 — G5 und Host-Abnahme](../05-Tasks/TASK-067-origin-g5.md)
- [TASK-068 — Sichtprüfung und Abschluss](../05-Tasks/TASK-068-mile011-close.md)

[Requirement-Zuordnung](../../openspec/changes/declare-relation-origin/TRACEABILITY.md) · [Führender Aufgabenstatus](../../openspec/changes/declare-relation-origin/tasks.md).
