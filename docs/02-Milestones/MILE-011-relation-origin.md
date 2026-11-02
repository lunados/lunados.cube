# MILE-011 — Herkunft von Beziehungen deklarieren und zeigen

Status: in_progress · Stand: 2026-11-02 · Voraussetzung: MILE-007 ([Abschluss](../10-Evidence/MILE-007/C-RESULT.md)), MILE-010 ([Abschluss](../10-Evidence/MILE-010/C-RESULT.md))

## Ergebnis

Eine Beziehung trägt eine gebundene Herkunft, und jede Flusssicht zeigt sie, sodass eine verdichtete Übersicht nicht mehr als festgelegte Entscheidung gelesen werden kann (G-02 → VR-01; Rang 3 der [Lernbilanz](../09-Research/learning-balance/LERNBILANZ.md)):

1. **Herkunft prüfen (G-02):** Ein neues Profil P1.14 bindet den Parameter `origin` einer Relation an einen Vertrag. Werte: `declared`, `derived`, `unknown`. Fehlt die Herkunft, lautet das Ergebnis UNRESOLVED statt PASS. Eine abgeleitete Beziehung nennt ihre Grundlage.
2. **Herkunftslinie zeigen (VR-01):** `cube.flow` zeichnet die Linienart nach der gebundenen Herkunft, nicht nach dem Prädikat: durchgezogen deklariert, gestrichelt abgeleitet, gepunktet unbekannt. Die Herkunft steht immer zusätzlich als Text, die Pfeilspitze bleibt neutral (Mockup [M-01A](../09-Research/visual-check/mockups/M-01A.svg)).
3. **Auslieferung** lokal (CLI, G4, G6) und, nach D-6, im G5-Remote.

Heute: `rel("uses", Boundary[api], Boundary[db])` besteht P1 auch dann, wenn die Beziehung nur verdichtet ist ([C4-03](../09-Research/grammar-sampling/reports/C4-03.md)). Die in `relations.json` vorgesehene Form `origin=` endet mit `P1_PREDICATE_PROFILE_MISSING`. `provenance_status` gibt es nur für Referenten. `cube.flow` unterscheidet Linien nur nach Prädikat (VP-07 `edge_styles`) und liest nur Migrationspläne. Aussagenmengen ohne Plan zeigt bisher nur `cube.cells` (MILE-007).

## Rahmenbedingungen

- Neue Fähigkeiten als eigenes Profil: P0, P1.1–P1.13 (P1.7 bleibt reserviert), P2 einschließlich VP-07 0.7.0–0.7.5, VP-10 und VP-11 sowie die vorhandenen lunados.lib-Einträge bleiben byte-gleich.
- Ablauf wie MILE-005 und MILE-008: Spezifikation mit Entscheidungen → Entscheidungen auflösen (eigener Docs-Commit) → Prüffälle, Orakel und Pins vor Code → Profil → Printer → Auslieferung → Sichtprüfung → Abschluss.
- Der Cube berechnet keine Herkunft und keine Ableitung. Er prüft die deklarierte Bindung und zeigt sie. Ein Abgleich mit einem Fremdmodell (ist `api → db` dort ausdrücklich festgelegt?) ist eine Adapter- oder LIB-Aufgabe und nicht Teil dieser Mile.
- Keine Kundendaten in Repo, Prüfunterlagen oder auf cube.lunados.net; alle Fälle synthetisch.

## Entscheidungen (2026-11-02, Nutzer)

D-1 bis D-8 hat der Nutzer wie vorgeschlagen freigegeben („Ja“).

| ID | Frage | Entscheidung | Grund | Nicht gewählt |
|---|---|---|---|---|
| **D-1** | Rahmen | **Drei Chargen** wie MILE-008: A Spezifikation und Prüffälle, B Profil P1.14, C Printer, Auslieferung und Sichtprüfung; Epic, zwei Stories, sechs Tasks, OpenSpec-Change | Profil und Darstellung hängen voneinander ab, sind aber getrennt prüfbar | zwei Miles (Profil, dann Printer) |
| **D-2** | Ort der Herkunft | **Profil P1.14 mit `binding-context/10`**, opt-in: typisierter Relationsparameter `origin ∈ {declared, derived, unknown}`, gebunden über einen Parametervertrag je Prädikat. Fehlt `origin` in einem `/10`-Kontext → UNRESOLVED (`P1_ORIGIN_UNDECLARED`); ein Wert außerhalb der Menge → FAIL | `relations.json` sieht `origin` bereits vor; kein Morphologieeingriff (C4-03) | Pflicht-Qualifikator; Ableitungsprädikat je Beziehung (`uses.derived`) |
| **D-3** | Grundlage einer Ableitung | `derived` **verlangt eine Grundlage**: Verweis auf die Quellaussagen oder auf einen Datensatz von lunados.lib `project.aggregate-relations/v1` (MILE-007), gelesen, nie nachgerechnet. Ohne Grundlage → UNRESOLVED (`P1_ORIGIN_BASIS_MISSING`). `unknown` ist eine gültige, ehrliche Angabe | eine verdichtete Kante soll auf ihre Quellen zeigen (C4-02) | `derived` ohne Grundlage zulassen |
| **D-4** | Sicht | **`cube.flow` liest auch Aussagenmengen** (wie `cube.cells` seit 0.11.0): neues opt-in-Profil `P2-VP-MIGRATION/0.7.6` mit `statements` statt `plan_id`; Herkunft gilt für Plan-Abhängigkeiten und für Aussagen | die C4-Fälle sind Architekturaussagen, keine Migrationspläne | Herkunft nur in Migrationsplänen |
| **D-5** | Darstellung | **Linienart nach Herkunft (M-01A):** durchgezogen / gestrichelt / gepunktet, Herkunft immer als Text, neutrale Pfeilspitze, feste Legende. In diesem Modus tragen Prädikate keine Linienart, sie bleiben Beschriftung. Ohne gebundene Herkunft nie durchgezogen. Dazu PO-1: Kopfzeile „FIXTURE ASSERTIONS“ statt „declared“ | eine Unterscheidung je Linienart, farbfrei | Herkunft und Prädikat gleichzeitig als Linienart |
| **D-6** | Auslieferung | **Lokal und G5 in dieser Mile:** CLI, G4 (`/10`), G6; danach G5-Kern `0.9.0-proof` mit Erwartungen vor Code, Offline-Parität und Host-Abnahme wie MILE-010 | seit MILE-010 gilt: was lokal geht, geht remote; die Prüfskripte sind vorhanden | G5 als eigene Mile |
| **D-7** | Andere Hosts | **Nicht in MILE-011.** Ein Host-Vergleich (ChatGPT, Grok) wird eine eigene kleine Mile: Anmeldung (G5 nutzt einen festen Bearer-Token, kein OAuth), Größe der Antworten, Zeitlimits. Das CPU-Budget hängt am Worker, nicht am Host | anderes Thema, eigene Risiken (Anmeldung) | Host-Vergleich als vierte Charge |
| **D-8** | Abnahme | Orakel, Prüffälle und Pins vor Code: C4-02 und C4-03 als `/10`-Fälle mit Gegenproben, die MILE-007-Verdichtung als `derived` mit Grundlage, VP-07 0.7.0–0.7.5 byte-gleich, P1.14 mit Regelabdeckung, G4 = G6 = CLI; **kurze angeleitete Sichtprüfung** durch den Nutzer | Muster der bisherigen Miles; keine Lesbarkeitsstudie | Lesbarkeitstest mit mehreren Personen |

## Drei Chargen

| Mile | Ergebnis | Abschlusskriterium | Aufgaben |
|---|---|---|---|
| **MILE-011-A — Spezifikation und Prüffälle** | Spezifikation P1.14 und VP-07.6 mit Detailfragen; Prüffälle, unabhängiges Orakel, Pins der vorhandenen Profile | Entscheidungen aufgelöst; Prüffälle, Orakel und Pins vor Code committet | TASK-063, TASK-064 |
| **MILE-011-B — Profil P1.14** | `binding-context/10` mit `origin` und Grundlage; Diagnosen; lokaler Adapter G4; Discovery | Prüffälle wie das Orakel; P1.1–P1.13 unverändert | TASK-065 |
| **MILE-011-C — Herkunftslinie und Auslieferung** | VP-07 0.7.6 (`cube.flow` mit Herkunftslinie und Aussagenmengen), G6; G5 `0.9.0-proof` mit Host-Abnahme; Sichtprüfung; Abschluss | Vektoren wie das Orakel, 0.7.0–0.7.5 byte-gleich, G5 = lokal, Sichtprüfung beantwortet, Abschlussprüfung `all_ok` | TASK-066, TASK-067, TASK-068 |

## Epics, Stories und Aufwand

[EPIC-011](../03-Epics/EPIC-011-relation-origin.md). US-032–033, TASK-063–068.

**Aufwand: 3–4,5 PT**, ohne die Zeit des Nutzers für Bereitstellung und Sichtprüfung. Die Lernbilanz schätzte G-02 → VR-01 auf 2,25 PT; dazu kommen hier `cube.flow` für Aussagenmengen (D-4) und G5 (D-6).

| Charge | Aufwand |
|---|---|
| A | 0,5–0,75 PT |
| B | 1–1,5 PT |
| C | 1,5–2,25 PT |

## Risiken

- Ein Profil verhindert keine falsche Angabe `origin=declared`. Dafür bräuchte es den Quellenabgleich mit dem Fremdmodell (außerhalb dieser Mile).
- Gestrichelt gegen gepunktet ist die schwächste Unterscheidung (offene Frage 3 der [Mockups](../09-Research/visual-check/MOCKUPS.md)). Deshalb steht die Herkunft immer auch als Text, und die Sichtprüfung fragt danach.
- Die CPU-Grenze des Workers (MILE-010, [Spezifikation §10](../../P3/remote-mcp-g5/G5_R5_ACCEPTANCE_SPEC.md)) gilt auch für das neue Profil. Große `cube.flow`-Prüfungen können remote mit `G5_CORE_UNAVAILABLE` enden.

## Nicht Teil von MILE-011

- Quellenabgleich mit Fremdmodellen (Structurizr-Workspace lesen, explizite und implizite Beziehungen trennen).
- Host-Vergleich mit ChatGPT oder Grok (D-7); Produktionsfreigabe von G5 (OAuth, Rate-Limits, CPU-Budget).
- Herkunftslinie in `cube.sequence`, `cube.axes` und `cube.instances`.

## Nachverfolgung

[OpenSpec-Change](../../openspec/changes/declare-relation-origin/proposal.md) · [Aufgabenstatus](../../openspec/changes/declare-relation-origin/tasks.md) · [Abdeckung](../../openspec/changes/declare-relation-origin/TRACEABILITY.md). TASK-063: Spezifikationen [P1.14](../../P1/relation-origin-profile-v1/P1_14_ACCEPTANCE_SPEC.md) und [VP-07.6](../../P2/visual-printer-migration-v1/VP07_6_ACCEPTANCE_SPEC.md), Entwurf `64cf9c0`, Q nach Vorschlag. TASK-064: Orakel, Vektoren HO-01–HO-12 und OL-01–OL-12, Pins 0.7.5 vor Code. Charge A abgeschlossen. TASK-065: P1.14 und lokaler G4-Adapter mit `/10`, Orakel und Regression geprüft; Charge B abgeschlossen. Charge C offen.
