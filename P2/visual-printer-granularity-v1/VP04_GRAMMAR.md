# VP-04 · Granularity / Complexity Budget Contract

## Versions und Namespace

- `P2-VP-GRANULARITY/0.4.0`, `aiaeao.cube.vp04-projection-request/1`
- `cube.flow`, `cube.diagramm`, `cube.tree` sind P2-View-IDs, keine Planner-View-IDs.
- `cube.lens.semantics`, `.provenance`, `.execution`, `.governance`, `.epistemology` sind **deklarierte Display-Lenses**.
- Morphology v9.4 / P1 bleiben reine Eingabeprovenienz; VP-04 führt keinen P1-Typvalidator aus.

## Projektionstransformation

```text
Full VP03 bundle (source SHA locked)
         +
View + Lens + Level + Focus + Strict Budget + Overflow Policy
         ↓
Selected unchanged original items and unchanged original edges/samples
         +
Derived ViewPrinter/LensPrinter 2D geometry
         +
Visible omission disclosure / complete loss ledger
         ↓
SVG (Unicode + forms + colors) + JSON print report
```

### Complexity limits (hard upper bounds per level; chosen request budget may be smaller)

| level | cube.flow items/edges | cube.diagramm samples/edges | cube.tree items/edges |
|---|---:|---:|---:|
| overview | 2 / 1 | 2 / 0 | 3 / 2 |
| standard | 4 / 4 | 4 / 0 | 5 / 4 |
| detail | 4 / 8 | 6 / 0 | 7 / 6 |

Flow/tree need at least 2 items and 1 declared edge. Chart needs at least 2 source samples and a typed metric declaration. VP02 underlying layout capacities are unchanged. `detail` fails if the source cannot fit *entirely*; it never truncates. `summarize` authorizes only presentation omissions, not new semantic group nodes. `reject` refuses every overflow. No silent truncation.

### Selection

1. Validate full source bundle via frozen VP03, including selected lens declarations.
2. Verify exact source bundle SHA-256 over canonical JSON.
3. Verify view namespace, level, typed focus and numeric budget (booleans rejected).
4. Preserve required focus; tree retains entire ancestry; edge focus retains endpoints and original edge.
5. Optimize deterministic, explicitly authored lens emphasis and existing edges within the budget; preserve source-defined order as a stable tie-breaker.
6. Keep flow only with at least one source edge; a tree must remain a valid rooted subtree.
7. For charts, preserve an original maximum sample in bar views. For line views, take a contiguous original source window; never join non-neighbor original points. Signal any resulting y-axis change.
8. Render using unchanged VP02/VP03 geometries; append a footer disclosure; embed full omission ledger in SVG metadata and report.

Kantenbezüge in VP03 werden bei der Teilprojektion intern neu indiziert. Der Ledger `shown_edges` verbindet ihre Original-ID mit der Darstellungskante; `omitted_edges` enthält Original-ID, beiden Endpunkte, predicate_id, declaration_ref und Ursache.

### Important distinctions

- `complete_input_view` heißt nur, dass der VP04-Printer alle Eingabe-Items dieser **deklarativen Fixture** zeigt; **kein** epistemisches Vollständigkeitsprädikat.
- `PARTIAL_EXPLICIT` ist eine Einschränkung der Ausgabe, keine negative Validierung der Quelle.
- Gruppierungen des Ledgers sind Mengenangaben ohne neue Objektidentität.
- Der Printer behauptet nichts über Wahrheit, zeitliche Reihenfolge, Provenance-Authentizität, Kausalität, Ausführungsrecht oder aktuelle Authority.
- Ein `cube.diagramm` enthält nur Zahlen aus einer erklärten Quelle, die in diesen Beispiel-Fixtures nicht empirisch verifiziert ist.

## Scope-Cut

P2-VP-04 ist **kein** Full-Graph-Auto-Layout, kein General-Aggregator, kein semantischer Clusterer, kein interaktiver Editor, keine Speicherung von Benutzerzustand, keine Server-API, kein responsives Dashboard und keine 3D-Implementierung. Die Beschränkung auf VP02-Layoutgrößen ist beabsichtigt. VP05 kann kombinatorische Abnahmekriterien und größer dimensionierte Beispielquellen festlegen.
