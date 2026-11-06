# TASK-085 — Live- und Host-Abnahme: Ergebnis

Stand: 2026-11-06, 15:10 UTC; Claude-Host-Nachweis ergänzt um 15:45 UTC. Am 2026-11-06 vom Nutzer zunächst mit ausstehender manueller Claude-Host-Prüfung akzeptiert; diese Prüfung ist inzwischen erfolgt (siehe Hosts). Den Abschluss von MILE-019 erklärt der Nutzer.

## Bereitstellung und lokale Prüfung

- Gateway-Version in MCP-Serverinfo und `/health` auf `0.4.0-proof` gesetzt; R10-Erwartungsdatei historisch unverändert, R10-Live-Skript mit optionaler Gateway-Version erweitert.
- `npm run check:freeze`: 20/20 Tests; `verify_g5.py`: 26/26 Python-Vertragstests; `npm run dry-run`: Bundle erfolgreich (1.226,71 KiB); `verify_release.py --require-npm-lock`: 56/56 Quellhashes und Lock-Prüfung bestanden.
- Nur `aiaeao-cube-g5-gateway` am bestehenden Endpunkt `https://aiaeao-cube-g5-gateway.jo-885.workers.dev/mcp` veröffentlicht. Die erste Code-Bereitstellung meldete Cloudflare-Version `99096665-81d1-4b3f-8574-d42a91448c16`; die nachfolgenden Secret-Wechsel erzeugten weitere Worker-Versionen. Die aktuelle sichtbare Gateway-Version aus `/health` ist `0.4.0-proof`. Der private R10-Core wurde nicht neu bereitgestellt.

## HTTP- und MCP-Ergebnisse

| Prüfung | Erwartet | Beobachtet |
| --- | --- | --- |
| `GET /health` | `200`, `0.4.0-proof` | `200`, `0.4.0-proof` |
| `POST /mcp` ohne oder mit falschem Bearer | `401` | jeweils `401` |
| Entwickler, Beta 01, Beta 02, Beta 12 mit absichtlich ungültigem MCP-JSON | Auth-Gate passiert, danach Protokollfehler | jeweils `400` |
| Beta 01 mit unerlaubter Origin | `403` nach Authentifizierung | `403` |
| Beta 12 nach individuellem Secret-Entzug | alter Wert `401`, Entwickler und Beta 01 weiter zugelassen | `401`, `400`, `400` |
| Beta 12 nach Neubelegung | alter Wert `401`, neuer Wert, Entwickler und Beta 01 zugelassen | `401`, `400`, `400`, `400` |

Die `400`-Antworten sind bewusst **keine** MCP-Erfolgsnachweise; sie zeigen nur das bestandene Auth-Gate. Die echten MCP-Läufe stehen separat in [Entwickler-Smoke](TASK-085-REMOTE-SMOKE.json), [Beta-01-Smoke](TASK-085-BETA-01-MCP.json), [Beta-02-Smoke](TASK-085-BETA-02-MCP.json) und [R10-Live-Prüfung](TASK-085-R10-LIVE.json). Alle drei Smoke-Läufe bestanden mit zehn Tools, 14 Ressourcen, P0/P1 und SVG-Byte-Parität. R10 bestand **58/58** mit erwarteter Gateway-Version `0.4.0-proof` und Core-Version `P3-MCP-REMOTE/0.9.3-proof`.

## Hosts und öffentliche Referenz

- **Codex CLI:** Ein flüchtiger, schreibgeschützter Host-Lauf nutzte Beta-Platz 01 über den vorhandenen lokalen G5-Protokolladapter. Der tatsächliche MCP-Aufruf `cube_discover_surface` endete erfolgreich; `release.version` war `P3-MCP-REMOTE/0.9.3-proof`, `deployment.remote_mcp_available` war `true`. Das ist eine Host-Prüfung der CLI-Sitzung, keine dauerhaft eingerichtete neue Verbindung im Codex-Desktop.
- **Claude:** Der Nutzer hat am 2026-11-06 in claude.ai einen eigenen Custom Connector (`Lunados CUBE BETA PRO`) mit Beta-Token im Request-Header `authorization` eingerichtet, getrennt vom bestehenden Proof-Connector, und die Verbindung als erfolgreich bestätigt. Welcher Beta-Platz verwendet wurde, ist hier nicht protokolliert. Über denselben Connector rief Claude in dieser Sitzung um etwa 15:45 UTC `cube_discover_surface` auf: `release.version` war `P3-MCP-REMOTE/0.9.3-proof`, `deployment.remote_mcp_available` war `true`, `deployment.remote_transport` `streamable_http`, zehn Tools. Das entspricht der [Prüfanweisung](../../../P3/remote-mcp-g5/docs/01_CLAUDE_CONNECTOR.md#mile-019-beta-host-prüfung-2026-11-06).
- **Öffentliche Referenz:** Unabhängiges, unauthentifiziertes `cube_read_public_reference` lieferte das aktuelle Manifest `v9.4` von `https://cube.lunados.net/manifest.json`; das aus dem Manifest gelesene Asset `core` von `https://cube.lunados.net/v9.4/core.json` meldete `sha256_verified: true`. Es wurde kein Beta-Token verwendet.

## Offene Grenze

Beide Host-Verbindungen (Codex CLI, Claude) sind mit je einem Beta-Token und einem read-only Aufruf beobachtet. Nebenbefund ohne Bezug zum Token: Die G5-Discovery meldet für `vplandscape` nur `P2-VP-LANDSCAPE/0.12.0`; das lokal vorhandene `0.12.1` aus MILE-018 ist remote noch nicht bereitgestellt. Token-Werte, Header und Empfängerzuordnungen sind in keinem Nachweis enthalten. Der Gateway bleibt ein G5-Proof mit den Grenzen aus [KNOWN_LIMITS.md](../../../P3/remote-mcp-g5/KNOWN_LIMITS.md), keine allgemeine Produktionsfreigabe.

Der bereitgestellte Quellstand und die MILE-019-Dokumente liegen derzeit als lokale, noch nicht committete Arbeitskopie vor.
