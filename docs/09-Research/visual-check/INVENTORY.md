# MILE-003-A — Darstellungsinventur V-01–V-12

Status: TASK-018 abgeschlossen (Nachweisart Doku/Code) · Stand: 2026-11-01 · Render-Nachweise folgen in TASK-019

Die Inventur beantwortet für jede Darstellungsanforderung aus der [Lückenbilanz §6](../grammar-sampling/GAP-LEDGER.md): Welche vorhandene Sicht kann die Unterscheidung tragen, über welches Merkmal, und wo ist eine Lücke? Grundlage sind ausschließlich Spezifikationen, READMEs und Code der Printer sowie `symbols.json`. **Nichts davon ist gerendert**; ein Urteil „trägt“ heißt hier „laut Vertrag darstellbar“, nicht „im SVG beobachtet“.

## Vorhandene Mechanismen

| Mechanismus | Wo | Was er leistet | Grenze |
|---|---|---|---|
| **M-1 Kantenstil je Prädikat** | VP-07 Pfad F, ES-1–ES-6 ([Spezifikation](../../../P2/visual-printer-migration-v1/VP07_ACCEPTANCE_SPEC.md)) | `solid`/`dashed`/`dotted`/`double` je `predicate_id`, Pflichtlegende (≤ 40 Zeichen); gilt für `cube.flow`, `cube.tree`, `cube.phases` | Pfeilspitze bleibt immer `relation-arrows.reference` (ES-2); Stil hängt am Prädikat, nicht an einer Kanteneigenschaft |
| **M-2 Linsenakzent** | VP-03 ([Linsengrammatik](../../../P2/visual-printer-2d-lab/VP03_LENS_GRAMMAR.md)) | Hervorhebung ausdrücklich deklarierter Knoten (gestrichelter Umriss) und Kanten (Akzentstrich) je Linse | Nur deklarierte Bindungen, keine Inferenz; Kantenakzent ist Farbe/Strichstärke |
| **M-3 Schraffur ohne Farbe** | VP-07 PV-5 | Schraffur A `/` und B `\` mit Legende für deklarierte Konflikte; ausdrücklich keine Statusfarbe | Nur Zellen in `cube.phases`, nur für die zwei Migrationskonflikte |
| **M-4 Auslassungsledger** | VP-04 ([Grammatik](../../../P2/visual-printer-granularity-v1/VP04_GRAMMAR.md)), VP-07 PV-1a | Fußzeilen-Hinweis im SVG, vollständiger Ledger ausgelassener Kanten/Knoten in Metadaten und Bericht | Darstellungsauslassung, keine Aggregation; erzeugt keine neuen Gruppenknoten |
| **M-5 Matrix mit Mitgliedschaftslegende** | VP-09 ([Spezifikation](../../../P2/visual-printer-axes-v1/VP09_ACCEPTANCE_SPEC.md)) AD-4, VP-09.2 | Kategoriale Matrix, Zelle listet deklarierte Aussagen; Legende nennt die Mitgliedschaftsregel und „blank = nothing declared, not 'no relation'“; Y × Y gerichtet (Zeile = Subjekt) | Nur Achsenpaare der geschlossenen Liste; Eingabe über P1.10-Migrationspläne; `--hide-empty` laut Spezifikation nur im Bericht protokolliert |
| **M-6 Sequenz mit Fragmenten** | VP-08 ([Spezifikation](../../../P2/visual-printer-sequence-v1/VP08_ACCEPTANCE_SPEC.md)) | Lebenslinien, nummerierte Nachrichten (call/return/async/self), `alt`/`opt`/`loop` mit Guard-Text, ein Panel je Trigger | Kein `par`; Guards werden nicht ausgewertet; keine Instanz-/Spurbegriffe |
| **M-7 Baumsicht** | VP-02 `cube.tree` ([View-Grammatik](../../../P2/visual-printer-2d-lab/VIEW_GRAMMAR.md)) | Eine Wurzel, genau n−1 Eltern→Kind-Kanten; Zyklen und Mehrfacheltern werden abgelehnt | Höchstens 7 Knoten; Hierarchie als Baum, nicht als verschachtelte Grenze |
| **M-8 VG-Anker** | `symbols.json` v9.4 (129 Anker) | u. a. `relation-arrows.derivation` ↦, `relation-arrows.projection` ⇉, Grenzanker ⬠ ⬕ ⬖, Aktionszustände wie `source-unavailable` ⦴ | Anker in `cube.flow`-Kanten auf `relation-arrows.reference` beschränkt (VP-02) |

## Inventur

Urteil: **trägt** · **teilweise** · **Lücke**. Vorrangige Unterscheidungen fett.

| ID | Unterscheidung | Kandidatensicht · Merkmal | Urteil | Begründung | Weiter in |
|---|---|---|---|---|---|
| **V-01** | abgeleitete vs. deklarierte Kante; unbekannte Herkunft | `cube.flow` mit M-1 (`uses.derived` → `dashed`, Legende „abgeleitet“) | **teilweise** | Trägt, wenn die Ableitung ein eigenes Prädikat hat (Konvention aus C4-02). Eine unmarkierte Ableitung erscheint wie deklariert; „unbekannte Herkunft“ hat kein eigenes Merkmal. Derivation-Anker ↦ ist für Kanten nicht zugelassen (ES-2, VP-02). | TASK-020 (Printer-Paar), TASK-021 (Variante „unbekannt“) |
| V-02 | „n Quellen → 1 Kante, k verworfen“ | M-4 Auslassungsledger | teilweise | Der Offenlegungsmechanismus ist da, beschreibt aber Darstellungsauslassung, keine Verdichtung; kein Zähler je verdichteter Kante. | — (Inventar) |
| V-03 | Zugehörigkeit als verschachtelte Grenze | M-7 `cube.tree`; Grenzanker ⬠ | teilweise | Hierarchie darstellbar, aber als Baum mit Kanten, nicht als Enthaltensein; keine verschachtelte Grenzform. | — |
| V-04 | Fremdtyp neben Cube-Konzept; Namensfallen-Hinweis | Knotenbeschriftung (deklarierter Text), `data-semantic-ref`, VP-07-Labelmap | teilweise | Fremdtyp nur als frei deklarierter Labeltext; kein Feld, keine Hinweisregel bei Namensgleichheit. | — |
| **V-05** | markiert / geprüft leer / unbekannt / ausgeblendet | M-5 `cube.axes` Y × Y | **teilweise** | Markiert (Einträge) und unbekannt (leer, Legende „nothing declared, not 'no relation'“) sind korrekt getrennt. **Geprüft leer** ist nicht darstellbar (keine Vollständigkeitserklärung, G-01). **Ausgeblendet** laut Spezifikation nur im Bericht; Sichtbarkeit im SVG ungeprüft. | TASK-019 (Render Y × Y, `--hide-empty`), TASK-021 (Mockup „geprüft leer“) |
| V-06 | Matrixkonvention in der Legende; Rückkopplungsmarken | M-5 Y × Y (gerichtet, Mitgliedschaftsregel in der Legende) | teilweise | Konvention wird über die Mitgliedschaftsregel benannt (Zeile = Subjekt). Keine Hervorhebung von Rückkopplungen; Reihenfolge nach P0-Lesereihenfolge, nicht nach Abhängigkeit. | TASK-019 |
| V-07 | MDM-Blöcke mit Domänen- und Relationstyp-Beschriftung | M-5, je ein Achsenpaar pro Sicht | Lücke | Kein Blocklayout; ein Achsenpaar pro Sicht, keine Domänendeklaration. | — |
| V-08 | Generationen als Spalten, „nicht zwingend parallel“ | `cube.phases` (deklarierte Schritte als Spalten) | teilweise | Spalten tragen deklarierte Schritte „nicht als Zeitskala“; Generationen müssten als Schritte deklariert werden; der Parallelitätshinweis fehlt. | — |
| **V-09** | Zeugenzyklus; „nicht abarbeitbar“ vs. „falsch nummeriert“ | `cube.flow` mit M-2 (deklarierte Kanten der Zyklusfolge hervorheben) | **teilweise** | Eine deklarierte Hervorhebung der Zyklenkanten ist möglich, aber per Linsenakzent (Farbe/Strichstärke) und nicht berechnet. `cube.tree` lehnt Zyklen ab (keine Darstellung). Die Unterscheidung „falsch nummeriert“ hat keinen Ort. | TASK-020 (Printer-Paar mit Linsenakzent), TASK-021 (Variante ohne Farbe) |
| V-10 | genommener vs. nicht genommener XOR-Pfad je Instanz; zwei Pfade als Fehler | M-6 `alt` mit Guards | teilweise | Alternativen auf Modellebene darstellbar; welcher Pfad in einer Instanz genommen wurde, und ein Widerspruch, nicht. | — |
| V-11 | Join mit Eingangsliste und Status je Eingang | M-6 | Lücke | Kein `par` in VP-08 (D-5); keine Synchronisationsdarstellung. | — |
| **V-12** | Instanz als Gruppierung; instanzübergreifende Kante als Fehler | M-6 (ein Panel je Trigger), VP-07 Partition nach `track` | **Lücke** | Gruppierung nur nach deklariertem Schlüssel (Trigger, Track), nicht nach Prozessinstanz; keine Markierung instanzübergreifender Kanten. M-3 (Schraffur) wäre als farbfreies Fehlermerkmal wiederverwendbar, gilt aber nur in `cube.phases`. | TASK-021 (Mockup) |

**Zusammenfassung:** 0 × trägt, 9 × teilweise, 3 × Lücke (V-07, V-11, V-12). Für V-01 und V-09 ist ein Minimalpaar aus vorhandenen Printern möglich; für V-05 teilweise; V-12 braucht ein Mockup.

## Folgerungen für die nächsten Tasks

- **TASK-019:** `cube.axes` Y × Y mit DSM-Material (Erwartung: Einträge vs. leere Zellen mit Legende; prüfen, ob `--hide-empty` im SVG sichtbar wird) und `cube.flow` mit Kantenstil für C4-Material.
- **TASK-020:** Printer-Paare für V-01 (ohne/mit `edge_styles`) und V-09 (ohne/mit Linsenakzent auf den Zyklenkanten).
- **TASK-021:** Mockups für V-05 „geprüft leer“, V-01 „Herkunft unbekannt“, V-09 farbfreie Zyklusmarkierung, V-12 Instanzgruppierung.
- Wiederverwendbar für Kandidatenregeln: M-1 (Kantenstil + Legende), M-3 (farbfreie Schraffur), M-4 (Offenlegung), M-5-Legendenformel „nothing declared, not 'no relation'“.

## Grenzen

Reine Doku-/Code-Inventur; Glyphenabdeckung je Host und Lesbarkeit sind nicht geprüft. Kandidatensichten wurden nach ihrer Spezifikation beurteilt; abweichendes Laufzeitverhalten zeigt erst TASK-019.
