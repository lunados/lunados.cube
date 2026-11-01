# Design — Darstellungsprüfung

Status: planned

## Context

P2 bietet Kern-Sichten über VP-03-Linsen sowie Plansichten (VP-07 Phasen/Fluss, VP-08 Sequenz, VP-09 Achsenmatrix). Laut VP-09-README behauptet eine leere Zelle nichts; Unbekannt und Leer sind dort also nicht getrennt. Die VG kennt Derivation (↦) und Projection (⇉) als Relationspfeile.

## Goals / Non-Goals

Belegen, welche Unterscheidungen heute darstellbar sind, und Kandidaten für fehlende sichtbar machen. Keine Printer-Implementierung, keine neuen Anker, kein Menschentest.

## Decisions

1. **D-1:** Agenten-Vorprüfung statt Menschentest; Antworten als Proxy markiert.
2. **D-2:** Handmockups als Kandidaten, nur mit vorhandenen Ankern, sichtbar gekennzeichnet.
3. Vorhandene Printer zuerst; ein Mockup nur, wenn das Inventar keine tragende Sicht belegt.
4. Erwartung vor jedem Render festhalten; Render über den lokalen MCP-Pfad mit Hash.

## Risks / Trade-offs

Eine Agenten-Vorprüfung kann Unterscheidbarkeit und Rückführbarkeit prüfen, aber nicht Verständlichkeit oder Suchzeit. Mockups können besser wirken als ein späterer Printer-Output; sie bleiben Kandidaten.

## Open Questions

- Welche Plansicht eignet sich für Graphen ohne Migrationsbezug (C4, DAG)?
- Reicht für V-01 der vorhandene Derivation-Anker, oder braucht es einen Kantenstil?
