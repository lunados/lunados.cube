# MILE-015 — Scope-Ketten und Ausgänge der Admission (P1)

Status: umgesetzt (lokal, G4) – [Nachweis](../10-Evidence/MILE-015/README.md) · Stand: 2026-11-05 · Voraussetzung: MILE-014 · Folge-Mile: [MILE-016](MILE-016-axis-pair-views.md)

## Anlass

lunados.explorer bindet seit E8 X-Referenten nach P1.6 (Abschnitt `x_bindings` im Funktionsblatt, Export als Instanzprofil mit Slots). Die Instanzprüfung im Paar-Scope trägt: F05 A1d ist PASS, F03a A4 und A29 melden die im Code belegten Lücken (C-ADM-1, fehlende Quelle der Authority). Drei Befunde lassen sich nur in P1 lösen. Sie sind hier gesammelt, damit der Cube in einem Schritt angepasst wird und nicht nach jedem Fall.

## Backlog

| ID | Befund (Explorer) | Vorschlag | Abnahme |
|---|---|---|---|
| **B1** | Eine gedruckte Relation `gated-by(core, admission)` liegt im Blatt-Scope, die Admission in ihrem Policy-Scope. P1 kennt je Kontext genau einen Prüf-Scope und meldet nach der Bindung `P1_SCOPE_CONFLICT`. Das betrifft jedes Blatt mit gebundener Freigabe. Eine Ebene reicht nicht: Policies erben und schränken ein (Morphologie 01.3, X × Z, Zeile Γ: „Thread erbt Projekt-Defaults, darf einschränken“), also Organisation ⊃ Projekt ⊃ Thread ⊃ Anfrage. | **Deklarierte Scope-Ketten.** Ein Kontext deklariert, welcher X-Scope in welchem liegt (`scope_nesting`, Paare innen → außen). P1 prüft nur die Struktur: jede Kette ist azyklisch, endet im Kontext-Scope, nennt nur deklarierte X-Scopes. Ein X-Endpunkt, dessen Scope über eine Kette im Prüf-Scope liegt, gilt dort; die P1.6-Prüfung bleibt im Paar-Scope. Ob ein innerer Scope tatsächlich enger ist, prüft P1 nicht (deklariert, ohne Prüfung). Undeklarierte Einbettung bleibt `P1_SCOPE_CONFLICT`. Neues Kontextformat (`binding-context/11`), alle älteren unverändert. | F05 und F03a: Relation zur gebundenen Admission ohne Scope-Konflikt; Gegenproben: Zyklus, Kette ohne Ende im Kontext-Scope, undeklarierte Einbettung → FAIL bzw. Konflikt |
| **B2** | Die Authority einer Versionsfreigabe (F03a A29) gilt genau einer Revision. `resource_scope_ref` erlaubt nur Resource, Projekt- und Thread-Grenze; der Explorer musste auf den Freigabe-Store ausweichen. | P1.6-Referenz v2: `resource_scope_ref` zusätzlich für `Y:resource-object:revision` und `Y:resource-object:artifact`. Neue Referenzversion mit neuem SHA-Pin, v1 bleibt gültig. | F03a XB2 bindet die Revision (A28); der Explorer-Pin folgt |
| **B3** | P1.6 bindet je Instanz genau eine Entscheidung; eine Migration beschreibt aber den zugelassenen und den abgelehnten Weg (F05: Card gültig oder Refusal in S4; F03a: approved oder `stale_version_reference`). | **Ohne neues Feld:** Jeder Ausgang ist eine eigene P1.6-Instanz (`admitted` mit Authority, `refused` mit Refusal); eine Admission wird je konkreter Anfrage entschieden (Morphologie 01.3, Z × T). Die Verzweigung ist ein exklusives Gateway nach P1.13, das `binding-context/10` schon trägt (`control_flow.gateways`, Ziele, `condition_ref`, Default). Neu ist nur eine Regel, die beides verbindet: Die Ziele eines Gateways sind Admissions mit derselben Anfrage (`request_ref`) und verschiedenen Entscheidungen. | F05 mit beiden Ausgängen gebunden und als Gateway deklariert; C-ADM-1/2 je Ausgang; Gegenprobe: zwei Ausgänge mit verschiedener Anfrage → FAIL |

## Rahmenbedingungen

- Additiv: neue Kontext- bzw. Referenzversion; alle bestehenden P1-Fixtures und Oracles unverändert grün.
- X-Scopes und Z-Platzierung bleiben getrennt: Schichten einer Landschaft (*hosted-by*) sind keine Scope-Ketten.
- Goldsatz: die fünf ausgearbeiteten Fälle in lunados.explorer (F01, F02, F03a, F04a, F05) drucken danach weiter mit P1 PASS; jede Abweichung wird als Digest sichtbar.
- Keine Änderung am Printer in dieser Mile.
- G5 als eigener Schritt am Ende (wie R8).

## Entscheidungen (2026-11-05, Nutzer)

| ID | Frage | Entscheidung |
|---|---|---|
| **D-1** | Backlog vor Änderungen sammeln | Ja; P1-Themen hier, Printer-Themen in MILE-016 |
| **D-2** | Vorgehen | Je Thema eine Task, als Mile aufgehängt |
| **D-3** | Einbettung | Ketten statt einer Ebene |
| **D-4** | „Darf nur einschränken“ | Nur deklariert und strukturell geprüft (azyklisch, endet im Kontext-Scope); kein Vergleich von Policy-Inhalten |
| **D-5** | Ausgänge der Admission | Je Ausgang eine P1.6-Instanz, Verzweigung als P1.13-Gateway; kein neues P1.6-Feld |

## Tasks und Aufwand (Schätzung)

| Task | Aufwand |
|---|---|
| B1 — Scope-Ketten (Spezifikation, `/11`, Prüffälle) | 0,75–1 PT |
| B2 — P1.6-Referenz v2 (Ressourcenbereich) | 0,25 PT |
| B3 — Verbindungsregel Gateway ↔ Admissions | 0,25–0,5 PT |

Umgesetzt in einer Task: [TASK-076](../05-Tasks/TASK-076-p115-scope-nesting.md) (`P1/scope-nesting-profile-v1/`). G5: [TASK-077](../05-Tasks/TASK-077-g5-r9.md) (Core `0.9.2-proof`, mit VP-07.8 aus MILE-014).

## Detailfragen (in der Spezifikation entschieden)

- B1: Verschiedene Scope-Arten in einer Kette sind erlaubt; geprüft wird nur die Struktur (Q-2). Ein Scope hat genau einen äußeren (Q-1).
- B3: Die Plan-Abhängigkeit `gated-by` zeigt auf den zugelassenen Ausgang; das Gateway nennt die übrigen (Q-4).

## Nicht Teil von MILE-015

- Sichten (MILE-016).
- Bindungen weiterer Freigaben in den Explorer-Fällen (F01 A11, F04a A7, F03a A13/A20 warten auf das Zielbild).
