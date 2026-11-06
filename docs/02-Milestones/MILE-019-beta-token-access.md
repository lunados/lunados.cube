# MILE-019 — Beta-Zugang per Token am bestehenden G5

Status: **in Arbeit, alle Abnahmekriterien belegt** (TASK-082–085 abgeschlossen; Claude-Host-Test am 2026-11-06 nachgetragen; Abschluss durch den Nutzer offen) · Stand: 2026-11-06 · Ausgangspunkt: bestehender G5-Remote-Proof mit Gateway und privatem Core · [MILE-017](MILE-017-staging-production.md) ist eingefroren

Ausarbeitung: [EPIC-013](../03-Epics/EPIC-013-beta-token-access.md) · [US-035–037](../04-US/README.md#mile-019--in-arbeit) · [TASK-082–085](../05-Tasks/README.md#mile-019--in-arbeit) · [OpenSpec-Change](../../openspec/changes/beta-token-access/proposal.md)

## Ziel und Entscheidung

Eine geschlossene Beta soll den aktuellen G5-MCP-Endpunkt parallel zum Entwicklerzugang verwenden können. Es bleibt vorerst bei **einem** Gateway/Core-Paar und **einem** MCP-Endpunkt. Bis zu zwölf voneinander getrennte Beta-Tokens dürfen den bestehenden Entwickler-Token nicht ersetzen oder ungültig machen. Diese Tokens sind Zugangsschlüssel, keine Lizenzprüfung mit Produktstufen oder Nutzerkonto.

Der bisherige Gateway akzeptiert genau ein Worker Secret `MCP_BEARER_TOKEN`. MILE-019 erweitert nur das Zugangstor, sodass bis zu zwölf optionale Beta-Token-Secrets (`MCP_BETA_TOKEN_01` bis `_12`) zusätzlich akzeptiert werden können. Der private Core, die Cube-Werkzeuge und ihre fachlichen Prüfungen bleiben unverändert. Dass Cube-Anfragen fachlich qualifiziert werden, ersetzt die Prüfung des Zugangsschlüssels nicht.

## Arbeitsumfang

1. Den aktuellen Endpunkt und den Entwicklerzugang als Ausgangszustand festhalten, ohne Secret-Werte in Repository oder Nachweisen zu kopieren.
2. Im Gateway **bis zu zwölf optionale** Beta-Tokens als getrennte Cloudflare Worker Secrets vorsehen. Ohne eingerichteten Beta-Token bleibt das heutige Authentifizierungsverhalten bestehen. Jeder Token wird ausschließlich im `Authorization: Bearer …`-Header akzeptiert, nie in URL oder MCP-Argumenten.
3. Token-Werte außerhalb des Repositorys erzeugen und einzeln an eingeladene Tester übergeben. Alle aktiven Tokens sind verschieden. Die Einrichtung der Secrets und ein Gateway-Deployment dürfen den vorhandenen Entwicklerzugang nicht stillschweigend ersetzen.
4. Ablehnung ohne Token und mit falschem Token, positiven Zugriff mit Entwickler- und Beta-Token sowie individuellen Entzug/Wechsel eines Beta-Tokens prüfen. Danach die MCP-Verbindung in Codex und Claude mit einem Beta-Token tatsächlich erproben.
5. Die vorhandenen G5-Offline- und Remote-Prüfungen wiederholen und die Ergebnisse mit Version und Zeitpunkt dokumentieren. Der öffentliche Referenz-Worker bleibt unabhängig erreichbar.

## Token-Modell für die erste geschlossene Beta

Es gibt höchstens zwölf **getrennte Token-Plätze** für eingeladene Beta-Teilnehmer. Ein Platz kann vorsorglich vorbereitet und bei Bedarf mit einem eigenen, zufälligen Token belegt werden; leere Plätze gewähren keinen Zugang. Ein belegter Platz kann einzeln entzogen oder neu belegt werden. Der Token wird im Client im Klartext eingegeben, aber nur über HTTPS übertragen und als Secret auf Cloudflare verwaltet. Die Zuordnung Platz ↔ Empfänger wird außerhalb des Repositorys verwaltet; sie ist keine geprüfte Personenidentität. Jede Person kann ihren Token weitergeben. Alle Beta-Tokens haben denselben Werkzeugumfang.

Ein einzelner Deployment-Stand bedeutet auch, dass Änderungen am G5-Gateway oder Core nach einem Deployment sofort für Entwickler und Beta-Teilnehmer gelten. Vor jedem solchen Deployment sind die bestehenden Prüfungen auszuführen; MILE-019 verspricht keine unabhängige Release-Stabilität für die Beta.

## Abnahme

- [x] Ein öffentlich erreichbarer Gateway-Endpunkt und ein nicht öffentlich gerouteter Core sind bestätigt; kein zweites G5-Paar wird für diese Mile angelegt.
- [x] Der bisherige Entwickler-Token funktioniert vor und nach Einführung des Beta-Zugangs.
- [x] Bis zu zwölf verschiedene Beta-Tokens können unabhängig vom Entwickler-Token belegt werden; fehlende, leere und falsche Tokens erhalten keine MCP-Berechtigung.
- [x] Entzug oder Wechsel eines Beta-Tokens sperrt nur dessen alten Wert; Entwicklerzugang und andere Beta-Tokens funktionieren weiter.
- [x] Codex und Claude haben mit einem Beta-Token je eine echte MCP-Verbindung und einen vorab festgelegten kleinen Werkzeugaufruf erfolgreich durchlaufen; Einschränkungen eines Hosts werden ausdrücklich dokumentiert ([Nachweis](../10-Evidence/MILE-019/TASK-085-RESULT.md#hosts-und-öffentliche-referenz)).
- [x] Die vorhandenen G5-Vertrags- und Remote-Prüfungen laufen nach dem Gateway-Deployment; Nachweise enthalten keine Token-Werte oder Anfrageinhalte.
- [x] Die öffentliche Read-only-Referenz bleibt erreichbar und unabhängig vom Beta-Token.

## Nicht in MILE-019

- Ein zweites Staging/Production-Deployment, Release-Tags und getrennte Betriebsumgebungen aus dem eingefrorenen MILE-017-Entwurf.
- Cloudflare Zero Trust Access, E-Mail-Allowlist, One-Time PIN oder OAuth für MCP-Clients. Das ist ein späteres Vorhaben mit eigener Entscheidung.
- Lizenzverwaltung, Public/Pro/Premium-Stufen, Nutzerkonten, Abrechnung und kryptografisch gesicherte Personenidentität hinter einem Token.
- Eine allgemeine Produktionsfreigabe von G5. Die in `P3/remote-mcp-g5/KNOWN_LIMITS.md` beschriebenen Grenzen gelten weiter; vor breiter Freigabe sind insbesondere Missbrauchs- und Kostenbegrenzung gesondert zu prüfen.

## Quellen im Repository

- [G5-Sicherheitsgrenze](../../P3/remote-mcp-g5/SECURITY.md) und [Bearer-Gate](../../P3/remote-mcp-g5/docs/04_BEARER_API_TOKEN_GATE.md)
- [Aktuelle G5-Grenzen](../../P3/remote-mcp-g5/KNOWN_LIMITS.md) und [Deployment-Anleitung](../../P3/remote-mcp-g5/DEPLOYMENT.md)
