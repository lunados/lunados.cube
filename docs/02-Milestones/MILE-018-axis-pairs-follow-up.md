# MILE-018 — Achsenpaare: Folgearbeiten (P2)

Status: **in Arbeit** (Nutzer, 2026-11-05: vor MILE-017) · Stand: 2026-11-05 · Voraussetzung: [MILE-016](MILE-016-axis-pair-views.md) umgesetzt (X × Y, `cube.landscape`, Status der Kreuzung; G5 R10)

## Anlass

MILE-016 hat die zwei wichtigsten Kreuzungen geliefert. Was dort als „später“ markiert war, und der VG-Anker der Landschaftsspalte stehen hier gesammelt, damit MILE-016 abgeschlossen ist und nichts verloren geht. Reihenfolge und Umfang werden vor Beginn mit dem Nutzer festgelegt.

## Backlog (aus MILE-016 übernommen)

| ID | Befund | Vorschlag | Abnahme |
|---|---|---|---|
| **B13** (neu) | `cube.landscape` zeichnet Schichtspalten ohne eigenen VG-Anker (MILE-016 B6, D-1). | Anker oder Form für die Schichtspalte im VG-Register festlegen (Ankerfrage zuerst, wie bei B4); danach im Printer setzen (neues Profil). | Anker im Register, Landschaft trägt ihn; 0.12.0 byte-identisch |
| B11 | X × Z zeigt heute Lens-Facetten, nicht die seit 0.7.8 gedruckten X-Endpunkte. | Zellregel um Abhängigkeiten zwischen Z-Referenten und X-Endpunkten erweitern (Gate-Karte: wo Grant und Admission an Module greifen). | später |
| B12 | X × X zeigt Facetten, nicht den Durchlauf Perception → Conclusion → Authority → Admission → Action → Result (Decision Helix). | Zellregel aus P1.6-Slots zwischen X-Endpunkten (`request_ref`, `authority_ref`, `basis_refs` …). | später, nach B9 |
| B4 | Kanten zwischen zwei Schritten im selben Modul fallen im Export weg (Projektionsverlust, „intern“). | Zählung oder Unterknoten am Modul; Ankerfrage zuerst (Schritte haben keinen VG-Anker). | später |
| B7 | Wiederherstellungswege (*recovers-via*) haben keine eigene Linienform. | Prädikat `recovers-via` als lokaler Vertrag mit eigener Linienform. | später, mit einem Fall mit Recovery-Pfad |
| B8 | Mehrere SVGs werden einzeln geschrieben; das Explorer-Cockpit liest die Ordner selbst. | Druck-Manifest (Plan, Sicht, Panels, Digests, Abdeckung) als stabile Schnittstelle für Viewer. | später; Cockpit liest dann das Manifest |

## Epics und Aufwand (Schätzung, 2026-11-05)

Die Epics sind unabhängig und einzeln ziehbar. Reihenfolge-Vorschlag: E18-1, E18-3, dann nach Bedarf.

| Epic | Backlog | Inhalt | Aufwand (PT) | Unsicherheit |
|---|---|---|---|---|
| E18-1 VG-Anker Schichtspalte | B13 | Ankerfrage im VG-Register klären, dann neues Profil der Landschaft | 0,25–0,5 | gering |
| E18-2 X × Z mit X-Endpunkten | B11 | Zellregel in `cube.axes`: wo Grant und Admission an Module greifen | 0,5 | gering (Muster wie X × Y) |
| E18-3 X × X als Decision Helix | B12 | Kette Perception → Conclusion → Authority → Admission → Action → Result aus deklarierten Slots | 0,75–1 | mittel |
| E18-4 Interne Kanten | B4 | Kanten innerhalb eines Moduls zählen oder als Unterknoten; Ankerfrage zuerst | 0,5 | mittel |
| E18-5 `recovers-via` | B7 | Eigene Linienform für Wiederherstellungswege; braucht einen Fall mit Recovery-Pfad | 0,25 | gering, wartet auf einen Fall |
| E18-6 Druck-Manifest | B8 | Stabile Schnittstelle für Viewer; Cockpit liest das Manifest | 0,5 | gering |
| E18-7 Auslieferung G5 (R11) | – | Neue Profile nach G6/G5, Erwartungen vorab, Live-Lauf | 0,25–0,5 | gering |
| **Summe** | | | **3–3,75** | |

## Rahmenbedingungen

- Neue Profile; `P2-VP-AXES/0.9.0…0.9.3`, `P2-VP-LANDSCAPE/0.12.0` und `P2-VP-MIGRATION/0.7.0…0.7.8` byte-identisch.
- Oracle vor Code wie in MILE-016; G5 als eigener Schritt.
