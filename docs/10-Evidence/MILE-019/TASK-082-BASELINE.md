# TASK-082 — Ausgangsstand und fixierter Zugangsvertrag

Datum: 2026-11-06 · Ergebnis: Task-Planung und erwartete Authentifizierungsfälle vor Gateway-Implementierung fixiert · Live-Zugang in dieser Task nicht erneut geprüft

## Ausgangsstand aus Repository und letztem Live-Nachweis

- Der konfigurierte MCP-Endpunkt ist `https://aiaeao-cube-g5-gateway.jo-885.workers.dev/mcp` ([G5-Statuskarte](../../../P3/remote-mcp-g5/docs/G5_CLIENT_AND_GATE_STATUS.json)); die Statuskarte enthält eine ältere Versions-ID und ist **kein** aktueller Live-Nachweis.
- Das [Gateway](../../../P3/remote-mcp-g5/gateway/src/index.mjs) exponiert `/health` und `POST /mcp`. `POST /mcp` prüft das erforderliche Worker Secret `MCP_BEARER_TOKEN` mit Mindestlänge 32, weist fehlende/falsche Bearer-Werte mit `401` ab und prüft erst danach Origin, Requestgröße und MCP-Handler. Fehlt das erforderliche Secret oder ist es zu kurz, antwortet der Gateway `503`. Ein `GET /mcp` erhält `405` vor der Authentifizierungsprüfung.
- Das [Gateway-Wrangler-Manifest](../../../P3/remote-mcp-g5/gateway/wrangler.jsonc) bindet `CORE` an `aiaeao-cube-g5-core`. Das [Core-Manifest](../../../P3/remote-mcp-g5/python-core/wrangler.jsonc) hat `workers_dev: false` und `preview_urls: false`.
- Der letzte dokumentierte Live-Lauf ist [R10 vom 2026-11-05](../../../P3/remote-mcp-g5/G5_R10_ACCEPTANCE.md): Core `0.9.3-proof`, Gateway `0.3.0-proof`, allgemeiner Remote-Smoke PASS und R10 58/58. Dieser Lauf belegt den damaligen Entwicklerzugang und die damalige Bereitstellung. Er beweist nicht, dass der Endpunkt heute unverändert antwortet.
- `MCP_BEARER_TOKEN` ist laut [Bearer-Gate-Anleitung](../../../P3/remote-mcp-g5/docs/04_BEARER_API_TOKEN_GATE.md) als Cloudflare Worker Secret eingerichtet. Sein Wert wurde für diese Task weder gelesen noch ausgegeben. Der Gateway-Code enthält derzeit keine Beta-Token-Plätze.

## Vor Implementierung fixierte Fälle

Die [Fallliste](../../../P3/remote-mcp-g5/gateway/tests/beta-token-contract.json) enthält **9 Konfigurationen und 36 einzelne Erwartungen**. Sie benutzt nur symbolische Credential-Labels. TASK-083 soll aus den Labels unterscheidbare synthetische Testwerte ableiten, niemals reale Secrets. `pass` bedeutet: Das Authentifizierungstor lässt die Anfrage zum bestehenden MCP-Handler durch; es behauptet keinen HTTP-200-Status für einen beliebigen MCP-Body.

| Fall | Abdeckung | Spezifikationsbezug |
|---|---|---|
| BETA-00 | Kein Beta-Secret, Entwickler weiter gültig, fehlender/fremder Token `401` | Entwicklerzugang; Authentifizierung vor MCP |
| BETA-01 | Ein Beta-Token parallel zum Entwickler-Token | Beta-Tokens |
| BETA-02 | Alle zwölf Plätze einzeln akzeptiert, dreizehnter Wert abgelehnt | Bis zu zwölf Beta-Tokens |
| BETA-03 | Zu kurzer Beta-Wert abgelehnt, Entwickler gültig | Fehlerhafter Beta-Platz |
| BETA-04 | Doppelt belegter Beta-Wert abgelehnt, anderer Beta-Wert gültig | Zu kurzer oder doppelt belegter Beta-Wert |
| BETA-05 | Ein Beta-Platz entfernt, alter Wert abgelehnt, anderer Beta- und Entwickler-Token gültig | Einzelner Widerruf |
| BETA-06 | Ein Beta-Platz ersetzt, alter Wert abgelehnt, neuer und andere Werte gültig | Einzelner Widerruf |
| BETA-07 | Gültiger Token mit falschem Origin `403`; ungültiger Token mit falschem Origin `401` | Authentifizierung vor MCP und bestehende Origin-Reihenfolge |
| BETA-08 | Fehlender Entwickler-Token `503` auch bei belegtem Beta-Platz | Entwickler-Secret fehlt |

Die tatsächliche Codex-/Claude-Verbindung der Spezifikation gehört zu [TASK-085](../../05-Tasks/TASK-085-beta-token-acceptance.md), nicht zu diesen lokalen Authentifizierungsfällen. Für den Einzelwiderruf müssen Entwickler- und Beta-Werte verschieden sein. Das wird bei der Ausgabe in [TASK-084](../../05-Tasks/TASK-084-beta-token-operations.md) geprüft; derselbe Bearer-Wert kann am Gateway nicht als zwei verschiedene Besitzer unterschieden werden.

## Prüfung am 2026-11-06

- `node --test tests/security.test.mjs tests/freeze.test.mjs` im Gateway: **10/10 bestanden** (bestehender Code, vor TASK-083).
- JSON der Fallliste geparst: 9 eindeutige Fall-IDs, 36 Checks, ein Fall mit zwölf belegten Beta-Plätzen.
- Keine Codeänderung und keine Cloudflare-Secret-Mutation in TASK-082. Live-HTTP, aktueller Entwickler-Token, Beta-Verbindung und Widerruf bleiben für TASK-085 offen.
