# Use Case C – Unabhängiger MCP-Agent / SDK-Client

**Ziel:** Der unabhängige Host authentifiziert sich eigenständig, liest Capability Surface und ruft Tools auf – ohne lokale G4 `stdio`-Verbindung oder den Claude Cloud Connector.

## Mindestvertrag eines Remote-Clients

- **Transport:** MCP Streamable HTTP (G5-Gateway: `POST /mcp`). Protokoll `2026-07-28`; Legacy-Handshake wird im Proof abgewiesen.
- **Authentifizierung:** HTTP `Authorization: Bearer <PROOF_TOKEN>` auf **jedem geschützten MCP-Request**.
- **Origin:** Native Clients lassen i. d. R. `Origin` weg. Bei vorhandenem `Origin` muss er exakt mit `MCP_ALLOWED_ORIGIN` im Gateway übereinstimmen; Standard ist Ablehnung aller Origin-Header.
- **Operationen:** sieben MCP-Tools; 14 P0-Resources (falls Host Resources unterstützt); `cube_read_reference` als Tool-Fallback.
- **Resultatsemantik:** Fachliches P1 `FAIL` ist kein Transportfehler; MCP-Fehler bei ungültiger Adapter-Konfiguration; Truth/Authority/Admission nicht inferieren.
- **Keine** freie REST-API, kein Shell-/Dateisystem-Werkzeug, kein automatisches ACG→SVG.

## Echte Remote-SDK-Abnahme (auf dem vorhandenen Mac)

Im Repository-Wurzelverzeichnis:

```sh
cd "$HOME/Downloads/lunados.cube"
source P3/adapters/mcp-local/.venv/bin/activate
export AIAEAO_G5_URL='https://aiaeao-cube-g5-gateway.jo-885.workers.dev/mcp'
export AIAEAO_G5_TOKEN="$(security find-generic-password -a "$USER" -s 'aiaeao-g5-mcp-token' -w)"
python3 P3/remote-mcp-g5/scripts/sdk_remote_smoke.py \
  --evidence P3/remote-mcp-g5/evidence/G5_R3_REMOTE_RECHECK_SANITIZED.json
unset AIAEAO_G5_TOKEN
```

`--evidence` wird vom bereits konsolidierten Skript unterstützt. Das JSON enthält nur normalisierte Status-/Hash-/Versionsergebnisse, **keinen Bearer-Token**. Vor einer Veröffentlichung dennoch manuell prüfen, ob weitere sensible Nutzdaten in einem angepassten Skript hinzugefügt wurden.

**Abnahmekriterien:** 401 für falschen Token; 403 für unerlaubte Origin; sieben Toolnamen; 14 P0-Resources; exakte MIME-Typen aus P0-Lock; P1 `PASS/FAIL/UNRESOLVED`; P2 SVG-Bytes **clientseitig** gegen Golden-Datei verglichen; mehrfacher Render exakt identisch.

## Unabhängiger Agent via Zed ACP

Zed Agent/ACP ist nicht automatisch ein unabhängiger MCP-Client mit eigener Tokenverwaltung. Für die Aussage *independent host* den tatsächlichen Agent-Namen, seine MCP-Verbindungsart und Tool-Call-Protokolle dokumentieren. Zed kann MCP weiterreichen; native Konfiguration des ACP-Agenten kann eine zweite Quelle sein. Siehe `02_ZED_REMOTE_MCP.md`.

## In einer anderen MCP-fähigen Anwendung

1. Eigene **Remote HTTP MCP** Serverdefinition anlegen (nicht G4 `stdio`).
2. Exakte URL und `Authorization`-Header eintragen.
3. Erst `tools/list` und `cube_discover_surface` remote durchführen.
4. Für P0 via Resources oder `cube_read_reference`, für P1 `cube_validate`, für P2 deklarierte Prepare/Check/Render-Jobs einsetzen.
5. Tatsächliche Serverantworten, Hashes und `isError` getrennt protokollieren; keine Toolnamen erfinden.
6. Fehlende Bearer-Header-Unterstützung oder nur OAuth im Host als `HOST_UNSUPPORTED` protokollieren; Gateway-Auth niemals deaktivieren.

## Minimaler Agent-Prompt

> Verwende ausschließlich den konfigurierten AIAEAO-G5-Remote-MCP-Server. Rufe `cube_discover_surface` tatsächlich auf, danach `cube_read_reference`, `cube_validate` und mit bekanntem VP-04-Job `cube_render_svg`. Melde aufgerufene Werkzeuge und tatsächliche Rückgaben. P1-Fachstatus nicht mit MCP-Error verwechseln. Keine Wahrheit, Authority oder Admission ableiten. Keine Secrets ausgeben. Nicht ausgeführte Prüfungen als `NOT TESTED` markieren.
