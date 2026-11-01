# MILE-005 — Vollständigkeit und Instanzbindung prüfbar machen

Status: planned · Stand: 2026-11-01 · Voraussetzung: MILE-004 (Lernbilanz) · **noch nicht umgesetzt**

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

## Offene Entscheidungen (vor TASK-032 vom Nutzer zu treffen)

| ID | Frage | Optionen (Beispiele, nicht vorweggenommen) |
|---|---|---|
| O-1 | Profilschnitt und Nummer | ein gemeinsames Profil (z. B. P1.12, binding-context/8) · zwei getrennte Profile |
| O-2 | Umfang einer Vollständigkeitserklärung | je Zelle/Paar · je Referent und Relationstyp · je Sicht (MILE-004: Zeilen-Vollständigkeit war eine Überbehauptung) |
| O-3 | Status bei unvollständiger Erklärung | UNRESOLVED wie P1.10.1 D-2 · eigener Status |
| O-4 | Form der Instanzbindung | Konvention „Instanz = Scope“ dokumentieren · typisierte `instance_ref` mit Regel „gleiche Instanz“ |
| O-5 | Auslieferung | nur lokaler MCP (G4/G6) · zusätzlich Remote G5 mit Host-Abnahme |
| O-6 | Ort der Populationsprüfung | im P1-Validator · als LIB-Eintrag · beides (Profil erklärt, LIB zählt) |

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
- O-5 (G5 mit Host-Abnahme) kann etwa +0,5–1 PT bedeuten.

| Charge | Aufwand |
|---|---|
| A | 1–1,25 PT |
| B | 2,25–3,5 PT |
| C | 1,75–2,5 PT |

Nutzen sehr hoch (Rang 1 und 2 der Lernbilanz), Komplexität mittel–hoch.

## Nachverfolgung

[OpenSpec-Change](../../openspec/changes/declare-completeness-and-instances/proposal.md) · [Aufgabenstatus](../../openspec/changes/declare-completeness-and-instances/tasks.md) · [Abdeckung](../../openspec/changes/declare-completeness-and-instances/TRACEABILITY.md).
