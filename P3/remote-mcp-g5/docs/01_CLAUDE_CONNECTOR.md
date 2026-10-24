# Use Case A – Claude / Claude Desktop / Claude.ai (Remote MCP)

**Status:** Remote-Connector wurde am 2026-10-24 durch Nutzer und Claude unabhängig geprüft. Nachweis: sieben Tools verfügbar; 27 echte Claude-MCP-Calls im Host-Abnahmebericht; formale MIME-Nachprüfung noch separat zu protokollieren.

## Voraussetzungen

- Remote-Endpunkt: `https://aiaeao-cube-g5-gateway.jo-885.workers.dev/mcp`.
- Cloudflare Worker Gateway Secret `MCP_BEARER_TOKEN` ist eingerichtet.
- Dasselbe Proof-Geheimnis liegt lokal im **macOS-Schlüsselbund** unter Service `aiaeao-g5-mcp-token`, Account `$USER`.
- Claude-Konto erlaubt Custom Connector mit **Request Headers**. Der Aufruf kommt bei Claude Remote Connectors aus Anthropic-Infrastruktur, nicht aus dem eigenen lokalen Browser.

## Einrichtung in Claude

1. Claude → **Customize → Connectors → Add custom connector** öffnen.
2. Name `AIAEAO Cube G5 Remote`, URL `https://aiaeao-cube-g5-gateway.jo-885.workers.dev/mcp`.
3. Authentication: **No sign in** – das bedeutet hier **kein OAuth-Login**, **nicht** tokenfreier MCP-Zugang.
4. Unter **Request headers** einen Eintrag mit Name `Authorization` und Wert `Bearer <DEIN_PROOF_TOKEN>` anlegen.
5. Speichern und den Connector in der gewünschten Konversation über **+ → Connectors** aktivieren.
6. Erst `cube_discover_surface` aufrufen, dann Tools nach Bedarf.

**Schlüsselbund → Zwischenablage, ohne Token-Ausgabe:**

```sh
printf 'Bearer %s' "$(security find-generic-password -a "$USER" -s 'aiaeao-g5-mcp-token' -w)" | pbcopy
```

In Claude als kompletten Header-Wert einsetzen, anschließend `printf '' | pbcopy` zum Leeren der Zwischenablage. Kein Secret in Prompt, Screenshot, Chat oder Repository. Connector-Konfigurationen mit festem Header übertragen das Secret an den externen Connector-Anbieter; nur für einen vertrauenswürdigen Host verwenden.

## Smoke-Prompt

> Verwende ausschließlich den Connector **AIAEAO Cube G5 Remote**. Rufe `cube_discover_surface` tatsächlich auf. Bestätige sieben MCP-Werkzeuge, 14 P0-Ressourcen (falls über Host sichtbar; sonst den Index über `cube_read_reference`) und `deployment.remote_mcp_available: true`. Gib keine Zugangsdaten aus. Trenne G5 Proof von Production Authorization.

## Akzeptanz / Sonderfälle

- `cube_get_capabilities` ist absichtlich nur die Legacy-P2-Card. Für den gesamten Cube `cube_discover_surface`.
- Claude Connector UI kann sich mit Produktversionen ändern; bei fehlender Header-Option **nicht** Bearer-Prüfung abschalten.
- Claude Remote Connector ≠ lokaler Claude Desktop `stdio`-Server. Für lokalen Offline-Zugriff G4-Profil getrennt behandeln und den verwendeten Connector im Testbericht nennen.
- Kein OAuth-Flow am G5-Server vorhanden; bei Client, der zwingend OAuth verlangt: `HOST_UNSUPPORTED`, keine Sicherheitslockerung.

**Verifizierte Quelle (24.10.2026):** https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp
