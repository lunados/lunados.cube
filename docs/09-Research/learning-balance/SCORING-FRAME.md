# MILE-004-B — Bewertungsrahmen (TASK-026)

Stand: 2026-11-01 · **Festgelegt vor jeder Bewertung.** Maßnahmenliste mit Eingabewerten: [MEASURES.json](MEASURES.json), erzeugt mit [build_frame.py](build_frame.py). Die Felder `score` sind leer und werden erst in TASK-027 gefüllt.

## Maßnahmen

25 Maßnahmen aus vier Quellen:
- G-01–G-10 aus der [Lückenbilanz](../grammar-sampling/GAP-LEDGER.md).
- T-01 und T-02 aus den Werkzeugbefunden.
- VR-01, VR-05, VR-09, VR-12 sowie PO-1–PO-6 aus der [Darstellungsübergabe](../visual-check/HANDOVER.md).
- Neu aus den [Probeergebnissen](PROBE-RESULTS.md): LR-1 (Ergebnisschema je Methode) und PO-8 (Partition ohne Zusammenlegung).

Dazu kommt HT, der Menschentest; er wird als spätere Maßnahme bewertet und ist nach D-4 nicht Teil von MILE-004.

Nicht bewertet werden:
- T-03: kein Eingriff.
- T-04: erledigt mit PR #31.
- PO-7: in G-03 aufgegangen.

## Eingabewerte aus den Quellen (nicht neu geschätzt)

- **Aufwand E** aus der PT-Spanne der Quelle, Mitte der Spanne: ≤ 0,5 PT → 1 · ≤ 1 → 2 · ≤ 2 → 3 · ≤ 3 → 4 · > 3 → 5.
- **Komplexität K** aus der Quelle: niedrig 1 · niedrig–mittel 1,5 · mittel 2 · mittel–hoch 2,5 · hoch 3.
- Wo eine Quelle keinen Wert nennt (T-01, T-02, LR-1, PO-8, HT), ist der Wert eine Annahme und als `inputs_assumed` markiert.
- **Abhängigkeiten** sind nur harte Voraussetzungen:
  - VR-01 → G-02
  - VR-05 → G-01
  - VR-09 → G-05
  - VR-12 → G-08
  - G-06 → G-05
  - G-07 → G-08
  - G-10 ist eine Alternative zu G-02, keine Voraussetzung.

## Bewertung in TASK-027

**Nutzen je Anwendungsfall**, Skala 0–3:

| Wert | Anker |
|---|---|
| 0 | kein Bezug zum Anwendungsfall |
| 1 | indirekt oder nur Randfall |
| 2 | schließt eine belegte Lücke in einem Fall des Anwendungsfalls |
| 3 | schließt belegte Lücken in mehreren Fällen oder ist Voraussetzung für mehrere Maßnahmen dieses Anwendungsfalls |

- **A — Architektursichten:** C4-01–03, ARC-01–03.
- **P — Prozessspuren:** BPMN-01–03.
- Nach D-1 bestimmen nur A und P den Rang. Vollständigkeit zählt, soweit sie Fälle aus A oder P trägt (ARC-02/03, BPMN-01/02).
- **I — Impact/Reihenfolge** (DAG, DSM) und **V — Vollständigkeit allgemein** werden ebenfalls bewertet, aber nur für die Sensitivitätsrechnung.

Bei visuellen Regeln und Printer-Befunden zählt nur der zusätzliche Darstellungsnutzen; der Nutzen der Voraussetzung wird nicht doppelt gezählt.

**Unsicherheit U:**

| Wert | Grundlage |
|---|---|
| 1 | belegt durch P1-Lauf, LIB-Aufruf oder Probe |
| 2 | belegt durch Doku-/Code-Analyse oder Agenten-Vorprüfung |
| 3 | Hypothese bzw. ungeprüft |

Jede Bewertung erhält eine Begründung in einem Satz mit Fall- oder Befundbezug.

## Rangregel

1. **Einzelscore** S = (A + P) / E. Bei Gleichstand gewinnt die kleinere K, dann die kleinere U, dann die Reihenfolge in MEASURES.json.
2. **Pakete:** Eine Maßnahme mit Voraussetzung wird nur zusammen mit ihrer noch offenen Voraussetzung gereiht.
   - Nutzen: Summe aus beiden.
   - Aufwand: Summe der PT-Mitten, dann neu nach der Aufwandsskala abgebildet.
   - K und U: jeweils das Maximum.
   - Gereiht wird jede Maßnahme mit dem besseren Wert aus „allein“ (nur ohne offene Voraussetzung) und „im Paket“; im Paket steht die Voraussetzung vor der abhängigen Maßnahme.
3. **Alternativen:** Von G-02 und G-10 wird nur die besser bewertete gereiht; die andere wird als Alternative geführt.
4. **Mindestnutzen:** Maßnahmen mit A + P = 0 werden in der Hauptliste nicht gereiht, sondern in einer Nebenliste geführt (Impact/Reihenfolge, Werkzeug).
5. **Auswahl MILE-005:** Rang 1 kommt immer in MILE-005. Rang 2 kommt hinzu, wenn beide zusammen in der Mitte der Spannen ≤ 5 PT ergeben und nicht dieselbe offene Nutzerentscheidung voraussetzen.

## Sensitivität (Transparenz, nicht rangbildend)

Zusätzlich werden drei Rangfolgen ausgewiesen:
- S′ = (A + P + I + V) / E, also ohne die Gewichtung nach D-1.
- Die vorläufige Rangfolge aus der Lückenbilanz §7.
- Die Abweichung, wenn U strafend eingeht: S″ = (A + P) / (E · U).

Ändert sich Rang 1 oder 2 zwischen S, S′ und S″, wird das in der Lernbilanz begründet.

## Änderungen

Eine Änderung an diesem Rahmen nach Beginn der Bewertung wird als Nachtrag mit Grund ausgewiesen; danach wird vollständig neu bewertet (Spec-Anforderung „Framed prioritization“).
