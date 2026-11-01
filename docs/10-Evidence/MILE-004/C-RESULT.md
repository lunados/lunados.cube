# MILE-004 — Abschlussnachweis (TASK-029)

Stand: 2026-11-01 · Branch `feature/mile004-learning-balance` · Prüfung: [verification.json](verification.json), Skript [verify_mile004.py](verify_mile004.py) · Hashes: [MANIFEST.json](MANIFEST.json)

## Prüfung

| Kriterium | Ergebnis |
|---|---|
| Probeplan vor dem Lauf committet (`a0f6e95`), Nachtrag L-2 vor dem zweiten Lauf (`caec0e2`); Erwartungen, Regeln, Eingaben durch den Nachtrag unverändert | erfüllt |
| Lauf mit dem committeten Plan (Hash), alle zwölf Quellen zum Laufzeitpunkt wie gepinnt | erfüllt |
| E-1/E-2: alle Instanzen schema-gültig, Träger wie erwartet, Regel R-E2 | erfüllt |
| L-1a, L-1b, L-2: gerendert, `plan_check` PASS, SVG-Hashes wie protokolliert | erfüllt |
| Bewertungsrahmen vor der Bewertung committet (`60d24d5`), dort unbewertet, seitdem unverändert | erfüllt |
| Probeplan, Maßnahmenliste, Bewertung und Rangfolge aus den Skripten reproduzierbar | erfüllt |
| Auswahl MILE-005 nach Regel (Rang 1 + 2, 5,0 PT ≤ 5 PT) | erfüllt |
| MILE-005 nur geplant: P0–P3 seit `main` (`b916cc6`) ohne Commit und im Arbeitsbaum unverändert | erfüllt |
| Relative Links in docs/ und openspec/ | keine kaputten |

## Chargen

| Mile | Abschlusskriterium | Nachweis |
|---|---|---|
| MILE-004-A | Probeplan mit gepinnten Quellen und Erwartungen vor dem Lauf; Ergebnisse je Probe mit Nachweisart | [PROBE-PLAN](../../09-Research/learning-balance/probes/PROBE-PLAN.md), [PROBE-RESULTS](../../09-Research/learning-balance/PROBE-RESULTS.md), [Lauf](task025-probe-run.json), [Fehlversuch](task025-probe-run-attempt1.json) |
| MILE-004-B | Rahmen vor der Bewertung; Rangfolge mit Begründung, Abhängigkeiten, Unsicherheit; sieben Leitfragen final | [SCORING-FRAME](../../09-Research/learning-balance/SCORING-FRAME.md), [LERNBILANZ](../../09-Research/learning-balance/LERNBILANZ.md), [RANKING.json](../../09-Research/learning-balance/RANKING.json) |
| MILE-004-C | MILE-005 mit Milestone, Stories, Tasks, OpenSpec-Vorschlag; Abschlussprüfung | [MILE-005](../../02-Milestones/MILE-005-completeness-instances.md), dieser Nachweis |

## Ergebnis

- **Leitfrage 1:** Der Envelope-Rahmen reicht für Projektion und instanzgebundene Spurprüfung; es fehlt nur die Typisierung der Ergebnisdetails (LR-1) und der Instanz je Eingang (G-08).
- **Leitfrage 4:** LENS trägt je Linse eine binäre Hervorhebung. Die Partition `track` packt Instanzen zusammen (PO-8). MODE bleibt präzise offen.
- **Rangfolge:** 1. G-01 → VR-05, 2. G-08, 3. G-02 → VR-01. MILE-005 übernimmt Rang 1 und 2.
- Keine Envelope- und keine Morphologiekandidaten.

## Grenzen

- Nutzen erwartet, nicht gemessen.
- Bewertung durch einen Agenten nach festem Rahmen.
- Envelope-Instanzen von Hand erstellt, kein Evaluator ausgeführt.
- Kein Menschentest (D-4).
- Die Auswahl liegt genau an der 5-PT-Grenze.
- Die gepinnten Quellen in `lunados.space` und `lunados.lib` liegen außerhalb dieses Repos; `verification.json` weist aus, ob sie heute noch übereinstimmen.

## Wiederholen

```sh
python3 -I docs/10-Evidence/MILE-004/verify_mile004.py     # Abschlussprüfung
.agent-env/venv/bin/python -B docs/09-Research/learning-balance/probes/run_probes.py   # Proben (Agent-Umgebung)
python3 -I docs/09-Research/learning-balance/score_measures.py   # Bewertung und Rangfolge
```
