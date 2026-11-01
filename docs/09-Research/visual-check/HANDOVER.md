# MILE-003-C — Übergabe an MILE-004 (TASK-023)

Stand: 2026-11-01 · Grundlage: [Inventur](INVENTORY.md), [Render-Nachweise](RENDER-RESULTS.md), [Printer-Paare](PAIRS.md), [Mockups](MOCKUPS.md), [Agenten-Vorprüfung](PRECHECK.md) · Abschlussprüfung: [C-RESULT](../../10-Evidence/MILE-003/C-RESULT.md)

Alle Aussagen beruhen auf Doku/Code, Rendern und einer Agenten-Vorprüfung (Proxy, D-1). **Kein menschlicher Lesbarkeitsnachweis.** Aufwand und Nutzen sind Planannahmen, keine Messung.

## 1. Stand je Darstellungsanforderung

| ID | Unterscheidung | Heute (vorhandene Printer) | Kandidat | Vorprüfung | Setzt voraus |
|---|---|---|---|---|---|
| **V-01** | abgeleitet / deklariert / Herkunft unbekannt | `cube.flow` + `edge_styles` trägt die Unterscheidung, wenn die Ableitung ein eigenes Prädikat hat (R-2b) | [M-01A](mockups/M-01A.svg) | alle Kriterien erfüllt; blind richtig | G-02 |
| **V-05** | markiert / geprüft leer / unbekannt / ausgeblendet | `cube.axes`: markiert ≠ leer; geprüft leer = unbekannt (R-1a); Ausblendung nur gezählt (R-1b) | [M-05C](mockups/M-05C.svg) (aus B; A als Kontrolle) | A/B: Zeilen-Vollständigkeit überbehauptet; C blind richtig (hoch) | G-01 |
| **V-09** | Zyklus, nicht abarbeitbar, nicht „falsch nummeriert“ | nur deklarierte Hervorhebung über Linse, farbabhängig, unvollständig (P-09b) | [M-09C](mockups/M-09C.svg) | A/B: nur ein von zwei Zyklen markiert; C blind richtig (hoch) | G-05 |
| **V-12** | Instanz als Gruppe, instanzübergreifende Kante als Verstoß | keine Sicht | [M-12B](mockups/M-12B.svg) | A: Paarung unklar, Ausführung nahegelegt; B blind richtig (hoch) | G-08 |
| V-02 | Verdichtung n → 1 mit Verlust | Auslassungsledger (Darstellung, nicht Verdichtung) | — | nicht geprüft | G-03 |
| V-03 | Zugehörigkeit als verschachtelte Grenze | Baum mit Kanten | — | nicht geprüft | — |
| V-04 | Fremdtyp neben Cube-Konzept | Freitext-Label | — | nicht geprüft | G-04 |
| V-06 | Matrixkonvention, Rückkopplung | Mitgliedschaftslegende vorhanden; Reihenfolge nach erstem Auftreten (R-1) | — | nur gerendert | deklarierte Reihenfolge |
| V-07 | MDM-Blöcke | Lücke | — | nicht geprüft | G-09 |
| V-08 | Generationen, „nicht zwingend parallel“ | `cube.phases` teilweise | — | nicht geprüft | G-05 |
| V-10 | genommener XOR-Pfad je Instanz | `cube.sequence` `alt` auf Modellebene | — | nicht geprüft | G-07, G-08 |
| V-11 | Join mit Status je Eingang | Lücke (kein `par`) | — | nicht geprüft | G-07 |

## 2. Kandidatenregeln für MILE-004

Reihenfolge nach erwartetem Nutzen je Aufwand. Jede Regel ist P2-Arbeit **nach** der genannten Profil-/LIB-Maßnahme aus der [Lückenbilanz §7](../grammar-sampling/GAP-LEDGER.md); ohne sie hätte der Printer nichts Wahres darzustellen.

| Rang | Regel | Inhalt | Voraussetzung (Rang §7) | Aufwand P2 | Nutzen | Komplexität |
|---|---|---|---|---|---|---|
| 1 | **VR-01 Herkunftslinie** | Linienart nach gebundener Herkunft, nicht nach Prädikat: durchgezogen deklariert, gestrichelt abgeleitet, gepunktet unbekannt; Herkunft immer zusätzlich beschriftet; Pfeilspitze neutral | G-02 (3) | 0,5–1 PT (VP-07 `edge_styles` um Herkunftsquelle erweitern) | hoch | niedrig |
| 2 | **VR-05 Zellzustände** | Eintrag mit ID; „keine · geprüft“ nur für den erklärten Umfang (Zelle oder ausdrücklich erklärte Zeile); unbekannt als Schraffur aus Linien; ausgeblendete Zeilen/Spalten mit Namen | G-01 (1) | 1–1,5 PT (VP-09) | sehr hoch | mittel |
| 3 | **VR-09 Zyklenkomponente** | Status „nicht abarbeitbar · k von n Kanten auf Zyklen“; Rahmen je starker Zusammenhangskomponente; jede Kante auf einem Zyklus doppelt; ein Zeuge nummeriert, als Beispiel benannt; direktes Layout | G-05/G-06 (2) | 1–2 PT (neue Status-/Rahmenelemente in `cube.flow`) | hoch | mittel |
| 4 | **VR-12 Instanz und Paarung** | Instanz als benannter, durchgezogener Rahmen ⬠; Join-Aussage mit ihren Eingängen; fremder Eingang gestrichelt mit schraffierter Marke „Regelverstoß“; Modellfluss getrennt von der Spur | G-08 (5) | 1–2 PT (keine Sicht vorhanden; Ort zu klären) | mittel (nur bei bestätigtem Prozess-Anwendungsfall) | mittel–hoch |

Summe P2: 3,5–6,5 PT zusätzlich zu den Profil-/LIB-Maßnahmen. Keine neue VG-Anker, keine Morphologieänderung: Alle Kandidaten nutzen vorhandene Anker (⌹ ⌼ ⬠ 𝗜 𝗥 𝗣, geprüft gegen `symbols.json`), Linienarten des VP-07-Satzes und Schraffur nach VP-07 PV-5.

## 3. Printer-Befunde (P2-Pflege, keine neue Grammatik)

| ID | Befund | Beleg | Vorschlag | Aufwand |
|---|---|---|---|---|
| PO-1 | „declared“ in zwei Bedeutungen: Kopfzeile `cube.flow` (= Fixture-Aussage) gegen `edge_styles`-Legende (= nicht abgeleitet) | R-2a/b, blind B06/B13 | Kopfzeile „FIXTURE ASSERTIONS“ o. ä. | < 0,25 PT |
| PO-2 | Gemeinsame Senkrechten in `cube.flow`: Kanten und Pfeilrichtung nur über das Ledger eindeutig | R-2, P-09, blind B04/B09 | Kanten mit eigenen Anschlusspunkten führen | 1–2 PT |
| PO-3 | Linsenakzent nur Farbe + Strichstärke, nicht farbfrei | P-09b, `attrs.json` | Linienart oder Doppellinie als Akzentoption | 0,5 PT |
| PO-4 | VP-03 lehnt eine Linse ohne Facettenbindung ab; kein „Vorher-Bild“ ohne Fokus | P-09a | dokumentieren oder neutrale Linse zulassen | < 0,25 PT |
| PO-5 | `cube.axes` ordnet nach erstem Auftreten; DSM-Lesart „über der Diagonale“ nicht deutbar | R-1 | deklarierte Achsenreihenfolge übernehmen | 0,5 PT |
| PO-6 | `hide_empty` nennt nur die Anzahl, nicht die ausgeblendeten Elemente | R-1b | Namen in der Legende | < 0,25 PT |
| PO-7 | Plansichten lesen nur P1.10-Migrationspläne; allgemeine Projektion beliebiger Aussagen fehlt | RENDER-RESULTS | an G-03 anschließen | in G-03 enthalten |

## 4. Erratum MILE-002

Die Zyklus-Variante in [dag-workitems.json](../grammar-sampling/models/dag-workitems.json) (`cycle_variant.cycle`) nennt einen Zyklus a→d→b→a. Mit `a requires d` entstehen **zwei** elementare Zyklen (a→d→b→a, a→d→c→a); jede der fünf Kanten liegt auf einem Zyklus. Das Modell ist in MILE-002-Fällen hash-gepinnt und bleibt unverändert. Folgearbeiten sollen Zyklen berechnen (G-05), nicht aus der Annotation übernehmen. Auch der [Fallbericht DAG-03](../grammar-sampling/reports/DAG-03.md) nennt nur diesen Zyklus (in Vorrangrichtung a → b → d → a). Das ist unvollständig, aber für „nicht abarbeitbar“ ausreichend, weil ein Zeuge genügt; MILE-002-Dokumente bleiben unverändert.

## 5. Offen

- Menschliche Lesbarkeit, Suchzeit und Verständlichkeit: [Skript für einen späteren Menschentest](HUMAN-TEST-SCRIPT.md), nicht durchgeführt.
- V-02–V-04, V-07, V-08, V-10, V-11 nur inventarisiert; V-06 nur gerendert.
- Glyphenabdeckung je Host, Druck und Verkleinerung nicht geprüft.
- Restbefunde der Vorprüfung: Fußzeile M-05C spricht noch von „Vollständigkeitserklärung“; Fallfragen nutzen andere Wörter als die Bilder („verdichtet“ gegen „abgeleitet“, „Abhängigkeit“ gegen `references`).
- Beide Prüfer waren dasselbe Modell; die blinde Prüfung ist angewiesen, nicht technisch erzwungen.
