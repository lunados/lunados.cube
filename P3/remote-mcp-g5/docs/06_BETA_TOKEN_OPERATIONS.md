# MILE-019 — Beta-Token-Betrieb

Stand: 2026-11-06. Ziel ist der bestehende Gateway-Worker `aiaeao-cube-g5-gateway` mit dem Endpunkt `https://aiaeao-cube-g5-gateway.jo-885.workers.dev/mcp`. Der private Core und `cube.lunados.net` werden dafür nicht geändert.

## Plätze und Aufbewahrung

`MCP_BEARER_TOKEN` bleibt der Entwicklerzugang. Die getrennten Beta-Plätze heißen `MCP_BETA_TOKEN_01` bis `MCP_BETA_TOKEN_12`. Jeder Wert ist ein zufälliger, eigener Bearer-Token mit mindestens 32 Zeichen. Ein freier Platz enthält kein Cloudflare-Secret und gewährt keinen Zugang. Ein hinterlegter, aber noch nicht ausgegebener Wert ist trotzdem ein aktiver Schlüssel, sobald der MILE-019-Gateway live ist.

Cloudflare speichert die Werte als **Worker Secrets** (`secret_text`), nie als Wrangler-`vars` oder in `.env`/`.dev.vars` im Repository. Die lokalen Werte liegen in macOS Keychain unter `aiaeao-g5-beta-token-01` bis `aiaeao-g5-beta-token-12`. Zuordnung Platz ↔ Empfänger, Ausgabezeit und Kontaktweg gehören in einen separaten, geschützten Passwortmanager-Eintrag außerhalb des Repositorys. Keine Token-Werte, Empfängerlisten oder Header in Chat, Tickets, Logs oder Nachweise kopieren. Für Codex und Claude werden zwei unterschiedliche Plätze verwendet.

## Vor jedem Cloudflare-Wechsel

1. Im Gateway-Verzeichnis `P3/remote-mcp-g5/gateway` den richtigen Account und Worker prüfen: `./node_modules/.bin/wrangler whoami` und `./node_modules/.bin/wrangler secret list`. `secret list` zeigt Namen und Typen, keine Werte.
2. Zuerst `GET /health` prüfen: Die Antwort muss vom Worker kommen und die Gateway-Version enthalten. Eine Cloudflare-Sperre wie `error code: 1010` beweist nichts über den Bearer, selbst wenn ihr HTTP-Status `403` ist. Dann den bestehenden Entwickler-Token aus Keychain mit `POST /mcp` ohne `Origin` prüfen: ein MCP-Protokollfehler wie `400` statt `401` zeigt, dass das Auth-Gate passiert wurde. Ohne/falscher Bearer muss `401` ergeben. Mit gültigem Bearer und unerlaubter `Origin` muss **vom Worker** `403` kommen. Ein `GET /mcp` ist hierfür ungeeignet (`405`). Für einen vollständigen MCP-Check das vorhandene `scripts/sdk_remote_smoke.py` verwenden.
3. Eine Änderung über `wrangler secret put`, `secret bulk` oder `secret delete` veröffentlicht unmittelbar eine neue Worker-Version. Ein einzelner Platz darf nur geändert werden, wenn der vorherige Entwickler-Test bestanden hat. Die Gateway-Version prüfen: Der MILE-019-Stand meldet seit 2026-11-06 `0.4.0-proof`.

## Platz neu belegen oder ausgeben

1. Einen noch freien Platz wählen und 48 zufällige Bytes als URL-sicheren Token erzeugen. Den Wert ausschließlich in Keychain bzw. Passwortmanager und in das gleichnamige Cloudflare Worker Secret übernehmen. Bei mehreren Plätzen Cloudflares `wrangler secret bulk` mit JSON **über stdin** verwenden; ein nicht genannter Schlüssel wie `MCP_BEARER_TOKEN` bleibt dabei erhalten. Keine Secret-Datei im Repository anlegen. Alternativ im Cloudflare-Dashboard unter **Workers & Pages → aiaeao-cube-g5-gateway → Settings → Variables and Secrets → Add → Secret** mehrere Werte eintragen und einmal **Deploy** wählen.
2. `wrangler secret list` muss den neuen Namen mit Typ `secret_text` zeigen. Danach den Entwickler-Test wiederholen und den neuen Token mit einem echten MCP-Client testen; erst dann an genau einen eingeladenen Empfänger über einen geschützten Kanal ausgeben. Der Empfänger trägt ihn als `Authorization: Bearer …` für HTTPS-`/mcp` ein, nicht als URL-Parameter oder MCP-Argument.
3. Für einen bereits lokal angelegten Platz kann der Inhaber den Wert ohne Terminalausgabe kurz in die Zwischenablage übernehmen: `security find-generic-password -s aiaeao-g5-beta-token-01 -w | pbcopy`. Danach die Zwischenablage leeren. Die Platznummer entsprechend ersetzen. Die Zwischenablage ist nur ein Transportweg, kein dauerhafter Speicher.

## Einzelnen Platz erneuern

1. Den alten Wert geschützt für den Negativtest behalten. Einen **neuen** zufälligen Wert erzeugen und im Passwortmanager/Keychain unter demselben Platz vorbereiten. Den Wert des **einen** Cloudflare-Secrets ersetzen (`wrangler secret put MCP_BETA_TOKEN_01` mit verdeckter Eingabe oder Dashboard-Edit und Deploy). Andere Beta-Secrets und `MCP_BEARER_TOKEN` nicht ändern.
2. Nach dem Deployment prüfen: neuer Wert authentifiziert, alter Wert ergibt `401`, Entwickler-Token und ein anderer Beta-Token funktionieren weiter. Die Host-Konfiguration des Empfängers aktualisieren und dessen alte Kopie entfernen. Erst nach erfolgreicher Prüfung den alten lokalen Wert löschen.
3. Schlägt die Prüfung fehl, keine Ausgabe des neuen Werts; Zustand des betroffenen Platzes und der Worker-Version klären. Cloudflare zeigt vorhandene Secret-Werte nicht erneut an.

## Einzelnen Platz widerrufen

1. `./node_modules/.bin/wrangler secret delete MCP_BETA_TOKEN_01` im Gateway-Verzeichnis ausführen oder im Dashboard genau dieses Secret entfernen und **Deploy** wählen. Die Nummer entsprechend ersetzen.
2. `secret list` muss das Fehlen dieses Platzes zeigen. Sein alter Wert muss `401` erhalten; Entwickler-Token und ein anderer Beta-Platz bleiben nutzbar. Erst dann den lokalen Keychain-Eintrag und die Empfängerkopie entfernen. Die Zuordnung und Widerrufszeit ohne Token-Wert extern dokumentieren.

## Nachweis und Grenzen

Im Repository stehen nur UTC-Zeitpunkt, Worker-Name, betroffene Secret-Namen, beobachtete Statuscodes und ein Verweis auf den Test. Die Secret-Liste belegt nur das **Vorhandensein**, nicht den Wert oder die Funktionsfähigkeit. Der Live-Nachweis für Beta-Zugang und Einzelwiderruf steht in [TASK-085](../../../docs/10-Evidence/MILE-019/TASK-085-RESULT.md). Ein Bearer-Token belegt Besitz, keine Personenidentität oder Lizenzstufe.

Cloudflare-Referenz: [Worker Secrets und Verhalten bei Secret-Änderungen](https://developers.cloudflare.com/workers/configuration/secrets/) · [Wrangler `secret bulk`](https://developers.cloudflare.com/workers/wrangler/commands/workers/#secret-bulk).
