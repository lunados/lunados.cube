# MILE-008 — Kontrollfluss und Spurkonformität prüfbar machen

Status: in_progress · Stand: 2026-11-02 · Voraussetzung: MILE-005 (Instanzbindung, Populationsregeln), MILE-007 ([Abschluss](../10-Evidence/MILE-007/C-RESULT.md))

## Ergebnis

G-07 aus der [Lückenbilanz](../09-Research/grammar-sampling/GAP-LEDGER.md), Rang 8 der [Lernbilanz](../09-Research/learning-balance/LERNBILANZ.md) (Paket G-08 → G-07, 4,75 PT). Cube kann für Prozessspuren drei Dinge, die heute fehlen:

1. **Kontrollfluss deklarieren (Profil):** Gateways mit Typ (exklusiv, parallel), ihre ein- und ausgehenden Flüsse, bei exklusiven Gateways die Bedingungsreihenfolge und den Default-Pfad. P1 prüft, dass die Deklaration wohlgeformt ist und dass Spur-Aussagen nur deklarierte Flüsse nennen.
2. **Spuren gegen das Modell prüfen (LIB):** Eine reine Funktion prüft je Instanz, ob jede Aktivierung eines exklusiven Gateways genau einen Pfad nahm, ob der Default nur ohne wahre Bedingung genommen wurde und ob ein paralleler Join alle Eingänge der eigenen Instanz hatte; überzählige Token werden ausgewiesen.
3. **Die BPMN-Fälle erneut laufen lassen:** BPMN-01 und BPMN-02 („nicht ausführbar“ in MILE-002) bekommen ein ausführbares, vorab erwartetes Ergebnis.

Heute: Zwei widersprüchliche Leitentscheidungen für denselben Token bestehen je einzeln; Bedingungsreihenfolge, Default und Exception sind nicht prüfbar; die erwarteten Eingänge eines Joins sind nicht Teil eines Vertrags ([BPMN-01](../09-Research/grammar-sampling/reports/BPMN-01.md), [BPMN-02](../09-Research/grammar-sampling/reports/BPMN-02.md)). MILE-005 deckt bereits Teile ab: `join_activation` und Zählregeln als Populationsregeln (P1.12, `analyze.population/v1`), aber ohne Gateway-Typ, Flussbindung und Bedingungen.

## Rahmenbedingungen

- P0, P1.1–P1.12, P2 und die vorhandenen lunados.lib-Einträge bleiben byte-gleich; P1.7 bleibt reserviert. Neue Fähigkeiten als eigenes Profil und eigener LIB-Eintrag.
- Profil-Ablauf wie P1.12: Prüffälle mit Erwartung vor der Spezifikation → Spezifikation mit Entscheidungen → Entscheidungen auflösen (eigener Docs-Commit) → Orakel vor Code → Implementierung, Vektoren, Tests → Adapter → Wiederholung.
- Keine Prozess-Engine: Der Cube führt nichts aus und wertet keine Bedingungen aus; geprüft werden deklarierte Modelle und beobachtete, deklarierte Spuren.
- Keine Kundendaten in Repo, Fixtures, Fällen oder auf cube.lunados.net.
- Die Lernbilanz bewertet den Nutzen als „hoch, aber nur bei bestätigtem Prozess-Anwendungsfall“; der Nutzer hat den Milestone ausdrücklich angelegt (2026-11-02).

## Entscheidungen (2026-11-02, Nutzer)

D-1 bis D-8 hat der Nutzer wie vorgeschlagen freigegeben („Ja“).

| ID | Frage | Entscheidung | Grund | Nicht gewählt |
|---|---|---|---|---|
| **D-1** | Rahmen | **Voller Milestone** wie MILE-005: drei Chargen, Epic, Stories, Tasks, OpenSpec-Change | neue Prüfsemantik in P1 und LIB | schlanker Milestone |
| **D-2** | Gateway-Umfang | **Exklusiv (XOR) und parallel (AND)**, jeweils Split und Join | BPMN-01/02; WCP-2/3/4/5 | inklusiv (OR), ereignisbasiert, komplex (später) |
| **D-3** | Profilschnitt | **Eigenes Profil P1.13** mit `binding-context/9` (Erweiterung von `/8`): `control_flow` mit Gateways, Flüssen, Bedingungsreihenfolge und Default. P1 prüft Wohlgeformtheit und Flussbindung der Spur-Aussagen; `/8` bleibt unverändert | gleicher Weg wie P1.12; eingefrorene Schichten bleiben byte-gleich | Erweiterung von P1.12 |
| **D-4** | Ort der Spurprüfung | **LIB `analyze.trace-conformance/v1`**, rein deklarativ, mit typisiertem Ergebnis, Orakel vor Evaluator; der Cube prüft nur die Deklaration | gleiche Arbeitsteilung wie `analyze.population/v1` (MILE-005 D-6) | Spurprüfung im P1-Validator |
| **D-5** | Bedingungen | **Nicht auswerten.** Trägt die Spur ausgewertete Bedingungsergebnisse, prüft LIB „erste wahre Bedingung in Reihenfolge, Default nur ohne wahre“; fehlen sie, bleibt diese Regel UNRESOLVED | §13.4.2 prüfbar, ohne Engine zu werden | Bedingungsausdrücke auswerten |
| **D-6** | Status | **FAIL** bei zwei Pfaden für eine Aktivierung, Join ohne alle Eingänge oder Token aus fremder Instanz; **UNRESOLVED** bei fehlender Spur-Abdeckung (P1.12) oder fehlenden Bedingungsergebnissen; überzählige Token werden gezählt, nicht als FAIL gewertet | gleiche Statuslogik wie P1.10.1/P1.12; §13.4.1 lässt Überschuss liegen | Überschuss als FAIL; Instanzabschluss prüfen (später) |
| **D-7** | Auslieferung | **Lokal** (G4 `cube_validate` mit `/9`, Discovery, LIB); G5 und Darstellung (Join-Status je Eingang, genommener Pfad) später mit VR-12 | wie MILE-005 D-5; Darstellung gehört zur Instanzsicht | G5 und Printer im selben Milestone |
| **D-8** | Prüffälle | BPMN-01, -02, -03 plus Varianten (XOR zwei Pfade, kein Pfad, Default trotz wahrer Bedingung, Reihenfolge, Join mit fehlendem Eingang, fremder Token, Überschuss), **Erwartung vor der Spezifikation**, Baseline mit dem unveränderten Runner, Wiederholung über lokales MCP | gleicher Nachweisweg wie MILE-005 | nur neue Fälle ohne Baseline |

## Drei Chargen

| Mile | Ergebnis | Abschlusskriterium | Aufgaben |
|---|---|---|---|
| **MILE-008-A — Prüffälle und Spezifikation** | Prüffälle mit Erwartung „heute“ und „nach Umsetzung“, Baseline-Lauf; Abnahmespezifikation P1.13 und Vertrag `analyze.trace-conformance/v1` mit Detailfragen | Erwartungen vor der Spezifikation committet; Entscheidungen aufgelöst | TASK-048, TASK-049 |
| **MILE-008-B — Profil und LIB** | P1.13 (`binding-context/9`): Schema, Diagnosen, Orakel vor Code, Vektoren, Tests; LIB-Eintrag mit Orakel, Fällen, Evaluator | Orakel vor Code; alle Vektoren und Fälle wie erwartet; P0/P1.1–P1.12 unverändert; `verify.py` grün | TASK-050, TASK-051 |
| **MILE-008-C — Adapter und Wiederholung** | `/9` im lokalen `cube_validate` mit Discovery; Wiederholung der BPMN-Fälle über lokales MCP mit vorab erwartetem Ergebnis; Abschluss | BPMN-01/02 ausführbar mit neuem, vorab erwartetem Ergebnis; Abschlussprüfung `all_ok` | TASK-052 |

## Epics, Stories und Aufwand

[EPIC-008](../03-Epics/EPIC-008-control-flow.md). US-026–027, TASK-048–052.

**Aufwand: 4–5,5 PT** (Lernbilanz: 4,75 PT Mitte), ohne Zeit des Nutzers.

| Charge | Aufwand |
|---|---|
| A | 0,75–1 PT |
| B | 2,5–3,25 PT |
| C | 0,75–1,25 PT |

## Nicht Teil von MILE-008

- Inklusive, ereignisbasierte und komplexe Gateways; Bedingungsauswertung; Instanzabschluss; Kompensation und Fehlerereignisse.
- Darstellung (VR-12, V-10, V-11): folgt als eigener Milestone.
- G5 und Host-Abnahme für `/9`.
- Reale Engine-Logs (Korrelation, Zeitstempel).

## Nachverfolgung

[OpenSpec-Change](../../openspec/changes/check-control-flow/proposal.md) · [Aufgabenstatus](../../openspec/changes/check-control-flow/tasks.md) · [Abdeckung](../../openspec/changes/check-control-flow/TRACEABILITY.md). TASK-048: [27 Prüffälle](../09-Research/control-flow/CHECK-CASES.md) vor der Spezifikation (`aefe6aa`); Baseline-Lauf und Probe bestätigen 27/27 Erwartungen für heute ([Abgleich](../10-Evidence/MILE-008/task048-baseline-check.json)). TASK-049: [Spezifikation P1.13](../../P1/control-flow-profile-v1/P1_13_ACCEPTANCE_SPEC.md), Entwurf `ff31bd5`, Q-1–Q-10 nach Vorschlag (Flüsse und Gateways als Referenten, `at_gateway`, `control_flow_role`, Bedingungsergebnisse nur in LIB, Abdeckung aus P1.12). Charge A abgeschlossen. TASK-050 (P1.13, KF 9/9) und TASK-051 (LIB `analyze.trace-conformance/v1`, 18/18) extern umgesetzt und in TASK-052 [geprüft](../10-Evidence/MILE-008/TASK-052-REVIEW.md): bestanden, sechs Befunde ohne Blocker. Charge B abgeschlossen.
