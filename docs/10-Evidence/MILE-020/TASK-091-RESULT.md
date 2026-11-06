# TASK-091 — D-3-ADR zum Lib-Host-Pfad: Ergebnis

Stand: 2026-11-06 · Ausführung: Codex · [Task](../../05-Tasks/TASK-091-lib-host-path-adr.md) · [führender Status](../../../openspec/changes/archive/2026-11-06-declare-module-capabilities/tasks.md) · [ADR-001](../../07-ADR/ADR-001-lib-snapshot-host-path.md).

## Entscheidung und Quellenstand

Die Nutzerentscheidung zu MILE-020 D-3 wurde in ADR-001 als **accepted** aufgenommen: direkter, gepinnter Lib-Snapshot für Build/Tests; Host-Snapshot zur Laufzeit; ein vorab ausgewählter SHA-256-Pin der exakten `INDEX.json`-Bytes ist in beiden Fällen führend. Für verwendete Einträge sind zusätzlich deren Hashes aus dem geprüften Index zu prüfen. Die ADR trennt diese Regel von vorhandenen Lesern und von einer erst noch zu implementierenden Host-Übergabe.

| Gelesene Quelle am 2026-11-06 | SHA-256 der exakten Datei-Bytes | Beobachtung |
|---|---|---|
| `lunados.lib/INDEX.json` | `aa2cfc92bd1aeb98ae72840fe5d225b7af6932824c57adc9635d6e82b9bbcdb6` | Index des ausgewählten lokalen Lib-Standes; kein ewiger Sollwert. |
| `lunados.lib/entries/project.aggregate-relations/v1/entry.json` | `a187a9e1291517c6534ad8974a381a97bcb953bcca1f0bf1a230c5532b20e32a` | Beispiel eines im Index deklarierten Entry-Hashes. |
| `lunados.cube/P2/visual-printer-cells-v1/scripts/materialize_s01_s16.py` | `6a23363cd81734e2bd7bf848b6b53de4e2bd98961089cbe7b5fd1bf3b697c1dc` | Direkter Build-Leser mit Nachbar-Checkout oder `--lib`; liest Index, verwendet selektierten Entry/Evaluator. Keine Prüfung eines unabhängig vorgegebenen Index-Pins. |
| `lunados.cube/P2/visual-printer-instances-v1/tests/test_vp11.py` | `038999bf26849652a8b83d23b2d8447d81ccdc70eb7cc799dcdbfba8b5b3475a` | Direkter Test-Leser des Lib-Schemas; ohne Nachbar-Checkout Skip. |
| `lunados.cube/P1/simulation-profile-v1/P1_8_ACCEPTANCE_SPEC.md` | `491bdd97a426cd99fc44525367a25f1dd8df05da4866d3127c9d3faf9125ec09` | `library_ref` wird nur auf Format geprüft, nicht aufgelöst. Die dortige P1.8 D-3 ist eine andere Entscheidung. |
| `lunados.cube/P3/remote-mcp-g5/python-core/core_runtime.py` | `ccf148d4c9d385de71b373b8d52983cf573da74b85335dcb51153677b0762642` | Aktueller G5-Quellwert `library_resolution: format_check_only`. |
| `agent-relay-poc-v3/docs/10-contracts/MILE-071-MODULE-CONTRACT-BASELINE.md` | `0cec7ddb479e389d2ba55e3a0571f14e83ca74c4103d14e6a0e5dc31b2dd1470` | Zielbild: Host-selected Descriptor snapshot; Cube empfängt über Host. Relay-HEAD beim Lesen: `6d6f62d234696e85f8618da83d31ac9a2915a918`. |

Der [Lib-Owner-Nachweis aus TASK-088](TASK-088-RESULT.md) bindet Index, 13 Entries, Deskriptor und Prüfskript. Er belegt Offline-Pins und Lib-Zuordnungen, nicht den hier erst festgelegten Host-Laufzeitpfad.

## Abnahme gegen TASK-091

| Prüffall | Dokumentierter Befund |
|---|---|
| Gleiche ausgewählte Index- und Entry-Bytes über direkten und Host-Pfad | Ein gemeinsamer, unabhängig gewählter Index-Pin plus Entry-Prüfung belegt dieselben ausgewählten Definitionen; der Pfadname allein genügt nicht. |
| Fehlender Pin oder Host-Snapshot | Explizit nicht verfügbar; kein direkter Laufzeit-Fallback. |
| Falscher Index- oder Entry-Hash; unterschiedliche Index-Pins | Bindung ablehnen beziehungsweise Gleichheit nicht behaupten; kein Wechsel zu `latest` oder Nachbar-Checkout. |
| Abgleich mit MILE-071 | Host-Pfad bleibt Laufzeit-Zielbild; ADR ergänzt Build-/Test-Pfad. Relay-Folgenotiz mit ADR-Verweis ist geplant, dessen Baseline wurde nicht geändert. |

Geändert wurden nur Cube-Dokumente: ADR-001, ADR-Index, Task-/Mile-/OpenSpec-Status und dieser Nachweis. Weder Cube- noch Lib-Reader, G5-Runtime, Host-Loader, Relay-Baseline, Vertrag oder Deployment wurden für TASK-091 geändert. Die Tabelle ist eine Prüfung der dokumentierten Entscheidung gegen Quellstand und Fälle, kein ausgeführter Host-Test.
