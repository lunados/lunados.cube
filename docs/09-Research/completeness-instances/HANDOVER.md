# MILE-005 — Übergabe (TASK-036)

Stand: 2026-11-02 · Abschlussprüfung: [verification.json](../../10-Evidence/MILE-005/verification.json), [C-RESULT](../../10-Evidence/MILE-005/C-RESULT.md)

## Was jetzt prüfbar und darstellbar ist

| Lücke (MILE-002) | Jetzt | Wo |
|---|---|---|
| **G-01:** „geprüft leer“ und „unbekannt“ waren nicht unterscheidbar, Zählregeln nicht ausführbar | Abdeckungserklärungen und Populationsregeln in `binding-context/8`. P1 prüft Erklärung und Abdeckung; ohne Abdeckung ist das Ergebnis UNRESOLVED `P1_COVERAGE_UNDECLARED`, nie FAIL. lunados.lib `analyze.population/v1` wertet Abwesenheit, Anzahl und Join-Aktivierung über Aussagenmengen aus. | [P1.12](../../../P1/coverage-instance-profile-v1/README.md), lunados.lib `entries/analyze.population/v1` |
| **G-08:** Instanz nur im Namen, BPMN-03 im gemeinsamen Scope ergab PASS | `instance_ref` auf Referenten und `requires_same_instance` auf Prädikaten. BPMN-03 im gemeinsamen Scope ergibt jetzt FAIL `P1_INSTANCE_MISMATCH`; der Fall mit Scope je Instanz bleibt unverändert. | [P1.12](../../../P1/coverage-instance-profile-v1/README.md), [Wiederholung](rerun/README.md) |
| **VR-05 / PO-6:** Zellzustände | VP-10 `cube.cells`: markiert, geprüft leer (nur im erklärten Umfang), unbekannt (Linienschraffur), ausgeblendet (mit Namen); unterscheidbar ohne Farbe | [VP-10](../../../P2/visual-printer-cells-v1/README.md), [Vergleich M-05C](../../../P2/visual-printer-cells-v1/M05C_COMPARISON.md) |

Lokal verfügbar über MCP:
- **G4:** `cube_validate` mit `/8`.
- **Discovery:** listet `/8` mit Einstiegsprofil P1.12.
- **G6:** `cube_plan_source` mit `printer: vpcells`, `cube_plan_views` mit `view: cube.cells`, dazu `cube_plan_check`.

## Folgearbeit (nicht Teil von MILE-005)

| Punkt | Inhalt | Bezug |
|---|---|---|
| G5 und Host-Abnahme | `/8` und VP-10 im Remote-Kern (Pyodide), Live-Smoke, unabhängige Host-Abnahme | MILE-005 D-5 |
| Menschliche Lesbarkeit | Prüfung der Zellzustände mit Menschen; das Skript liegt vor | [HUMAN-TEST-SCRIPT](../visual-check/HUMAN-TEST-SCRIPT.md) |
| Deklarierte Achsenreihenfolge | DSM-Lesart „über der Diagonale“, Rückkopplung; heute ordnet die Matrix nach erstem Auftreten | PO-5 |
| Aussagenmengen ohne Plan | VP-10 liest heute Migrationspläne; eine allgemeine Projektion beliebiger Aussagen fehlt | PO-7, G-03 |
| Weitere Paare | Zellzustände für Y × Z (ungerichtet) oder Z × Z | VP-10 D-3 |
| Instanzsicht | Instanz als Rahmen, instanzübergreifende Kante als Verstoß | VR-12 |
| Kontrollfluss | Exklusivität je Gatewaytyp, Synchronisation, Spurkonformität | G-07 |
| Mehrere Aussagen in `cube_validate` | Populationsregeln werden in P1 nur erklärt; die Auswertung bleibt LIB-seitig. Eine Cube-seitige Deklaration des LIB-Aufrufs (P1.8-Replay) ist möglich und liegt als Referenzfall vor. | D-6 |
| Push und Abnahme | Branches `feature/mile005-completeness-instances` (lunados.cube) und `feature/analyze-population` (lunados.lib) | Nutzerfreigabe |

## Befunde unterwegs

- P1.12 löste Prädikate aus `predicate_profile_refs` nicht auf (`5f32bce`, behoben, mit Test).
- Die Prüfsummenliste `P3/charge3-p16` ist ein historischer Schnappschuss und war schon vor MILE-005 veraltet. Sie wird in der Abschlussprüfung ausgewiesen, aber nicht erzwungen.
