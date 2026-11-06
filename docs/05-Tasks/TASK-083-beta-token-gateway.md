# TASK-083 — Gateway für parallele Tokens

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/beta-token-access/tasks.md).

Stories: [US-035](../04-US/US-035-developer-access.md), [US-036](../04-US/US-036-beta-access.md), [US-037](../04-US/US-037-beta-revocation.md) · Mile: [MILE-019](../02-Milestones/MILE-019-beta-token-access.md) · Aufwand: geschätzt 0,5–0,75 PT

## Ziel und Arbeit

Das bestehende Gateway akzeptiert neben `MCP_BEARER_TOKEN` bis zu zwölf **optionale**, getrennte Cloudflare Worker Secrets `MCP_BETA_TOKEN_01` bis `_12`. Der bestehende Entwickler-Token bleibt Pflicht und gültig. Nur ausreichend lange, eindeutige Beta-Tokens gelten; leere, kurze oder mehrfach belegte Werte dürfen keine Beta-Berechtigung auslösen. Die Prüfung liegt vor Origin-, Body- und MCP-Verarbeitung wie bisher. Keine Änderung am privaten Core, an Werkzeugen oder am Endpunkt.

## Abnahme und Nachweis

Gezielte Gateway-Tests decken die in TASK-082 fixierten Fälle ab. Ein fehlender Beta-Platz verhält sich wie bisher; zwölf gültige Plätze funktionieren; Entzug eines Platzes entzieht nur dessen Wert. Syntax-, Gateway- und G5-Offline-Prüfung sind grün. Live- und Host-Ergebnisse gehören erst zu [TASK-085](TASK-085-beta-token-acceptance.md).

## Abhängigkeiten und Grenze

[TASK-082](TASK-082-beta-auth-contract.md). Keine Token-Werte im Code, in Fixtures oder in Ausgaben. Kein OAuth, Access oder zweites Deployment.

## Ergebnis (2026-11-06)

Das Gateway akzeptiert lokal den bestehenden Entwickler-Token und bis zu zwölf getrennte optionale Beta-Tokens. Die [Ergebnisnotiz](../10-Evidence/MILE-019/TASK-083-RESULT.md) enthält die ausgeführten Prüfungen und Grenzen: 20/20 Gateway-Tests, G5-Offline-Gate mit 26 Vertragstests, Wrangler-Bundle und 55 Quell-Hashes bestanden. Kein Secret wurde eingerichtet und kein Live-Endpunkt verändert.
