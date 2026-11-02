# Check control flow

Status: done · 2026-11-02 · archiviert · [MILE-008](../../../../docs/02-Milestones/MILE-008-control-flow.md) · [Nachweis](../../../../docs/10-Evidence/MILE-008/C-RESULT.md)

## Why

Zwei widersprüchliche Leitentscheidungen für denselben Token bestehen heute je einzeln; Bedingungsreihenfolge, Default und Exception sind nicht prüfbar; die erwarteten Eingänge eines Joins sind nicht Teil eines Vertrags (G-07; BPMN-01, BPMN-02). P1.12 bringt Instanzbindung und Populationsregeln, aber keine Gateway-Typen und keine Flussbindung.

## What Changes

- Profil P1.13 mit `binding-context/9`: deklarierter Kontrollfluss (exklusive und parallele Gateways, Flüsse, Bedingungsreihenfolge, Default) und Flussbindung der Spur-Aussagen.
- LIB `analyze.trace-conformance/v1`: Spur je Instanz gegen das Modell, typisiertes Ergebnis.
- `/9` im lokalen `cube_validate`; Wiederholung der BPMN-Fälle.

## Capabilities

### New Capabilities

- `control-flow-declaration`: Kontrollfluss deklarieren und Spur-Aussagen an deklarierte Flüsse binden.
- `trace-conformance`: beobachtete Spur je Instanz gegen das deklarierte Modell prüfen, außerhalb des Cube.

## Impact

Neues P1-Profil, neuer LIB-Eintrag, lokaler Adapter (P3). Keine Änderung an P0, P1.1–P1.12, P2 oder der Morphologie. Grobe Planung: 4–5,5 PT.
