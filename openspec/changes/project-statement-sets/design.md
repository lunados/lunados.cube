# Design — Aussagenmengen projizieren

Status: proposed · Umsetzung offen

## Context

Entscheidungen D-1–D-8 in [MILE-007](../../../docs/02-Milestones/MILE-007-statement-sets.md) (Vorschlag).

## Decisions

- **Aussagenmenge (D-2, D-3):** gleiche Aussageform wie `analyze.population/v1`; der Printer löst nur Referenten und Prädikate gegen den Kontext auf. Keine P1-Bewertung, Status `declared_unverified`.
- **Verdichtung (D-4):** reine LIB-Funktion; die Strategie ist Pflicht und steht im Ergebnis. Der Cube rechnet nicht nach, er liest das typisierte Ergebnis.
- **Darstellung (D-5, D-6):** `cube.cells` 0.11.0 als neues Profil; Achsen aus dem Kontext, Zeile = Subjekt; abgeleitete Einträge als Text „abgeleitet · n Quellen“, kein Farbwert. 0.10.x wird vor jedem Code gepinnt.
- **Auslieferung (D-7):** lokal, CLI und G6.

## Risks

- Die Zugehörigkeit Kind → Eltern muss deklariert sein; fehlt sie, kann nicht verdichtet werden (Fehler statt Annahme).
- Structurizr-Strategien sind aus der Dokumentation abgeleitet, nicht mit Structurizr ausgeführt (wie C4-02).
