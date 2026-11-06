# EPIC-014 — Quellengebundene Modul-Fähigkeiten

Status: abgeschlossen für den benannten Stand ([CLOSURE](../10-Evidence/MILE-020/CLOSURE.md)) · Milestone: [MILE-020](../02-Milestones/MILE-020-module-capability-descriptors.md) · Change: [declare-module-capabilities](../../openspec/changes/archive/2026-11-06-declare-module-capabilities/proposal.md)

## Ergebnis und Grenze

Module beschreiben ihre Fähigkeiten selbst, versioniert und gehasht. Der Cube zeigt gepinnte Verweise; Verbraucher lesen die jeweilige Quelle. Deskriptor, Strukturvalidität, Implementierungsstatus, aktuelle Host-Verfügbarkeit, Admission und tatsächliche Ausführung bleiben getrennte Aussagen.

Sieben logische MILE-071-Rollen und der interne Bereich `translator/` im Connector werden in einer Owner-Matrix abgedeckt. Daraus folgen weder sieben Repositories noch sieben Services. Ein Zielbild oder Adapterregister belegt keine laufende Fähigkeit. Keine neuen Fähigkeiten, Codeverlagerung, Explorer-Bindung, Workflow Builder oder Playbook-Library.

## Stories und Reihenfolge

1. [US-038 — Vertrag](../04-US/US-038-capability-contract.md): Quellenbasis, D-1, Schema und Offline-Prüfung.
2. [US-039 — Owner-Deskriptoren](../04-US/US-039-owned-module-descriptors.md): Lib mit D-2, Toolbox/Translator, Cube und Relay-Rollen.
3. [US-040 — Grenzen](../04-US/US-040-descriptor-boundaries.md): D-3 in ADR-001 festgehalten; D-4 für Connector und `translator/` geklärt.
4. [US-041 — Discovery](../04-US/US-041-neighbor-discovery.md): gemeinsame neighbors, Regression und Abnahme.

D-1 ist durch den Nutzer als eigenes dokumentarisches Format mit gezieltem v2-Verweis [entschieden](../10-Evidence/MILE-020/TASK-086-RESULT.md#d-1--verhältnis-zum-module-contract-v2). D-2 ist ebenfalls [entschieden und umgesetzt](../10-Evidence/MILE-020/TASK-088-RESULT.md): drei `cube-profile`, zehn `standalone`. D-4 ordnet [Connector und `translator/` demselben Ziel-Repo zu](../10-Evidence/MILE-020/TASK-092-RESULT.md). D-3 „beides, Hash führend“ ist in [ADR-001](../07-ADR/ADR-001-lib-snapshot-host-path.md) festgehalten.

## Akzeptanz und Nachweise

Alle sechs Mile-Kriterien sind in [TRACEABILITY.md](../../openspec/changes/archive/2026-11-06-declare-module-capabilities/TRACEABILITY.md) auf Stories und Tasks abgebildet und in [TASK-094](../10-Evidence/MILE-020/TASK-094-RESULT.md) für den benannten Quell-/live G5-Stand abgenommen. Nach Neustart zeigt auch die lokale Codex-Host-Verbindung den gepinnten Block. Die Relay-Artefakte liegen weiter im isolierten Worktree; ihre Integration ist nach [CLOSURE](../10-Evidence/MILE-020/CLOSURE.md) kein Abschlusskriterium der Mile.

Führender Ausführungsstatus: [tasks.md](../../openspec/changes/archive/2026-11-06-declare-module-capabilities/tasks.md). Aufwand der Detailplanung: 2,5–4,5 PT, ohne Entscheidungswartezeit oder zusätzlich erforderliche Bereitstellung; die ursprünglichen 2–3 PT sind eine grobe Mile-Schätzung.
