# MILE-003-B — Minimalpaare aus vorhandenen Printern (TASK-020)

Stand: 2026-11-01 · Spezifikationen: [P-01](pairs/P-01.json), [P-09](pairs/P-09.json) (Erwartungen committet vor dem Rendern, `02318c5`; P-09-Nachtrag vor dem zweiten Lauf) · Lauf: [task020-render-log.json](../../10-Evidence/MILE-003/task020-render-log.json), Fehlversuch: [attempt1](../../10-Evidence/MILE-003/task020-render-log-attempt1.json)

| Paar | Anforderung | Art | Ergebnis |
|---|---|---|---|
| P-01 | V-01 | strenges Minimalpaar aus TASK-019 (R-2a/R-2b), nur `edge_styles` verschieden | Printer trägt die Unterscheidung, wenn die Ableitung ein eigenes Prädikat hat |
| P-09 | V-09 | Printer-Paar, **kein strenges Minimalpaar** (Linse und Präfixliste verschieden) | Printer trägt eine von Hand deklarierte Zyklusmarkierung; nichts davon ist berechnet |
| — | V-05 | kein Printer-Paar möglich | „geprüft leer“ und „unbekannt“ rendern identisch (R-1a) → [TASK-021](../../05-Tasks/TASK-021-mockups.md) |
| — | V-12 | kein Printer-Paar möglich | keine Instanzgruppierung in einer Sicht (Inventur) → TASK-021 |

## P-01 — abgeleitete vs. deklarierte Kante

| Seite | SVG | Beobachtung |
|---|---|---|
| ohne `edge_styles` | [R-2a-01.svg](../../10-Evidence/MILE-003/R-2a/R-2a-01.svg) | beide Kanten gleich; Prädikat nur im Deklarationsledger |
| mit `edge_styles` | [R-2b-01.svg](../../10-Evidence/MILE-003/R-2b/R-2b-01.svg) | abgeleitete Kante gestrichelt, Legende „deklariert (Komponente)“ / „abgeleitet (implied, UnlessAny)“ |

Fallfrage: „Ist API → Database festgelegt oder nur verdichtet?“ Einzelheiten und Erwartungsabgleich in [RENDER-RESULTS](RENDER-RESULTS.md).

## P-09 — Zyklusmarkierung

Darstellungsabbildung (A): Work Items als `Y:resource-object:resource`, Prädikat `requires`, Zyklus-Variante des [DAG-Modells](../grammar-sampling/models/dag-workitems.json) (a requires d). Zyklenkanten tragen `witness_ref`-Präfix `cycle:`; nur mit deklarierter Präfixliste hebt die Epistemologie-Linse sie hervor (Adapter AD-4).

| Erwartung (vorab) | Beobachtung | Abgleich |
|---|---|---|
| P-09a: Epistemologie-Linse ohne Präfixliste, keine Hervorhebung | **Abgelehnt:** „selected lens has no explicit facet bindings: cannot infer relevance“ (VP-03) | **abweichend** — VP-03 rendert keine Linse ohne Fokus. Nachtrag: Vergleichsseite mit Provenienz-Linse (P-09a2) |
| P-09a2: alle fünf Kanten mit gleichem Provenienz-Akzent, Zyklus nicht hervorgehoben | wie erwartet; Linsenfeld „Provenance · 5 declared focus“ | erfüllt |
| P-09b: genau a→d, d→b, b→a hervorgehoben; c→a, d→c nicht | e1 (b→a), e3 (d→b), e5 (a→d) grün und etwas breiter; e2, e4 grau | erfüllt |
| P-09b: Linsenfeld nennt drei Fokusse | „Epistemology · 3 declared focus“ | erfüllt |
| Unterscheidung farbfrei? (Beobachtung) | Farbe plus etwas größere Strichstärke; Bewertung in TASK-022 | offen |
| Keine Aussage „nicht abarbeitbar“, keine Abgrenzung zu „falsch nummeriert“ | keine | erfüllt — Lücke bleibt |
| Ein Panel, keine Auslassung | „panel 01/01“, „Shown 4 items / 5 edges · omitted 0“ | erfüllt |

SVGs: [P-09a2-01.svg](../../10-Evidence/MILE-003/P-09a2/P-09a2-01.svg), [P-09b-01.svg](../../10-Evidence/MILE-003/P-09b/P-09b-01.svg).

**Zusatzbefund Layout:** Die rechtwinklige Kantenführung legt mehrere Kanten auf gemeinsame Senkrechten (an wi:a laufen e1, e2 und e5 übereinander, an wi:d e3, e4 und e5). Einzelne Kanten — und damit der Zyklus — lassen sich im Bild schwer verfolgen; die Hervorhebung hilft, ersetzt aber nicht die eindeutige Führung. Kein Lesbarkeitstest.

## Folgerungen

- **V-01:** Der vorhandene Mechanismus (Kantenstil je Prädikat + Legende) genügt, sobald die Herkunft im Prädikat steckt; die Lücke ist die fehlende Herkunftsbindung (G-02), nicht die Darstellung.
- **V-09:** Darstellbar ist nur eine *deklarierte* Hervorhebung über einen Umweg (Witness-Präfix → Epistemologie-Linse). Ein berechneter Zeugenzyklus (G-05) und eine farbfreie, layoutrobuste Markierung fehlen → Mockup in TASK-021.
- **Neu:** VP-03 lehnt eine Linse ohne Fokus ab. Ein „Vorher-Bild“ ohne Hervorhebung braucht deshalb eine andere Linse.
