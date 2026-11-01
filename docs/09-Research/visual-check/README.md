# MILE-003 — Prüfprotokoll Darstellung

Status: in_progress. [Inventur V-01–V-12](INVENTORY.md) [Render-Nachweise](RENDER-RESULTS.md), [Printer-Paare](PAIRS.md), [Mockups](MOCKUPS.md) und die [Agenten-Vorprüfung](PRECHECK.md) liegen vor.

## Vorrangige Unterscheidungen

| ID | Unterscheidung | Fallfrage (aus MILE-002) | Fall |
|---|---|---|---|
| V-01 | abgeleitete vs. deklarierte Kante; unbekannte Herkunft | „Ist API → Database festgelegt oder nur verdichtet?“ | C4-02, C4-03 |
| V-05 | markiert / geprüft leer / unbekannt / ausgeblendet | „Hat printer keine Abhängigkeit zu parser — oder wissen wir es nicht?“ | DSM-03, ARC-03 |
| V-09 | Zeugenzyklus; „nicht abarbeitbar“ vs. „falsch nummeriert“ | „Ist dieser Plan abarbeitbar — und wo liegt der Zyklus?“ | DAG-03, DAG-01 |
| V-12 | Instanzgruppierung; instanzübergreifende Kante als Fehler | „Hat Ship für i1 wegen i2 gestartet?“ | BPMN-03 |

## Kriterien der Agenten-Vorprüfung

1. **Unterscheidbar ohne Farbe:** Die beiden Seiten eines Paares unterscheiden sich in Form, Linienart, Glyphe oder Text, nicht nur in Farbe.
2. **Legende:** Die Unterscheidung ist in einer Legende oder im Text benannt.
3. **Rückführbar:** Jede gezeigte Aussage verweist auf ihre Quelle (ID, Referent, Fallbezug) oder ist aufrufbar.
4. **Unbekannt sichtbar:** „Unbekannt“ wird nie wie „leer“, „abwesend“ oder „deklariert“ dargestellt.
5. **Fallfrage beantwortbar:** Die Fallfrage ist allein aus der Darstellung beantwortbar; die Antwort des Agenten wird als **Proxy** protokolliert.
6. **Keine Überbehauptung:** Die Darstellung suggeriert keine Ausführung, Kausalität, Parallelität oder Wahrheit, die die Quelle nicht trägt.

Ergebnis je Kriterium: erfüllt / nicht erfüllt / nicht anwendbar, mit Begründung. Kein Kriterium belegt menschliche Lesbarkeit.

## Kennzeichnung von Mockups

Jedes Handmockup trägt sichtbar „MOCKUP — kein Printer-Output“, nennt Fall und Kandidatenvariante und verwendet nur Anker aus `symbols.json` v9.4.
