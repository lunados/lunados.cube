# MILE-016 — Sichten nach Achsenpaaren: X × Y und Landschaft (P2)

Status: **abgeschlossen** (2026-11-05, vom Nutzer abgenommen; [Nachweis](../10-Evidence/MILE-016/README.md)): B9, B6, B10 im Printer, im Explorer abgenommen (X × Y, Landschaft, Cockpit), G6 und G5 R10 live 58/58. VG-Anker der Schichtspalte und Backlog B11, B12, B4, B7, B8 nach [MILE-018](MILE-018-axis-pairs-follow-up.md) verschoben · Voraussetzung: MILE-014; X × Y nach [MILE-015](MILE-015-scopes-and-admission-outcomes.md) B3

## Anlass

Die Drucke der Explorer-Fälle sind vollständig, aber kleinteilig, und sie zeigen fast nur Y/Z ↔ Y/Z (`cube.flow`) und Y/Z × T (`cube.phases`). Die Morphologie ordnet Sichten nach Achsenkombinationen (01.3 „Cross-axis matrices — n : m“: X × Y, X × X, X × Z, Y × Z, X × T, Y × T, Z × T, MEAS/FUNC). Der Cube hat dafür schon eine Sichtfamilie: **VP-09 `cube.axes`**, eine kategoriale Matrix über zwei deklarierte Achsen mit geschlossener Paarliste (Z × T, F × Z, Y × T, F × T, X × X, Y × Z, X × Z; Y × Y seit 0.9.2), Zellregeln je Paar (CM) und dem Grundsatz „leer = nichts deklariert“. Diese Mile baut darauf auf, statt Einzelsichten zu erfinden.

Es fehlen zwei Dinge:

1. **X × Y**, die einzige kanonische Kreuzung (Morphologie §3.3), ist nicht in der Paarliste. Gerade sie zeigt, was die Bindungen aus E8 aussagen: wer unter welcher Admission oder Authority handelt (Ξ × Actor = *performed-by*, Γ × Principal = *authenticated identity for Admission*).
2. Eine **Landschaft**: Y × Z als Graph mit Schichten als Spalten und mehreren Zeitpunkten untereinander, wie die Übersicht „current and target“ aus dem früheren Projektdurchlauf (Plattform → DNS → Provider → Account → System; p0 und p4; ausgemustert und neu; Herkunft „im Repo gefunden“ gegen „geplant“).

## Backlog

| ID | Befund | Vorschlag | Abnahme |
|---|---|---|---|
| **B9** (neu, zuerst) | X × Y fehlt in `cube.axes`; die Instanzketten der Explorer-Bindungen sind unsichtbar (vorher B5). | Paar **X × Y** in VP-09 (neues Profil): Zeilen = X-Dimensionen, Spalten = Y-Anker; eine Zelle listet die P1.6-Slots, die einen Y-Anker unter einem X-Endpunkt dieser Dimension nennen (z. B. Γ × Principal: `principal_ref` einer Admission; Ξ × Actor: `performed_by_ref` einer Action; Γ × Actor: `holder_ref` einer Authority). In `open` deklarierte Lücken erscheinen als eigener Eintrag „offen“. Zellregel nur aus deklarierten Slots, keine Hülle. | F05 XB1 und F03a XB1/XB2 als X × Y; Lücken sichtbar; `check-panels` PASS |
| **B6** (zuerst) | Keine Gesamtsicht über Ressourcen, Konten und Module je Zeitpunkt. | **`cube.landscape`** als Graph über Y × Z: Spalten = deklarierte Schichtenfolge (Option wie `axis_order` aus VP-10.1), Knoten = Y- und Z-Referenten, Kanten = deklarierte Abhängigkeiten mit Prädikat (Zellregel CM-6 von VP-09), Platzierung über *hosted-by* (Z, nicht X-Scope); zwei oder mehr deklarierte Schritte untereinander, „eingeführt“/„ausgemustert“ aus den Übergängen (CM-3), Herkunft aus der Herkunftslinie (MILE-011). Keine neue Semantik, nur eine Anordnung bekannter Aussagen. | Landschaft für F02 und F05 (Current und BETA); `check-panels` PASS; VG-Anker für die Schichtspalte |
| **B10** (zuerst) | Die Kreuzungen haben unterschiedlichen Status: X × Y kanonisch (§3.3), X × X illustrativ (Annex D.3), X × Z, Y × Z und die T-Paare abgeleitet. | Jede Achsensicht nennt im Panel den Status ihrer Kreuzung und die Quelle, wie die Herkunftslinie; abgeleitete Kreuzungen sind erlaubt, aber erkennbar. | Statuszeile in allen `cube.axes`-Paaren und in `cube.landscape` |
| B11 | X × Z zeigt heute Lens-Facetten, nicht die seit 0.7.8 gedruckten X-Endpunkte. | Zellregel um Abhängigkeiten zwischen Z-Referenten und X-Endpunkten erweitern (Gate-Karte: wo Grant und Admission an Module greifen). | später |
| B12 | X × X zeigt Facetten, nicht den Durchlauf Perception → Conclusion → Authority → Admission → Action → Result (Decision Helix). | Zellregel aus P1.6-Slots zwischen X-Endpunkten (`request_ref`, `authority_ref`, `basis_refs` …). | später, nach B9 |
| B4 | Kanten zwischen zwei Schritten im selben Modul fallen im Export weg (Projektionsverlust, „intern“). | Zählung oder Unterknoten am Modul; Ankerfrage zuerst (Schritte haben keinen VG-Anker). | später |
| B7 | Wiederherstellungswege (*recovers-via*) haben keine eigene Linienform. | Prädikat `recovers-via` als lokaler Vertrag mit eigener Linienform. | später, mit einem Fall mit Recovery-Pfad |
| B8 | Mehrere SVGs werden einzeln geschrieben; das Explorer-Cockpit liest die Ordner selbst. | Druck-Manifest (Plan, Sicht, Panels, Digests, Abdeckung) als stabile Schnittstelle für Viewer. | später; Cockpit liest dann das Manifest |

## Rahmenbedingungen

- Neue Profile; `P2-VP-MIGRATION/0.7.0…0.7.8` und `P2-VP-AXES/0.9.0…0.9.2` byte-identisch.
- Goldsatz wie MILE-015.
- Seitens lunados.explorer: `print_sheet.py` druckt zusätzlich `cube.axes`-Paare und `cube.landscape`; das Cockpit bekommt die Sicht „Achsen“.
- G5 als eigener Schritt.

## Entscheidungen (2026-11-05, Nutzer)

| ID | Frage | Entscheidung |
|---|---|---|
| **D-1** | Landschaft im Printer oder nur im Explorer | Im Printer (geprüft, mit VG-Anker) |
| **D-2** | Viewer | Zunächst statisches Cockpit im Explorer (`cases/cockpit.html`); Veröffentlichung als Seite später |
| **D-3** | TOML-Builder | Format im Explorer, Adapter für weitere Formate im Connector; nicht Teil dieser Mile. **Präzisiert 2026-11-05:** keine Explorer-Sache und keine Übersetzung, sondern eine Referenz in lunados.connector, mit der eine AI AIAEAO-TOML (Relay-Launcher, Pipelines, Runnables, Runbooks) eindeutig formuliert (Connector MILE-004) |
| **D-4** | Sichten nach Achsenkombinationen | Ja, über die bestehende Familie `cube.axes` |
| **D-5** | Abgeleitete Kreuzungen | Erlaubt, Status sichtbar im Panel (B10) |
| **D-6** | Umfang | Zuerst X × Y (B9) und Landschaft (B6) mit Status (B10); Sichtfamilie allgemein spezifiziert, übrige Paare als eigene Tasks |

## Tasks und Aufwand (Schätzung)

| Task | Aufwand |
|---|---|
| B9 — X × Y in `cube.axes` ([TASK-078](../05-Tasks/TASK-078-vp093-x-y.md), VP-09.3) | 0,5–0,75 PT |
| B6 — `cube.landscape` ([TASK-079](../05-Tasks/TASK-079-vp12-landscape.md), VP-12) | 1–1,5 PT |
| B10 — Status der Kreuzung | 0,25 PT |
| später: B11, B12, B4, B7, B8 | je 0,25–0,5 PT |

## Offene Fragen (für die Spezifikation)

- B6: Schichtenfolge frei deklariert oder aus den P1.11-Rollen abgeleitet? Welche Schritte zeigt die Landschaft per Default (erster und letzter)?
- B9: Spalten als Y-Anker (Actor, Principal …) oder als Y-Referenten (konkrete Akteure)? VP-09 kennt beide Formen (`Y:kind`, `Y:referent`).
