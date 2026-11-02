# TASK-068 — Sichtprüfung und Abschluss

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/archive/2026-11-02-declare-relation-origin/tasks.md).

Story: [US-032](../04-US/US-032-relation-origin-profile.md), [US-033](../04-US/US-033-origin-line-view.md) · Mile: MILE-011-C · Aufwand: 0,25–0,5 PT

## Ziel und Arbeit

Kurze angeleitete Sichtprüfung der Herkunftslinie durch den Nutzer (Anleitung committet); Abschlussprüfung, C-RESULT, Specs konsolidieren, Change archivieren.

## Ergebnis und Akzeptanz

- Jeder Prüfpunkt beantwortet, jedes „nein“ bearbeitet; Abschlussprüfung `all_ok`.

## Abhängigkeiten und Grenze

[TASK-067](TASK-067-origin-g5.md)

Umfang gemäß [MILE-011](../02-Milestones/MILE-011-relation-origin.md). P0, P1.1–P1.13, VP-07 0.7.0–0.7.5, VP-10, VP-11 und vorhandene lunados.lib-Einträge bleiben byte-gleich.

## Ergebnis (2026-11-02)

- Prüfung von TASK-065–067 (umgesetzt mit ChatGPT/Codex): Orakel, Pins und R6-Erwartungen unverändert; HO-01–HO-12 und OL-01–OL-12 unabhängig gegen die Orakel nachgerechnet, OL je Kante; Pins 0.7.0–0.7.5 byte-gleich; G5 offline 26/26 und 87/87.
- Korrigiert: `VP07_SHA256SUMS.txt` (acht Dateien veraltet) und der Orakel-Lauf `run_vectors_ol.py` (prüft jetzt jede Kante); Commit `e860778`.
- [Sichtprüfung](../10-Evidence/MILE-011/visual-check/SICHTPRUEFUNG.md): S-1–S-6 ja; die englische Legendenüberschrift unter `locale de` ist angenommen.
- Abschlussprüfung `all_ok` ([verification.json](../10-Evidence/MILE-011/verification.json)); [C-RESULT](../10-Evidence/MILE-011/C-RESULT.md); Specs `relation-origin` und `origin-line-view` konsolidiert, Change archiviert.

