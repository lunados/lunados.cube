# TASK-037 — G5-Kern mit P1.12

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/archive/2026-11-02-deliver-remote-and-ordered-cells/tasks.md).

Story: [US-021](../04-US/US-021-remote-v8.md) · Mile: MILE-006-A · Aufwand: 0,5 PT

## Ziel und Arbeit

P1.12 (`cube_p112`) in `assemble_core.py` aufnehmen; Discovery-Abschnitt `p112_coverage_instance` im Kern; Version `0.7.0-proof`; Assembly-Prüfung mit K-01–K-21; Parität G4/G5 offline; Erwartungen für die Live-Abnahme vorab festlegen.

## Ergebnis und Akzeptanz

- Offline-Prüfung `verify_g5.py` PASS; Parität G4/G5 für alle K-Vektoren.
- Erwartungsdatei für die Host-Abnahme vor der Bereitstellung committet.

## Abhängigkeiten und Grenze

MILE-005 (P1.12, Adapter G4)

Umfang gemäß [MILE-006](../02-Milestones/MILE-006-remote-and-order.md). Keine neue Prüfsemantik; P0, P1.1–P1.12, VP-07, VP-09 und VP-10 0.10.0 bleiben byte-gleich.

## Ergebnis (2026-11-02)

- **Erwartungen vorab:** [G5_R4_P112_EXPECTATIONS.json](../../P3/remote-mcp-g5/evidence/G5_R4_P112_EXPECTATIONS.json) (`68ba97f`) mit 13 K-Vektoren, Discovery-Feldern, Envelope, Fehlerfällen, Golden und Regressionen. Festgelegt vor jeder Kern-Änderung.
- **Kern `P3-MCP-REMOTE/0.7.0-proof`:** `cube_p112` wird mit zusammengestellt (103 Dateien). Neuer Discovery-Abschnitt `p112_coverage_instance` mit `population_evaluation_by_cube: false`. Keine neuen Laufzeit-Assets nötig (P1.12 liest nur die vorhandene P1.10-Profildatei). Gateway unverändert.
- **Assembly-Prüfung:** alle K-01–K-21 über den gestagten Kern wie Orakel; `/7` mit P1.12-Feldern ergibt `P1_MCP_CONFIG_INVALID`.
- **Parität G4/G5 offline:** P1.12 21/21 identisch, P1.11 unverändert 15/15. `verify_g5.py`: PASS G5 OFFLINE. `SHA256SUMS.txt` der G5-Quellen aktualisiert.
- **Nächster Schritt:** [TASK-038](TASK-038-g5-host-acceptance.md). Der Nutzer stellt nach [DEPLOYMENT.md](../../P3/remote-mcp-g5/DEPLOYMENT.md) bereit (nur der private Python-Worker; das Gateway bleibt unverändert).
