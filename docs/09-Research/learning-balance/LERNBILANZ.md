# MILE-004-B — Lernbilanz (TASK-027)

Stand: 2026-11-01 · Rahmen: [SCORING-FRAME.md](SCORING-FRAME.md) (`60d24d5`, vor der Bewertung, unverändert) · Bewertung: [MEASURES-SCORED.json](MEASURES-SCORED.json) · Rangfolge: [RANKING.json](RANKING.json), berechnet mit [score_measures.py](score_measures.py)

Nutzen ist **erwartet, nicht gemessen**. Die Gewichtung folgt D-1: Architektursichten (A) und Prozessspuren (P) bestimmen den Rang. Impact/Reihenfolge (I) und Vollständigkeit allgemein (V) gehen nur in die Sensitivität ein.

## Ergebnis in drei Sätzen

Vorn steht die **Vollständigkeitserklärung mit Populationsprüfung (G-01) samt Darstellung der vier Zellzustände (VR-05)**: Sie trifft als einzige Maßnahme beide Anwendungsfälle mehrfach (ARC-02/03, BPMN-01/02). Danach kommt die **typisierte Instanzbindung (G-08)**: klein, gut belegt und Voraussetzung für Spurprüfung (G-07) und Instanzdarstellung (VR-12). Zusammen 5,0 PT (Mitte der Spannen); beide gehen nach der Auswahlregel in **MILE-005**.

## Rangfolge (Hauptliste)

S = (A + P) / E. Pakete reihen eine Maßnahme zusammen mit ihrer offenen Voraussetzung; gezeigt wird je Maßnahme ihr bester Platz.

| Rang | Einheit | Ebene | A | P | PT (Mitte) | E | K | U | S | Begründung (Kurzform) |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | **G-01 → VR-05** | Profil + LIB, dann P2 | 3+2 | 3+0 | 4,25 | 5 | 2,5 | 2 | **1,60** | Vollständigkeit trägt ARC-02/03 und BPMN-01/02; VR-05 macht „geprüft leer“ vs. „unbekannt“ sichtbar (M-05C) |
| 2 | **G-08** | Profil/Dokumentation | 0 | 3 | 0,75 | 2 | 1,5 | 1 | **1,50** | BPMN-03; Voraussetzung für G-07 und VR-12; P1 und Proben E-2/L-2 |
| 3 | G-02 → VR-01 | Profil, dann P2 | 3+3 | 0 | 2,25 | 4 | 2 | 2 | 1,50 | Herkunft in C4-02/03; M-01A erfüllt alle Kriterien |
| 5 | LR-1 | LIB-Vertrag | 2 | 2 | 1,5 | 3 | 2 | 1 | 1,33 | E-1/E-2: fachlicher Ergebniskern sonst untypisiert |
| 6 | G-04 | Profil + Doku | 3 | 1 | 1,5 je Sprache | 3 | 2 | 2 | 1,33 | C4-01, ARC-01: Abbildungsprofile und Namensfallen |
| 7 | G-08 → VR-12 | P2 | 0 | 3+2 | 2,25 | 4 | 2,5 | 2 | 1,25 | Instanz und Paarung sichtbar (M-12B) |
| 8 | G-08 → G-07 | Profil + LIB | 0 | 3+3 | 4,75 | 5 | 3 | 2 | 1,20 | BPMN-01/02 Exklusivität, Synchronisation; NE-Fälle |
| 9 | PO-3 | P2 | 1 | 0 | 0,5 | 1 | 1 | 1 | 1,00 | farbfreier Linsenakzent |
| 10 | PO-1 | P2 | 1 | 0 | 0,18 | 1 | 1 | 2 | 1,00 | „declared“ eindeutig |
| 11 | PO-8 | P2 | 0 | 1 | 0,38 | 1 | 1,5 | 1 | 1,00 | Partition `track` ohne Zusammenlegung |
| 13 | PO-2 | P2 | 2 | 1 | 1,5 | 3 | 2 | 2 | 1,00 | cube.flow ohne gemeinsame Senkrechten |
| 14 | HT | Studie | 1 | 1 | 1,25 | 3 | 1 | 2 | 0,67 | Menschentest, sinnvoll nach Umsetzung von VR-01/VR-12 |
| 15 | G-09 | Profil | 1 | 0 | 0,75 | 2 | 1 | 1 | 0,50 | Domänen- und Prädikatdisziplin |
| 16 | G-03 | LIB | 2 | 0 | 2,5 | 4 | 2 | 1 | 0,50 | Projektion mit Quellenspur (C4-02) |
| 17 | G-05 | LIB | 1 | 0 | 2,5 | 4 | 1,5 | 1 | 0,25 | Graphanalyse; für A nur indirekt |

Rangnummern wie in RANKING.json; Rang 4 (G-01 allein) und Rang 12 (G-02 allein) sind durch die besseren Paketplätze 1 und 3 abgedeckt. Gleichstände wurden nach der festen Regel aufgelöst (kleinere K, dann kleinere U): Rang 2 vor 3, PO-3 vor PO-1 vor PO-8 vor PO-2. Je Maßnahme steht die Begründung in einem Satz in [MEASURES-SCORED.json](MEASURES-SCORED.json).

**Alternative:** G-10 (typisierte Relationsoperanden) wird statt G-02 nicht gereiht; G-02 ist besser bewertet.

**Nebenliste (A + P = 0, nicht gereiht):** G-06 (`impact.propagate` v2), VR-09 (Zyklenkomponente), T-01, T-02, PO-4, PO-5, PO-6. Sie bleiben für Impact/Reihenfolge, DSM und Werkzeuge wertvoll, tragen aber die gewählten Anwendungsfälle nicht.

## Auswahl für MILE-005

Rang 1 (**G-01 → VR-05**, 4,25 PT) und Rang 2 (**G-08**, 0,75 PT) ergeben zusammen 5,0 PT. Das liegt an der Grenze der Regel (≤ 5 PT), also gehen beide in MILE-005. Rang 3 (G-02 → VR-01) liegt im Score gleichauf mit Rang 2 und ist der nächste Kandidat.

## Sensitivität

| Rechnung | Rang 1 | Rang 2 | Abweichung von S |
|---|---|---|---|
| S (rangbildend) | G-01 → VR-05 (1,60) | G-08 (1,50) | — |
| S′ = (A+P+I+V)/E, ohne D-1 | G-01 → VR-05 (3,20) | G-01 allein (2,50) | Rang 1 gleich; G-08 fällt ohne D-1 zurück, PO-3/PO-5/PO-6 rücken vor |
| S″ = (A+P)/(E·U) | G-08 (1,50) | LR-1 (1,33) | Rang 1 wechselt |
| MILE-002 §7 (vorläufig) | G-01 | G-05/G-06 | G-05/G-06 fallen unter D-1 in Hauptliste bzw. Nebenliste |

**Begründung der Abweichungen:**

- Unter S″ fällt G-01 zurück, weil seine Prozess- und ArchiMate-Belege teils nicht ausgeführt wurden (NE, U = 2). MILE-005 enthält G-08 ohnehin. Für G-01 soll MILE-005 mit einem risikomindernden Schritt beginnen: erst NE-Fälle als ausführbare Prüffälle mit Erwartung vorab, dann Profil und LIB.
- Die vorläufige MILE-002-Reihenfolge stellte das Zyklus-Gate und `impact.propagate` auf Rang 2. Unter D-1 tragen diese DAG-Maßnahmen keinen Architektur- oder Prozessfall; sie bleiben hoch bewertet, falls Impact/Reihenfolge später Priorität bekommt (S′).

## Die sieben Leitfragen — final

1. **Reicht der Envelope-Rahmen?** Ja, für Projektion (Architektur) und instanzgebundene Spurprüfung (Prozess): Alle Pflichtunterscheidungen sind ausdrückbar, keine fallen zusammen (E-1, E-2). Es fehlt eine **Typisierung der Ergebnisdetails** ohne heutigen Bindungspunkt → LIB-Vertragsrevision LR-1 (Rang 5), keine neue Envelope. Präzise offen: Teilergebnisse, Abbruch, mehrfacher Ergebnisempfang über längere Spuren, Effektklassen jenseits `pure_declarative`.
2. **Welche Analysemethoden eignen sich für LIB?** Populationsprüfung (G-01, Rang 1), Ergebnisschema je Methode (LR-1, Rang 5), Spurkonformität (G-07, Rang 8), Projektion mit Quellenspur (G-03, Rang 16), Graphanalyse und `impact.propagate` v2 (G-05 Rang 17, G-06 Nebenliste). Alle sind rein und deklarativ beschreibbar; keine ist umgesetzt.
3. **Welche Referenz- und Kardinalitätsregeln gehören in Profile?** Vollständigkeitserklärung je Sicht/Referent und Relationstyp (G-01), Instanzbindung (G-08), Relationsherkunft (G-02), Abbildungsprofile je Fremdsprache (G-04), Prädikateigenschaften und Domänen (G-09). Reihenfolge wie oben.
4. **Welche Bindungen brauchen LENS, MODE und Achsen?** LENS trägt je Linse eine binäre deklarierte Hervorhebung, keine Klassifikation (L-1); Herkunft gehört in G-02 + VR-01. Die Partition gruppiert nur Subjekte und packt Stränge zusammen (L-2); Instanzgruppierung braucht G-08, VR-12 und PO-8. MODE bleibt präzise offen bis zu einem eingefrorenen Schema (P0 §3.10, C021). VP-09-Achsenpaare wurden nicht geprobt.
5. **Welche visuellen Unterscheidungen sind ungesichert?** Alle vier Vorrangunterscheidungen haben einen Kandidaten mit blind richtiger Agentenantwort (M-01A; nach der Vorprüfung korrigiert: M-05C, M-09C, M-12B); keiner ist an Menschen geprüft (HT, Rang 14). Printer-seitig: Begriff „declared“ (PO-1), gemeinsame Senkrechten (PO-2), farbabhängiger Linsenakzent (PO-3), Partition ohne Gruppierungsgarantie (PO-8). Die übrigen acht Anforderungen sind nur inventarisiert bzw. gerendert.
6. **Wo fehlen Ausdrucksmöglichkeiten, wo nur Vertrag oder Prüfer?** Bestätigt aus MILE-002: Ausdruck fehlt für „geprüft leer“ ohne Vollständigkeitserklärung und für n-stellige Synchronisation; nur Vertrag fehlt für Herkunft, Instanz, Prädikateigenschaften, Fremdbegriffe; nur Prüfer fehlt für Population, Graphanalyse, Spurkonformität. Neu aus MILE-004: Auch dem **Ergebnisvertrag** fehlt nur Typisierung, kein Ausdruck. Keine Lücke betrifft Konzepte oder VG-Anker.
7. **Welche Aufgaben stiften den höchsten erwarteten Nutzen?** Für Architektursichten und Prozessspuren: (a) „unbekannt“ nie als „leer“ oder „verletzt“ ausgeben — in Architekturmodellen und Prozessaktivierungen (G-01, VR-05); (b) instanzgenaue Prozessspuren (G-08, dann VR-12 und G-07); (c) herkunftsbewusste Architektursichten (G-02, VR-01, dann G-03). Impact- und Reihenfolgefragen (DAG) bleiben wertvoll, sind aber nach D-1 nachrangig.

## Envelope- und Morphologiekandidaten

Keine. Keine Probe erfüllt das Prüfkriterium für eine Envelope-Erweiterung (R-E1); kein Fall begründet eine Morphologieänderung.

## Grenzen

- Bewertung durch einen Agenten nach festem Rahmen; Nutzenanker beziehen sich auf Fälle der Stichprobe, nicht auf gemessenen Kundennutzen.
- Fünf Eingabewerte (T-01, T-02, LR-1, PO-8, HT) sind markierte Annahmen.
- Die Auswahl für MILE-005 liegt genau an der Aufwandsgrenze von 5 PT; eine höhere Schätzung für G-01 würde G-08 nach der Regel aus MILE-005 drängen.
