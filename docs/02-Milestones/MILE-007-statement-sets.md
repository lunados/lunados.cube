# MILE-007 — Aussagenmengen ohne Plan darstellen und verdichten

Status: in_progress · Stand: 2026-11-02 · Voraussetzung: MILE-006 ([Abschluss](../10-Evidence/MILE-006/C-RESULT.md))

## Ergebnis

Der nächste schlanke Schritt aus der [Übergabe von MILE-005](../09-Research/completeness-instances/HANDOVER.md): PO-7 und G-03.

1. **Aussagen ohne Plan darstellen (PO-7):** Die Zellmatrix liest eine deklarierte Aussagenmenge direkt. Heute muss Material in einen P1.10-Migrationsplan umgebogen werden ([RENDER-RESULTS](../09-Research/visual-check/RENDER-RESULTS.md): Module als `Y:resource-object:resource`, `dependsOn` als `references`).
2. **Verdichten mit Quellenspur und Verlust (G-03):** Eine reine LIB-Funktion verdichtet Beziehungen auf eine höhere Ebene, etwa Komponenten zu Containern ([C4-02](../09-Research/grammar-sampling/reports/C4-02.md)). Das Ergebnis nennt für jede abgeleitete Beziehung alle Quellen und weist den Verlust aus.
3. **Abgeleitete Einträge sichtbar:** In der Matrix sind abgeleitete von deklarierten Einträgen unterscheidbar, mit Quellenzahl; der Verlust steht in Legende und Ledger.

## Rahmenbedingungen

- Keine neue Prüfsemantik in P1. P0, P1.1–P1.12, VP-07, VP-09 und VP-10 0.10.0/0.10.1 bleiben byte-gleich; die neue Eingabe kommt als eigenes Profil.
- Der Cube rechnet die Verdichtung nicht; er liest das typisierte LIB-Ergebnis (wie bei `analyze.population/v1`).
- Ablauf wie bisher: Spezifikation mit Entscheidungen, Prüffälle und Orakel vor Code, Tests, Nachweise.
- Keine Kundendaten in Repo, Fixtures, Fällen oder auf cube.lunados.net.

## Entscheidungen (2026-11-02, Nutzer)

D-1 bis D-8 hat der Nutzer wie vorgeschlagen freigegeben („ja“).

| ID | Frage | Entscheidung | Grund | Nicht gewählt |
|---|---|---|---|---|
| **D-1** | Rahmen | **Schlankes MILE-007** mit Milestone, Epic, Stories, Tasks und OpenSpec-Change | gleiche Nachverfolgung wie MILE-001–006 | nur Spezifikation je Paket |
| **D-2** | Form der Aussagenmenge | **JSON-Format `aiaeao.cube.statement-set/1`**: Bezug auf einen `binding-context/8`, Aussagen `{statement_id, subject, predicate_id, object}` wie in `analyze.population/v1`, optional `derived_from` und `origin` (`declared` / `derived`) | gleiche Aussageform wie in LIB; Referenten und Prädikate aus dem Kontext | ACG-Ausdrücke parsen; Plan-Wrapper erzeugen (biegt Vokabular und Titel um) |
| **D-3** | Prüfung der Aussagen | **nur Auflösung**: Referenten und Prädikate müssen im Kontext stehen, Fehler sind Printer-Diagnosen; Aussagen bleiben `declared_unverified` | P1 prüft weiter einzelne Ausdrücke; keine zweite Prüfsemantik | jede Aussage durch P1 schicken |
| **D-4** | Verdichtung | **LIB `project.aggregate-relations/v1`**, rein deklarativ. Eingaben: Aussagen, Zugehörigkeit Kind → Eltern, **Strategie als Pflichtparameter** (`all`, `unless_same`, `unless_any`; Structurizr-Varianten). Ergebnis `aiaeao.projection-result/v1`: abgeleitete Aussagen mit allen Quellen, unterdrückte und interne Quellen, Verlustzahlen | Verdichten gehört in die Bibliothek (C4-02); Strategie muss sichtbar gewählt sein | Verdichtung im Printer; `project.dsm`/`project.mdm` (später) |
| **D-5** | Darstellung | **`cube.cells` liest Aussagenmengen** als neues Profil `P2-VP-CELLS/0.11.0` im Paket `vpcells`: Achsen sind die Y-Referenten des Kontexts, Einträge die Aussagen des gewählten Prädikats; abgeleitete Einträge tragen „abgeleitet · n Quellen“; Abdeckung, Zellzustände und `axis_order` wie 0.10.x | Matrix ist die Sicht für DSM und Container-Abhängigkeiten; Zellzustände bleiben nutzbar | auch `cube.flow` und `cube.axes` (später, mit VR-01 Herkunftslinie) |
| **D-6** | Matrixkonvention (DSM-01) | **fest: Zeile = Subjekt, Spalte = Objekt**, in Legende und Bericht ausgewiesen; keine Transponierung | eindeutige Lesart; eine Option „transponiert“ würde dieselbe Zelle umdeuten | wählbare Konvention |
| **D-7** | Auslieferung | **lokal**: CLI und G6 (`cube_plan_source` mit Aussagenmenge, `cube_plan_views` `cube.cells`); G5 nicht | wie MILE-005/006; Plansichten laufen nur lokal | G5 |
| **D-8** | Prüffälle und Sichtprüfung | **C4-02** (2 Quellen → 1 Kante, 1 unterdrückt bzw. intern), **DSM-01** (Module mit `dependsOn` ohne Umbiegen) und die Strategievarianten, Erwartung vor Code; am Ende **eine kurze Sichtprüfung** wie MILE-006-C | belegt Verdichtung, Verlust und Darstellung an vorhandenem Material | Wiederholung aller MILE-002-Fälle |

## Drei Chargen

| Mile | Ergebnis | Abschlusskriterium | Aufgaben |
|---|---|---|---|
| **MILE-007-A — Vertrag und Prüffälle** | Spezifikation (Aussagenmenge, Projektionsergebnis, Darstellung) mit Detailfragen; Prüffälle mit Erwartung | Entscheidungen aufgelöst; Fälle und Erwartungen committet, bevor Code entsteht | TASK-043, TASK-044 |
| **MILE-007-B — Verdichtung in LIB** | `project.aggregate-relations/v1` mit Ergebnisschema, Orakel, Fällen und Evaluator | Orakel und Fälle vor dem Evaluator; `verify.py` grün; alle Fälle wie erwartet | TASK-045 |
| **MILE-007-C — Darstellung** | VP-10 0.11.0 liest Aussagenmengen und Projektionsergebnisse; G6; Sichtprüfung; Abschluss | Vektoren wie erwartet; 0.10.0/0.10.1 byte-gleich; Sichtprüfung beantwortet | TASK-046, TASK-047 |

B und C hängen von A ab. C nutzt für abgeleitete Einträge das Ergebnis aus B, die Darstellung deklarierter Aussagen geht schon vorher.

## Epics, Stories und Aufwand

[EPIC-007](../03-Epics/EPIC-007-statement-sets.md). US-024–025, TASK-043–047.

**Aufwand: 2,25–3,5 PT**, ohne die Zeit des Nutzers für die Sichtprüfung. Angehoben nach Q-3 (eigener Matrix-Zeichner, +0,25–0,5 PT in C).

| Charge | Aufwand |
|---|---|
| A | 0,5–0,75 PT |
| B | 0,75–1 PT |
| C | 1–1,75 PT |

## Nicht Teil von MILE-007

- `project.dsm` und `project.mdm` (Domänenblöcke, DSM-02), Prädikatmerkmale (G-09).
- Herkunftslinie in `cube.flow` (VR-01), Instanzsicht (VR-12), Kontrollfluss (G-07).
- Prüfung von Herkunft in P1 (typisierter Herkunftsparameter, C4-03).
- G5.

## Nachverfolgung

[OpenSpec-Change](../../openspec/changes/project-statement-sets/proposal.md) · [Aufgabenstatus](../../openspec/changes/project-statement-sets/tasks.md) · [Abdeckung](../../openspec/changes/project-statement-sets/TRACEABILITY.md). TASK-043: [Spezifikation VP-10 0.11.0](../../P2/visual-printer-cells-v1/VP110_ACCEPTANCE_SPEC.md), Entwurf `3279fe4`, Q-1–Q-10 nach Vorschlag (Y × Y und Z × Z, eigener Zeichner, Zugehörigkeit als Aussagen, Strategien ohne Spurverlust). TASK-044: [Prüffälle](../09-Research/statement-sets/README.md) A-01–A-10 und S-01–S-16 mit Erwartung vor Code, Pins 0.10.0 (16) und 0.10.1 (9); Präzisierungen SS-4, PR-4/5, DR-7/8. Charge A abgeschlossen. TASK-045: lunados.lib `project.aggregate-relations/v1` (Orakel und Fälle `cee4e36` vor Evaluator `a9b6dd6`), A-01–A-10 10/10, Differenzprüfung 150/150, `verify --cube` 139/139, [Lauf](../10-Evidence/MILE-007/task045-run.json); PR-6 (Projektionsdatensatz mit `library_ref`). Charge B abgeschlossen.
