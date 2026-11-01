# MILE-002 — Abschlussnachweis (TASK-017)

Stand: 2026-11-01 · Branch `feature/mile002-grammar-sampling` · Prüfung: [verification.json](verification.json) · Hashes: [MANIFEST.json](MANIFEST.json)

## Prüfung

| Kriterium | Ergebnis |
|---|---|
| 15 Matrixfälle mit Fallbericht und mindestens einem Nachweis (v2-Fall oder LIB-Aufruf) | erfüllt |
| Je Ansatz zwei Normalfälle und ein Gegenfall, Berichtskopf passend zur Matrix | erfüllt |
| Alle 35 v2-Fälle mit dem aktuellen Runner ladbar (Herkunft, Registerhash, Regelverweise, Modellhashes) | erfüllt, 0 Fehler |
| Erwartung vor dem Lauf committet und seitdem unverändert (Commit des Falls ist Vorfahre des Lauf-HEAD) | erfüllt für alle Fälle und LIB-Aufrufe |
| Letzter Gesamtlauf deckt alle v2-Fälle ab, alle Erwartungen in 2/2 Verbindungen getroffen, Readiness bestanden | erfüllt ([task014-bpmn-report.json](task014-bpmn-report.json), HEAD `66efa7b`, 35 Fälle) |
| LIB-Aufrufe | 4/4 erwartungsgemäß, Evaluator-Hash unverändert |
| Regelverweise im Quellenregister definiert | erfüllt |
| Relative Links in docs/ und openspec/ | keine kaputten |

## Chargen

| Mile | Abschlusskriterium | Nachweis |
|---|---|---|
| MILE-002-A | Quellen-/Regelregister; Herkunftserweiterung v2, v1 unverändert gültig | [SOURCE-REGISTER](../../09-Research/grammar-sampling/SOURCE-REGISTER.md), [SOURCE-LOCK](SOURCE-LOCK.json), [TASK-010-RESULT](TASK-010-RESULT.md) |
| MILE-002-B | Konkrete Modelle, Erwartungen, Cube-Ausdruck/Bindung, Beobachtungen oder belegte Prüfgrenzen für alle 15 Fälle | 15 [Fallberichte](../../09-Research/grammar-sampling/README.md); Läufe task011–task015 |
| MILE-002-C | Verknüpftes Lückenregister, vorläufige Nutzen-/Aufwandseinschätzung, Übergabe an MILE-003/004 | [GAP-LEDGER](../../09-Research/grammar-sampling/GAP-LEDGER.md) |

## Grenzen

- Stichprobe von 15 Fällen; kein Vollständigkeits- oder Interoperabilitätsnachweis.
- ArchiMate ohne normative Endpunkt-Zulässigkeit (Entscheidung 2026-11-01); BPMN-Regeln aus der bereitgestellten Spezifikation gelesen; Structurizr nicht ausgeführt; NetworkX nicht ausgeführt.
- Alle Konzeptabbildungen sind Versuchsabbildungen; P1-PASS belegt nur deklarative Typisierung im jeweiligen Kontext.
- Der lokale MCP-Server lief aus einem Arbeitsbaum mit nicht committeten P3-Änderungen; deren Dateihashes stehen in jedem Laufbericht.
- Nutzen ist erwartet, nicht gemessen.

## Wiederholen

```sh
scripts/dev/agent_env.sh   # nur in der Agent-VM; auf dem Mac die Adapter-venv
.agent-env/venv/bin/python -B -m unittest discover -s scripts/research/tests
.agent-env/venv/bin/python -B scripts/research/comparison_runner.py --cases docs/09-Research/grammar-sampling/cases --output /tmp/mile002-replay-1
```

LIB-Aufrufe: je Datei unter [lib-calls/](../../09-Research/grammar-sampling/lib-calls/) das Feld `call` an `python -I evaluator/evaluate.py` in `lunados.lib/entries/impact.propagate/v1` übergeben und mit `expected` vergleichen (Index → ID über `lib_mapping.numberings` im Modell).
