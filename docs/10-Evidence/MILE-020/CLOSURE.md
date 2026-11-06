# MILE-020 — Abschlussnachweis

Stand: 2026-11-06 · Entscheidung: Der Nutzer hat nach Klärung des Relay-Integrationsumfangs den formalen Abschluss von [MILE-020](../../02-Milestones/MILE-020-module-capability-descriptors.md) beauftragt.

## Grundlage

[TASK-094](TASK-094-RESULT.md) weist alle sechs Mile-Kriterien für den benannten lokalen Owner-Stand und den ausgelieferten G5-Stand als **PASS** aus. Nach dem vom Nutzer durchgeführten Neustart lieferte auch die lokale Codex-MCP-Verbindung alle sieben `neighbors` bytegleich zum gepinnten Asset. Die Task-Nachweise [086–093](../../05-Tasks/README.md#mile-020--abgeschlossen) bleiben die Detailquellen für Format, Owner-Deskriptoren, Lib-Zuordnung, ADR, Namen und Discovery. Die [führende Checkliste](../../../openspec/changes/archive/2026-11-06-declare-module-capabilities/tasks.md) enthält TASK-086–094 als ausgeführt.

## Beschlossene Scope-Grenze

Die Relay-Deskriptoren wurden im isolierten TASK-090-Worktree erstellt, gepinnt und für MILE-020 lokal abgenommen. **Ein Commit oder die Integration in Relay-`main` ist kein Abnahmekriterium, keine Task und keine Voraussetzung für den Abschluss von MILE-020.** Die Formulierung „müssen integriert werden“ gilt ausschließlich für eine **spätere dauerhafte Verbraucher-Bindung** an diese Relay-Deskriptoren: Dafür sind sie im zuständigen Relay-Stand zu integrieren und dort erneut gegen die gewählten Pins zu prüfen. Dieser Integrationsschritt liegt außerhalb der geschlossenen Mile und ist keine rückwirkend offene Abnahme.

Der Abschluss ist keine allgemeine Produktionsfreigabe, keine Host-Ausführung der beschriebenen Fähigkeiten und keine Authority oder Admission aus Deskriptoren. Für die geplanten Verbraucher MILE-022 und MILE-023 gelten die Referenzen, Status- und Hashregeln aus [TASK-094](TASK-094-RESULT.md#übergabe-an-mile-022-und-mile-023).
