# G5 – gezielter Claude-R4-Final-Recheck (kopierbarer Prompt)

> Verwende **ausschließlich** den bestehenden Remote-MCP-Connector `AIAEAO Cube G5 Remote` (Cloudflare), nicht den lokalen G4-Server. Der G5-Source-Freeze wurde konsolidiert; der Gateway wurde danach erneut deployed und der unabhängige Python-SDK-R3-Test meldete `PASS G5 ACTUAL REMOTE MCP: auth, Origin, 7 tools, 14 resources, P0, P1, VP06 byte parity`.
>
> Bitte schließe gezielt die vorher offenen G5-R4-Abnahmepunkte ab und nutze nur **echte aktuelle MCP-Aufrufe**:
>
> 1. `cube_discover_surface`: bestätige `deployment.remote_mcp_available=true`, sieben Tools und G5-Status **Proof, nicht Production**.
> 2. Führe `ListMcpResources` aus. Vergleiche die MIME-Informationen für `morphology.md` und `visual/README.md` mit dem gepinnten P0-Lock. Erwartet: **`text/markdown`** für beide. Lese die Resources bei Verfügbarkeit. Falls Resource-Discovery nicht im Host verfügbar ist, markiere genau diese Prüfung `NOT TESTED` – der Tool-Fallback reicht für den MIME-Abgleich nicht automatisch.
> 3. Prüfe die Legacy-P2-Card mit `cube_get_capabilities` und die vollständige Surface über `cube_discover_surface` auf unveränderte Domänengrenzen.
> 4. Falls die erhaltenen SVG-Bytes direkt zugänglich sind, `cube_render_svg` mit einem vorhandenen Golden Fixture ausführen und den SHA-256 **clientseitig aus den empfangenen UTF-8-Bytes** neu berechnen, nicht nur den Serverwert wiederholen. Wenn die Host-Laufzeit das nicht ermöglicht: `NOT TESTED` vermerken und die separate bestandene SDK-R3-Byte-Prüfung als ergänzende, **nicht hosteigene** Evidenz bezeichnen.
> 5. Keine weiteren 27 Calls wiederholen, sofern für diese offenen Punkte nicht nötig. Keine Änderungen an Repo, Cloudflare, Prompts, Fixtures, Secrets oder Git. Kein Token ausgeben.
>
> Erstelle einen kurzen Addendum-Report mit tatsächlich aufgerufenen Werkzeugen, MIME-Typen, Hashquelle (serverreported vs. clientcomputed), R4.1/R4.5/R4.8-Status und abschließend `G5-R4 PASS / INCOMPLETE / FAIL`. Unterscheide den bereits nachgewiesenen R3-SDK-Client von der unabhängigen Claude-Host-Evidenz. `Production AUTHORIZED` darf daraus **nicht** gefolgert werden.
