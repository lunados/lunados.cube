# Design — Kontrollfluss prüfen

Status: decided · Umsetzung offen

## Context

Entscheidungen D-1–D-8 in [MILE-008](../../../docs/02-Milestones/MILE-008-control-flow.md) (entschieden 2026-11-02).

## Decisions

- **Profil (D-2, D-3):** P1.13 erweitert `/8` zu `/9` um `control_flow`; der Validator projiziert `/9` auf `/8` und prüft P1.12 unverändert, dazu Wohlgeformtheit und Flussbindung.
- **Spurprüfung (D-4, D-5, D-6):** reine LIB-Funktion; Bedingungen werden nie ausgewertet, nur aufgezeichnete Ergebnisse gelesen. FAIL nur bei belegtem Verstoß, UNRESOLVED bei fehlender Abdeckung oder fehlenden Bedingungsergebnissen.
- **Auslieferung (D-7):** lokal; Darstellung und G5 später.

## Risks

- Prozessnutzen ist laut Lernbilanz an einen bestätigten Anwendungsfall gebunden.
- Handgeschriebene Spuren; Engine-Logs (Korrelation, Zeitstempel) bleiben ungeprüft.
