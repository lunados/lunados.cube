# TASK-085 — Live- und Host-Abnahme

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/beta-token-access/tasks.md).

Stories: [US-035](../04-US/US-035-developer-access.md), [US-036](../04-US/US-036-beta-access.md), [US-037](../04-US/US-037-beta-revocation.md) · Mile: [MILE-019](../02-Milestones/MILE-019-beta-token-access.md) · Aufwand: geschätzt 0,5–0,75 PT zuzüglich Host-Einrichtung

## Ziel und Arbeit

Vor dem Gateway-Deployment eine neue sichtbare Gateway-Versionsbezeichnung festlegen und die Live-Erwartungen darauf abstimmen; der lokale Kandidat meldet noch `0.3.0-proof` wie R10. Danach den bestehenden Entwicklerzugang, zwei unterschiedliche Beta-Plätze, Negativfälle und einen individuellen Widerruf live prüfen. Den bisherigen G5-Remote-Smoke und die für den aktuellen Core-Stand geltende R-Serie ausführen. Codex und Claude verbinden sich jeweils mit einem Beta-Token und rufen einen vorher festgelegten kleinen, read-only Cube-Aufruf auf. Den öffentlichen Referenz-Worker unabhängig prüfen.

## Abnahme und Nachweis

Ein datierter Bericht enthält Gateway-Version, Endpunkt ohne Token, erwartete und beobachtete HTTP-/MCP-Ergebnisse, Host-Resultate und offene Abweichungen. Er enthält keine Tokens, Empfängerlisten oder beliebigen Request-Bodies. MILE-019 bleibt offen, solange Entwicklerzugang, Einzelwiderruf oder beide Host-Verbindungen nicht nachgewiesen sind.

**Abnahmeentscheidung vom 2026-11-06:** Der Nutzer akzeptiert diese Task ausdrücklich mit ausstehender manueller Claude-Host-Prüfung. Die beobachteten Ergebnisse und diese Grenze stehen im [TASK-085-Nachweis](../10-Evidence/MILE-019/TASK-085-RESULT.md). Diese Task-Akzeptanz schließt MILE-019 noch nicht.

## Abhängigkeiten und Grenze

[TASK-082](TASK-082-beta-auth-contract.md), [TASK-083](TASK-083-beta-token-gateway.md), [TASK-084](TASK-084-beta-token-operations.md). Keine allgemeine Produktionsfreigabe; G5-Grenzen bleiben separat bewertet.
