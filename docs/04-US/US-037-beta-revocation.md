# US-037 — Beta-Zugang einzeln entziehen

Status: planned · Epic: [EPIC-013](../03-Epics/EPIC-013-beta-token-access.md) · Mile: [MILE-019](../02-Milestones/MILE-019-beta-token-access.md)

Als Betreiber möchte ich einen Beta-Token einzeln entfernen oder ersetzen, damit ein ausgeschiedener Teilnehmer den alten Schlüssel nicht weiter nutzen kann und alle anderen Zugänge gültig bleiben.

## Akzeptanz

- Für jeden der höchstens zwölf Plätze ist Einrichtung, Wechsel und Entfernung ohne Änderung des Entwickler-Tokens beschrieben.
- Nach dem Entzug wird der alte Wert mit `401` abgewiesen; Entwickler-Token und ein anderer Beta-Token funktionieren weiter.
- Vor der Ausgabe werden Beta-Tokens auf ausreichende Stärke und Unterschiedlichkeit geprüft. Ein ungültig konfigurierter Platz gewährt keinen Zugang.
- Nachweise verwenden nur Platz-IDs und Ergebnisse, keine Token-Werte und keine Empfängerlisten.

Szenarien: [G5-Beta-Token-Gate](../../openspec/changes/beta-token-access/specs/g5-beta-token-gate/spec.md), Anforderung „Einzelner Widerruf“.

## Aufgaben

- [TASK-082 — Zugangsvertrag und Ausgangsstand](../05-Tasks/TASK-082-beta-auth-contract.md)
- [TASK-083 — Gateway für parallele Tokens](../05-Tasks/TASK-083-beta-token-gateway.md)
- [TASK-084 — Token-Einrichtung und Widerruf](../05-Tasks/TASK-084-beta-token-operations.md)
- [TASK-085 — Live- und Host-Abnahme](../05-Tasks/TASK-085-beta-token-acceptance.md)

[Führender Aufgabenstatus](../../openspec/changes/beta-token-access/tasks.md).
