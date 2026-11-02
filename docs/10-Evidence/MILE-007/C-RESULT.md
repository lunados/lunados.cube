# MILE-007 — Abschlussnachweis

Stand: 2026-11-02 · Branches `feature/mile007-statement-sets` (lunados.cube), `feature/aggregate-relations` (lunados.lib) · Prüfung: [verification.json](verification.json), Skript [verify_mile007.py](verify_mile007.py) · Hashes: [MANIFEST.json](MANIFEST.json)

## Prüfung

| Kriterium | Ergebnis |
|---|---|
| Entscheidungen D-1–D-8 (`71ad6f9`) und Q-1–Q-10 (`594563c`) vor Code; Prüffälle A-01–A-10, Orakel S-01–S-16 und Pins 0.10.1 vor Code (`91e1c57` vor `310b522`); LIB-Orakel, Schema und Fälle vor dem Evaluator (`cee4e36` vor `a9b6dd6`) | erfüllt |
| Erwartungen, Orakel und Pins seitdem unverändert | erfüllt |
| lunados.lib `project.aggregate-relations/v1`: A-01–A-10 10/10 (Evaluator = Erwartung = Orakel), Differenzprüfung 150/150, `verify.py --cube` 139/139 | erfüllt |
| VP-10 0.11.0: S-01–S-16 16/16; 0.10.0 16/16 und 0.10.1 9/9 byte-gleich; J 14/14, O 10/10; Printer-Tests grün | erfüllt |
| Adapter: G6 mit `statements`/`projection`, gleich der CLI; MILE-005/006-Adapter und Discovery grün; G6-Parität 201/201 ([TASK-046-Lauf](task046-run.json)) | erfüllt |
| Sichtprüfung nach [Anleitung](SICHTPRUEFUNG.md): 5/5 ja | erfüllt |
| P0, P1, VP-07, VP-09, die übrigen P2-Pakete und G5 seit `main` unverändert; Quellen von 0.10.0/0.10.1 in `vpcells` unverändert; alle Prüfsummenlisten halten | erfüllt |
| Relative Links in docs/, openspec/ und VP-10 | keine kaputten |

## Chargen

| Mile | Abschlusskriterium | Nachweis |
|---|---|---|
| MILE-007-A | Entscheidungen aufgelöst; Fälle und Erwartungen vor Code | [Spezifikation](../../../P2/visual-printer-cells-v1/VP110_ACCEPTANCE_SPEC.md), [Prüffälle](../../09-Research/statement-sets/README.md) |
| MILE-007-B | Orakel und Fälle vor dem Evaluator; `verify.py` grün | [Lauf TASK-045](task045-run.json) |
| MILE-007-C | Vektoren wie erwartet; 0.10.x byte-gleich; Sichtprüfung beantwortet | [Lauf TASK-046](task046-run.json), [Renderings](task046/README.md), [Sichtprüfung](SICHTPRUEFUNG.md) |

## Ergebnis

- **PO-7:** Aussagenmengen (`aiaeao.cube.statement-set/1`) lassen sich ohne Migrationsplan als Matrix zeigen, mit eigenen Konzepten und Prädikaten, Y × Y oder Z × Z. DSM-01 läuft ohne Umbiegen.
- **G-03:** lunados.lib verdichtet Beziehungen eine Ebene hoch mit Pflichtstrategie, vollständiger Quellenspur und Verlustbericht (`aiaeao.projection-result/v1`). Der Cube liest das Ergebnis als Datensatz mit `library_ref` und rechnet nicht nach.
- C4-02 (`all`): API → DB `uses.derived` aus zwei Quellen, eine Beschreibung verworfen, eine interne Beziehung; mit `unless_same`/`unless_any` neben deklarierten Container-Beziehungen werden die Quellen als unterdrückt ausgewiesen.

## Grenzen

- Alles lokal (CLI, G4/G6); kein G5.
- Eine Ebene je Verdichtung; `project.dsm`, `project.mdm` und Domänenblöcke (DSM-02) fehlen.
- Structurizr-Strategien aus der Dokumentation abgeleitet, nicht mit Structurizr ausgeführt.
- Orakel, Evaluator und Printer vom selben Autor; die Übereinstimmung kontrolliert Implementierungsunterschiede.
- Alle Fälle synthetisch, ohne Kundendaten.

## Offen

G-07 (Kontrollfluss, eigener Milestone in der Größe von MILE-005), VR-12 (Instanzsicht), VR-01 (Herkunftslinie in `cube.flow`), Plansichten remote.
