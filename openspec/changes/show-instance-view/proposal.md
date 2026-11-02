# Show instance view

Status: proposed · 2026-11-02 · [MILE-009](../../../docs/02-Milestones/MILE-009-instance-view.md) · Entscheidungen offen

## Why

Keine Sicht gruppiert nach Prozessinstanz; welcher Pfad in einer Instanz genommen wurde und welcher Eingang eines Joins fehlt, ist nur im JSON-Ergebnis von `analyze.trace-conformance/v1` lesbar (V-10, V-11, V-12; VR-12).

## What Changes

- Paket VP-11 `cube.instances`: Instanzrahmen, genommener Pfad, Join je Eingang, Regelverstöße; liest `binding-context/9` und optional das LIB-Ergebnis als Datensatz.
- Printer `vpinstances` in G6 (lokal).
- Kurze Sichtprüfung.

## Capabilities

### New Capabilities

- `instance-view`: Prozessspur je Instanz mit genommenem Pfad und Join-Status, Urteil aus lunados.lib gelesen.

## Impact

Neues P2-Paket, G6-Option (P3 lokal). Keine Änderung an P0, P1, VP-07–VP-10, lunados.lib oder der Morphologie. Grobe Planung: 2–3,25 PT.
