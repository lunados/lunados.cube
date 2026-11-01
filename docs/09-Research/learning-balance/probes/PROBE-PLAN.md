# MILE-004-A — Probeplan (TASK-024)

Stand: 2026-11-01 · Maschinenlesbar: [PROBE-PLAN.json](PROBE-PLAN.json), erzeugt mit [build_probes.py](build_probes.py) (deterministisch) · **festgelegt vor jedem Lauf**

Vier Proben prüfen die offenen Leitfragen 1 (Envelope) und 4 (LENS, MODE, Achsen) an je einem Architektur- und einem Prozessfall (MILE-004 D-1, D-2). Quellen sind mit Repo, Commit und SHA-256 gepinnt, darunter `evaluator-result/v0.2` und `evaluator-call/v0.1` aus EXP-024 Charge 3 (`lunados.space@1ae1f44`) und `entry.v1` aus `lunados.lib@4d07650`.

## Leitfrage 1 — Reicht der Envelope-Rahmen?

| Probe | Fall | Instanzen | Erwartung |
|---|---|---|---|
| **E-1** Projektion mit Quellenspur | C4-02, Gegenfall C4-03 | E-1a verdichtet mit Verlust · E-1b ohne Verlust · E-1c Herkunft nicht gebunden (unresolved) | schema-gültig; nur „bewertet/unaufgelöst“ und die Bindung an die Eingaben sind typisiert; Endpunkte, Strategie, Verlust und Grund stehen nur in `outcome.detail`/`value`/`parameters` |
| **E-2** Spurprüfung mit Instanzbindung | BPMN-03, BPMN-02 | E-2a konform (i1) · E-2b instanzübergreifend (J1) · E-2c unvollständig (i2, unresolved) | schema-gültig; Instanz der Aktivierung und je Token ohne typisierten Ort; konform/Verstoß nur in `outcome.value` |

Je Probe sind sechs Pflichtunterscheidungen mit erwartetem Träger festgelegt: **T** typisiertes Feld, **U** nur untypisiert (`detail`, `value`, `findings`, `parameters`, `content`, `ref`), **N** nicht darstellbar. Entscheidungsregeln (aus [Lernvergleich §1](../../cube-grammar-2026-11-01/LERNVERGLEICH.md)):

- **R-E1** — mindestens ein N oder zwei fachlich verschiedene Fälle in allen Feldern gleich → Kandidat Envelope-Erweiterung.
- **R-E2** — nur U → Typisierungslücke; Maßnahme dort, wo ein typisierter Bindungspunkt existiert; fehlt er in Envelope und LIB-Eintrag: Kandidat LIB-Vertragsrevision mit Ergebnisschema-Verweis, Envelope unverändert.
- **R-E3** — alles T → keine Maßnahme.

Erwartet wird für beide Proben **R-E2**. Werkzeug: `jsonschema` (Draft 2020-12) in der Agent-Umgebung, Identitätsprüfung Aufruf ↔ Ergebnis wie im EXP-024-Harness, Trägerklassifikation gegen das Schema.

## Leitfrage 4 — Welche Bindungen brauchen LENS, MODE und Achsen?

| Probe | Fall | Aufrufe | Erwartung |
|---|---|---|---|
| **L-1** Herkunft je Kante als LENS | C4-02/C4-03 | L-1a Provenienz-Linse · L-1b Epistemologie-Linse mit Präfix `derived:` | L-1a: alle drei Kanten gleicher Akzent, Herkunftsklassen nur in Metadaten. L-1b: nur die abgeleitete Kante hervorgehoben; deklariert und ungebunden gleich → je Linse eine binäre Unterscheidung |
| **L-2** Instanzgruppierung | BPMN-03 | `cube.flow`, Partition `track`, Track-Map i1/i2 | zwei Panels; J1 in beiden wiederholt; die instanzübergreifende Kante ist nicht markiert; dass J1 zu i1 gehört, steht nicht im Bild |
| L-2/MODE | — | **NE** | P0 v9.4 friert für Mode weder Werte noch Übergänge noch Bindung ein (§3.10, C021); kein Validator oder Printer liest MODE |

Entscheidungsregeln: Zeigt eine Linse drei Herkunftsklassen, trägt LENS die Herkunft; sonst braucht Herkunft eine typisierte Bindung (G-02) und einen Kantenstil (VR-01). Macht die Partition die Kante J1 ← i2/tok-credit als instanzübergreifend sichtbar, trägt die vorhandene Bindung die Instanzgruppierung; sonst fehlen Instanzbindung und Verstoßmarkierung (G-08, VR-12).

## Grenzen

Die Envelope-Instanzen sind von Hand erstellt; es läuft kein Evaluator. E-1 und E-2 sind Vertrags- und Schemaanalysen, L-1 und L-2 Render-Läufe über den lokalen MCP-Pfad. Vier Proben belegen Ausdrückbarkeit an diesen Fällen, nicht die Vollständigkeit des Rahmens.
