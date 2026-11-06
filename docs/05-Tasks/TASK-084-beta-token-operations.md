# TASK-084 — Token-Einrichtung und Widerruf

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/beta-token-access/tasks.md).

Stories: [US-036](../04-US/US-036-beta-access.md), [US-037](../04-US/US-037-beta-revocation.md) · Mile: [MILE-019](../02-Milestones/MILE-019-beta-token-access.md) · Aufwand: geschätzt 0,25–0,5 PT

## Ziel und Arbeit

Eine kurze [Betriebsanleitung](../../P3/remote-mcp-g5/docs/06_BETA_TOKEN_OPERATIONS.md) für Erzeugung, sichere Aufbewahrung, Ausgabe, Erneuerung und Entzug der bis zu zwölf Beta-Tokens schreiben. Jeden Platz getrennt führen; Empfängerzuordnung außerhalb des Repositorys halten. Cloudflare Worker Secrets statt Wrangler-`vars` verwenden. Bei der Live-Einrichtung den bestehenden Entwickler-Token vor und nach dem Secret-Wechsel prüfen und keine Token-Werte in Chat, Shell-History oder Nachweis kopieren.

## Abnahme und Nachweis

Die Anleitung zeigt, wie ein einzelner Platz belegt, ersetzt und entfernt wird. Ein Nachweis dokumentiert nur Secret-Namen/Platz-IDs, Zeitpunkt und beobachtete Ergebnisse. Die tatsächliche Live-Einrichtung wird erst als erledigt markiert, wenn Cloudflare-Secrets vorhanden und geprüft sind; eine reine Anleitung genügt dafür nicht.

## Abhängigkeiten und Grenze

[TASK-083](TASK-083-beta-token-gateway.md) vor Live-Einrichtung. Die Anzahl zwölf ist eine Obergrenze, keine Pflicht, sofort zwölf gültige und verteilte Tokens zu erzeugen.
