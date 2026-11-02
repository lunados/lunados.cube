# TASK-053 — Spezifikation und Detailfragen

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/show-instance-view/tasks.md).

Story: [US-028](../04-US/US-028-instance-path-view.md), [US-029](../04-US/US-029-join-input-view.md) · Mile: MILE-009-A · Aufwand: 0,25–0,5 PT

## Ziel und Arbeit

Abnahmespezifikation VP-11 (`cube.instances`): Eingaben (`binding-context/9`, optional `aiaeao.trace-conformance-result/v1`), Prüfung des Datensatzes, Zustände und Texte, Layout, Bericht, Ledger, Diagnosen, Invarianten. Detailfragen werden benannt und vom Nutzer entschieden; eigener Commit.

## Ergebnis und Akzeptanz

- Spezifikation mit aufgelösten Detailfragen, bevor Orakel und Code entstehen.

## Abhängigkeiten und Grenze

Entscheidungen D-1–D-8

Umfang gemäß [MILE-009](../02-Milestones/MILE-009-instance-view.md). Keine neue Prüfsemantik; P0, P1, VP-07–VP-10 und lunados.lib-Einträge bleiben byte-gleich.

## Ergebnis (2026-11-02)

- [Spezifikation VP-11](../../P2/visual-printer-instances-v1/VP11_ACCEPTANCE_SPEC.md): Eingaben IN, TR, RC mit abgeleiteten LIB-Eingaben, Zeichnung DR-1–DR-9, Ledger und Bericht, Diagnosen `VP11_*`, Vektorplan I-01–I-31. Entwurf `0b5b114`; Q-1–Q-10 nach Vorschlag entschieden.
- Q-1 präzisiert D-3: Ein `binding-context/9` enthält keine Aussagen; die Spur kommt als Aussagenmenge.
