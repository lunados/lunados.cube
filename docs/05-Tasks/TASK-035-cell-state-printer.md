# TASK-035 — Printer-Stand für vier Zellzustände

Planungsstand: ausgearbeitet. Ausführungsstatus ausschließlich in [tasks.md](../../openspec/changes/declare-completeness-and-instances/tasks.md).

Story: [US-020](../04-US/US-020-cell-states.md) · Mile: MILE-005-C · Aufwand: 1–1,5 PT

## Ziel und Arbeit

Eigener Printer-Stand (neue Revision neben VP-09, VP-09 byte-gleich): Abnahmespezifikation, Zellzustände aus der Vollständigkeitserklärung, Schraffur für unbekannt (Kandidat M-05C), benannte Ausblendung (PO-6), Vektoren und Tests.

## Ergebnis und Akzeptanz

- „geprüft leer“ nur für den erklärten Umfang; farbfrei unterscheidbar.
- Abnahme nach eigener Spezifikation; Vergleich mit Mockup M-05C dokumentiert.

## Eingaben

[Lernbilanz](../09-Research/learning-balance/LERNBILANZ.md), [Lückenbilanz](../09-Research/grammar-sampling/GAP-LEDGER.md) (G-01, G-08), [Darstellungsübergabe](../09-Research/visual-check/HANDOVER.md) (VR-05), [Probeergebnisse](../09-Research/learning-balance/PROBE-RESULTS.md).

## Abhängigkeiten und Grenze

[TASK-033](TASK-033-profile-impl.md)

Umfang gemäß [MILE-005](../02-Milestones/MILE-005-completeness-instances.md). P0, P1.1–P1.9 und P2 bleiben byte-gleich; neue Fähigkeiten als eigenes Profil bzw. eigener Printer-Stand.

## Ergebnis (2026-11-02)

Umgesetzt als eigener Printer-Stand **VP-10** (`P2-VP-CELLS/0.10.0`) in [`P2/visual-printer-cells-v1/`](../../P2/visual-printer-cells-v1/README.md).

- **Ablauf:** Spezifikation mit Entscheidungen D-1–D-9 (`af74525`), Entscheidungen nach Vorschlag (`1ab7fc2`), Orakel vor Code (`2316f45`), Implementierung (`639e6c0`).
- **Ergebnis:** J-01–J-14 14/14 gegen das Orakel, 24 Tests grün. „Geprüft leer“ steht nur im erklärten Umfang (Paar, Zeile oder Spalte). Unbekannt ist mit Linien schraffiert, ausgeblendete Werte werden mit Namen genannt. Die vier Zustände unterscheiden sich ohne Farbe; das ist als Audit-Invariante geprüft und im Test zusätzlich mit umgefärbtem SVG.
- **VP-09 byte-gleich:** `VP07_SHA256SUMS`, `VP09_SHA256SUMS` und die gepinnten 0.9.0- und 0.9.1-Ausgaben sind unverändert. `vpcells` importiert `vpaxes`, ohne es zu ändern.
- **Vergleich mit M-05C:** Alle zwölf sichtbaren Zellen, die ausgeblendete Spalte und ihre Benennung stimmen überein. Die Abweichungen (Prädikat, Reihenfolge, Schraffurrichtung, Legende statt Streifen) sind begründet in [M05C_COMPARISON.md](../../P2/visual-printer-cells-v1/M05C_COMPARISON.md).
- **Vektorkorrektur vor dem Code-Commit:** Bei J-12 kamen eine dritte Phase und der Ausschnitt `p1:p2` hinzu, weil `cube.phases` einen Ausschnitt mit nur einer Phase ablehnt. Die Erwartungen sind unverändert.
- **Nebenbefund P1.12:** Prädikate aus `predicate_profile_refs` wurden nicht aufgelöst. Behoben in `5f32bce`, mit neuem Test; K-01–K-21 bleiben 21/21.
- **Nachweis:** [task035-run.json](../10-Evidence/MILE-005/task035-run.json), Renderings und Berichte unter [task035/](../10-Evidence/MILE-005/task035/).

Offen bleiben die menschliche Lesbarkeit, die deklarierte Achsenreihenfolge (PO-5) und weitere Paare.
