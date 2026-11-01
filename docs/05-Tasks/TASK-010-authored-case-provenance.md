# TASK-010 — Neu erstellte Fälle mit expliziter Herkunft zulassen

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/sample-five-grammars/tasks.md).

Story: [US-005](../04-US/US-005-source-bound-cases.md) · Mile: MILE-002-A · Aufwand: 2–3 h

## Ziel und Arbeit

Den begrenzten Herkunftsvertrag des Runners additiv versionieren: historische Exaktextraktion weiter unterstützen; neu erstellte synthetische Fixtures mit eigenen Hashes, Regel-/Quellenverweisen und vorab fixierten Erwartungen zulassen. Zuerst einen einfachen neuen Fall durch den bestehenden lokalen MCP-Pfad führen.

## Ergebnis und Akzeptanz

- Historische v1-Fälle und ihre Hashprüfungen bleiben unverändert; bereits geprüfte Fehlergrenzen bleiben erhalten.
- Neue Fälle erhalten explizite Herkunftsart, eigene Modell-/Argumenthashes, Quellenreferenz, Profilrevision und Erwartung; fehlende Herkunft wird vor Aufruf zurückgewiesen.
- Manuell analysierte, nicht ausführbare Fälle werden als solche dokumentiert und nicht durch einen erfundenen MCP-Aufruf ersetzt.
- Kein allgemeines Plugin-/Adapterframework; der Runner bleibt auf lokale deklarative Prüfungen begrenzt.

## Eingaben / betroffene Ablagen

[Fallmatrix](../09-Research/grammar-sampling/CASE-MATRIX.md), [Quellenplan](../09-Research/grammar-sampling/SOURCE-PLAN.md), [bestehender Fallvertrag](../09-Research/analysis-readiness/README.md). Neue Fallberichte unter `docs/09-Research/grammar-sampling/`; neue Rohprotokolle unter `docs/10-Evidence/MILE-002/`. TASK-010 betrifft zusätzlich den vorhandenen kleinen Runner und dessen Tests.

## Gezielte Verifikation

Bestehende Runner-Regressionen plus ein neuer positiver Fall, fehlende Herkunft und manipulierte Eingabe. Das neue Format/Schema und die unveränderte v1-Wiederholung dokumentieren.

## Abhängigkeiten und Grenze

[TASK-009](TASK-009-source-baselines.md)

Umfang gemäß [MILE-002](../02-Milestones/MILE-002-grammar-sampling.md). Keine neuen kanonischen Kategorien, Envelopes, produktiven Adapter oder Analysebibliotheken implementieren. Begrenzte Versuchsprofile bleiben Kandidaten. Noch kein Ausführungsnachweis vorhanden.
