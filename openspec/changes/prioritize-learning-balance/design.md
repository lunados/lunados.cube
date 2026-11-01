# Design — Lernbilanz und Maßnahmenwahl

Status: planned

## Context

Die [Lückenbilanz](../../../docs/09-Research/grammar-sampling/GAP-LEDGER.md) nennt zehn Lücken (G-01–G-10), vier Werkzeugbefunde und eine vorläufige Rangfolge. Die [Darstellungsübergabe](../../../docs/09-Research/visual-check/HANDOVER.md) ergänzt vier Kandidatenregeln und sieben Printer-Befunde. Leitfrage 1 (Envelope) ist „nicht direkt geprüft“, Leitfrage 4 (LENS/MODE/Achsen) „weitgehend offen“.

## Goals / Non-Goals

Offene Leitfragen mit kleinen Proben schließen oder präzisieren; alle Maßnahmen nach einem festen Rahmen reihen; MILE-005 ausplanen. Keine Implementierung, kein Menschentest, keine Nutzenmessung.

## Decisions

1. **D-1:** Nutzen wird für Architektursichten und Prozessspuren bewertet.
2. **D-2:** Vier Proben (E-1, E-2, L-1, L-2), Erwartung vor dem Lauf.
3. **D-3:** Ergebnis ist Lernbilanz plus Plan MILE-005, ohne Umsetzung.
4. **D-4:** Kein Menschentest.
5. Bewertungsrahmen vor der Bewertung committen; visuelle Regeln erben die Position ihrer Profil-/LIB-Voraussetzung.

## Risks / Trade-offs

Die Gewichtung nach D-1 senkt die DAG-/Impact-Maßnahmen (G-05, G-06), die in MILE-002 vorn lagen; das wird offen ausgewiesen. Proben mit vier Fällen belegen Ausdrückbarkeit, nicht Vollständigkeit des Envelope-Rahmens.

## Open Questions

- Welcher Envelope-Vertrag ist maßgeblich (`evaluator-result/v0.2` oder ein Nachfolger) und wo liegt seine versionierte Quelle?
- Ist MODE in P0 v9.4 an eine Prüfung gebunden oder nur beschreibend?
