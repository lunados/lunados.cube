# Deliver remote and ordered cells

Status: decided · 2026-11-02 · [MILE-006](../../../docs/02-Milestones/MILE-006-remote-and-order.md) · noch nicht umgesetzt

## Why

MILE-005 hat Abdeckung, Instanzbindung und Zellzustände lokal umgesetzt. Drei Dinge fehlen, bevor weitere Fähigkeiten gebaut werden: Die Prüfung ist remote nicht verfügbar, die Matrix ordnet nach erstem Auftreten statt in deklarierter Reihenfolge (PO-5), und die Darstellung wurde nie von Menschen gelesen.

## What Changes

- G5-Kern mit P1.12 (`binding-context/8`, `0.7.0-proof`), Host-Abnahme live.
- VP-10 0.10.1 (opt-in) mit `axis_order` und Rückkopplungsmarke; 0.10.0 byte-gleich.
- Kurze, angeleitete Sichtprüfung der Darstellung durch den Nutzer (D-6, revidiert).

## Capabilities

### New Capabilities

- `remote-coverage-validation`: `/8` über den Remote-Connector.
- `declared-axis-order`: Matrix in deklarierter Reihenfolge mit DSM-Lesart.
- `readability-check`: kurze Sichtprüfung mit Anleitung und ja/nein-Prüfpunkten.

## Impact

G5-Kern (P3), neuer VP-10-Stand (P2), Anleitung zur Sichtprüfung (docs). Keine Änderung an P0, P1.1–P1.12, VP-07, VP-09, VP-10 0.10.0 oder der Morphologie. Grobe Planung: 1,75–2,25 PT.
