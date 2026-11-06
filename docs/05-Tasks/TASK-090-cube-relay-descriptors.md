# TASK-090 — Cube und Relay-Rollen quellengebunden beschreiben

Ausgeführt am 2026-11-06: [Cube-Owner-Deskriptor](../../module-capabilities/v1/README.md) und vier Relay-Deskriptoren im isolierten, vom Nutzer freigegebenen lokalen TASK-090-Worktree erstellt und geprüft. [Ergebnis und Grenzen](../10-Evidence/MILE-020/TASK-090-RESULT.md). Führender Status in [tasks.md](../../openspec/changes/archive/2026-11-06-declare-module-capabilities/tasks.md).

Story: [US-039](../04-US/US-039-owned-module-descriptors.md) · Mile: [MILE-020](../02-Milestones/MILE-020-module-capability-descriptors.md) · Aufwand: 0,5–0,75 PT (Schätzung)

## Ziel und Arbeit

Cube-Deskriptor im Cube und Deskriptoren für Core/Server, Server GUI, App/Application Service und aiaeao-connector im Relay-Repo erstellen. Logische Rollen dürfen Quellen teilen, müssen aber in der Abdeckungsmatrix einzeln erkennbar sein. MILE-071 ist Ziel-/Owner-Baseline, keine Implementierungsevidenz. registry.py belegt registrierte Adapter, keinen laufenden Provider. Package-/Root-Derivate und v2-/Companion-/Fixture-Grenzen explizit nennen; unsichere Behauptungen candidate/unknown lassen.

## Abnahme und Nachweis

Zusammen mit TASK-088/089 ist jede der sieben logischen Rollen einschließlich `lunados.connector` mit internem `translator/`-Bereich abgedeckt. Jeder Deskriptor hat eine eindeutige Quelle, Version und extern prüfbaren Hash. Cube unterscheidet P0/P1/P2/P3; Relay trennt Receipt, beobachteten Start, Result/Outcome und Verification. implemented erfordert konkrete Quellenevidenz im beschriebenen Umfang und behauptet keine Host-Verfügbarkeit.

Nachweis: [TASK-090-RESULT.md](../10-Evidence/MILE-020/TASK-090-RESULT.md) mit sieben Rollen, Quellen-/Deskriptorpins, ausgeführter Offline-Prüfung und Worktree-Grenze.

## Abhängigkeiten und Grenze

Voraussetzungen: TASK-087; Abdeckungsmatrix aus TASK-086; D-4 vor endgültiger Connector-Benennung.

Keine neue API, kein Provideraufruf, keine normative Änderung am Module Contract, keine Behauptung sieben eigenständiger Produkte oder Services.
