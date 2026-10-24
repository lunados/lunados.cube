# Use Case B – Zed: Native Agent / externer ACP-Agent

**Status:** Zed unterstützt direkte Remote-MCP-Server mit HTTP-Headern laut aktueller offizieller Dokumentation; **G5-spezifische Zed Host Acceptance noch nicht durchgeführt.**

## Nativer Zed Agent

1. Zed öffnen → **Settings → AI → MCP Servers → Add Server → Add Remote Server**.
2. Name `aiaeao-cube-g5-remote`; URL `https://aiaeao-cube-g5-gateway.jo-885.workers.dev/mcp`.
3. Falls Header-Felder angeboten werden: `Authorization` als Headername und `Bearer <DEIN_PROOF_TOKEN>` als vollständigen Headerwert eintragen.
4. Die Konfiguration kann auch über **zed: open settings file** gepflegt werden:

```json
{
  "context_servers": {
    "aiaeao-cube-g5-remote": {
      "url": "https://aiaeao-cube-g5-gateway.jo-885.workers.dev/mcp",
      "headers": {
        "Authorization": "Bearer REPLACE_LOCALLY_WITH_PROOF_TOKEN"
      }
    }
  }
}
```

Dies ist **nur eine Vorlage**. Den Placeholder ersetzen, nur in der persönlichen Zed-Konfiguration speichern, **niemals** in einer geteilten Projektdatei oder einem Commit. Zed dokumentiert diese Header-Konfiguration in `context_servers`, aber keine verbindliche automatische Auswertung von macOS-Keychain-Referenzen in diesem Feld. Deshalb nicht `$(security ...)` oder `${VAR}` als funktionierende Zed-Syntax behaupten. Vor dem Eintragen prüfen, ob der lokale Client die Secrets sicher verwahrt. Der Proof-Token ist ein Shared Secret – beim Ablegen im Klartext entsteht ein entsprechendes Risiko.

5. Im MCP-Servers-Panel prüfen, ob der Server **active** erscheint.
6. Nativen Zed Agent öffnen und den Smoke-Prompt verwenden.

**Smoke-Prompt:**

> Nutze ausschließlich den MCP-Server `aiaeao-cube-g5-remote`. Rufe `cube_discover_surface` auf, prüfe sieben Tools und lese den P0-Index über `cube_read_reference`. Melde, ob die Calls wirklich remote ausgeführt wurden, und erfinde keine Resource-Discovery, falls diese im Host nicht verfügbar ist.

## Wichtige Grenze: Resources vs Tools

Zed beschreibt in seiner MCP-Dokumentation **Tools und Prompts** als unterstützte Features. Direkte Resource-Discovery darf für den Zed-Use-Case daher nicht vorausgesetzt werden. Für P0 ist `cube_read_reference` der ausdrücklich vorgesehene Tool-Fallback; Resource-Integration separat ausweisen, nicht simulieren.

## Externer Agent innerhalb von Zed (ACP)

Zed kann MCP-Server an ACP-Agents weiterreichen, **muss es aber nicht in jeder Agent-Konfiguration**. Es existieren zwei Integrationswege:

- **Zed-Forwarding:** Server in Zed konfigurieren, ACP-Agenten im Agent Panel starten, prüfen ob `cube_discover_surface` tatsächlich angeboten und aufgerufen wird.
- **Agent-native MCP-Konfiguration:** Derselbe externe Agent kann seinen eigenen HTTP-MCP-Connector nutzen. Dann liegt seine Authentifizierung und Policy **außerhalb** von Zed. Verbindungsweg ausdrücklich protokollieren.

Achtung: Zed-native Agent-Profile/Permissions gelten nicht automatisch für ACP-Agents. Prüfe die Agent-eigene Tool-Policy. **Nicht denselben Server doppelt konfigurieren**, ohne die zwei Toolquellen unterscheiden zu können.

## Kurze Zed-Abnahme

- MCP-Serverstatus **active**, sieben `cube_*`-Tools erkennbar.
- Mindestens `cube_discover_surface`, `cube_read_reference`, `cube_validate` und `cube_render_svg` mit geeigneten Fixtures tatsächlich aufgerufen.
- Authorization-Header vorhanden; fehlender Header darf nicht zum Auto-OAuth-Fluss des nicht-OAuth-fähigen G5-Proofs führen.
- P0/P1/P2 und Cross-Domain-Grenzen getrennt dokumentiert.
- Host-Ressourcenliste `NOT TESTED/UNSUPPORTED` statt falsch als `PASS` ausweisen.

**Verifizierte Quellen (24.10.2026):**
- https://zed.dev/docs/ai/mcp
- https://zed.dev/docs/ai/external-agents
- https://zed.dev/docs/ai/agent-settings
