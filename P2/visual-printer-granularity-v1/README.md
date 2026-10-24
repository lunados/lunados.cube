# AIAEAO Visual Printer · VP-04 Granularity & Complexity Budget

**Experimenteller lokaler Release Candidate** · `P2-VP-GRANULARITY/0.4.0` · Morphology **v9.4** · kein Webdienst · **kein 3D**.

VP-04 reduziert eine unveränderte VP-03-Lens-Quelle auf einen *expliziten Darstellungs-Ausschnitt* und erzeugt ein SVG **und** einen maschinenlesbaren Verlustbericht. VP-03 mit 113 vorhandenen Tests liegt nebenan als byteidentischer Snapshot in `../visual-printer-2d-lab/` und wird nicht modifiziert.

## Lokal starten (Mac / Linux)

Im entpackten ZIP:

```bash
cd P2/visual-printer-granularity-v1
python3 scripts/verify_vp04.py
open granularity_preview.html          # macOS; alternativ Finder
```

Einen Auftrag drucken:

```bash
python3 -m vpgranularity \
  --input fixtures/tree_resources__overview.json \
  --output /tmp/tree-overview.svg \
  --report /tmp/tree-overview.report.json
```

Der **Printer benötigt nur Python 3.10+ und Standardbibliothek**. Das unabhängige JSON-Schema-Orakel `jsonschema` ist für den vollständigen optionalen Schema-Gate nützlich; `CairoSVG`/`Pillow` nur zum Erzeugen von PNG-Vorschauen. Der CLI-Druck nutzt weder Browser, Netzwerk, JavaScript noch externe Schriftdateien.

## Projektion

`projection.granularity` ist exakt `overview`, `standard` oder `detail`. Die getrennten `cube.flow`, `cube.diagramm`, `cube.tree` und fünf `cube.lens.*` bleiben VP-02-/VP-03-Definitionen. Die Eingabe enthält die **vollständige unveränderte VP-03-Bundle** mit SHA-256-Bindung und ein VP-04-Projektionsprofil (`PROJECTION_REQUEST.schema.json`).

- **overview:** 2 `flow`-Knoten und 1 Kante; bis 2 Samples für Charts; bis 3 Tree-Knoten und 2 Hierarchiekanten.
- **standard:** bis 4 `flow`-Knoten und 4 Kanten; 4 Samples; bis 5 Tree-Knoten und 4 Kanten.
- **detail:** vollständige VP-02-Kapazität: 4 `flow`-Knoten / 8 Kanten, 6 Samples, 7 Tree-Knoten / 6 Kanten. **Keine Reduktion zulässig**; zu niedriges Budget führt zu Fehler.

Das Budget `max_items`/`max_edges` kann innerhalb dieser Grenzen weiter abgesenkt werden. `overflow=reject` führt zu einer deterministischen Ablehnung jeder Quelle oberhalb des Budgets. `overflow=summarize` selektiert einen deklarationsgetreuen Ausschnitt und protokolliert **alle** ausgelassenen Source-IDs und Relationen; es gibt **keine künstliche Sammel-Entität** und keine neue Semantic-Relation. Hier heißt „Aggregation“ ausschließlich **Bilanz der Auslassungen**, nicht Zusammenführen von Konzepten oder Messwerten.

**Fokus** ist `null` oder ein expliziter `{ "kind": "node|edge|sample|metric", "id": "..." }`-Verweis auf ein existierendes Element. Der Fokus erhält Priorität bei Auswahl. Ein Fokus auf einen Tree-Nachfahren erfordert sämtliche Ahnen; passt das nicht ins Budget, wird der Druck **abgewiesen**. Edge-Fokus in Graphen benötigt beide Endpunkte.

### Schutz vor irreführender Reduktion

- `cube.flow`: Nur Original-Knoten und Original-Kanten; Auswahl bevorzugt deklarierte Konnektivität. Ohne eine darstellbare Originalrelation **Fehler**, nicht erfundene Pfeile.
- `cube.tree`: Die Teilmenge bleibt verwurzelt und vorfahren-geschlossen. Keine Neu-Eltern, keine Mehrfach-Eltern, keine künstliche Baumkante.
- `cube.diagramm` Balken: Die höchste Originalprobe bleibt als Skalenanker erhalten. Line: **Nur zusammenhängende Original-Probenfenster**; keine Linie zwischen entfernten Samples. Wenn das Anzeigeintervall andere Achsenticks erhält, `chart_axis_rescaled=true` plus Warnhinweis im SVG. Damit sind Skalendifferenzen nachvollziehbar, kein Nachweis der Vergleichbarkeit.
- `cube.lens.*`: Bereits deklarierte Hervorhebungen für sichtbare Targets werden mitgenommen, ausgelassene Bindings separat protokolliert. Keine automatische Lens-Relevanz-Inferenz. Enthält der Ausschnitt kein ursprünglich hervorgehobenes Target, meldet die Ausgabe ausdrücklich `no_visible_declared_targets`.
- Sichtbare Graph-Kanten erhalten neben der lokalen SVG-Kanten-ID die **ursprüngliche Source-Kanten-ID**. Deren Deklarationsverweise bleiben erhalten.
- Jedes SVG besitzt eine visuelle Auslassungsbilanz und einen XML-Metadaten-Block mit Original-IDs, Kanten, Binding-Verlusten und SHA-256. Der JSON-Druckbericht trägt die vollständigen, strukturierten Daten.

**Nicht behauptet:** semantische Gültigkeit, Wahrheit, Messwertgenauigkeit, Berechtigungen, abgeschlossene Ausführung, Beobachtungs-/Zeit-Witnesses oder Admission. P1-Claims sind im Report `NOT_EVALUATED`. Weder Lens noch Focus noch Farbe stiften neue Tatsachen.

## Enthaltene Artefakte

- `vpgranularity/`: minimales API und CLI, keine Anwendung
- `fixtures/`: 20 statische JSON-Aufträge (alle drei Views × alle drei Granularities plus Fokusvarianten)
- `outputs/`: 20 SVG-Goldens + 20 vollständige JSON-Reports
- `granularity_preview.html`: statischer 3×3-Vergleich, ohne JavaScript
- `previews/`: neun gerasterte Golden-Previews + Kontaktbogen; zur Sichtprüfung, nicht als browserunabhängiger Glyphennachweis
- `PROJECTION_REQUEST.schema.json`, `PRINT_REPORT_VP04.schema.json`: JSON Schema Draft 2020-12
- `SOURCE_LOCK_VP04.json`, `VP04_SHA256SUMS.txt`, `VP04_RELEASE_MANIFEST.json`: Provenienz und Integrität
- `VP04_GRAMMAR.md`, `VP04_ACCEPTANCE.md`, `LOCAL_TEST_REPORT_VP04.json`: Vertrag, Abnahme und Grenzen

**P0, P1, GitHub und Cloudflare werden nicht verändert.** 3D bleibt bis zur abgeschlossenen 2D-Evaluation zurückgestellt.
