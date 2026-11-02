# EPIC-011 — Herkunft von Beziehungen

Status: planned · Milestone: [MILE-011](../02-Milestones/MILE-011-relation-origin.md) · Voraussetzung: [EPIC-007](EPIC-007-statement-sets.md), [EPIC-010](EPIC-010-remote-plan-views.md)

## Ergebnis

Jede Beziehung trägt eine gebundene Herkunft (deklariert, abgeleitet, unbekannt). P1 prüft die Bindung, `cube.flow` zeigt sie als Linienart mit Text, lokal und remote.

## Umfang

- Profil P1.14 (`binding-context/10`) mit typisiertem Parameter `origin` und Grundlage für Ableitungen;
- VP-07 0.7.6: `cube.flow` mit Herkunftslinie, auch für Aussagenmengen;
- G4, G6 und G5; kurze Sichtprüfung.

Keine Berechnung von Herkunft oder Ableitung im Cube; kein Quellenabgleich mit Fremdmodellen.

## Akzeptanz

- Fehlende Herkunft ergibt UNRESOLVED, nie PASS; eine Ableitung ohne Grundlage ebenso.
- Ohne gebundene Herkunft ist keine Linie durchgezogen; die Herkunft ist ohne Farbe und ohne Linienart allein (Text) lesbar.
- Vorhandene Profile und Printer bleiben byte-gleich; remote = lokal.

## Stories

- [US-032 — Herkunft einer Beziehung deklarieren und prüfen](../04-US/US-032-relation-origin-profile.md)
- [US-033 — Herkunftslinie sehen](../04-US/US-033-origin-line-view.md)
