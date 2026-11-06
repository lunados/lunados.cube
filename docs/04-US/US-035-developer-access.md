# US-035 — Entwicklerzugang erhalten

Status: planned · Epic: [EPIC-013](../03-Epics/EPIC-013-beta-token-access.md) · Mile: [MILE-019](../02-Milestones/MILE-019-beta-token-access.md)

Als Entwickler möchte ich meinen bisherigen G5-Endpunkt und Token während und nach der Einführung von Beta-Tokens weiterverwenden, damit ich mich bei der Arbeit nicht selbst ausschließe.

## Akzeptanz

- Derselbe `/mcp`-Endpunkt und dasselbe Gateway/Core-Paar bleiben in Gebrauch.
- Ohne konfigurierte Beta-Tokens verhält sich das Authentifizierungstor wie bisher.
- Der bestehende Entwickler-Token funktioniert vor und nach Einrichtung der Beta-Tokens; ein fehlerhafter oder entfernter Beta-Platz sperrt ihn nicht.
- Fehlende oder falsche Bearer-Tokens werden vor jeder MCP-Operation abgewiesen.

Szenarien: [G5-Beta-Token-Gate](../../openspec/changes/beta-token-access/specs/g5-beta-token-gate/spec.md), Anforderungen „Entwicklerzugang“ und „Authentifizierung vor MCP“.

## Aufgaben

- [TASK-082 — Zugangsvertrag und Ausgangsstand](../05-Tasks/TASK-082-beta-auth-contract.md)
- [TASK-083 — Gateway für parallele Tokens](../05-Tasks/TASK-083-beta-token-gateway.md)
- [TASK-085 — Live- und Host-Abnahme](../05-Tasks/TASK-085-beta-token-acceptance.md)

[Führender Aufgabenstatus](../../openspec/changes/beta-token-access/tasks.md).
