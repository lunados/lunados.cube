# TASK-055 — Printer VP-11 `cube.instances`

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/show-instance-view/tasks.md).

Story: [US-028](../04-US/US-028-instance-path-view.md), [US-029](../04-US/US-029-join-input-view.md) · Mile: MILE-009-B · Aufwand: 1–1,5 PT

## Ziel und Arbeit

Paket `P2/visual-printer-instances-v1`: Eingabeprüfung, Zeichnung, Bericht und Ledger, CLI, materialisierte Vektoren, Tests; Invarianten wie VP-10 (ohne Farbe unterscheidbar, kein aktiver SVG-Inhalt, Ledger passt).

## Ergebnis und Akzeptanz

- Alle Vektoren wie Orakel; Pins der vorhandenen Printer halten; Tests grün.

## Abhängigkeiten und Grenze

[TASK-054](TASK-054-vp11-cases.md)

Umfang gemäß [MILE-009](../02-Milestones/MILE-009-instance-view.md). Keine neue Prüfsemantik; P0, P1, VP-07–VP-10 und lunados.lib-Einträge bleiben byte-gleich.

## Ergebnis (2026-11-02)

- Paket [`vpinstances`](../../P2/visual-printer-instances-v1/README.md): `trace.py` (Kontext, Spur, Datensätze nach TR-1–TR-5 und RC-1–RC-3, ohne Nachrechnen), `view.py` (Rahmen, Blöcke, Zeilen, Urteilszeilen, Modellfeld, Ledger, Bericht, Prüfung der Invarianten), `api.py` (G6-Form), `__main__.py` (CLI `from-trace`, `print-instances`, `check-instances`); deutsche Texte in einer gepinnten Datei.
- Vektoren I-01–I-34 34/34 wie das Orakel (Orakel und Pins `e842081` vor dem Code); 15 Tests grün, darunter der Abgleich der eigenen Ergebnisprüfung mit dem LIB-Schema und die Farbfreiheit der Zeilenmarken.
- VP-10 unverändert: 0.11.0 15/15, 0.10.1 9/9, 0.10.0 16/16 byte-gleich, S-Vektoren 16/16. Vorhandene Printer nur importiert, nicht geändert.
