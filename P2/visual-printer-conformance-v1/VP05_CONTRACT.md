# VP-05 – Combinatorial Display Conformance (P2-VP-CONFORMANCE/0.5.0)

**Status:** lokales Engineering-Experiment auf Basis von VP-04; keine Morphologie- oder P1-Freigabe. `cube.flow`, `cube.diagramm` und `cube.tree` sind ausschließlich Printer-View-IDs und keine Planner-View-Namen.

## Matrix

3 Views × 5 Lenses × 3 Granularities = 45 Konfigurationen. Je View zwei unveränderte deklarierte Quellmodelle = **90 konkrete Fälle**. Die Quellen sind exakt aus dem eingefrorenen VP-04-Verzeichnis übernommen. Es entstehen **54 gültige SVGs und 36 erwartete Ablehnungen**: Drei Quellen enthalten ausschließlich `cube.lens.semantics`-Deklarationen. Für die übrigen vier Lenses fehlt damit eine deklarierte Relevanz; der Printer darf sie nicht inferieren.

Vorab festgelegtes Prüforakel: `fixtures/INDEPENDENT_ORACLE.json` mit `source_items`, `shown_items`, `shown_edges`, `completeness` je Quelle × Level. Es ist unabhängig von SVG-Digests und Output-Statistik. Die Lens-Deklarationen werden ausdrücklich aus der Quell-Bundle auf Anwesenheit geprüft. Das Programm vergleicht die Erwartungen mit jeder tatsächlich gerenderten Ausgabe.

## Unabhängige Invarianten

1. Quell-Bundle SHA-256 und View-ID bleiben gebunden; ohne explizite Lens-Deklaration: **Ablehnung** statt neutraler Rückfallinterpretation.
2. Sichtbare und ausgelassene Source-IDs bilden eine exakte disjunkte Partition. Kanten werden ausschließlich als originale, unmodifizierte Kanten ausgegeben.
3. Tree-Projektionen sind wurzel-/vorfahren-geschlossen; Liniencharts verwenden zusammenhängende Probenfenster, Balkencharts erhalten eine Maximalprobe.
4. Jede sichtbare Lens-Hervorhebung ist rückwärts an die ursprüngliche Deklaration gebunden, auch wenn eine SVG-Kante intern umnummeriert wird. Unsichtbare Bindings bleiben im Ledger.
5. XML-SVG darf keine Skripte, Remote-Bilder, fremde Objekte, Events, Animationen oder Remote-Referenzen enthalten. SVG-Metadaten und VP-04-Druckbericht stimmen exakt überein.
6. Keine semantischen Typprüfungs-, epistemischen oder Authority-Claims werden von einer grafischen Prüfung abgeleitet.

## Split-Decision-Policy – bewusst nur Empfehlungen

Der Nutzer kann bei Komplexitätsüberschreitung ein höheres Level nutzen, fokussieren oder mehrere Druckaufträge stellen. **VP-05 erzeugt keine automatische Multi-SVG-Serie.** Die Aufteilungs-Machbarkeit ist ein begrenzter Heuristik-Probe-Lauf:

- Aus **der gleichen ursprünglichen Quell-Bundle** werden nacheinander mögliche `focus`-Anfragen gestellt (bei Graphen Nodes/Edges, bei Charts Samples).
- Für jeden Fokus wird ein zulässiger VP-04-Ausschnitt erzeugt. Ein deterministischer Greedy-Cover-Vorschlag sucht bis zu acht Panels, die möglichst alle Original-Items und Original-Edges abdecken. Kanten erhalten im Cover höheres Gewicht als einzelne Items.
- Rückgabe `FEASIBLE`, `NOT_FEASIBLE` oder `NOT_REQUIRED`, inklusive konkreter fokussierter Panel-Vorschläge, tatsächlicher Überlappungen und ungedeckter Original-IDs. **Weder Minimalität noch tatsächliche Printbarkeit einer vollständigen Multi-SVG-Story wird behauptet.** Diese Panels werden als **deskriptive Vorschläge**, nicht als zusätzlich ausgegebene SVG-Dateien geliefert.
- Ein Fokus, der die notwendigen Vorfahren einer Tree-Teilansicht nicht aufnehmen kann, wird verworfen. Es wird kein künstlicher Baum erzeugt.
- `SINGLE_COMPLETE`: Alle Original-Items/-Kanten sind in einer SVG sichtbar.
- `SINGLE_DISCLOSED`: Ein unvollständiger, bewusst begrenzter Ausschnitt, mit vollständigem Verlustledger, wird als Einzelausgabe akzeptiert.
- `SPLIT_RECOMMENDED`: Bei hoher Reduktionslast (≥60% der Items, sowie Standardverlusten mit Kanten-/Lens-Sichtbarkeitsverlust) und vollständig abdeckbarem Fokussierungsvorschlag.
- `REFOCUS_OR_RAISE_BUDGET`: Bei entsprechender Reduktionslast, aber nicht vollständig abdeckbarer Fokussierung. Für solche Fälle explizit keine Panel-Abdeckung behaupten.

Die Reduktionsentscheidung ist **keine neue Semantik**: Ein übersichtlich dargestelltes oder teilbares Modell ist weder wahr noch autorisiert. `'semantic_conformance'` wird ausschließlich im eingefrorenen VP-04-Druckbericht mit `NOT_EVALUATED` dargestellt.

## Explizite Grenzen / Scope-Cut

- `jsonschema` ist optional zum Prüfen der JSON-Schemata; der Python-Printer selbst benutzt ausschließlich Standardbibliothek.
- VP-04-Layoutlimits bleiben absichtlich klein. 90 Matrix-Fälle sind eine feste Regression-Basis und kein Beweis für unbegrenzte Graph-Komplexität.
- Cross-platform Unicode/font quality ist noch durch den Nutzer auf macOS/Safari, Claude und Grok abzunehmen.
- Keine automatische Pagination-Ausgabe, kein semantisches Clustering oder Routing, kein Application-Server, kein UI-State, kein 3D.
- VP-04-, VP-03-, VP-02- und VP-01-Implementierungen bleiben byteidentisch eingefroren.

**Audit-Level:** Der Einzelauftrags-CLI führt die unabhängigen strukturellen Invarianten aus, erhält aber ohne explizites unabhängiges Erwartungsprofil keine `INDEPENDENT_ORACLE_*`-Prüfmarkierungen. Diese zusätzlichen vier Vergleiche laufen nur im vollständigen 90-Fälle-Matrix-Gate. Ein CLI-`PASS` ist daher keine Behauptung, dass der Eingabeauftrag in der eingefrorenen Matrix vorkommt.
