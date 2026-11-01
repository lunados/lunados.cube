# TASK-018 — Darstellungsanforderungen gegen vorhandene Sichten inventarisieren

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/check-visual-distinctions/tasks.md).

Story: [US-012](../04-US/US-012-presentation-inventory.md) · Mile: MILE-003-A · Aufwand: 2 h

## Ziel und Arbeit

Für V-01–V-12 aus Spezifikationen, READMEs und Code der Printer VP-03…VP-09 und aus symbols.json bestimmen: Sicht, Eingabeformat, tragendes Merkmal (Kantenstil, Anker, Zellinhalt, Gruppierung) oder Lücke.

## Ergebnis und Akzeptanz

- Inventurtabelle mit Nachweisart Doku/Code; strittige Zeilen als ‚nicht geprüft‘, nicht als vorhanden.

## Eingaben / betroffene Ablagen

[Lückenbilanz §6](../09-Research/grammar-sampling/GAP-LEDGER.md), [Fallberichte](../09-Research/grammar-sampling/README.md), [Prüfprotokoll](../09-Research/visual-check/README.md). Neue Ergebnisse unter `docs/09-Research/visual-check/`, Rohnachweise und SVGs unter `docs/10-Evidence/MILE-003/`.

## Abhängigkeiten und Grenze

[MILE-002 abgeschlossen](../02-Milestones/MILE-002-grammar-sampling.md)

Umfang gemäß [MILE-003](../02-Milestones/MILE-003-visual-check.md). Keine Printer-, Morphologie- oder VG-Ankeränderung. Mockups sind Kandidaten, kein Printer-Output. Die Agenten-Vorprüfung ist kein menschlicher Lesbarkeitsnachweis. Noch kein Ausführungsnachweis vorhanden.

## Ergebnis

Abgeschlossen am 2026-11-01. [Inventur](../09-Research/visual-check/INVENTORY.md): acht vorhandene Mechanismen (M-1 Kantenstil je Prädikat, M-2 Linsenakzent, M-3 farbfreie Schraffur, M-4 Auslassungsledger, M-5 Matrix mit Mitgliedschaftslegende, M-6 Sequenzfragmente, M-7 Baumsicht, M-8 VG-Anker) mit Fundstelle und Grenze; Urteil je Anforderung: 0 × trägt, 9 × teilweise, 3 × Lücke (V-07, V-11, V-12). Vorrang: V-01 und V-09 als Printer-Paar möglich, V-05 teilweise, V-12 nur als Mockup. Nachweisart ausschließlich Doku/Code; ob `--hide-empty` im SVG sichtbar wird, prüft TASK-019.

