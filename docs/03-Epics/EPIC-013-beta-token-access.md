# EPIC-013 — Paralleler Beta-Zugang zu G5

Status: in_progress · Milestone: [MILE-019](../02-Milestones/MILE-019-beta-token-access.md) · Change: [beta-token-access](../../openspec/changes/beta-token-access/proposal.md)

## Ergebnis

Der bestehende G5-MCP-Endpunkt nimmt den bisherigen Entwickler-Token und bis zu zwölf getrennte Beta-Tokens an. Ein Beta-Token kann einzeln entzogen oder gewechselt werden, ohne den Entwicklerzugang oder andere Beta-Zugänge zu unterbrechen. Die reale Verbindung wird mit Codex und Claude geprüft.

## Umfang und Grenze

Nur das Authentifizierungstor des bestehenden Gateways und der sichere Umgang mit seinen Worker Secrets ändern sich. Core, Cube-Verträge, öffentlicher Referenz-Worker und Endpunkt bleiben bestehen. Der eingefrorene [MILE-017-Entwurf](../02-Milestones/MILE-017-staging-production.md) für zwei Umgebungen sowie PIN, Access und OAuth sind nicht Teil dieses Epics. Ein Token belegt den Besitz des Schlüssels, nicht die Person oder eine Produktlizenz.

## Stories und Reihenfolge

1. [US-035 — Entwicklerzugang erhalten](../04-US/US-035-developer-access.md): bestehender Schlüssel und Endpunkt bleiben beim Umstellen erreichbar.
2. [US-036 — Beta-Zugang nutzen](../04-US/US-036-beta-access.md): eingeladene Nutzer verbinden Codex oder Claude mit eigenem Token.
3. [US-037 — Beta-Zugang einzeln entziehen](../04-US/US-037-beta-revocation.md): ein Token wird unabhängig von allen anderen gewechselt oder entfernt.

## Akzeptanz

Alle Kriterien aus [MILE-019](../02-Milestones/MILE-019-beta-token-access.md) und die Szenarien der [Verhaltensspezifikation](../../openspec/changes/beta-token-access/specs/g5-beta-token-gate/spec.md) sind nachgewiesen. Ein bestandener lokaler Test allein belegt keine Live-Verbindung; fehlende Cloudflare- oder Host-Prüfungen bleiben offen.

Führender Ausführungsstatus: [tasks.md](../../openspec/changes/beta-token-access/tasks.md).
