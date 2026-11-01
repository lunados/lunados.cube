# BPMN-03 — Join kombiniert Signale verschiedener Prozessinstanzen

Status: ausgeführt 2026-11-01 · Gegenfall · Matrix: [BPMN-03](../CASE-MATRIX.md) · Lauf: [task014-bpmn-report.json](../../../10-Evidence/MILE-002/task014-bpmn-report.json) · Bewertung: **teilweise belegt; Lücke ohne Instanz-Scope**

## Aufgabe und Fremdreferenz

**Nutzeraufgabe:** „Hat *Ship* für i1 gestartet, weil die Kreditprüfung von i2 fertig war?“ Konkret zeigen, welche Bindung diese Verwechslung ausschließt bzw. wo sie fehlt. Keine Engine bauen.

**Regeln (Wortlaut gelesen):** §13.2 — jede Start-Event-Occurrence erzeugt eine neue Prozessinstanz (außer bei Korrelation); Abschluss verlangt, dass kein Token *in der Instanz* verbleibt. §10.6.2 bezieht Pfadentscheidungen auf „a given instance“. §13.4.1 selbst erwähnt Instanzen nicht; die Instanzbindung der Token folgt aus §13.2.

**Spur:** i1 hat `tok-stock`; i2 hat bisher nur `tok-credit` ([Modell](../models/bpmn-order.json)).

## Cube-Ausdruck und Vertrag

Gleicher Ausdruck, zwei Arten der Instanzbindung:

| Lauf | Kontext | Erwartung (vorab, `66efa7b`) | Ergebnis |
|---|---|---|---|
| BPMN-03-join-cross-instance-scoped | **Instanz als Scope:** Validierung im Scope i1; `i2/tok-credit` mit Scope i2 deklariert | FAIL / P1_REFERENT_MISMATCH + P1_SCOPE_CONFLICT | wie erwartet: „Declared referent scope differs from the context scope“; Scope-Konsistenz FAIL |
| BPMN-03-join-cross-instance-shared | **Gemeinsamer Spur-Scope:** Instanz nur im Referentnamen | PASS | PASS |

## Befunde

| Dimension | Befund |
|---|---|
| **Ausdruck** | Belegt: Instanzzugehörigkeit lässt sich über den Referenten-Scope ausdrücken. |
| **Vertragsbindung** | Teilweise: Das funktioniert nur, wenn jede Instanz als eigener Validierungsscope modelliert wird. Damit trägt der Cube-Scope zugleich die Prozessinstanz-Identität — eine Überladung, und für jede Instanz braucht es einen eigenen Kontext. Eine eigenständige Instanz-/Korrelationsbindung (z. B. `instance_ref` je Aufzeichnung plus Regel „gleiche Instanz“ im Prädikatvertrag) fehlt. |
| **Prüfung** | **Belegt:** Mit Instanz-Scope wird die Verwechslung erkannt (FAIL). **Konkrete Lücke:** Mit gemeinsamem Scope besteht sie (PASS); die Instanz im Namen bindet nichts. |
| **Darstellungsbedarf** | Instanz als sichtbare Gruppierung (Swimlane/Band je Instanz); instanzübergreifende Kanten als Fehler hervorheben. → MILE-003 |
| **Nutzen** | Hoch: Korrelationsfehler sind in Message-getriebenen Prozessen schwer zu finden. Messbar: alle Join-Aufzeichnungen mit Eingängen aus genau einer Instanz. |

## Kleinster Eingriff und Unsicherheit

**Profil:** entweder die Konvention „Instanz = Scope“ ausdrücklich festschreiben (heute schon wirksam, aber überladen) oder eine typisierte Instanzbindung je Aufzeichnung mit Prädikatregel „gleiche Instanz“. Keine Engine, keine Morphologieänderung — `Y:identified-object:bounded-execution` ist als Instanzbegriff vorhanden.

Unsicherheit: Echte Korrelation (§13.2, Konversationen, Correlation Keys) ist komplexer als eine Instanz-ID; nur der einfache Fall wurde geprüft.
