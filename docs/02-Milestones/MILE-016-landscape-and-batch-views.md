# MILE-016 — Landscape View, Instanzkette und Sammelausgabe (P2)

Status: geplant (Entwurf) · Stand: 2026-11-05 · Voraussetzung: MILE-014; B5 nach [MILE-015](MILE-015-scopes-and-admission-outcomes.md)

## Anlass

Die Drucke der Explorer-Fälle sind vollständig, aber kleinteilig: viele Panels je Plan, keine Gesamtsicht. Aus einem früheren Projektdurchlauf liegt eine Übersicht „current and target“ vor (Schichten Plattform → DNS → Provider → Account → System; Ist und Ziel untereinander; ausgemusterte und neue Objekte; Herkunft „im Repo gefunden“ gegen „geplant“). Sie zeigt die Y-/Z-Landschaft auf einen Blick, die den Funktionsblättern fehlt. Dazu kommen Befunde aus dem Explorer, die nur der Printer lösen kann.

## Backlog

| ID | Befund | Vorschlag | Abnahme |
|---|---|---|---|
| **B6** | Keine Gesamtsicht über Ressourcen, Module und Konten je Phase. | Neue Sicht `cube.landscape` aus demselben `binding-context/10`-Plan: Spalten = deklarierte Schichtenfolge (wie die deklarierte Achsenfolge aus MILE-006), Zeilen = Objekte, zwei oder mehr gewählte Schritte untereinander; Ausmusterung und Einführung aus den Übergängen, Herkunft aus der Herkunftslinie (MILE-011). Keine neue Semantik, nur eine Anordnung. | Landschaft für F02 und F05 (Current und BETA); `check-panels` PASS; VG-Anker für die neue Form |
| **B4** | Kanten zwischen zwei Schritten im selben Modul fallen im Export weg (Projektionsverlust, „intern“). | Interne Kanten als Zählung oder Unterknoten am Modul zeichnen. Schritte haben keinen VG-Anker (`bounded-execution`); zuerst klären, ob ein Anker nötig ist. | Fälle mit internen Kanten (F01, F03a, F04a) zeigen sie; keine Änderung an bestehenden Profilen |
| **B5** | Gezeichnet wird nur der X-Endpunkt; die gebundene Kette (Action, Authority, Principal, Grant) bleibt unsichtbar. | Kette in `cube.instances` (VP-11) oder als Detail am Vertragsanker; deklarierte Lücken (offene Slots) sichtbar markieren. | F05 XB1 vollständig, F03a XB1/XB2 mit markierter Lücke |
| **B7** | Wiederherstellungswege (*recovers-via*) haben kein eigenes Prädikat bzw. keinen eigenen Typ; im Explorer fallen sie unter `runtime` oder `gate`. | Prädikat `recovers-via` als lokaler Vertrag mit eigener Linienform; Typ im Explorer nur, wenn ein Fall ihn braucht. | Ein Fall mit Recovery-Pfad (Kandidat: Mail-Migration aus dem Vordurchlauf) |
| **B8** | Mehrere SVGs werden einzeln geschrieben; der Sammelexport ist in VP-06 zurückgestellt. Das Explorer-Cockpit liest deshalb die Ordner selbst. | Ein Manifest je Druck (Plan, Sicht, Panels, Digests, Abdeckung) als stabile Schnittstelle für Viewer. | Cockpit des Explorers liest das Manifest statt der Ordner |

## Rahmenbedingungen

- Neues Profil bzw. neue Sicht; `0.7.0…0.7.8` byte-identisch.
- Goldsatz wie MILE-015.
- G5 als eigener Schritt.

## Entscheidungen (2026-11-05, Nutzer)

| ID | Frage | Entscheidung |
|---|---|---|
| **D-1** | Landscape View im Printer oder nur im Explorer | Im Printer (geprüft, mit VG-Anker) |
| **D-2** | Viewer | Zunächst statisches Cockpit im Explorer; Veröffentlichung als Seite später |
| **D-3** | TOML-Builder | Format im Explorer, Adapter für weitere Formate im Connector; nicht Teil dieser Mile |

## Tasks und Aufwand (Schätzung)

| Task | Aufwand |
|---|---|
| B6 — `cube.landscape` (Spezifikation, Sicht, Prüffälle) | 1–1,5 PT |
| B8 — Druck-Manifest | 0,25 PT |
| B5 — Instanzkette | 0,5 PT |
| B4 — interne Kanten (Ankerfrage zuerst) | 0,25–0,5 PT |
| B7 — `recovers-via` | 0,25 PT |

## Offene Fragen

- B6: Schichtenfolge frei deklariert oder aus den P1.11-Rollen abgeleitet?
- B4: Reicht eine Zählung am Modul, oder braucht es Schritte als Knoten?
