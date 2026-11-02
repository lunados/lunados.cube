# TASK-050 — Profil P1.13

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/check-control-flow/tasks.md).

Story: [US-026](../04-US/US-026-control-flow-profile.md) · Mile: MILE-008-B · Aufwand: 1,25–1,75 PT

## Ziel und Arbeit

Paket `P1/control-flow-profile-v1`: Schema `/9`, Validator (Projektion `/9` → `/8`, Kontrollfluss-Prüfungen), Diagnosen, unabhängiges Orakel vor Code, materialisierte Vektoren, Tests, Golden.

## Ergebnis und Akzeptanz

- Orakel vor Code; alle Vektoren wie erwartet; P0, P1.1–P1.12 byte-gleich (SHA256SUMS); alle P1-Suiten grün.

## Abhängigkeiten und Grenze

[TASK-049](TASK-049-control-flow-spec.md)

Umfang gemäß [MILE-008](../02-Milestones/MILE-008-control-flow.md). Keine Änderung an P0, P1.1–P1.12, P2 oder lunados.lib-Einträgen; neue Fähigkeiten als eigenes Profil und eigener LIB-Eintrag.
