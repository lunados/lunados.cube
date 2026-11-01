# MILE-003-C — Agenten-Vorprüfung (TASK-022)

Stand: 2026-11-01 · Plan mit Antwortschlüssel, festgelegt vor der Bewertung: [precheck/PLAN.json](precheck/PLAN.json) (`1f329ef`) · Ergebnisse: [precheck/RESULTS.json](precheck/RESULTS.json) · Merkmalsauslese: [attrs.json](precheck/attrs.json) mit [attrs.py](precheck/attrs.py) · Rasterung: [raster.js](precheck/raster.js), [Protokoll](precheck/raster-log.json)

**Alle Antworten sind Agenten-Proxy, kein Lesbarkeitsnachweis.** Die Prüfung ist **nicht blind**: Derselbe Agent hat die Mockups und Erwartungen verfasst und kannte den Antwortschlüssel. Sie prüft regelgebunden Unterscheidbarkeit, Benennung und Rückführbarkeit. Verständlichkeit, Suchzeit, Druck und Verkleinerung prüft sie nicht.

Verfahren: zwölf Eingaben hash-geprüft, in Farbe und in Graustufen gerastert, Fallfrage nur aus dem Bild beantwortet; für Kriterium 1 zusätzlich Strichmuster, Strichstärke und Farbe der tragenden Elemente maschinell ausgelesen.

## Ergebnis je Einheit

✓ erfüllt · ✗ nicht erfüllt · – nicht anwendbar. Bei Printer-Paaren steht links die Seite ohne, rechts die Seite mit Unterscheidung.

| Einheit | Anf. | C1 ohne Farbe | C2 Legende | C3 rückführbar | C4 unbekannt sichtbar | C5 Fallfrage (Proxy) | C6 keine Überbehauptung |
|---|---|---|---|---|---|---|---|
| P-01 (R-2a / R-2b) | V-01 | ✗ / ✓ | ✗ / ✓ | ✓ | – | ✓¹ / ✓ | ✗ / ✓² |
| M-01A | V-01 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| R-1a/b (Ausgangslage) | V-05 | ✗ | ✗ | ✓ | ✗ | ✗ | ✓ |
| M-05A | V-05 | ✓ | ✓ | ✓ | ✓ | ✓ | **✗** |
| M-05B | V-05 | ✓ | ✓ | ✓ | ✓ | ✓ | **✗** |
| P-09 (P-09a2 / P-09b) | V-09 | ✗ | ✗ | ✓ | – | ✗ | ✓ |
| M-09A | V-09 | ✓ | ✓ | ✓ | – | **✗** | **✗** |
| M-09B | V-09 | ✓ | ✓ | ✓ | – | **✗** | **✗** |
| M-12A | V-12 | ✓ | ✓ | ✓ | – | **✗** | **✗** |

¹ nur durch Nachschlagen des Prädikatnamens „uses-implied“ im Ledger. ² Vermerk: „declared“ in zwei Bedeutungen (Kopfzeile = Fixture-Aussage, Legende = nicht abgeleitet).

Summe über alle Bewertungen: 35 × erfüllt, 18 × nicht erfüllt, 5 × nicht anwendbar. Nur **M-01A** erfüllt alle Kriterien.

## Befunde

1. **V-09 — der Zyklusgraph hat zwei Zyklen, und jede Kante liegt auf einem.** Mit `a requires d` entstehen a→d→b→a und a→d→c→a; die starke Zusammenhangskomponente umfasst alle vier Knoten. Die Modellannotation `cycle_variant.cycle` nennt nur den ersten. P-09 und M-09A/B wurden danach gebaut: Der Gegensatz „hervorgehoben/doppelt“ gegen „einfach“ legt nahe, e2 und e4 lägen auf keinem Zyklus. Das ist falsch. Der Befund stammt aus dem Antwortschlüssel (Berechnung), nicht aus dem Bild. Das Modell ist in MILE-002 hash-gepinnt und bleibt unverändert; Erratum zur Übergabe.
2. **V-05 — Vollständigkeit auf der falschen Ebene.** M-05A/B schreiben „Vollständigkeit: Zeile printer“, das Modell erklärt nur die Zelle printer → parser als analysiert. In derselben Zeile steht printer → resolver als unbekannt — ein Widerspruch im Bild. Die Kandidatenregel muss „geprüft“ je Zelle oder je deklariertem Umfang zeigen, nicht je Zeile. Die Zustandstrennung selbst (C1–C5) trägt in beiden Varianten.
3. **V-12 — Paarung und Ausführung.** M-12A zeigt drei Eingänge an einem AND-Join mit zwei Eingängen; welche Token die Aussage paart (i1/tok-stock mit i2/tok-credit), ist nicht erkennbar. Join → ship innerhalb der Grenze von i1 legt eine Ausführung nahe, die die Handspur nicht enthält. „Fehler“ steht nicht im Bild, und die Strichlinie ist doppelt belegt (Instanzgrenze, fremder Eingang).
4. **V-01 — trägt.** M-01A erfüllt alle sechs Kriterien; das Printer-Paar zeigt, dass der Mechanismus (Kantenstil + Legende) vorhanden ist. Offen bleibt die Herkunftsbindung (G-02). R-2a stellt die abgeleitete Kante unter „DECLARED RELATIONSHIPS“ ohne Unterschied dar.
5. **Printer-Hervorhebung ist nicht farbfrei.** In P-09b unterscheiden sich hervorgehobene Kanten nur in Farbe und Strichstärke (2,8 gegen 1,6); die Legende nennt keinen Zyklus. In R-2b trägt das Strichmuster `8 5` die Unterscheidung.
6. **Gemeinsame Senkrechten** in `cube.flow` (R-2, P-09) und im printerähnlichen M-09A: Kanten sind nur durch Verfolgen zuzuordnen; M-09B mit direkten Kanten vermeidet das.

## Offene Fragen aus TASK-021 (Proxy-Antworten)

| # | Frage | Antwort |
|---|---|---|
| 1 | Ist „doppelt“ in M-09A bei überlagerten Strängen eindeutig? | An den Waagerechten ja (Beschriftung). An den Senkrechten bei wi:a und wi:d liegen bis zu drei Linien dicht beieinander; Zuordnung nur durch Verfolgen. Layoutabhängig. |
| 2 | Reicht in M-05A der Text, oder braucht „unbekannt“ eine Fläche? | Beide trennen die Zustände. A verlangt Lesen jeder Zelle, B macht unbekannte Zellen als Fläche auffindbar. Suchzeit ist per Proxy nicht messbar: B als Kandidat, A als Kontrolle im Menschentest. |
| 3 | Ist gepunktet gegen gestrichelt ausreichend verschieden? | In der Rasterung ja (`2 4` gegen `8 5`), zusätzlich durch Beschriftung redundant. Verkleinerung und Druck ungeprüft; Beschriftung Pflicht lassen. |
| 4 | Verdeckt die Schraffurmarke in M-12A die Richtung? | Nein, die Pfeilspitze liegt außerhalb der Marke; die Marke berührt aber die Grenze von i1. |

## Folgerungen für die Kandidatenregeln (zur Übergabe)

- **V-01:** Regel M-01A beibehalten; Beschriftung der Herkunft verpflichtend.
- **V-05:** Variante B bevorzugen; „geprüft“ nur für den deklarierten Umfang (Zelle oder ausdrücklich erklärte Zeile) zeigen.
- **V-09:** Zyklenkomponente markieren (alle Kanten, die auf einem Zyklus liegen), Zeuge als ein Beispiel benennen, Status etwa „nicht abarbeitbar · 5 von 5 Kanten auf Zyklen · Zeuge …“; direktes Layout.
- **V-12:** behauptete Paarung als eigene, benannte Aussage zeigen; Modellfluss (Join → ship) von der Spur trennen; „instanzübergreifend = Regelverstoß“ benennen; Instanzgrenze nicht gestrichelt.

Keine Printer-, Anker- oder Morphologieänderung. Kein Lesbarkeitsnachweis. Die Mockups bleiben unverändert; Korrekturen sind Kandidaten für die Übergabe.
