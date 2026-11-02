# EPIC-006 — Remote nutzbar und lesbar

Status: planned · Milestone: [MILE-006](../02-Milestones/MILE-006-remote-and-order.md) · Voraussetzung: [EPIC-005](EPIC-005-completeness-and-instances.md)

## Ergebnis

Die MILE-005-Fähigkeiten sind über den Remote-Connector prüfbar. Die Zellzustands-Matrix ist in deklarierter Reihenfolge lesbar, und ihre Darstellung ist kurz von einem Menschen gesichtet.

## Umfang

- G5-Kern mit P1.12;
- VP-10 0.10.1 mit Achsenreihenfolge;
- Kurze, angeleitete Sichtprüfung (D-6, revidiert).

Keine neue Prüfsemantik, keine Änderung an P0, P1.1–P1.12, VP-07, VP-09 oder VP-10 0.10.0.

## Akzeptanz

- Live-Abnahme von `/8` über den Remote-Connector mit vorab festgelegten Erwartungen.
- VP-10 0.10.1 nach eigener Spezifikation; 0.10.0 byte-gleich.
- Sichtprüfung durchgeführt; jedes „nein“ behoben oder ausdrücklich als offen ausgewiesen.

## Stories

- [US-021 — `/8` remote prüfen](../04-US/US-021-remote-v8.md)
- [US-022 — Matrix in deklarierter Reihenfolge lesen](../04-US/US-022-declared-order.md)
- [US-023 — Kurze Sichtprüfung](../04-US/US-023-readability-test.md)
