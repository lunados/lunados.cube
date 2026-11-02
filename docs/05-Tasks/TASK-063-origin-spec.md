# TASK-063 — Spezifikation und Detailfragen

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/archive/2026-11-02-declare-relation-origin/tasks.md).

Story: [US-032](../04-US/US-032-relation-origin-profile.md), [US-033](../04-US/US-033-origin-line-view.md) · Mile: MILE-011-A · Aufwand: 0,25–0,5 PT

## Ziel und Arbeit

Abnahmespezifikationen P1.14 (`binding-context/10`: Parametervertrag `origin`, Grundlage einer Ableitung, Diagnosen, Discovery) und VP-07.6 (`cube.flow` mit Herkunftslinie und Aussagenmengen, Legende, PO-1). Detailfragen werden benannt und vom Nutzer entschieden; eigener Commit.

## Ergebnis und Akzeptanz

- Spezifikationen mit aufgelösten Detailfragen, bevor Prüffälle und Code entstehen.

## Abhängigkeiten und Grenze

Entscheidungen D-1–D-8

Umfang gemäß [MILE-011](../02-Milestones/MILE-011-relation-origin.md). P0, P1.1–P1.13, VP-07 0.7.0–0.7.5, VP-10, VP-11 und vorhandene lunados.lib-Einträge bleiben byte-gleich.

## Ergebnis (2026-11-02)

- [Spezifikation P1.14](../../P1/relation-origin-profile-v1/P1_14_ACCEPTANCE_SPEC.md): `binding-context/10`, `origin_binding` je Prädikat, `origin` ∈ {declared, derived, unknown}, Grundlage über `origin_bases` (Aussagen oder Projektionsdatensatz), `statement-set/2`, Herkunft auch an Plan-Abhängigkeiten, drei neue Codes; Vektoren HO-01–HO-12 geplant. Entwurf `64cf9c0`; Q-1–Q-9 nach Vorschlag entschieden.
- [Spezifikation VP-07.6](../../P2/visual-printer-migration-v1/VP07_6_ACCEPTANCE_SPEC.md): `cube.flow` mit Linienart je Kante nach gebundener Herkunft, Herkunftstext, feste Legende, Aussagenmengen-Pfad mit drei zusätzlichen Konzepten, PO-1; Vektoren OL-01–OL-12 geplant. Entwurf `64cf9c0`; Q-1–Q-10 nach Vorschlag entschieden.

