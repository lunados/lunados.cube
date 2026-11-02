# TASK-070 — Gesamtüberblick RELEASE_INDEX

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/record-current-state/tasks.md).

Story: [US-034](../04-US/US-034-current-state-recorded.md) · Mile: MILE-012 · Aufwand: 0,25 PT

## Ziel und Arbeit

`RELEASE_INDEX.md` im Repo-Root neu: Stand aller Schichten (P0 v9.4, P1.1–P1.14 mit Kontextversionen, P2 VP-01–VP-11 mit Profilen, lunados.lib-Einträge mit Verweis, P3 lokal G4/G6 und remote G5 `0.9.0-proof` mit Gateway `0.2.0-proof`), Einstiegspunkte, Prüfskripte, Verweis auf die Grenzen-Seite. Der VP-06-Text bleibt als Abschnitt „Historie“ erhalten.

## Ergebnis und Akzeptanz

- Versionen und Pfade stimmen mit dem Repo überein (geprüft per Skript); keine kaputten Links.

## Abhängigkeiten und Grenze

[TASK-069](TASK-069-g5-ledger-limits.md) (Verweis auf die Grenzen-Seite).

Umfang gemäß [MILE-012](../02-Milestones/MILE-012-record-current-state.md). Keine Änderung an Code oder Payloads.

## Ergebnis (2026-11-02)

- [`RELEASE_INDEX.md`](../../RELEASE_INDEX.md) beschreibt den Stand nach MILE-011: P0 v9.4 mit P0-Lock, P1 mit allen Paketen und Kontexten `/1`–`/10`, P2 VP-01–VP-11 mit Profilen, die gelesenen lunados.lib-Einträge, P3 lokal (Versionsangabe `0.3.0-rc1`, seitdem ohne neue Angabe erweitert), G5 `0.9.0-proof` mit Ledger und Grenzen-Seite, Public Reference MCP, Host-Integrationen; Prüfskripte. Der VP-06-Text vom 2026-10-24 steht unverändert unter „History“.
- Geprüft: alle Links lösen auf; jede genannte Profilversion steht im Code.

