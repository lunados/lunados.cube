# Design — G5-Beta-Tokens

Status: proposed · 2026-11-06 · [MILE-019](../../../docs/02-Milestones/MILE-019-beta-token-access.md)

## Ausgangspunkt

Das Gateway prüft vor dem MCP-Handler `MCP_BEARER_TOKEN` als Worker Secret. Der Core ist über `CORE` intern gebunden. Der bestehende Endpunkt und der Entwickler-Token bleiben die Rückfallbasis.

## Vorgeschlagene Entscheidung

- Zwölf optionale Worker-Secret-Plätze `MCP_BETA_TOKEN_01` bis `_12` ergänzen den vorhandenen Pflicht-Token. Die Plätze sind keine neuen Worker und keine Umgebungen.
- Pro Anfrage wird der Bearer-Wert mit dem Entwickler-Token und allen gültig belegten Beta-Plätzen verglichen. Fehlende, zu kurze oder doppelte Beta-Werte werden nicht als Zugangsschlüssel akzeptiert; ein Fehler an Beta-Plätzen darf den Entwicklerzugang nicht sperren.
- Jeder Platz kann durch Ändern oder Entfernen nur seines Secrets entzogen werden. Die Ausgabe und Zuordnung der Werte erfolgt außerhalb des Repositorys. Es gibt keine Nutzeridentität, Produktstufe oder Tool-spezifische Berechtigung.
- Die bestehenden Origin- und Größenprüfungen sowie alle zehn MCP-Werkzeuge bleiben unverändert. Authentifizierung erfolgt vor fachlicher Verarbeitung.

## Bereitstellung und Grenze

Cloudflare Worker Secrets sind pro Worker getrennte verschlüsselte Bindings; zwölf zusätzliche Plätze liegen unter dem dokumentierten Variablenlimit des Workers Paid-Plans. Secret-Änderungen können neue Worker-Versionen unmittelbar deployen. Deshalb sind Ausgangswert, Reihenfolge und Live-Rückprüfung Teil der Tasks. Ein Code- oder Secret-Deployment wirkt auf Entwickler und Beta-Nutzer zugleich. Die öffentliche Referenz und der private Core bleiben getrennt.

Cloudflare PIN/Access, OAuth und ein zweites G5-Deployment sind außerhalb dieser Änderung.
