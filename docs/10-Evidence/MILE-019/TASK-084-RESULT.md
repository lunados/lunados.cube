# TASK-084 — Token-Einrichtung und Widerruf: Ergebnis

Stand: 2026-11-06, 14:47 UTC. Worker: `aiaeao-cube-g5-gateway`. Endpunkt: `https://aiaeao-cube-g5-gateway.jo-885.workers.dev/mcp`.

## Ausgeführt

- [Betriebsanleitung](../../../P3/remote-mcp-g5/docs/06_BETA_TOKEN_OPERATIONS.md) für Platzbelegung, sichere Ausgabe, Erneuerung und Widerruf geschrieben. Sie enthält keine Token-Werte oder Empfängerzuordnung.
- Ausgangsmetadaten per `wrangler secret list`: nur `MCP_BEARER_TOKEN` (`secret_text`). Zwölf verschiedene, zufällige 64-Zeichen-Werte für `MCP_BETA_TOKEN_01` bis `_12` lokal im macOS Keychain unter `aiaeao-g5-beta-token-01` bis `-12` erzeugt und wieder ausgelesen. Kein Token-Wert wurde in Shell-History, Datei, Chat oder Nachweis ausgegeben.
- Alle zwölf Beta-Werte in **einem** `wrangler secret bulk`-Vorgang als Worker Secrets übertragen. Die nachfolgende Secret-Liste zeigte alle zwölf Namen und weiterhin `MCP_BEARER_TOKEN`, jeweils mit Typ `secret_text`. Cloudflare zeigt die gespeicherten Werte nicht wieder an; der Nachweis umfasst erfolgreichen Upload und Metadaten, keinen Rückvergleich der Werte.
- Platz `MCP_BETA_TOKEN_12` vor Ausgabe einmal mit einem neuen Wert ersetzt. Der neue lokale Keychain-Wert wurde geprüft; Cloudflare bestätigte die Einzelplatz-Aktualisierung und zeigte danach den Platz sowie den Entwickler-Secret-Namen weiter an. Es wurde kein Token an einen Empfänger ausgegeben.

## Live-Beobachtung

Der erste Versuch, den Entwicklerzugang zu prüfen, lieferte `403`, aber mit Cloudflare `error code: 1010` **vor dem Worker**. Dieser Versuch zählt ausdrücklich nicht als Auth-Nachweis. Mit einem üblichen HTTP-Client-Header war `GET /health` vom Worker erreichbar und meldete `0.3.0-proof`. Vor dem Wechsel von Platz 12 waren die Worker-Antworten: Entwickler-Token `400` auf absichtlich ungültiges MCP-JSON, Platz 01 `401`, falscher Token `401`, Entwickler-Token mit unerlaubter Origin `403`. Nach dem Wechsel: Entwickler-Token `400`, Platz 01 `401`, Platz 12 `401`, falscher Token `401`, Entwickler-Token mit unerlaubter Origin `403`. Damit blieb der Entwicklerzugang bei einem tatsächlichen Secret-Wechsel erhalten. `400` bedeutet hier nur: Bearer-Gate passiert, danach MCP-Protokollfehler; es ist kein vollständiger MCP-Smoke.

## Grenze für TASK-085

Der Live-Worker meldet weiterhin `0.3.0-proof` und akzeptiert die Beta-Tokens **noch nicht**. Der MILE-019-Gateway-Quellcode ist nicht deployt. Positive Beta-Authentifizierung, individueller Widerruf mit `401` nach zuvor positivem Beta-Zugang, R10-Remote-Smoke sowie Codex-/Claude-Host-Verbindungen gehören zu [TASK-085](../../05-Tasks/TASK-085-beta-token-acceptance.md). Die zwölf Plätze sind vorbereitet und nicht verteilt.
