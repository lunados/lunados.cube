# Design — Herkunft von Beziehungen

Status: decided · Umsetzung offen

## Context

Entscheidungen D-1–D-8 in [MILE-011](../../../docs/02-Milestones/MILE-011-relation-origin.md) (entschieden 2026-11-02). Grundlage: Lückenbilanz G-02, Darstellungsregel VR-01 und Mockup M-01A (MILE-003), Lernbilanz Rang 3 (MILE-004), Aussagenmengen und Verdichtung (MILE-007), Plansichten remote (MILE-010).

## Decisions

- **Profil (D-2, D-3):** P1.14 mit `binding-context/10`; `origin` als typisierter Parameter; `derived` mit Grundlage, `unknown` gültig, fehlend UNRESOLVED.
- **Sicht (D-4, D-5):** `cube.flow` 0.7.6 liest Aussagenmengen; Linienart nach Herkunft, Text immer, Pfeilspitze neutral; PO-1.
- **Auslieferung (D-6):** lokal und G5; andere Hosts später (D-7).
- **Abnahme (D-8):** Orakel und Pins vor Code; kurze Sichtprüfung.

## Risks

- Ein Profil verhindert keine falsche Angabe `declared`; der Quellenabgleich fehlt.
- Gestrichelt gegen gepunktet ist die schwächste Unterscheidung; der Text trägt die Herkunft auch allein.
- CPU-Grenze des G5-Workers bei großen Flusssichten.
