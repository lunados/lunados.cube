# TASK-071 — Live-Ausgangswert R5 und R6

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/record-current-state/tasks.md).

Story: [US-034](../04-US/US-034-current-state-recorded.md) · Mile: MILE-012 · Aufwand: 0,25 PT

## Ziel und Arbeit

Der Nutzer lässt die vorhandenen Abnahmeskripte `r5_remote_acceptance.py` und `r6_remote_acceptance.py` einmal gegen den bereitgestellten Kern laufen; die Ergebnisse werden als Ausgangswert committet und in der Grenzen-Seite eingeordnet. Optional, nach Entscheidung des Nutzers: Rotation des Bearer-Tokens nach `DEPLOYMENT.md`, danach derselbe Lauf.

## Ergebnis und Akzeptanz

- Ein Lauf R5 und R6 committet; Abweichungen ausschließlich als benannte Grenzen; Entscheidung zur Rotation festgehalten.

## Abhängigkeiten und Grenze

[TASK-069](TASK-069-g5-ledger-limits.md).

Umfang gemäß [MILE-012](../02-Milestones/MILE-012-record-current-state.md). Keine Änderung an Code oder Payloads.

## Ergebnis (2026-11-02)

- Lauf durch den Nutzer gegen Kern `0.9.0-proof` und Gateway `0.2.0-proof`: Remote-Smoke, dann [R5](../../P3/remote-mcp-g5/evidence/G5_M12_BASELINE_R5.json) 86/88 und [R6](../../P3/remote-mcp-g5/evidence/G5_M12_BASELINE_R6.json) 25/26.
- Abweichungen: D-01 nur bei der Versionsangabe (R5 erwartet `0.8.0-proof`, bereitgestellt ist `0.9.0-proof`); P-K08-sequence und P-OL-07 mit `G5_CORE_UNAVAILABLE`. Alle anderen Aufrufe byte-gleich. Vom Nutzer als bekannte Grenzen hingenommen; eingeordnet in [`KNOWN_LIMITS.md`](../../P3/remote-mcp-g5/KNOWN_LIMITS.md).
- Token-Rotation: nicht durchgeführt; der Nutzer belässt den bestehenden Bearer-Token.

