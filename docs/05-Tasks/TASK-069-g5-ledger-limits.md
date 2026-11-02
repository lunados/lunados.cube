# TASK-069 — G5-Ledger und bekannte Grenzen

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/record-current-state/tasks.md).

Story: [US-034](../04-US/US-034-current-state-recorded.md) · Mile: MILE-012 · Aufwand: 0,25 PT

## Ziel und Arbeit

`P3/remote-mcp-g5/G5_ACCEPTANCE.md` nachführen: R5 (MILE-010) mit Offline 88/88, Live 87/88 bzw. 86/88, Host 7/7; R6 (MILE-011) mit Offline 26/26, Live 25/26 dreimal, Host 9/9; „Production operations“ wird R7, offen und nicht geplant. Neue Seite `P3/remote-mcp-g5/KNOWN_LIMITS.md`: was remote zuverlässig geht, welche Aufrufe an der CPU-Grenze scheitern (belegt), der sporadische Abbruch ohne Ursache, Anmeldung per Bearer-Token, Ausweg lokal über G4/G6, Optionen für später (Workers Paid mit `limits.cpu_ms`, anderer Weg für schwere Aufgaben, OAuth).

## Ergebnis und Akzeptanz

- Jede Zahl ist auf einen Nachweis im Repo verlinkt; keine neue Behauptung ohne Beleg.

## Abhängigkeiten und Grenze

Keine.

Umfang gemäß [MILE-012](../02-Milestones/MILE-012-record-current-state.md). Keine Änderung an Code oder Payloads.

## Ergebnis (2026-11-02)

- [`G5_ACCEPTANCE.md`](../../P3/remote-mcp-g5/G5_ACCEPTANCE.md): R5 (Nachdeploy) als überholt, R5.PV mit Offline 88/88, Live 87/88, 87/88, 86/88, 87/88 und Host 7/7; neu R6 mit Offline 26/26 und 87/87, Live dreimal 25/26 und Host 9/9; „Production operations“ heißt jetzt R7, nicht geplant. Jede Zeile mit Belegen verlinkt.
- Neue Seite [`KNOWN_LIMITS.md`](../../P3/remote-mcp-g5/KNOWN_LIMITS.md): was remote geht, CPU-Abbrüche (139 ms in R5, 522 ms in R6), der Abbruch ohne Ursache, Bearer-Token, die gleich gebliebene Gateway-Version trotz neuem Argument `origin_lines`, kein Stabilitätsnachweis; Ausweg lokal über G4/G6; Optionen für später.
- G5-Prüfsummenliste nachgezogen (41 Dateien), `verify_release` grün.

