# MILE-003-A — Render-Nachweise mit vorhandenen Printern (TASK-019)

Stand: 2026-11-01 · Spezifikationen und Erwartungen: [R-1](renders/R-1.json), [R-2](renders/R-2.json), committet vor dem Rendern (`657efe8`; R-2-Aufrufargument nachgetragen in `1b4f4b7`) · Lauf: [task019-render-log.json](../../10-Evidence/MILE-003/task019-render-log.json)

Gerendert mit der Implementierung hinter den MCP-Tools `cube_plan_source`, `cube_plan_views` und `cube_plan_check` (P3-MCP-LOCAL/0.3.0-rc1) in der Agent-Umgebung. Alle vier Läufe: `plan_check` PASS. Die SVGs liegen mit Bericht und Quelle unter [10-Evidence/MILE-003](../../10-Evidence/MILE-003/); Hashes im Laufprotokoll.

## Darstellungsabbildung

Beide Plansichten lesen nur P1.10-Migrationspläne. Um MILE-002-Material zu zeigen, musste es umgebogen werden:

- **DSM (R-1):** Module als `Y:resource-object:resource`, Abhängigkeit mit dem Katalogprädikat `references` — das einzige Y → Y-Prädikat im P1.10-Katalog. MILE-002 nutzte `Artifact` und `dependsOn`.
- **C4 (R-2):** API als `Runtime`, Order Controller als `Integration`, Database als `Provider` — der VP-07-Adapter bildet nur sechs Konzepte ab (AD-2). MILE-002 nutzte `Boundary`/`Tool`. Eigene Prädikate reicht der Adapter durch.

Das ist selbst ein Befund: Die vorhandenen Plansichten sind an das Migrationsvokabular gebunden; eine allgemeine Projektion beliebiger Cube-Aussagen fehlt (vgl. G-03).

## R-1 — DSM als `cube.axes` Y × Y

| Erwartung (vorab) | Beobachtung | Abgleich |
|---|---|---|
| 4 × 4-Matrix in Quellreihenfolge parser, resolver, validator, printer | 4 × 4, Reihenfolge **resolver, validator, printer, parser** — erstes Auftreten in den Abhängigkeiten, nicht Referentenliste | **abweichend** (Erwartung falsch gelesen; AX-3 „source order“ meint die Migrationsquelle) |
| Genau vier Zellen mit `<dependency> · references` | d-rp, d-vr, d-pv, d-fb an den erwarteten Positionen | erfüllt |
| Übrige Zellen leer und ununterscheidbar; „geprüft leer“ = „unbekannt“ | alle leeren Zellen identisch | erfüllt — **V-05-Lücke im Bild belegt** |
| Legende: Mitgliedschaftsregel und „blank ≠ no relation“ | „Membership: cell lists declared dependencies from the row … (subject) to the column … (object)“ und „blank cell = nothing declared for this pair, not "no relation"“ | erfüllt |
| Rückkopplung ohne Hervorhebung | keine Hervorhebung; wegen der Reihenfolge nach erstem Auftreten liegt d-fb unter der Diagonale — die DSM-Lesart „Rückkopplung über der Diagonale“ trägt hier gar nicht | erfüllt, mit Zusatzbefund |
| R-1b: Spalte printer ausgeblendet, Bericht `hidden_cols = [m:printer]` | Bericht wie erwartet; **SVG-Legende zeigt „0 empty row(s) and 1 empty column(s) hidden; the report counts them.“** | erfüllt; offene Frage beantwortet: Anzahl sichtbar, Identität nur im Bericht |

## R-2 — C4 als `cube.flow` aus einem P1.10-Plan

| Erwartung (vorab) | Beobachtung | Abgleich |
|---|---|---|
| Drei Knoten, zwei Kanten | drei Knoten (I/R/P-Glyphen mit Anker-ID), Kanten e1, e2; **zwei Panels** (je Schritt p0, p1), nicht eines | erfüllt; Panelzahl abweichend (Partition erzeugt Panels je Schritt) |
| R-2a: gleiche Linienart, Pfeilspitze `reference` | beide durchgezogen, gleiche Pfeilspitze; Linsenakzent der Provenienz-Linse auf beiden Kanten | erfüllt |
| R-2a: Unterscheidung höchstens über Prädikattext | Kanten nur „e1“/„e2“ beschriftet; Prädikat steht im **Deklarationsledger** unter der Grafik („e2 · c4:api → c4:db · uses-implied“) | erfüllt — Unterscheidung nur durch Nachschlagen |
| R-2b: abgeleitete Kante gestrichelt, deklarierte durchgezogen | e2 gestrichelt, e1 durchgezogen | erfüllt |
| R-2b: Legende mit beiden Einträgen | „solid · deklariert (Komponente)“, „dashed · abgeleitet (implied, UnlessAny)“, Überschrift „line style is not a verdict, cause or time order“ | erfüllt |
| R-2b: Pfeilspitzen und Farbe unverändert; ES-5-Hashes | unverändert; `base_svg_sha256` je Panel im Bericht und in den SVG-Metadaten | erfüllt |

Zusatzbeobachtung: In beiden Varianten kreuzt die waagerechte Führung von e1 die senkrechte von e2; Lesbarkeit nicht geprüft.

## Folgerungen

| Anforderung | Stand nach TASK-019 |
|---|---|
| V-01 | **Printer-Paar vorhanden** (R-2a/R-2b): Mit eigenem Ableitungsprädikat und `edge_styles` farbfrei unterscheidbar, mit Legende. „Herkunft unbekannt“ weiter ohne Merkmal → TASK-021. |
| V-05 | Markiert vs. leer und „ausgeblendet (Anzahl)“ sichtbar; **„geprüft leer“ und „unbekannt“ im Bild identisch** → TASK-021-Mockup. |
| V-06 | Konvention über die Mitgliedschaftsregel benannt; **Reihenfolge folgt dem ersten Auftreten**, daher ist „über/unter der Diagonale“ ohne deklarierte Ordnung nicht deutbar. |

Keine Printer-, Anker- oder Morphologieänderung. Kein Lesbarkeitsnachweis.
