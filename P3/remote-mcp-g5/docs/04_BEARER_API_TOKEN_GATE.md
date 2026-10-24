# Use Case D – API-Token-Gate und Vertrauensgrenze

**Wichtig:** G5 implementiert ein **Bearer-Proof-Gate für den MCP-Endpunkt**, **keinen** API-Key-Service für beliebige Nutzer, **kein** OAuth und **kein** mandantenfähiges Autorisierungssystem.

## Ablauf im tatsächlichen Code

```text
Agent (Claude / Zed / SDK)
   │ POST https://aiaeao-cube-g5-gateway.jo-885.workers.dev/mcp
   │ Authorization: Bearer <Proof-Secret>
   ▼
Cloudflare Gateway [P3 JS, öffentlich]
   ├─ /health: GET, offen, authenticated:false (keine MCP-Berechtigung)
   ├─ /mcp nur POST; sonst 405
   ├─ MCP_BEARER_TOKEN muss 32+ Zeichen haben; sonst 503
   ├─ Bearer-Match; fehlt/falsch → 401
   ├─ Origin, falls gesetzt, exakt auf MCP_ALLOWED_ORIGIN prüfen → sonst 403
   ├─ Requestlimit: 2 MiB + 4096 B → bei Überschreitung 413
   ├─ MCP SDK createMcpHandler(..., legacy:'reject'), 7 Toolnamen + 14 Resources
   ▼ Cloudflare Service Binding CORE (kein öffentlicher Core-Endpunkt)
Python-Core Worker [P0/P1/P2 unverändert]
   ├─ gepinnte P0-Ressourcen (SHA-256) / read only
   ├─ P1 Validator
   └─ P2 deterministic Printer
```

Im Gateway-Code: `gateway/src/index.mjs` und `gateway/src/security.mjs`; Core `workers_dev:false` in `python-core/wrangler.jsonc`.

## Token: Lebenszyklus (bestehender Proof)

**Erstellung bereits erfolgt**, lokal im Keychain-Service `aiaeao-g5-mcp-token`, Cloudflare Worker Secret `MCP_BEARER_TOKEN`. Nicht erneut erzeugen, solange der Proof getestet wird; Rotation ist ein **separater kontrollierter Vorgang**.

**Status prüfen (ohne Secret-Ausgabe):**

```sh
security find-generic-password -a "$USER" -s 'aiaeao-g5-mcp-token' >/dev/null 2>&1 && echo 'Local proof secret exists'
cd "$HOME/Downloads/lunados.cube/P3/remote-mcp-g5/gateway"
npx wrangler secret list
```

`secret list` zeigt Namen, nicht den Secret-Wert. Rechte und Account-Kontext beachten.

**Temporär in die Zwischenablage kopieren (nicht anzeigen):**

```sh
printf 'Bearer %s' "$(security find-generic-password -a "$USER" -s 'aiaeao-g5-mcp-token' -w)" | pbcopy
# Nach Einrichtung des Connectors
printf '' | pbcopy
```

**Für einen nativen Prozess temporär über Env:**

```sh
export AIAEAO_G5_TOKEN="$(security find-generic-password -a "$USER" -s 'aiaeao-g5-mcp-token' -w)"
# ... nur im betreffenden Prozess benutzen ...
unset AIAEAO_G5_TOKEN
```

Diese Umgebungsvariable ist **nicht** automatisch eine Claude-/Zed-Header-Konfiguration. Die jeweiligen Hosts benötigen ihre eigene Übertragung des Headers. Prozessumgebungen und Zwischenablage sind kein langfristiger Secret Store.

## Negative HTTP-Tests ohne Token-Leck

Bei Tests `POST /mcp` verwenden; `GET /mcp` gibt bereits wegen der Methode `405` zurück und testet die Authentifizierung **nicht**.

```sh
URL='https://aiaeao-cube-g5-gateway.jo-885.workers.dev/mcp'
# HTTP 401: kein Authorization-Header
curl -sS -o /dev/null -w '%{http_code}\n' -X POST "$URL" -H 'Content-Type: application/json' --data '{}'
# HTTP 401: explizit falscher Token
curl -sS -o /dev/null -w '%{http_code}\n' -X POST "$URL" -H 'Authorization: Bearer wrong' --data '{}'
# HTTP 403: korrekter Token, unerlaubte Origin. Auth nicht als Kommandozeilenliteral übergeben.
# Empfohlen: offizieller sdk_remote_smoke.py (führt diesen Fall ohne Token-Dump aus)
```

**Positive Tests:** `sdk_remote_smoke.py` statt selbst zusammengebauter JSON-RPC-Payloads. Ein korrekt autorisierter `POST` mit nicht-MCP-konformem JSON kann einen Protokollfehler liefern – das ist **kein** Token-Gate-Fail.

## Berechtigungsmodell von G5

| Dimension | Proof-Verhalten | Konsequenz |
|---|---|---|
| Authentifizierung | Ein statisches globales Bearer-Secret | Wer es besitzt, kann alle sieben Tools nutzen |
| Identität | Keine Client-/User-Identität | Keine Einzelnutzer-Auditierbarkeit |
| Tool-Autorisierung | Globale sieben erlaubte Tools | Keine per-Agent-/per-Tool-RBAC |
| Rate Limit / Quota | Kein eingebautes per-Key-Limit | Abuse-/Kostenrisiko vor Produktion lösen |
| Browser Origin | Ein exakt konfigurierbarer Origin, sonst reject | Origin ist zusätzliche Browser-Prüfung, **kein** Auth-Ersatz |
| Privacy | Prompts/Inputs gelangen bei Remote-Aufrufen an Cloudflare; bei Claude zusätzlich über dessen Connector-Dienst | Keine vertraulichen Daten ohne separate Prüfung |
| Runtime | Stateless Gateway, Python Core privat | Core niemals mit `workers_dev:true` veröffentlichen |

## Schlüsselwechsel / Revocation

1. Vorab Clients und Zugriffsunterbrechung planen; G5 hat **nur einen akzeptierten Token gleichzeitig**, keine nahtlose Dual-Key-Rotation.
2. Neuen starken Token außerhalb von Chat/Repo erzeugen und sicher speichern; Cloudflare Worker Secret `MCP_BEARER_TOKEN` aktualisieren (`wrangler secret put` oder Dashboard). **Cloudflare deployt damit eine neue Version**.
3. Alle angebundenen Clients auf den neuen Header ändern; alten Token lokal/bei Hosts entfernen.
4. 401/403/Positive-Remote-Smoke erneut verifizieren; R3-Evidence aktualisieren.
5. Bei bestätigter Kompromittierung zuerst öffentliche Gateway-Route deaktivieren, dann rotieren und eventuell Logs kontrollieren.

## Nicht durch G5 bewiesen – eigenes Production-Gate

OAuth/OIDC und dynamische Client-Identität; Authentifizierungs- und Autorisierungsmodell pro Agent/Benutzer/Workspace; eigenständige Schlüssel, Rotation ohne Unterbrechung, RBAC, Limits und Abrechnungsgrenzen, Datenschutz/Retention, Cloudflare Access/WAF, Telemetrie und Incident Response. **Ein erfolgreiches Bearer-Gate ist keine Produktionszulassung.**

**Referenzen (24.10.2026):**
- https://developers.cloudflare.com/workers/configuration/secrets/
- https://developers.cloudflare.com/workers/runtime-apis/bindings/service-bindings/
