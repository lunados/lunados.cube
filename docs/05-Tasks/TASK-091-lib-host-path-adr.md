# TASK-091 — D-3 als Host-Pfad-ADR festhalten

Planungsstand: ausgearbeitet; [ADR-001](../07-ADR/ADR-001-lib-snapshot-host-path.md) und [Nachweis](../10-Evidence/MILE-020/TASK-091-RESULT.md) erstellt. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/archive/2026-11-06-declare-module-capabilities/tasks.md).

Story: [US-040](../04-US/US-040-descriptor-boundaries.md) · Mile: [MILE-020](../02-Milestones/MILE-020-module-capability-descriptors.md) · Aufwand: 0,125–0,25 PT (Schätzung)

## Ziel und Arbeit

Unter docs/07-ADR eine nächste freie ADR-ID verwenden. Nutzerentscheidung vom 2026-11-06 festhalten: gepinnter direkter Lib-Stand für Build/Tests und Host-Snapshot zur Laufzeit, in beiden Fällen INDEX.json-Hash führend. Entry-Hashes aus dem INDEX bleiben zusätzlich prüfbar. Kontext, Alternativen, Folgen, fehlender/falscher Hash und Abweichung zur MILE-071-Zielformulierung beschreiben; im Relay eine dokumentarische Folge-/Verweisnotiz planen, ohne dessen Baseline stillschweigend umzuschreiben.

## Abnahme und Nachweis

ADR referenziert D-3 und die konkreten aktuellen Leserquellen. Eine Entscheidungstabelle beschreibt gleiche Bytes über zwei Pfade, fehlenden Snapshot und Hashmismatch. Pfadname allein belegt keine Gleichheit; bei Mismatch kein stiller Wechsel auf Nachbar-Checkout oder latest. Bestehendes Verhalten, beschlossene Regel und künftig nötige Umsetzung sind klar getrennt.

Nachweis: [TASK-091-RESULT](../10-Evidence/MILE-020/TASK-091-RESULT.md) mit Quellenpins und Verweisen auf owner-lokale Artefakte.

## Abhängigkeiten und Grenze

Voraussetzungen: TASK-086; unabhängig von D-1/D-2/D-4.

Nur ADR und dokumentarische Folgen; kein Host-Loader, Laufzeitumbau oder Nachweis einer bereits vorhandenen Host-Anbindung.
