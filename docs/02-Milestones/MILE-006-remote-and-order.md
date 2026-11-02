# MILE-006 — Remote prüfen und Matrix lesbar ordnen

Status: in_progress · Stand: 2026-11-02 · Voraussetzung: MILE-005 ([Übergabe](../09-Research/completeness-instances/HANDOVER.md))

## Ergebnis

Der kurze Folgeschritt aus der MILE-005-Übergabe. Er macht das Erreichte nutzbar und lesbar, ohne neue Prüfsemantik:

1. **Remote prüfen:** `cube_validate` im G5-Remote-Server nimmt `binding-context/8` an (P1.12); dazu kommen Discovery und eine Host-Abnahme wie bei P1.11.
2. **Matrix ordnen (PO-5):** VP-10 ordnet die Y × Y-Matrix nach einer deklarierten Achsenreihenfolge und zeigt die DSM-Lesart (Einträge über der Diagonale als „Rückkopplung“) farbfrei.
3. **Kurze Sichtprüfung:** eine angeleitete Sichtprüfung von zwei Renderings (Zellzustände, Reihenfolge) durch den Nutzer; Mängel werden behoben oder benannt.

## Rahmenbedingungen

- P0, P1.1–P1.12, VP-07, VP-09 und VP-10 0.10.0 bleiben byte-gleich. Die Achsenreihenfolge kommt als VP-10 0.10.1 (opt-in).
- Ablauf wie bisher: Spezifikation mit Entscheidungen, Orakel bzw. Erwartung vor Code, Tests, Nachweise.
- Keine Kundendaten in Repo, Fixtures, Prüfunterlagen oder auf cube.lunados.net.

## Entscheidungen (2026-11-02, Nutzer)

Nach Erörterung entschieden. D-6 hatte der Nutzer zunächst bestätigt („über die Mockups können ein paar Augen drüber fliegen“). D-1 bis D-5 gelten wie vorgeschlagen; der Nutzer hat ohne Einwand den Start mit D-1 freigegeben. D-6 hat der Nutzer nach TASK-040 enger gefasst (2026-11-02): kein Lesbarkeitstest mit vielen Personen, sondern eine kurze, angeleitete Sichtprüfung; Funktionslücken zeigen sich in der Praxis.

| ID | Frage | Entscheidung | Grund | Nicht gewählt |
|---|---|---|---|---|
| **D-1** | Rahmen | **Schlankes MILE-006** mit Milestone, Epic, Stories, Tasks und OpenSpec-Change | gleiche Nachverfolgung wie MILE-001–005 | nur Spezifikation und Nachweis je Paket |
| **D-2** | Umfang G5 | **nur `/8` in `cube_validate`** plus Discovery (`0.7.0-proof`) | Plansichten laufen heute nirgends remote; das wäre ein eigener, größerer Schritt | zusätzlich Plansichten remote (VP-10) |
| **D-3** | Bereitstellung und Abnahme | **Agent** stellt den Kern zusammen, prüft offline und legt die Erwartungen vorab fest; **Nutzer** stellt nach `DEPLOYMENT.md` bereit; **Agent** führt die Host-Abnahme live über den G5-Connector durch und schreibt den Bericht | gleiche Rollen wie bei R4 P1.11; Abnahme im echten Host | Abnahme durch den Nutzer allein |
| **D-4** | Quelle der Reihenfolge | **ausdrückliche Option `axis_order`** in VP-10 0.10.1; nicht aufgeführte Referenten folgen und werden gekennzeichnet | eindeutige Bedeutung, keine Grenze von 12 | VP-07-Ebenenzuordnung zweckentfremden |
| **D-5** | DSM-Lesart | **„Rückkopplung“** für Einträge über der Diagonale, nur bei deklarierter Reihenfolge, farbfrei; die Legende sagt, dass es nur aus der Reihenfolge folgt | M-05C; erst mit Reihenfolge deutbar | nur ordnen |
| **D-6** | Sichtprüfung (revidiert 2026-11-02) | **kurze Sichtprüfung mit Anleitung**: zwei Renderings, sieben Prüfpunkte mit ja/nein, Durchführung durch den Nutzer (ca. 10 Minuten); Mängel beheben oder benennen | der Printer arbeitet weitgehend zuverlässig; zufällige Bewertungen vieler Personen bringen keinen Befund | Lesbarkeitstest mit Testheft, vorab festgelegten Antworten und Auswertung je Zustand (ursprüngliche Fassung) |

## Drei Chargen

| Mile | Ergebnis | Abschlusskriterium | Aufgaben |
|---|---|---|---|
| **MILE-006-A — Remote `/8`** | G5-Kern mit P1.12, Discovery, Erwartungen vorab; Bereitstellung; Host-Abnahme | Offline-Prüfung und Parität G4/G5; Live-Abnahme mit vorab festgelegten Erwartungen, Bericht R4 | TASK-037, TASK-038 |
| **MILE-006-B — Achsenreihenfolge** | VP-10 0.10.1 mit `axis_order` und Rückkopplungsmarke | Orakel vor Code; Vektoren wie erwartet; 0.10.0 byte-gleich | TASK-039, TASK-040 |
| **MILE-006-C — Sichtprüfung** | Anleitung; Durchführung durch den Nutzer; Mängel bearbeitet | Anleitung committet; jeder Prüfpunkt mit ja/nein beantwortet; jedes „nein“ behoben oder als offen benannt | TASK-041, TASK-042 |

A und B sind unabhängig. C nutzt je ein Rendering aus MILE-005 (Zellzustände) und aus B (Reihenfolge).

## Epics, Stories und Aufwand

[EPIC-006](../03-Epics/EPIC-006-remote-and-readability.md). US-021–023, TASK-037–042.

**Aufwand: 1,75–2,25 PT**, ohne die Zeit des Nutzers für Bereitstellung und Sichtprüfung.

| Charge | Aufwand |
|---|---|
| A | 0,75–1 PT |
| B | 0,75–1 PT |
| C | 0,1–0,25 PT |

## Nachverfolgung

[OpenSpec-Change](../../openspec/changes/deliver-remote-and-ordered-cells/proposal.md) · [Aufgabenstatus](../../openspec/changes/deliver-remote-and-ordered-cells/tasks.md) · [Abdeckung](../../openspec/changes/deliver-remote-and-ordered-cells/TRACEABILITY.md). TASK-037: G5-Kern `0.7.0-proof` mit P1.12, Parität 21/21, [Erwartungen](../../P3/remote-mcp-g5/evidence/G5_R4_P112_EXPECTATIONS.json). TASK-038: bereitgestellt (`42e7b8a9…`), Host-Abnahme PASS, [Bericht](../../P3/remote-mcp-g5/evidence/G5_R4_P112_HOST_REPORT.md). Charge A abgeschlossen. TASK-039: [Spezifikation VP-10.1](../../P2/visual-printer-cells-v1/VP10_1_ACCEPTANCE_SPEC.md), Q-1–Q-6 nach Vorschlag, Orakel O-01–O-10 und 0.10.0-Pins vor Code. TASK-040: VP-10.1 umgesetzt (`b2f75f5`), O-01–O-10 10/10, 16/16 Ausgaben aus 0.10.0 byte-gleich, G6-Option `axis_order`, [Nachweise](../10-Evidence/MILE-006/task040/README.md). Charge B abgeschlossen. D-6 auf kurze Sichtprüfung revidiert (`bb86565`). TASK-041: [Anleitung](../10-Evidence/MILE-006/SICHTPRUEFUNG.md). TASK-042: Sichtprüfung durch den Nutzer 7/7 ja, keine Mängel. Charge C abgeschlossen.
