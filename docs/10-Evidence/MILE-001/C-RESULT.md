# Charge C — Vergleich und Übergabe

Datum: 2026-11-01 · TASK-005, TASK-007 und TASK-008 erfüllt.

[Vollständiger Bericht](c-report.json) · [Wiederholungsanleitung](../../09-Research/analysis-readiness/README.md) · [Milestone](../../02-Milestones/MILE-001-analysis-readiness.md)

## Beobachtung

Der Ausgangsfall `P1-mode-unbound` und die Variante `P1-mode-display` haben identischen Ausdruck und Kontext. Der einzige Eingabeunterschied ist das Hinzufügen von `/qualification_profiles`. Beide Eingaben und Hashes sind im Bericht getrennt erhalten. In **beiden frischen lokalen Verbindungen** gilt:

- Ausgangsstand: UNRESOLVED / P1_QUALIFIER_PROFILE_MISSING.
- Variante: PASS / keine Diagnose.
- Negativkontrolle Methodenkardinalität: erwartetes FAIL / P1_METHOD_SIGNATURE.

Alle vorab fixierten Erwartungen stimmen. Der aktuelle Code-/Quellenstand blieb während des Laufs unverändert. Die realen lokalen Discovery-Antworten enthalten die neue Metadatenversion; die Legacy-Hashes entsprechen weiterhin der Ausgangsbasis. Der G4-Pfad wurde seit der bestandenen Charge-A-Prüfung nicht verändert. Konfigurationsfehler und Nichterreichbarkeit sind auch im gemeinsamen Abschlusslauf getrennt protokolliert.

## Durchgeführte Prüfung

```sh
P3/adapters/mcp-local/.venv/bin/python -B -m unittest discover -s scripts/research/tests -v
P3/adapters/mcp-local/.venv/bin/python -B scripts/research/comparison_runner.py --output /private/tmp/mile001-c-run --compare P1-mode-unbound P1-mode-display
```

Ergebnis: 11 Runner-Tests OK; SDK-Lauf Exit 0, 3 Fälle × 2 frische Verbindungen, Vergleich und Fehlerkontrollen erfolgreich. Zusammen mit Charge A sind 91 unterschiedliche gezielte Tests bestanden (56 G4 + 19 G6 + 5 Discovery + 11 Runner); die acht Tests aus Charge B sind in den elf Runner-Tests enthalten und werden nicht doppelt gezählt.

## Abschlusskriterien und Grenzen

| Mile | Nachweis | Ergebnis |
|---|---|---|
| A: Fähigkeiten sichtbar | A-CAPABILITY-BASELINE, a-before/a-after, 80 Tests; aktuelle Discovery zusätzlich im c-report | erfüllt |
| B: Fälle wiederholbar | b-report und c-report: jeweils 3 Fälle × 2 frische stdio-Verbindungen; Fehlergrenzen und fünf getrennte Dimensionen | erfüllt |
| C: Vergleich/Übergabe | c-report comparison, getrennte Eingaben, einzige Profiländerung; Arbeitsanleitung und konsolidierte Specs | erfüllt |

Diese Prüfung belegt Analysebereitschaft für die begrenzten Fälle. Sie beweist keine vollständige Grammatikabdeckung, keine Ausführungsfähigkeit von Envelopes und keine verständliche Visualisierung. Ausdruck/Bindung als Gesamturteil, Visualisierung und Nutzen bleiben NOT_ASSESSED. Datei-/Modulpräsenz in Discovery bleibt von tatsächlichem Runtime-Laden getrennt.

Das Fallformat v1 nimmt exakte historische Proben auf; neue fachliche Fixtures für MILE-002 brauchen eine explizite neue Herkunftsdeklaration bzw. Vertragsrevision. Das ist ein dokumentierter Anschluss, kein behaupteter allgemeiner Fremdmodellimport. Ein bereits laufender Desktop-Chat übernimmt geänderten Servercode nicht automatisch; die Nachweise stammen aus ausdrücklich neu gestarteten lokalen Verbindungen. Öffentliche Lesereferenz und G5 wurden nicht als lokale Validierung verwendet.

## Übergabe

MILE-001-A/B/C und TASK-001–008 sind erfüllt. Die sieben Requirement-Gruppen sind mit diesen Nachweisen abgeglichen; die gelieferten Teilumfänge stehen unter `openspec/specs/`. Der Change ist als `2026-11-01-prepare-grammar-comparison` archiviert. OpenSpec-CLI nicht vorhanden: Konsolidierung und Archivierung wurden dateibasiert ausgeführt und geprüft, keine CLI-Ausführung behauptet. Nächster fachlicher Schritt: MILE-002, konkrete Vergleichsfälle und deren Quellenbindung.
