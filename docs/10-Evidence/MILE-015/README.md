# MILE-015 — Nachweis

Stand: 2026-11-05 · Branch `feature/mile015-016-backlog` · lokal (G4); G5 nicht ausgeliefert

## Reihenfolge

| Schritt | Commit |
|---|---|
| Spezifikation `P1_15_ACCEPTANCE_SPEC.md` und unabhängiges Oracle SN-01…SN-14, vor jedem Laufzeitcode | d9483ae |
| Laufzeit P1.15, Referenz v2, Schema, Tests, G4-Dispatch und Discovery | 63e3e0b |

## Prüfungen (lokal, Container-Klon mit Test-Stub für `mcp`)

| Suite | Ergebnis |
|---|---|
| P1.15 `tests/test_p115.py` (Oracle SN-01…SN-14, Schema, Regression `/1…/10` byte-identisch, Konfigurationsfehler, Referenz v2, parallele Gateways) | 7 Tests OK |
| P1 alle Profile | OK |
| P2 `visual-printer-migration-v1` | 131 Tests OK |
| P3 `mcp-local` (inkl. `test_mile015_adapter.py`, Discovery auf 11 Kontexte) | 253 Tests OK |
| G5-Offline-Gate `verify_g5.py` | OK (unverändert, P1.15 nicht ausgeliefert) |

## Abnahme mit lunados.explorer (P1.15-06)

Blätter mit Bindungen werden als `binding-context/11` exportiert (Scope-Kette Policy ⊂ Blatt, Ausgänge als exklusives Gateway); der Printer liest die `/10`-Projektion.

| Blatt | Pläne P1 | Panels Ablauf / Phasen | X-Referenten |
|---|---|---|---|
| F01 | PASS | 19 / 3 | 1 ungebunden (UNRESOLVED, Profil fehlt) |
| F02 | PASS | 35 / 6 | – |
| F03a | PASS | 31 / 5 | XB1 FAIL (C-ADM-1, kein Principal – im Code belegte Lücke), XB2 UNRESOLVED (Authority ohne Quelle; Ressourcenbereich jetzt die Revision), 1 ungebunden |
| F04a | PASS | 33 / 6 | 1 ungebunden |
| F05 | PASS | 26 / 4 | XB1 **PASS** im Blatt-Scope, mit Ausgang „abgelehnt“ am Gateway |

Panelzahlen und Planstatus unverändert gegenüber MILE-014. Gegenproben am F05-Kontext: ohne `scope_nesting` → `P1_SCOPE_CONFLICT`; Ablehnung ohne Refusal → `P1_INSTANTIATION_CONDITION`; Ablehnung mit anderer Anfrage → `P1_ADMISSION_OUTCOME_CONFLICT`.

## Offen

- Bestätigung im venv des Nutzers (P1.15, P3).
- G5-Auslieferung als eigener Schritt.
