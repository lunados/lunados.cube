# TASK-019 — MILE-002-Material mit vorhandenen Printern rendern

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/archive/2026-11-01-check-visual-distinctions/tasks.md).

Story: [US-012](../04-US/US-012-presentation-inventory.md) · Mile: MILE-003-A · Aufwand: 2 h

## Ziel und Arbeit

Wo ein Eingabeformat existiert (z. B. Y × Y für DSM, Sequenz für BPMN), kleine Quellen aus den MILE-002-Modellen erstellen und über den lokalen MCP-Pfad rendern; Erwartung vorher festhalten.

## Ergebnis und Akzeptanz

- SVG und Bericht mit Hash je Lauf; Abweichung von der Erwartung wird berichtet, nicht korrigiert.

## Eingaben / betroffene Ablagen

[Lückenbilanz §6](../09-Research/grammar-sampling/GAP-LEDGER.md), [Fallberichte](../09-Research/grammar-sampling/README.md), [Prüfprotokoll](../09-Research/visual-check/README.md). Neue Ergebnisse unter `docs/09-Research/visual-check/`, Rohnachweise und SVGs unter `docs/10-Evidence/MILE-003/`.

## Abhängigkeiten und Grenze

[TASK-018](TASK-018-inventory.md)

Umfang gemäß [MILE-003](../02-Milestones/MILE-003-visual-check.md). Keine Printer-, Morphologie- oder VG-Ankeränderung. Mockups sind Kandidaten, kein Printer-Output. Die Agenten-Vorprüfung ist kein menschlicher Lesbarkeitsnachweis. Noch kein Ausführungsnachweis vorhanden.

## Ergebnis

Abgeschlossen am 2026-11-01. [Render-Nachweise](../09-Research/visual-check/RENDER-RESULTS.md): R-1 (DSM als `cube.axes` Y × Y, mit/ohne `hide_empty`) und R-2 (C4 als `cube.flow`, mit/ohne `edge_styles`); Erwartungen vor dem Rendern committet (`657efe8`, Aufrufargument nachgetragen `1b4f4b7`, erster Fehlversuch protokolliert). Alle vier Läufe `plan_check` PASS. Abweichungen berichtet, nicht korrigiert: Achsenreihenfolge nach erstem Auftreten, zwei Panels je Schritt. Befunde: V-01 als Printer-Paar belegt; „geprüft leer“ = „unbekannt“ im Bild belegt; Ausblendungsanzahl im SVG sichtbar; Plansichten nur über Umabbildung ins Migrationsvokabular nutzbar.

