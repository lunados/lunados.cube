# BPMN-01 — XOR-Entscheidung in einer abgegrenzten Instanz

Status: ausgeführt 2026-11-01 (zwei Läufe ausführbar, einer begründet nicht ausführbar) · Normalfall · Matrix: [BPMN-01](../CASE-MATRIX.md) · Lauf: [task014-bpmn-report.json](../../../10-Evidence/MILE-002/task014-bpmn-report.json) · Bewertung: **teilweise; konkrete Lücke bei Übergangssemantik**

## Aufgabe und Fremdreferenz

**Nutzeraufgabe:** „Welchen Pfad hat Bestellung i1 am Entscheidungspunkt genommen — und war das der einzige?“ Alternative aktivierte Pfade mit Instanzbezug beschreiben; ein Syntax-PASS ist keine Ausführung.

**Regeln (Wortlaut gelesen, Spezifikation BPMN 2.0.2, formal/13-12-09, lokale PDF-Hash in SOURCE-LOCK):**

- §10.6.2 (S. 289 f.): Für eine gegebene Prozessinstanz kann nur einer der Pfade genommen werden; ein Default-Pfad greift, wenn keine Bedingung wahr ist, sonst Laufzeit-Exception.
- §13.4.2 (S. 435): Jeder ankommende Token aktiviert das Gateway und wird zu genau einem ausgehenden Flow geleitet; Bedingungen in Reihenfolge, die erste wahre entscheidet; Default genau dann, wenn keine wahr ist; ohne Default Exception. Workflow-Muster WCP-4/5/8.
- §13.2, §13.3.1, Glossar: Token ist ein theoretisches Hilfskonzept; Werkzeuge müssen Token nicht implementieren.

Hinweis: Die Konformitätsklausel verweist auf „Clause 14 / 14.2.2“, die Ausführungssemantik steht tatsächlich in Kapitel 13.

**Modell:** [bpmn-order.json](../models/bpmn-order.json), synthetisch, mit handgeschriebener Token-Spur (keine Engine).

## Cube-Ausdruck und Vertrag

**Versuchsabbildung (A):** Token-Aufzeichnung → `Y:resource-object:evidence` (nicht `X:scope:event` — ein Token ist kein zugelassenes Ereignis); Aktivität → `Y:identified-object:work-item`; Instanz i1 = Scope `bpmn:i1`. Prädikat `routedTo` Evidence → WorkItem.

| Lauf | Ausdruck (gekürzt) | Erwartung (vorab, `66efa7b`) | Ergebnis |
|---|---|---|---|
| BPMN-01-routed | `rel("routedTo", Evidence[i1/tok-route], WorkItem[approve-manual])` | PASS | PASS |
| BPMN-01-ctrl-other-branch | `rel("routedTo", Evidence[i1/tok-route], WorkItem[approve-auto])` | PASS | PASS — Widerspruch nur zwischen zwei Aussagen |
| BPMN-01-exclusivity | `not_executable` | kein Fachstatus | `NOT_EXECUTED` |

## Befunde

| Dimension | Befund |
|---|---|
| **Ausdruck** | Belegt: instanzgebundene Leitentscheidung als Aufzeichnung, getrennt von Ausführung und Ergebnis (`BoundedExecution`, `Outcome`, `X:endpoint:result` existieren als eigene Konzepte). |
| **Vertragsbindung** | **Konkrete Lücke:** keine Übergangs-, Bedingungs- oder MODE-Verträge in binding-context/1; die Exklusivität steht nur als Freitext im Prädikatvertrag. |
| **Prüfung** | **Konkrete Lücke:** Zwei widersprüchliche Leitentscheidungen für denselben Token bestehen je einzeln. Reihenfolge der Bedingungen, Default und Exception sind nicht prüfbar. |
| **Darstellungsbedarf** | Genommener Pfad je Instanz hervorgehoben, nicht genommene Pfade sichtbar; Widerspruch (zwei Pfade) als Fehler kennzeichnen. → MILE-003 |
| **Nutzen** | Hoch für Prozessanalyse und Audit: „Welche Instanz ging welchen Weg?“ Messbar: Anteil der Instanzen mit genau einer Leitentscheidung je XOR-Aktivierung. |

## Kleinster Eingriff und Unsicherheit

**Profil + LIB, keine Engine, keine Morphologie:** ein versioniertes Kontrollfluss-Profil, das Gateway-Typ und Exklusivität an Prädikate bindet, und eine reine Spurprüfung (`analyze.trace-conformance/v1`: Spur + Modell → Abweichungen je Instanz). Die Bedingungsauswertung bleibt Sache der Engine; Cube prüft beobachtete Spuren (Integrationsrichtung „BPMN-Ausführung → Cube“ aus dem Research).

Unsicherheit: Die Spur ist handgeschrieben; reale Engine-Logs (Korrelation, Zeitstempel) wurden nicht geprüft. Höhere Kontextformate (P1.8 Szenarien, P1.10 Transitionen) wurden für BPMN nicht untersucht.
