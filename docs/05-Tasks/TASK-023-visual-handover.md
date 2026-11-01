# TASK-023 — Nachweise prüfen und MILE-003 übergeben

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/archive/2026-11-01-check-visual-distinctions/tasks.md).

Story: [US-014](../04-US/US-014-agent-precheck-handover.md) · Mile: MILE-003-C · Aufwand: 1–2 h

## Ziel und Arbeit

Vollständigkeit prüfen, Kandidaten visueller Regeln mit Aufwand an MILE-004 übergeben, Skript für einen späteren Menschentest beilegen, OpenSpec konsolidieren.

## Ergebnis und Akzeptanz

- Status, Links, Hashes stimmen; offene Punkte bleiben offen.

## Eingaben / betroffene Ablagen

[Lückenbilanz §6](../09-Research/grammar-sampling/GAP-LEDGER.md), [Fallberichte](../09-Research/grammar-sampling/README.md), [Prüfprotokoll](../09-Research/visual-check/README.md). Neue Ergebnisse unter `docs/09-Research/visual-check/`, Rohnachweise und SVGs unter `docs/10-Evidence/MILE-003/`.

## Abhängigkeiten und Grenze

[TASK-022](TASK-022-agent-precheck.md)

Umfang gemäß [MILE-003](../02-Milestones/MILE-003-visual-check.md). Keine Printer-, Morphologie- oder VG-Ankeränderung. Mockups sind Kandidaten, kein Printer-Output. Die Agenten-Vorprüfung ist kein menschlicher Lesbarkeitsnachweis. Ausführungsnachweis siehe Ergebnis.

## Ergebnis

Erledigt am 2026-11-01. Abschlussprüfung mit [verification.json](../10-Evidence/MILE-003/verification.json) und [C-RESULT](../10-Evidence/MILE-003/C-RESULT.md), Hashes in [MANIFEST.json](../10-Evidence/MILE-003/MANIFEST.json). [Übergabe an MILE-004](../09-Research/visual-check/HANDOVER.md): vier Kandidatenregeln VR-01, VR-05, VR-09, VR-12 mit Voraussetzung, Aufwand, Nutzen und Komplexität, sieben Printer-Befunde, Erratum zum DAG-Modell aus MILE-002. [Skript für einen späteren Menschentest](../09-Research/visual-check/HUMAN-TEST-SCRIPT.md). Spec konsolidiert in [visual-distinction-check](../../openspec/specs/visual-distinction-check/spec.md), Change archiviert. Offen bleiben menschliche Lesbarkeit und die nur inventarisierten Anforderungen.
