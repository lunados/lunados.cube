# TASK-054 — Prüffälle, Orakel und Pins

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/archive/2026-11-02-show-instance-view/tasks.md).

Story: [US-028](../04-US/US-028-instance-path-view.md), [US-029](../04-US/US-029-join-input-view.md) · Mile: MILE-009-A · Aufwand: 0,25–0,5 PT

## Ziel und Arbeit

Prüffälle aus BPMN-01/02/03 und den MILE-008-Fällen, je mit und ohne LIB-Ergebnis, plus Eingabefehler; unabhängiges Orakel (erwartete Texte, Zustände, Ledger-Einträge, Diagnosen je Fall); Pins der vorhandenen Printer (Digests).

## Ergebnis und Akzeptanz

- Fälle, Orakel und Pins committet, bevor Printer-Code entsteht; synthetisch, ohne Kundendaten.

## Abhängigkeiten und Grenze

[TASK-053](TASK-053-vp11-spec.md)

Umfang gemäß [MILE-009](../02-Milestones/MILE-009-instance-view.md). Keine neue Prüfsemantik; P0, P1, VP-07–VP-10 und lunados.lib-Einträge bleiben byte-gleich.

## Ergebnis (2026-11-02)

- [Vektoren I-01–I-34](../../P2/visual-printer-instances-v1/fixtures/i01_i34_materialized.json) aus den lunados.lib-Fällen CF-11–CF-29 (INDEX `bf59c17e…`) und Varianten: 18 Fälle mit Datensatz, 3 ohne, 1 Sicht mit zwei Instanzen und sechs Datensätzen, 8 Fehler, 3 Warnungen, 1 deutsche Fassung. Datensätze aus dem LIB-`expected` bzw. dem gepinnten Evaluator; der Evaluator stimmt für alle 18 Fälle mit `expected` überein.
- Jede Spur-Aussage eines gültigen Kontexts besteht P1.13; I-25, I-26 und I-32 bleiben dort wie gewollt UNRESOLVED, I-23 wird abgelehnt.
- [Orakel](../../P2/visual-printer-instances-v1/oracles/independent_i01_i34.json) von Hand aus der Spezifikation: Rahmen, Blöcke, Zeilen, Urteilszeilen, Modellzeilen, Warnungen, Fehlercodes, Verstoßmarken. Präzisierungen TR-4, TR-5, DR-1a–DR-7a in §9 der [Spezifikation](../../P2/visual-printer-instances-v1/VP11_ACCEPTANCE_SPEC.md), ohne Änderung einer Entscheidung.
- VP-10 0.11.0 gepinnt: 15 CLI-Ausgaben (S-01–S-15), 15/15 byte-gleich.
