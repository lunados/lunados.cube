# TASK-017 — Nachweise prüfen und MILE-002 übergeben

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/sample-five-grammars/tasks.md).

Story: [US-011](../04-US/US-011-grammar-gap-ledger.md) · Mile: MILE-002-C · Aufwand: 1 h

## Ziel und Arbeit

Vollständigkeit und Nachvollziehbarkeit der 15 Fälle, Quellenbindungen, Rohprotokolle und offenen Grenzen prüfen. Nur tatsächlich erfüllte Kriterien schließen und den Research-Change bei vollständigem Abschluss konsolidieren/archivieren.

## Ergebnis und Akzeptanz

- Alle fünf Ansätze sind mit je zwei Normalfällen und einem Gegenfall vertreten; der Ausgangsstand und Versuchsprofile bleiben getrennt.
- Ein nicht prüfbares konkretes Verhalten kann als begründete Lücke dokumentiert sein. Fehlende Fallausarbeitung oder fehlende notwendige Quellen gelten hingegen nicht als erledigt.
- MILE-003 erhält konkrete Darstellungsanforderungen; MILE-004 erhält eine vorläufige Maßnahmenliste. Keine visuellen Nutzertests vorwegnehmen.
- Status, Links, Quellen-/Artefakthashes und OpenSpec-Konsolidierung stimmen mit den tatsächlich gelieferten Ergebnissen überein.

## Eingaben / betroffene Ablagen

[Fallmatrix](../09-Research/grammar-sampling/CASE-MATRIX.md), [Quellenplan](../09-Research/grammar-sampling/SOURCE-PLAN.md), [bestehender Fallvertrag](../09-Research/analysis-readiness/README.md). Neue Fallberichte unter `docs/09-Research/grammar-sampling/`; neue Rohprotokolle unter `docs/10-Evidence/MILE-002/`. TASK-010 betrifft zusätzlich den vorhandenen kleinen Runner und dessen Tests.

## Gezielte Verifikation

Abdeckungsmatrix für 15 Fälle und sieben Leitfragen prüfen. Passende Regressionen nur bei Codeänderungen; reine Analyse nicht mit einem allgemeinen Software-Test-PASS versehen.

## Abhängigkeiten und Grenze

[TASK-016](TASK-016-gap-ledger.md)

Umfang gemäß [MILE-002](../02-Milestones/MILE-002-grammar-sampling.md). Keine neuen kanonischen Kategorien, Envelopes, produktiven Adapter oder Analysebibliotheken implementieren. Begrenzte Versuchsprofile bleiben Kandidaten. Noch kein Ausführungsnachweis vorhanden.
