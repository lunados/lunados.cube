# TASK-076 — P1.15: Scope-Ketten, Referenz v2 und Ausgänge der Admission

Mile: [MILE-015](../02-Milestones/MILE-015-scopes-and-admission-outcomes.md) · Aufwand: 1,25–1,75 PT · Status: erledigt (lokal), 2026-11-05

## Ziel und Arbeit

Neues Profil `P1.15/scope-nesting-profile-v1` mit `binding-context/11` (Spezifikation [P1_15_ACCEPTANCE_SPEC.md](../../P1/scope-nesting-profile-v1/P1_15_ACCEPTANCE_SPEC.md)):

- **B1** deklarierte Scope-Ketten (`scope_nesting`), strukturell geprüft (SN-1…SN-7);
- **B2** P1.6-Referenz v2 mit Revision und Artefakt als Ressourcenbereich der Authority;
- **B3** Ausgänge einer Admission als P1.6-Instanzen an einem exklusiven Gateway (AO-1…AO-3).

Reihenfolge: Spezifikation und unabhängiges Oracle (SN-01…SN-14) vor dem Code; dann Laufzeit, Tests, G4-Dispatch; zuletzt Abnahme mit den Fällen aus lunados.explorer.

## Akzeptanz

P1.15-01…06 der Spezifikation. `/1…/10` byte-identisch.

## Ergebnis

- SN-01…SN-14 gegen das vorab committete Oracle (d9483ae); P1.15 7 Tests, P1 alle, P2 131, P3 253 Tests grün; G5-Offline-Gate unverändert.
- lunados.explorer: F05 im Blatt-Scope PASS mit zwei Ausgängen; F03a XB2 bindet die Revision; alle Pläne der fünf Fälle P1 PASS, Panelzahlen unverändert ([Nachweis](../10-Evidence/MILE-015/README.md)).

## Abhängigkeiten und Grenze

MILE-014. Keine Änderung an P0, P1.1…P1.14 und am Printer; G5 als eigener Schritt.
