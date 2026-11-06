# TASK-082 — Zugangsvertrag und Ausgangsstand

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/archive/2026-11-06-beta-token-access/tasks.md).

Stories: [US-035](../04-US/US-035-developer-access.md), [US-036](../04-US/US-036-beta-access.md), [US-037](../04-US/US-037-beta-revocation.md) · Mile: [MILE-019](../02-Milestones/MILE-019-beta-token-access.md) · Aufwand: geschätzt 0,25–0,5 PT

## Ziel und Arbeit

Den aktuellen Gateway/Core-Endpunkt und den vorhandenen Entwicklerzugang ohne Secret-Ausgabe festhalten. Vor Änderungen die Erwartungen für null, einen und zwölf Beta-Tokens, ungültige Werte, doppelte Werte und Entzug eines Platzes fixieren. Das Verhalten des bestehenden `MCP_BEARER_TOKEN` und die `401`-Grenze vor dem MCP-Handler bleiben explizit.

## Abnahme und Nachweis

Vor Implementierung liegen reproduzierbare Testfälle und eine kurze Ausgangsnotiz vor. Kein Token-Wert oder Klartext-Secret erscheint in ihnen. Die Szenarien der [Spezifikation](../../openspec/changes/archive/2026-11-06-beta-token-access/specs/g5-beta-token-gate/spec.md) sind auf diese Fälle abgebildet.

## Abhängigkeiten und Grenze

Keine Codeänderung in dieser Task; keine Cloudflare-Secret-Mutation. Voraussetzung für [TASK-083](TASK-083-beta-token-gateway.md).

## Ergebnis (2026-11-06)

Die [Ausgangsnotiz](../10-Evidence/MILE-019/TASK-082-BASELINE.md) dokumentiert den Code- und letzten belegten Live-Stand, die Grenzen der Aussage sowie die vor Implementierung fixierten [9 Fälle mit 36 Erwartungen](../../P3/remote-mcp-g5/gateway/tests/beta-token-contract.json). Bestehende Gateway-Tests: 10/10 bestanden. Ein erneuter Live-Zugriff und die neuen Beta-Fälle sind noch nicht ausgeführt; das ist Teil der späteren Tasks.
