# MILE-009 — Instanzsicht: Pfad und Join je Instanz zeigen

Status: in_progress · Stand: 2026-11-02 · Voraussetzung: MILE-008 ([Abschluss](../10-Evidence/MILE-008/C-RESULT.md))

## Ergebnis

VR-12 aus der [Darstellungsübergabe](../09-Research/visual-check/HANDOVER.md) mit V-10 und V-11 aus der [Lückenbilanz](../09-Research/grammar-sampling/GAP-LEDGER.md). Eine neue Sicht zeigt für deklarierte Prozessspuren:

1. **Instanz als Rahmen:** jede Instanz als benannter, durchgezogener Rahmen; ein Token aus einer fremden Instanz ist als „nicht Teil“ dieser Aussage und als Regelverstoß benannt (V-12, Mockup [M-12B](../09-Research/visual-check/mockups/M-12B.svg)).
2. **Genommener Pfad:** je Aktivierung eines exklusiven Gateways der genommene und die nicht genommenen Pfade; zwei Pfade für eine Aktivierung als Regelverstoß (V-10).
3. **Join je Eingang:** die Eingangsliste eines parallelen Joins mit Status je Eingang, „wartet“ getrennt von „unvollständig“ (V-11).

Das Urteil kommt aus lunados.lib `analyze.trace-conformance/v1` (MILE-008); die Sicht zeichnet es, sie prüft nicht selbst.

Heute: Keine Sicht gruppiert nach Prozessinstanz; `cube.sequence` zeigt Alternativen nur auf Modellebene und hat kein `par` ([Inventur](../09-Research/visual-check/INVENTORY.md), V-10 teilweise, V-11 und V-12 Lücke). Das Ergebnis von MILE-008 ist nur als JSON lesbar.

## Rahmenbedingungen

- P0, P1 (einschließlich P1.13), VP-07, VP-08, VP-09, VP-10 (alle Profile) und die lunados.lib-Einträge bleiben byte-gleich; P1.7 bleibt reserviert. Neue Darstellung als eigenes Paket.
- Ablauf wie MILE-007: Spezifikation mit Entscheidungen → Entscheidungen auflösen (eigener Docs-Commit) → Prüffälle, Orakel und Pins vor Code → Printer, Vektoren, Tests → G6 → kurze Sichtprüfung → Abschluss.
- Schlank nach Absprache (2026-11-02): kein bestätigter Prozess-Anwendungsfall genannt; Prüffälle nur aus BPMN-01/02/03 und den MILE-008-Fällen.
- Keine Kundendaten in Repo, Fixtures, Fällen oder auf cube.lunados.net.

## Entscheidungen (2026-11-02, Nutzer)

D-1 bis D-8 hat der Nutzer wie vorgeschlagen freigegeben („Ja“).

| ID | Frage | Entscheidung | Grund | Nicht gewählt |
|---|---|---|---|---|
| **D-1** | Rahmen | **Schlanke Mile wie MILE-007:** drei Chargen, Epic, zwei Stories, fünf Tasks, OpenSpec-Change | gleiche Nachverfolgung; reine Darstellung ohne neue Prüfsemantik | voller Milestone mit Baseline-Wiederholung; nur Spezifikation |
| **D-2** | Ort | **Neues Paket VP-11** `P2/visual-printer-instances-v1` mit der Sicht `cube.instances` | keine vorhandene Sicht trägt Instanz und Join; vorhandene Printer bleiben byte-gleich | `par` in `cube.sequence` (VP-08); neues Profil in `vpcells` (Matrix passt nicht zu Pfad und Join) |
| **D-3** | Eingabe | Ein `binding-context/9` (Gateways, Flüsse, Spur-Aussagen mit Instanz) und **optional das LIB-Ergebnis** `aiaeao.trace-conformance-result/v1` als Datensatz mit `library_ref`. Der Printer prüft Format, Bezug und Eingabe-Hash und **rechnet nichts nach**; die Gültigkeit des Kontexts kommt aus P1.13 (`cube_validate`) | gleiche Arbeitsteilung wie der Verdichtungsdatensatz in MILE-007 (Q-10) | Spurprüfung im Printer; Kontext ohne P1.13-Bezug |
| **D-4** | Inhalt | Nach VR-12 und M-12B: **Instanzrahmen** ⬠ benannt und durchgezogen; je Gateway-Aktivierung **„genommen“ / „nicht genommen“**, zwei Pfade als **„Regelverstoß“** mit Schraffurmarke; **Join-Aussage mit Eingangsliste**, Status je Eingang („angekommen“, „fehlt“, „aus Instanz … · nicht Teil“); Modellfluss im **getrennten Feld** „Prozessmodell · keine Spur“ | M-12B war in der Agenten-Vorprüfung blind richtig; M-12A legte eine Ausführung nahe | BPMN-Notation (kein VG-Anker); Tokensimulation |
| **D-5** | Ohne Urteil | Ohne LIB-Ergebnis wird die Spur gezeichnet, Gateways und Joins tragen **„nicht geprüft“**; UNRESOLVED aus LIB als **„nicht prüfbar“ mit Grund**. Ein Schritt gilt nur als gestartet, wenn ein Token ihn belegt | „unbekannt“ nie als „leer“ oder „verletzt“ (Lernbilanz, Leitfrage 7a) | Urteil aus der Zeichnung ableiten |
| **D-6** | Unterscheidung | **Ohne Farbe:** Text, Linienart aus dem VP-07-Satz und Schraffur nach VP-07 PV-5; nur vorhandene VG-Anker; Ledger im SVG und Bericht wie VP-10; deterministisch | gleiche Invarianten wie VP-10 (`STATES_DIFFER_WITHOUT_COLOUR`) | Farbcodierung; neue Anker |
| **D-7** | Auslieferung | **Lokal:** CLI und G6 (`cube_plan_source`, `cube_plan_views`, `cube_plan_check`) mit neuem Printer `vpinstances` | wie MILE-007 D-7 | G5 und `/9` remote im selben Milestone (später mit „Plansichten remote“) |
| **D-8** | Prüffälle und Abnahme | Fälle aus BPMN-01/02/03 und den MILE-008-Fällen (u. a. CF-12, CF-21–CF-23, CF-29), jeweils mit und ohne LIB-Ergebnis; **Orakel** (erwartete Texte, Zustände und Ledger-Einträge je Fall) **und Pins** der vorhandenen Printer **vor Code**; **kurze angeleitete Sichtprüfung** durch den Nutzer, höchstens fünf ja/nein-Punkte | Nachweisweg von MILE-007; Sichtprüfung kurz nach Vorgabe des Nutzers | Lesbarkeitstest mit vielen Personen |

## Drei Chargen

| Mile | Ergebnis | Abschlusskriterium | Aufgaben |
|---|---|---|---|
| **MILE-009-A — Spezifikation und Prüffälle** | Abnahmespezifikation VP-11 mit Detailfragen; Prüffälle, Orakel und Pins | Entscheidungen aufgelöst; Orakel und Pins vor Code committet | TASK-053, TASK-054 |
| **MILE-009-B — Printer** | VP-11 `cube.instances`: Eingabeprüfung, Zeichnung, Bericht, Ledger, CLI, Vektoren, Tests | alle Vektoren wie Orakel; vorhandene Printer byte-gleich | TASK-055 |
| **MILE-009-C — G6 und Abnahme** | `vpinstances` in G6, gleich der CLI; kurze Sichtprüfung; Abschluss | G6 = CLI; Sichtprüfung beantwortet; Abschlussprüfung `all_ok` | TASK-056, TASK-057 |

## Epics, Stories und Aufwand

[EPIC-009](../03-Epics/EPIC-009-instance-view.md). US-028–029, TASK-053–057.

**Aufwand: 2–3,25 PT** (Übergabe: 1–2 PT nur für P2), ohne Zeit des Nutzers.

| Charge | Aufwand |
|---|---|
| A | 0,5–1 PT |
| B | 1–1,5 PT |
| C | 0,5–0,75 PT |

## Nicht Teil von MILE-009

- G5 und `/9` remote; Plansichten remote.
- Änderungen an P1.13 oder `analyze.trace-conformance/v1`; inklusive und ereignisbasierte Gateways, Instanzabschluss (Grenzen von MILE-008).
- Zeitachse, Engine-Logs, Animation.
- VR-01 (Herkunftslinie in `cube.flow`); Menschentest mit vielen Personen.

## Nachverfolgung

[OpenSpec-Change](../../openspec/changes/show-instance-view/proposal.md) · [Aufgabenstatus](../../openspec/changes/show-instance-view/tasks.md) · [Abdeckung](../../openspec/changes/show-instance-view/TRACEABILITY.md). TASK-053: [Spezifikation VP-11](../../P2/visual-printer-instances-v1/VP11_ACCEPTANCE_SPEC.md), Entwurf `0b5b114`, Q-1–Q-10 nach Vorschlag (Spur als Aussagenmenge zum `/9`-Kontext, LIB-Ergebnis als Datensatz mit `library_ref`, Aufrufeingaben gegen Kontext und Spur geprüft, Rahmen untereinander, fremde Token nur am fehlenden Join-Eingang, `records` in G6).
