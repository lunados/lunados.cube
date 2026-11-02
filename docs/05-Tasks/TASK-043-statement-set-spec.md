# TASK-043 — Spezifikation und Detailfragen

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/project-statement-sets/tasks.md).

Story: [US-024](../04-US/US-024-statement-set-view.md) · Mile: MILE-007-A · Aufwand: 0,25–0,5 PT

## Ziel und Arbeit

Abnahmespezifikation für das Format `aiaeao.cube.statement-set/1`, das Ergebnis `aiaeao.projection-result/v1` und VP-10 0.11.0 (Eingabe, Achsen, Anzeige abgeleiteter Einträge, Legende, Ledger, Diagnosen). Detailfragen werden benannt und vom Nutzer entschieden; separater Commit.

## Ergebnis und Akzeptanz

- Spezifikationen mit aufgelösten Detailfragen, bevor Prüffälle und Code entstehen.

## Abhängigkeiten und Grenze

Entscheidungen D-1–D-8 in MILE-007

Umfang gemäß [MILE-007](../02-Milestones/MILE-007-statement-sets.md). Keine neue Prüfsemantik; P0, P1.1–P1.12, VP-07, VP-09 und VP-10 0.10.0/0.10.1 bleiben byte-gleich.

## Ergebnis (2026-11-02)

- [Spezifikation VP-10 0.11.0](../../P2/visual-printer-cells-v1/VP110_ACCEPTANCE_SPEC.md): Format `aiaeao.cube.statement-set/1`, Ergebnis `aiaeao.projection-result/v1`, Zeichenregeln DR-1–DR-6, Schnittstellen, Diagnosen. Entwurf `3279fe4`; Q-1–Q-10 nach Vorschlag entschieden.
- Folge von Q-2/Q-3: C4 liegt in Z, und der VP-07-Weg kennt nur sechs Konzepte. Deshalb Y × Y und Z × Z mit eigenem Matrix-Zeichner; Aufwand Charge C +0,25–0,5 PT.
