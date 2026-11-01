# MILE-005 — Vollständigkeit und Instanzbindung prüfbar machen

Status: in_progress · Stand: 2026-11-01 · Voraussetzung: MILE-004 (Lernbilanz) · Entscheidungen getroffen, **noch nicht umgesetzt**

## Ergebnis

Cube kann für Architektursichten und Prozessspuren drei Dinge, die heute fehlen:

1. **Vollständigkeit erklären und prüfen (G-01):** „unbekannt“, „geprüft leer“ und „verletzt“ sind unterscheidbar; Zählregeln über Aussagenmengen liefern bei unvollständiger Erklärung UNRESOLVED statt FAIL.
2. **Instanzen typisiert binden (G-08):** Zugehörigkeit einer Aussage oder eines Tokens zu einer Prozessinstanz ist typisiert; ein Join über zwei Instanzen wird auch im gemeinsamen Scope erkannt.
3. **Vier Zellzustände darstellen (VR-05):** eine Matrixsicht zeigt markiert, geprüft leer (nur für den erklärten Umfang), unbekannt und ausgeblendet farbfrei unterscheidbar — als eigener Printer-Stand, nicht als Änderung an VP-09.

Herkunft: Rang 1 (G-01 → VR-05) und Rang 2 (G-08) der [Lernbilanz](../09-Research/learning-balance/LERNBILANZ.md); Auswahlregel des [Bewertungsrahmens](../09-Research/learning-balance/SCORING-FRAME.md).

## Rahmenbedingungen

- P0, P1.1–P1.9 und P2 bleiben byte-gleich; P1.7 bleibt reserviert. Neue Fähigkeiten entstehen als eigenes P1-Profil und als eigener Printer-Stand.
- Profil-Ablauf wie P1.9: Abnahmespezifikation mit Entscheidungen → Entscheidungen auflösen (eigener Docs-Commit) → Implementierung (Schema, Diagnosen, Regelabdeckung, Orakel vor Code, materialisierte Vektoren, Tests, Golden) → Adapter → Host-Abnahme.
- Keine Kundendaten in Repo, Fixtures oder Vektoren.

## Entscheidungen (2026-11-01, Nutzer; TASK-032 vorgezogen)

Vom Nutzer nach Erörterung entschieden; alle Empfehlungen übernommen. Abgelehnte Optionen bleiben zur Nachvollziehbarkeit genannt.

| ID | Frage | Entscheidung | Grund | Nicht gewählt |
|---|---|---|---|---|
| **D-1** (O-1) | Profilschnitt und Nummer | **Ein gemeinsames Profil** (Arbeitstitel P1.12, `binding-context/8`), zwei getrennte Abschnitte: Vollständigkeit, Instanzbindung | höhere Kontexte bauen ohnehin aufeinander auf; ein Durchlauf und eine Abnahme statt zwei | zwei Profile (Instanzbindung vorab) |
| **D-2** (O-2) | Umfang einer Vollständigkeitserklärung | **Referent × Relationstyp × Richtung** als Grundeinheit; zusätzlich **Erklärung je Paar** für einzelne geprüfte Zellen; **keine Erklärung je Sicht** — der Umfang einer Sicht ergibt sich aus den Einzelerklärungen | schließt Überbehauptungen wie in M-05A/B konstruktionsbedingt aus; Paar-Ebene deckt DSM-03 | nur je Paar; je Sicht |
| **D-3** (O-3) | Status bei unvollständiger Erklärung | **UNRESOLVED** wie P1.10.1 D-2, mit eigenem Diagnosecode (Arbeitstitel `P1_COVERAGE_UNDECLARED`), der den fehlenden Umfang nennt | keine Änderung der P1-Statusmenge; „unbekannt“ maschinell unterscheidbar | eigener Status |
| **D-4** (O-4) | Form der Instanzbindung | **Typisierte `instance_ref`** (optional) an Referenten bzw. Spur-Aussagen; Prädikatvertrag mit Eigenschaft „gleiche Instanz verlangt“ (Arbeitstitel `requires_same_instance`) | erkennt den instanzübergreifenden Join auch im gemeinsamen Scope (BPMN-03 shared) | nur Konvention „Instanz = Scope“ |
| **D-5** (O-5) | Auslieferung | **Lokal (G4/G6)** in MILE-005; **G5 mit Host-Abnahme** als eigener Folgeschritt, sobald das Profil stabil ist | alle bisherigen Nachweise liefen lokal; spart 0,5–1 PT | G5 sofort |
| **D-6** (O-6) | Ort der Populationsprüfung | **Arbeitsteilung:** Profil erklärt Umfang und Zählregeln, P1-Validator prüft Wohlgeformtheit und Statusabbildung; **LIB-Eintrag** zählt rein über eine Aussagenmenge, mit Orakel und typisiertem Ergebnisschema (erster Anwendungsfall für LR-1) | `cube_validate` prüft Einzelausdrücke; Zählen braucht Mengen; keine Erweiterung von P1 auf Mengen | nur Erklärung, Zählung später |

**Detailfragen der Spezifikation (2026-11-01, Nutzer, alle nach Vorschlag):** Q-1 `instance_ref` zeigt auf einen deklarierten Referenten vom Konzept `Y:identified-object:bounded-execution`; Q-2 Abdeckungserklärungen dürfen optional eine `instance_ref` tragen; Q-3 Codes `P1_COVERAGE_UNDECLARED`, `P1_INSTANCE_MISMATCH`, `P1_INSTANCE_UNDECLARED`; Q-4 unbekannte Referenten/Prädikate → `P1_BINDING_CONTEXT_REQUIRED`, Schemafehler → `P1_MCP_CONFIG_INVALID`; Q-5 `P1.12/coverage-instance-profile-v1`, `context-v8.schema.json`; Q-6 lokale Discovery listet `binding-context/8`.

Folge für den Ablauf: TASK-031 schreibt die Abnahmespezifikation mit diesen Entscheidungen als „decided“; TASK-034 (LIB) entfällt nicht. Der Aufwandsrahmen bleibt bei 5,25–7,25 PT (G5 ausgeklammert).

## Drei Chargen

| Mile | Ergebnis | Abschlusskriterium | Aufgaben |
|---|---|---|---|
| **MILE-005-A — Prüffälle und Spezifikation** | ausführbare Prüffälle für die bisher nicht ausgeführten Fälle; Abnahmespezifikation mit aufgelösten Entscheidungen | Prüffälle mit Erwartung vor Code committet; Spezifikation und Entscheidungs-Commit vorhanden | TASK-030–032 |
| **MILE-005-B — Profil und LIB** | P1-Profil für Vollständigkeit und Instanzbindung; Populationsprüfung | Orakel vor Code; alle Vektoren und Prüffälle wie erwartet; P0/P1.1–P1.9 unverändert | TASK-033–034 |
| **MILE-005-C — Darstellung und Abnahme** | Printer-Stand mit vier Zellzuständen; Adapter; Wiederholung der MILE-002-Fälle | Printer-Abnahme nach Spezifikation; MILE-002-Fälle ARC-03, DSM-03, BPMN-03 mit neuem, vorab erwartetem Ergebnis | TASK-035–036 |

A geht B voraus (die Prüffälle aus TASK-030 sind die Orakel-Grundlage); C setzt B voraus.

## Risikominderung

Die Lernbilanz zeigt: Unter Unsicherheitsstrafe fällt G-01 zurück, weil seine Belege teils nicht ausgeführt wurden (NE). Deshalb beginnt MILE-005 mit **TASK-030**: Die NE-Fälle aus MILE-002 werden zu ausführbaren Prüffällen mit Erwartung vorab, bevor Spezifikation und Code entstehen.

## Epics, Stories und Aufwand

[EPIC-005](../03-Epics/EPIC-005-completeness-and-instances.md). US-018–020, TASK-030–036.

**Aufwand: 5,25–7,25 PT, rund 5–7 PT.**
- Die Quellen schätzen 5,0 PT (Mitte der Spannen: G-01 3, VR-05 1,25, G-08 0,75).
- Darin fehlen Spezifikation, Adapter und Abnahme.
- G5 mit Host-Abnahme ist nach D-5 ausgeklammert (sonst etwa +0,5–1 PT).

| Charge | Aufwand |
|---|---|
| A | 1–1,25 PT |
| B | 2,25–3,5 PT |
| C | 1,75–2,5 PT |

Nutzen sehr hoch (Rang 1 und 2 der Lernbilanz), Komplexität mittel–hoch.

## Nachverfolgung

[OpenSpec-Change](../../openspec/changes/declare-completeness-and-instances/proposal.md) · [Aufgabenstatus](../../openspec/changes/declare-completeness-and-instances/tasks.md) · [Abdeckung](../../openspec/changes/declare-completeness-and-instances/TRACEABILITY.md) · [Arbeitsordner](../09-Research/completeness-instances/README.md). TASK-030: [Prüffälle](../09-Research/completeness-instances/CHECK-CASES.md), [Baseline](../10-Evidence/MILE-005/task030-baseline-check.json). TASK-031: [Abnahmespezifikation P1.12](../../P1/coverage-instance-profile-v1/P1_12_ACCEPTANCE_SPEC.md); Detailfragen Q-1–Q-6 am 2026-11-01 nach Vorschlag entschieden. Charge A abgeschlossen.
