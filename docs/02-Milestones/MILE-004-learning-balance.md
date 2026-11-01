# MILE-004 — Lernbilanz und Maßnahmenwahl

Status: done · Stand: 2026-11-01 · Voraussetzung: MILE-002 und MILE-003 abgeschlossen und abgenommen

## Ergebnis

Die sieben Leitfragen aus dem [Lernvergleich](../09-Research/cube-grammar-2026-11-01/LERNVERGLEICH.md) sind beantwortet oder präzise offen. Die beiden bisher offenen Fragen — Envelope-Rahmen (1) und Bindungen für LENS, MODE und Achsen (4) — sind durch kleine, vorab erwartete Proben geprüft. Alle Maßnahmen aus der [Lückenbilanz](../09-Research/grammar-sampling/GAP-LEDGER.md) und der [Darstellungsübergabe](../09-Research/visual-check/HANDOVER.md) sind nach Nutzen, Aufwand, Komplexität und Unsicherheit priorisiert. Für die ein bis zwei obersten Maßnahmen ist MILE-005 ausgeplant, noch ohne Umsetzung.

## Entscheidungen (2026-11-01)

- **D-1 Anwendungsfälle:** Die Priorität bestimmen **Architektursichten** (verdichtete Sichten mit Herkunft; C4, ArchiMate) und **Prozessspuren** (instanzgenaue Abläufe; BPMN). Impact/Reihenfolge und Vollständigkeit zählen, soweit sie diese beiden tragen.
- **D-2 Offene Leitfragen:** kleine Proben (2–4 Fälle) mit Erwartung vor dem Lauf; Ergebnis ist eine Antwort oder eine präzise offene Frage.
- **D-3 Ergebnis:** Lernbilanz plus ausgeplanter Folgemilestone MILE-005 für die ein bis zwei obersten Maßnahmen; keine Umsetzung in MILE-004.
- **D-4 Menschentest:** nicht Teil von MILE-004; das [Skript](../09-Research/visual-check/HUMAN-TEST-SCRIPT.md) bleibt für später.

## Drei Miles / Chargen

| Mile | Ergebnis | Abschlusskriterium | Aufgaben |
|---|---|---|---|
| **MILE-004-A — Offene Leitfragen proben** | Leitfragen 1 und 4 beantwortet oder präzise offen | Probeplan mit gepinnten Quellen und Erwartungen vor dem Lauf; Ergebnisse je Probe mit Nachweisart | TASK-024–025 |
| **MILE-004-B — Lernbilanz** | Alle Maßnahmen nach festem, vorab committetem Bewertungsrahmen priorisiert | Bewertungsrahmen vor der Bewertung; Rangfolge mit Begründung, Abhängigkeiten und Unsicherheit; sieben Leitfragen final | TASK-026–027 |
| **MILE-004-C — Folgeplanung und Übergabe** | MILE-005 ausgeplant; EPIC-001 abgeschlossen | Milestone, Stories, Tasks und OpenSpec-Vorschlag für MILE-005; Abschlussprüfung mit Hashes | TASK-028–029 |

A liefert die Antworten auf Frage 1 und 4 für B; C baut auf der Rangfolge aus B auf.

## Umfang und Prüflogik

- **Proben (A):** E-1 Projektion mit Quellenspur (C4-02, Architektur) und E-2 instanzgebundene Spurprüfung (BPMN-02/03, Prozess) im vorhandenen Envelope-Vertrag; L-1 Herkunft je Kante (C4-03) als LENS-Bindung und L-2 Instanzgruppierung (BPMN-03) als Achse, Partition oder MODE. Prüfkriterium für eine Envelope-Erweiterung laut Lernvergleich §1: zwei fachlich verschiedene Zustände werden ununterscheidbar, oder Pflichtbindungen sind nur als Freitext unterzubringen.
- **Bewertung (B):** Maßnahmen G-01–G-10, T-01–T-04, VR-01–VR-12 und PO-1–PO-7 werden mit einem vorab festgelegten Rahmen bewertet (Nutzen je Anwendungsfall nach D-1, Aufwand, Komplexität, Unsicherheit, Abhängigkeiten). Visuelle Regeln folgen ihrer Profil-/LIB-Voraussetzung.
- **Grenzen:** keine Implementierung, keine Morphologie-, Envelope-, Printer- oder Ankeränderung; ein Envelope- oder Morphologie-Kandidat wird nur mit Probenbeleg genannt. Nutzen bleibt erwartet, nicht gemessen.

## Epics, Stories und Aufwand

[EPIC-001](../03-Epics/EPIC-001-grammar-learning.md). US-015–017, TASK-024–029. **9–12 h, grob 1–1,5 PT** (0,5–1 PT laut Roadmap plus etwa 0,5 PT für die Proben nach D-2). A: 4–5 h; B: 3–4 h; C: 2–3 h. Nutzen sehr hoch (übersetzt den Vergleich in umsetzbare Arbeit), Komplexität niedrig–mittel.

## Nachverfolgung

[OpenSpec-Change](../../openspec/changes/archive/2026-11-01-prioritize-learning-balance/proposal.md) · [Aufgabenstatus](../../openspec/changes/archive/2026-11-01-prioritize-learning-balance/tasks.md) · [Abdeckung](../../openspec/changes/archive/2026-11-01-prioritize-learning-balance/TRACEABILITY.md) · [Arbeitsordner](../09-Research/learning-balance/README.md). MILE-004-A abgeschlossen: [Probeplan](../09-Research/learning-balance/probes/PROBE-PLAN.md), [Probeergebnisse](../09-Research/learning-balance/PROBE-RESULTS.md). MILE-004-B abgeschlossen: [Bewertungsrahmen](../09-Research/learning-balance/SCORING-FRAME.md), [Lernbilanz](../09-Research/learning-balance/LERNBILANZ.md). TASK-028: [Plan MILE-005](MILE-005-completeness-instances.md). Alle Abschlusskriterien der drei Chargen sind mit Nachweisen erfüllt ([C-RESULT](../10-Evidence/MILE-004/C-RESULT.md)).
