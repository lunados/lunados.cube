# BPMN-02 — AND-Join mit korrekt korrelierten Eingängen

Status: ausgeführt 2026-11-01 (ein Lauf ausführbar, einer begründet nicht ausführbar) · Normalfall · Matrix: [BPMN-02](../CASE-MATRIX.md) · Lauf: [task014-bpmn-report.json](../../../10-Evidence/MILE-002/task014-bpmn-report.json) · Bewertung: **teilweise; konkrete Lücke bei Synchronisation**

## Aufgabe und Fremdreferenz

**Nutzeraufgabe:** „Durfte *Ship* für Bestellung i1 starten — lagen beide Prüfergebnisse vor?“ Instanz, erwartete Eingänge und Synchronisationsbedingung an einer kleinen dokumentierten Spur unterscheiden.

**Regeln (Wortlaut gelesen):** §13.4.1 (S. 434) — das Parallel Gateway ist aktiviert, wenn auf **jedem** eingehenden Sequence Flow mindestens ein Token liegt; es verbraucht genau einen Token je Eingang und erzeugt einen je Ausgang; überzählige Token bleiben am Eingang. WCP-2/WCP-3. §13.2 (S. 426): Instanz-Abschluss verlangt, dass kein Token in der Instanz verbleibt. §10.6.4: Join synchronisiert parallele Flüsse.

**Spur:** In i1 liegen `tok-stock` (f-stock-done) und `tok-credit` (f-credit-done) vor ([Modell](../models/bpmn-order.json)).

## Cube-Ausdruck und Vertrag

Abbildung wie [BPMN-01](BPMN-01.md); Prädikat `joins` Evidence → Evidence (binär).

| Lauf | Ausdruck (gekürzt) | Erwartung (vorab, `66efa7b`) | Ergebnis |
|---|---|---|---|
| BPMN-02-join-same-instance | `rel("joins", Evidence[i1/tok-stock], Evidence[i1/tok-credit])` im Scope i1 | PASS | PASS |
| BPMN-02-sync-condition | `not_executable` | kein Fachstatus | `NOT_EXECUTED` |

## Befunde

| Dimension | Befund |
|---|---|
| **Ausdruck** | Teilweise: Eine Zwei-Eingangs-Synchronisation ist als binäre Relation schreibbar. Ein Join mit drei und mehr Eingängen, „genau einer je Eingang“ und „Überschuss bleibt liegen“ sind nicht ausdrückbar. |
| **Vertragsbindung** | **Konkrete Lücke:** Die erwarteten Eingänge (welche Flows) sind nicht Teil des Vertrags; ein Übergangsvertrag fehlt. |
| **Prüfung** | Belegt nur die Typgültigkeit der Paaraussage. Ob alle Eingänge vorlagen, wird nicht geprüft (Populationsprüfung, wie [ARC-02](ARC-02.md)). |
| **Darstellungsbedarf** | Join mit Eingangsliste und Status je Eingang (vorhanden/fehlend) in der Sequenz- bzw. Phasensicht. → MILE-003 |
| **Nutzen** | Hoch: „Warum wartet diese Instanz?“ ist eine häufige Betriebsfrage. Messbar: Wartende Joins zeigen die fehlenden Eingänge. |

## Kleinster Eingriff und Unsicherheit

**Profil + LIB:** im Kontrollfluss-Profil je Join die erwartete Eingangsmenge; die Prüfung „ein Token je Eingang, gleiche Instanz“ als Teil von `analyze.trace-conformance/v1`. Statuslogik wie P1.10.1: fehlender Eingang = UNRESOLVED (unvollständig), kein FAIL. Keine Morphologieänderung.

Unsicherheit: Token-Verbrauch und Überschuss betreffen den Laufzeitzustand; ob Cube ihn überhaupt abbilden soll oder nur beobachtete Spuren prüft, ist eine MILE-004-Entscheidung.
