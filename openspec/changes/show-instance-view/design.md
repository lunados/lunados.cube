# Design — Instanzsicht

Status: decided · Umsetzung offen

## Context

Entscheidungen D-1–D-8 in [MILE-009](../../../docs/02-Milestones/MILE-009-instance-view.md) (entschieden 2026-11-02). Grundlage: VR-12 und Mockup M-12B aus MILE-003, Ergebnis von MILE-008.

## Decisions

- **Ort (D-2):** neues Paket VP-11; vorhandene Printer bleiben byte-gleich.
- **Eingabe (D-3):** `binding-context/9` und optional das LIB-Ergebnis als Datensatz; der Printer rechnet nicht nach.
- **Darstellung (D-4–D-6):** Instanzrahmen, „genommen“ / „nicht genommen“, Join je Eingang, „Regelverstoß“; ohne Urteil „nicht geprüft“; ohne Farbe unterscheidbar.
- **Auslieferung (D-7):** lokal, CLI und G6.

## Risks

- Der Nutzen ist laut Lernbilanz an einen bestätigten Prozess-Anwendungsfall gebunden; die Mile bleibt deshalb schlank.
- Mehrere Instanzen mit vielen Gateways können groß werden; das Layout muss deterministisch und lesbar bleiben.
