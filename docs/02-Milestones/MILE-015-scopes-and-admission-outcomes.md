# MILE-015 — Eingebettete X-Scopes und Ausgänge der Admission (P1)

Status: geplant (Entwurf) · Stand: 2026-11-05 · Voraussetzung: MILE-014 · Folge-Mile: [MILE-016](MILE-016-landscape-and-batch-views.md)

## Anlass

lunados.explorer bindet seit E8 X-Referenten nach P1.6 (Abschnitt `x_bindings` im Funktionsblatt, Export als Instanzprofil mit Slots). Die Instanzprüfung im Paar-Scope trägt: F05 A1d ist PASS, F03a A4 und A29 melden die im Code belegten Lücken (C-ADM-1, fehlende Quelle der Authority). Drei Befunde lassen sich nur in P1 lösen. Sie sind hier gesammelt, damit der Cube in einem Schritt angepasst wird und nicht nach jedem Fall.

## Backlog

| ID | Befund (Explorer) | Vorschlag | Abnahme |
|---|---|---|---|
| **B1** | Eine gedruckte Relation `gated-by(core, admission)` liegt im Blatt-Scope, die Admission in ihrem Policy-Scope. P1 kennt je Kontext genau einen Prüf-Scope und meldet nach der Bindung `P1_SCOPE_CONFLICT`. Das betrifft jedes Blatt mit gebundener Freigabe, ist also kein Randfall. | Ein Kontext deklariert eingebettete X-Scopes (`scope_nesting`: innerer X-Scope ↔ äußerer Kontext-Scope). Ein X-Endpunkt mit deklariert eingebettetem Scope gilt im äußeren Prüf-Scope; die P1.6-Prüfung bleibt im Paar-Scope. Undeklarierte Einbettung bleibt `P1_SCOPE_CONFLICT`. Neues Kontextformat, alte Formate unverändert. | F05 und F03a: Relation zur gebundenen Admission im Blatt-Scope ohne Scope-Konflikt; Gegenprobe ohne Deklaration weiter FAIL |
| **B2** | Die Authority einer Versionsfreigabe (F03a A29) gilt genau einer Revision. `resource_scope_ref` erlaubt nur Resource, Projekt- und Thread-Grenze; der Explorer musste auf den Freigabe-Store ausweichen. | P1.6-Referenz v2: `resource_scope_ref` zusätzlich für `Y:resource-object:revision` und `Y:resource-object:artifact`. Neue Referenzversion mit neuem SHA-Pin, v1 bleibt gültig. | F03a XB2 bindet die Revision (A28); der Explorer-Pin folgt |
| **B3** | P1.6 bindet je Instanz genau eine Entscheidung. Eine Migration beschreibt aber den zugelassenen und den abgelehnten Weg (F05: Card gültig oder Refusal in S4; F03a: approved oder `stale_version_reference`). Abgelehnte Wege bleiben heute ungebunden. | Eine Admission darf als Paar von Instanzen mit gemeinsamer Anfrage deklariert werden (je Ausgang eine, `refused` mit `refusal_ref`). Der Plan verweist auf das Paar, nicht auf einen Ausgang. Ob das ein neues Feld oder eine Gruppierung ist, entscheidet die Spezifikation. | F05 mit beiden Ausgängen gebunden; C-ADM-1/2 je Ausgang geprüft |

## Rahmenbedingungen

- Additiv: neue Kontext- bzw. Referenzversion; alle bestehenden P1-Fixtures und Oracles unverändert grün.
- Goldsatz: die fünf ausgearbeiteten Fälle in lunados.explorer (F01, F02, F03a, F04a, F05) drucken danach weiter mit P1 PASS; jede Abweichung wird als Digest sichtbar.
- Keine Änderung am Printer in dieser Mile.
- G5 als eigener Schritt am Ende (wie R8).

## Entscheidungen (2026-11-05, Nutzer)

| ID | Frage | Entscheidung |
|---|---|---|
| **D-1** | Backlog vor Änderungen sammeln | Ja; P1-Themen hier, Printer-Themen in MILE-016 |
| **D-2** | Vorgehen | Je Thema eine Task, als Mile aufgehängt |

## Tasks und Aufwand (Schätzung)

| Task | Aufwand |
|---|---|
| B1 — eingebettete X-Scopes (Spezifikation, Kontextformat, Prüffälle) | 0,5–1 PT |
| B2 — P1.6-Referenz v2 (Ressourcenbereich) | 0,25 PT |
| B3 — Ausgänge einer Admission (Spezifikation zuerst) | 0,5–1 PT |

## Offene Fragen

- B1: Reicht eine Ebene der Einbettung (Kontext ⊃ X-Scope), oder braucht es Ketten (Policy ⊃ Event)?
- B3: Gehören die Ausgänge in P1.6 (Instanz) oder in P1.13 (Kontrollfluss, exklusives Gateway)?

## Nicht Teil von MILE-015

- Darstellung der Instanzkette und Landscape View (MILE-016).
- Bindungen weiterer Freigaben in den Explorer-Fällen (F01 A11, F04a A7, F03a A13/A20 warten auf das Zielbild).
