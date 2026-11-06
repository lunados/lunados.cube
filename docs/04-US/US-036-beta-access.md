# US-036 — Beta-Zugang nutzen

Status: planned · Epic: [EPIC-013](../03-Epics/EPIC-013-beta-token-access.md) · Mile: [MILE-019](../02-Milestones/MILE-019-beta-token-access.md)

Als eingeladener Beta-Teilnehmer möchte ich mit einem zugewiesenen Token denselben G5-MCP-Endpunkt in Codex oder Claude nutzen, damit ich die bereitgestellten Cube-Werkzeuge ohne zusätzlichen PIN- oder OAuth-Schritt erproben kann.

## Akzeptanz

- Bis zu zwölf getrennte optionale Token-Plätze können belegt werden; ein leerer Platz gewährt keinen Zugang.
- Jeder gültige Beta-Token erlaubt denselben bestehenden MCP-Werkzeugumfang; ein falscher Token erhält `401`.
- Codex und Claude führen je eine echte MCP-Verbindung und einen vorab festgelegten kleinen Aufruf mit einem Beta-Token aus; Host-Einschränkungen bleiben als solche ausgewiesen.
- Token-Werte erscheinen weder in Repository-Dateien noch in Nachweisen, URLs oder MCP-Argumenten.

Szenarien: [G5-Beta-Token-Gate](../../openspec/changes/beta-token-access/specs/g5-beta-token-gate/spec.md), Anforderungen „Beta-Tokens“ und „Host-Verbindung“.

## Aufgaben

- [TASK-082 — Zugangsvertrag und Ausgangsstand](../05-Tasks/TASK-082-beta-auth-contract.md)
- [TASK-083 — Gateway für parallele Tokens](../05-Tasks/TASK-083-beta-token-gateway.md)
- [TASK-084 — Token-Einrichtung und Widerruf](../05-Tasks/TASK-084-beta-token-operations.md)
- [TASK-085 — Live- und Host-Abnahme](../05-Tasks/TASK-085-beta-token-acceptance.md)

[Führender Aufgabenstatus](../../openspec/changes/beta-token-access/tasks.md).
