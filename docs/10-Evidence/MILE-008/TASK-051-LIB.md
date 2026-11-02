# TASK-051 — Trace-conformance LIB verification

Stand: 2026-11-02. TASK-051 erfüllt; TASK-052 und MILE-008-C bleiben offen.

## Artefakt und Reihenfolge

Repository `lunados.lib`, Branch `codex/task-051-trace-conformance`, neuer Eintrag `entries/analyze.trace-conformance/v1/`, Status `candidate-authored`.

1. `ebb3110`: Vertrag, typisiertes Ergebnisschema, unabhängiges Programmorakel und 18 Fälle **vor** dem Evaluator.
2. `d823a4a`: eigenständiger Evaluator, Eintrag, Cube-Methodenreferenz, INDEX, Build-Skript und Differenzprüfung.
3. `5511574`: Review-Korrektur: bedingungsloser einzelner Merge-Ausgang bleibt ohne künstliches `order`; Eingabeprüfung entspricht der P1.13-Sonderregel. Minimale Sortierkorrektur in Evaluator/Orakel für einarmige unbedingte Gateways; Erwartungen unverändert, erneut vollständig geprüft.

Vorab-Erwartungen: TASK-048 CF-11…CF-19 und CF-21…CF-29. CF-20 existiert nicht. Originalerwartungen bleiben in jedem Fall als `preregistered_expected` erhalten. Die dokumentierte Normalisierung (`id`→`gateway`, `to`→`target`, `predicate`→`predicate_id`, opaker `condition_ref`, Deklarations-IDs) folgt der aufgelösten P1.13-Spezifikation. Der bedingungslose einflüssige Merge bleibt wie im Quellmodell ohne `order`; Q-2 betrifft Referenten, keine Reihenfolge. Quellhashes stehen in `cases/SOURCES.json`.

## Ausgeführte Prüfungen

- Vor Evaluator: Programmorakel gleich handfestgelegtem Vollergebnis für 18/18 Fälle; bestehendes `python3 scripts/verify.py --cube <lunados.cube>`: 12 Einträge, 139/139.
- Nach Implementierung: derselbe Gesamtprüfbefehl: **13 Einträge, 159/159**. Alle 18 neuen Evaluatorausgaben entsprechen Erwartung und Orakel exakt und validieren gegen `schema/trace-conformance-result.v1.schema.json`; Cube-Referenzfall PASS ohne Diagnosen und ohne Warrant-/Authority-/Admission-Promotion.
- `python3 scripts/differential_trace.py`: **471** vollständige Ergebnis-/Schemaabgleiche, **18** unveränderte Projektionen auf die Vorab-Erwartungen, **9** Ablehnungen ungültiger Aufrufe. Umfasst mehrfachen Tokenbedarf, Join/ Split/ Merge-Kapazitäten 0…3, doppelte/umgeordnete Beobachtungen, Bedingungsreihenfolge mit unbekannten Werten, FAIL vor UNRESOLVED, fremde Instanz und globale/andere/paarweise Abdeckung.
- Neues `entry.json` gegen `schema/entry.v1.schema.json`: gültig. `git diff --check`: ohne Befund. Bestehende LIB-Einträge unverändert; Cube-P0/P1/P2 in TASK-051 nicht geändert.

## Grenzen

Rein deklarative Referenzfunktion, keine Engine, keine Bedingungsauswertung und kein Instanzabschluss. Der Aufrufer liefert das vollständige Aktivierungstoken-Inventar. Mehrere Aktivierungen werden deterministisch nach Token-ID zu Kapazitäten zugeordnet; historische Kausalität/Zeitfolge wird nicht behauptet. Bei wartendem Join bleibt das erste Token je Eingang ausstehend; nur darüber hinausgehende Token gelten als Überschuss. Diese Präzisierungen stehen im neuen `CONTRACT.md`.

Orakel und Evaluator haben getrennten Code (Mengen-/Kapazitätsvergleich versus konsumierende Warteschlangen), aber denselben Autor und dieselbe Fixture-Welt: Implementierungsdifferenzkontrolle, keine unabhängige externe Replikation. Kein Push, keine Veröffentlichung; Adapter/MCP-Wiederholung gehört zu TASK-052.
