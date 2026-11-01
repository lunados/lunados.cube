# TASK-003 — Minimales Fall- und Berichtsformat festlegen

Planungsstand: umgesetzt und verifiziert. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/archive/2026-11-01-prepare-grammar-comparison/tasks.md).

Story: [US-003](../04-US/US-003-repeatable-probes.md) · Mile: MILE-001-B · Aufwand: 1–2 h

## Ziel und Arbeit

Aus den vorhandenen MCP-Proben einen PASS-, FAIL- und UNRESOLVED-Fall auswählen. Erwartung vor dem Lauf fixieren. Ein kleines versioniertes Format für Fälle und Berichte anhand dieser Beispiele ausarbeiten.

## Eingaben / betroffene Bereiche

`docs/09-Research/cube-grammar-2026-11-01/evidence/mcp-probes.json`; `docs/99-templates/RESEARCH-CASE.md`; Delta `comparison-evidence`.

Die genannten Ablagen wurden im beschriebenen Umfang umgesetzt; konkrete Nachweise siehe Ergebnisverweis.

## Ergebnis

Drei referenzierte Fixtures, Schema/Formatdefinition und Regeln für Ergebnisvergleich und Herkunft.

## Akzeptanz

- Fall-ID, Quellen-/Codeversion, exakte Eingabe, Profile, Operation, Aufrufart und erwartete Diagnose sind erfasst.
- Berichte trennen Ausdruck, Bindung, Prüfung, Darstellung und Nutzen; ungeprüfte Felder haben keine Erfolgsvoreinstellung.
- Historische Eingaben bleiben unverändert; neue Fixtures verweisen auf Herkunft und Hash.

## Gezielte Verifikation

Drei vollständige Beispieldatensätze gegen das Format prüfen; eine fehlende Pflichtbindung gezielt zurückweisen. Keine neue universelle Modellgrammatik entwickeln.

## Abhängigkeiten und Grenze

Keine; vorhandene Research-Basis verwenden.

Umfangsgrenze: [MILE-001](../02-Milestones/MILE-001-analysis-readiness.md). Keine Veränderung an Morphologie oder Envelope-Semantik. Der konkrete Nachweis ist unten verlinkt; daraus folgt keine fachliche Gesamtvalidierung.


## Abschlussnachweis

Abgeschlossen am 2026-11-01. [Charge B: Ausführung und Nachweis](../10-Evidence/MILE-001/B-RESULT.md).
