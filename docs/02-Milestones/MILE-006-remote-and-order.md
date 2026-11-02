# MILE-006 — Remote prüfen und Matrix lesbar ordnen

Status: in_progress · Stand: 2026-11-02 · Voraussetzung: MILE-005 ([Übergabe](../09-Research/completeness-instances/HANDOVER.md))

## Ergebnis

Der kurze Folgeschritt aus der MILE-005-Übergabe. Er macht das Erreichte nutzbar und lesbar, ohne neue Prüfsemantik:

1. **Remote prüfen:** `cube_validate` im G5-Remote-Server nimmt `binding-context/8` an (P1.12); dazu kommen Discovery und eine Host-Abnahme wie bei P1.11.
2. **Matrix ordnen (PO-5):** VP-10 ordnet die Y × Y-Matrix nach einer deklarierten Achsenreihenfolge und zeigt die DSM-Lesart (Einträge über der Diagonale als „Rückkopplung“) farbfrei.
3. **Lesbarkeit mit Menschen:** Unterlagen für einen kurzen Lesbarkeitstest der Zellzustände und Mockups; einige Personen sehen ihn durch.

## Rahmenbedingungen

- P0, P1.1–P1.12, VP-07, VP-09 und VP-10 0.10.0 bleiben byte-gleich. Die Achsenreihenfolge kommt als VP-10 0.10.1 (opt-in).
- Ablauf wie bisher: Spezifikation mit Entscheidungen, Orakel bzw. Erwartung vor Code, Tests, Nachweise.
- Keine Kundendaten in Repo, Fixtures, Testunterlagen oder auf cube.lunados.net.

## Entscheidungen (2026-11-02, Nutzer)

Nach Erörterung entschieden. D-6 hat der Nutzer ausdrücklich bestätigt („über die Mockups können ein paar Augen drüber fliegen“). D-1 bis D-5 gelten wie vorgeschlagen; der Nutzer hat ohne Einwand den Start mit D-1 freigegeben.

| ID | Frage | Entscheidung | Grund | Nicht gewählt |
|---|---|---|---|---|
| **D-1** | Rahmen | **Schlankes MILE-006** mit Milestone, Epic, Stories, Tasks und OpenSpec-Change | gleiche Nachverfolgung wie MILE-001–005 | nur Spezifikation und Nachweis je Paket |
| **D-2** | Umfang G5 | **nur `/8` in `cube_validate`** plus Discovery (`0.7.0-proof`) | Plansichten laufen heute nirgends remote; das wäre ein eigener, größerer Schritt | zusätzlich Plansichten remote (VP-10) |
| **D-3** | Bereitstellung und Abnahme | **Agent** stellt den Kern zusammen, prüft offline und legt die Erwartungen vorab fest; **Nutzer** stellt nach `DEPLOYMENT.md` bereit; **Agent** führt die Host-Abnahme live über den G5-Connector durch und schreibt den Bericht | gleiche Rollen wie bei R4 P1.11; Abnahme im echten Host | Abnahme durch den Nutzer allein |
| **D-4** | Quelle der Reihenfolge | **ausdrückliche Option `axis_order`** in VP-10 0.10.1; nicht aufgeführte Referenten folgen und werden gekennzeichnet | eindeutige Bedeutung, keine Grenze von 12 | VP-07-Ebenenzuordnung zweckentfremden |
| **D-5** | DSM-Lesart | **„Rückkopplung“** für Einträge über der Diagonale, nur bei deklarierter Reihenfolge, farbfrei; die Legende sagt, dass es nur aus der Reihenfolge folgt | M-05C; erst mit Reihenfolge deutbar | nur ordnen |
| **D-6** | Lesbarkeitstest | **Unterlagen jetzt** (Renderings aus VP-10, Skript angepasst); Durchführung durch den Nutzer mit einigen Personen; Auswertung danach | bisher nur Agenten-Vorprüfung als Proxy | später gesondert |

## Drei Chargen

| Mile | Ergebnis | Abschlusskriterium | Aufgaben |
|---|---|---|---|
| **MILE-006-A — Remote `/8`** | G5-Kern mit P1.12, Discovery, Erwartungen vorab; Bereitstellung; Host-Abnahme | Offline-Prüfung und Parität G4/G5; Live-Abnahme mit vorab festgelegten Erwartungen, Bericht R4 | TASK-037, TASK-038 |
| **MILE-006-B — Achsenreihenfolge** | VP-10 0.10.1 mit `axis_order` und Rückkopplungsmarke | Orakel vor Code; Vektoren wie erwartet; 0.10.0 byte-gleich | TASK-039, TASK-040 |
| **MILE-006-C — Lesbarkeitstest** | Testunterlagen; Durchführung; Auswertung | Unterlagen vor der Durchführung committet; Auswertung gegen vorab festgelegte Antworten | TASK-041, TASK-042 |

A und B sind unabhängig. C nutzt die Renderings aus B, wenn B fertig ist, sonst die aus MILE-005.

## Epics, Stories und Aufwand

[EPIC-006](../03-Epics/EPIC-006-remote-and-readability.md). US-021–023, TASK-037–042.

**Aufwand: 1,75–2,5 PT**, ohne die Zeit des Nutzers für Bereitstellung und Test.

| Charge | Aufwand |
|---|---|
| A | 0,75–1 PT |
| B | 0,75–1 PT |
| C | 0,25–0,5 PT |

## Nachverfolgung

[OpenSpec-Change](../../openspec/changes/deliver-remote-and-ordered-cells/proposal.md) · [Aufgabenstatus](../../openspec/changes/deliver-remote-and-ordered-cells/tasks.md) · [Abdeckung](../../openspec/changes/deliver-remote-and-ordered-cells/TRACEABILITY.md). TASK-037: G5-Kern `0.7.0-proof` mit P1.12, Parität 21/21, [Erwartungen](../../P3/remote-mcp-g5/evidence/G5_R4_P112_EXPECTATIONS.json). TASK-038: bereitgestellt (`42e7b8a9…`), Host-Abnahme PASS, [Bericht](../../P3/remote-mcp-g5/evidence/G5_R4_P112_HOST_REPORT.md). Charge A abgeschlossen.
