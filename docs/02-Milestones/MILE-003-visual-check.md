# MILE-003 — Darstellung prüfen (Agenten-Vorprüfung)

Status: in_progress · Stand: 2026-11-01 · Voraussetzung: MILE-002 abgeschlossen

## Ergebnis

Für die zwölf Darstellungsanforderungen V-01–V-12 aus der [Lückenbilanz](../09-Research/grammar-sampling/GAP-LEDGER.md) ist belegt, welche heutige Sicht (Graph, Matrix, Sequenz, Phasen) die geforderte Unterscheidung tragen kann. Für die vier vorrangigen Unterscheidungen liegen Minimalpaare vor — aus vorhandenen Printern oder als markierte Handmockups — und eine dokumentierte Agenten-Vorprüfung. Ergebnis ist ein Darstellungsbefund mit Kandidaten für visuelle Regeln und ein vorbereitetes Skript für einen späteren menschlichen Lesbarkeitstest.

## Entscheidungen (2026-11-01)

- **D-1 Prüfende:** ausschließlich Agenten-Vorprüfung. Sie prüft Unterscheidbarkeit, Legende, Rückführbarkeit und ob eine Fallfrage allein aus der Darstellung beantwortbar ist. **Kein menschlicher Lesbarkeitsnachweis**; Aussagen über Verständlichkeit bleiben offen.
- **D-2 Mockups:** Wo vorhandene Printer eine Unterscheidung nicht darstellen, werden Handmockups als SVG gezeichnet, sichtbar als „MOCKUP — kein Printer-Output“ gekennzeichnet, nur mit vorhandenen VG-Ankern und ohne Printer-Code.

## Drei Miles / Chargen

| Mile | Ergebnis | Abschlusskriterium | Aufgaben |
|---|---|---|---|
| **MILE-003-A — Darstellungsinventur** | Für V-01–V-12: tragende Sicht/Printer/Anker oder begründete Lücke | Inventurtabelle mit Nachweisart je Zeile (Doku/Code, Render, nicht geprüft); MILE-002-Material dort gerendert, wo ein Eingabeformat existiert | TASK-018–019 |
| **MILE-003-B — Minimalpaare und Kandidaten** | Für V-01, V-05, V-09, V-12 je ein Minimalpaar (Unterscheidung vorhanden/nicht vorhanden) | Paare aus Printer-Output oder markiertem Mockup, mit Eingabe, Hash und Fallbezug | TASK-020–021 |
| **MILE-003-C — Vorprüfung und Übergabe** | Agenten-Vorprüfung nach festem Protokoll; Kandidaten visueller Regeln; Skript für späteren Menschentest | Prüfbericht je Paar, Übergabe an MILE-004, ehrliche Grenzen | TASK-022–023 |

A geht B voraus; C verwendet A und B.

## Umfang und Prüflogik

- Vorrang: V-01 (abgeleitet vs. deklariert), V-05 (vier Zellzustände), V-09 (Zeugenzyklus), V-12 (Instanzgruppierung). Die übrigen acht nur inventarisiert.
- Vorhandene Sichten: Kern-P2 `cube.flow`/`cube.diagramm`/`cube.tree` (VP-03-Linsen), Plansichten `cube.phases`/`cube.flow` (VP-07), `cube.sequence` (VP-08), `cube.axes` (VP-09); 129 VG-Anker (u. a. Derivation ↦, Projection ⇉).
- Erwartung vor dem Rendern festhalten; Rendern ausschließlich über den lokalen MCP-Pfad bzw. die CLI, Ergebnisse mit Hash.
- Prüfprotokoll in [visual-check/README](../09-Research/visual-check/README.md); Fragen stammen aus den Fallberichten.

## Epics, Stories und Aufwand

[EPIC-001](../03-Epics/EPIC-001-grammar-learning.md). US-012–014, TASK-018–023. **11–15 h, grob 1–2 PT.** A: 3–4 h; B: 5–7 h; C: 3–4 h. Nutzen hoch (Grundlage für visuelle Regeln in MILE-004), Komplexität mittel. Ein menschlicher Lesbarkeitstest ist nicht enthalten und wäre ein eigener Schritt.

## Nachverfolgung

[OpenSpec-Change](../../openspec/changes/check-visual-distinctions/proposal.md) · [Aufgabenstatus](../../openspec/changes/check-visual-distinctions/tasks.md) · [Abdeckung](../../openspec/changes/check-visual-distinctions/TRACEABILITY.md). TASK-018 erledigt: [Inventur](../09-Research/visual-check/INVENTORY.md).
