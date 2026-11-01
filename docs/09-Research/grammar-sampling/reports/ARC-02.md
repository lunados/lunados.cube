# ARC-02 — Abgegrenzte Belegung mit zählbaren Zielreferenzen

Status: ausgeführt 2026-11-01 (ein Lauf ausführbar, einer begründet nicht ausführbar) · Normalfall · Matrix: [ARC-02](../CASE-MATRIX.md) · Lauf: [task012-archimate-report.json](../../../10-Evidence/MILE-002/task012-archimate-report.json) · Bewertung: **konkrete Lücke (Prüfung)**

## Aufgabe und Fremdreferenz

**Nutzeraufgabe:** „Besteht *Financial Processing* aus zwei bis drei Teilfunktionen?“ Zähldomäne und Vollständigkeit festlegen; die Min-/Max-Regel als lokales Versuchsprofil kennzeichnen.

**Regel:** R-AM-4 — Composition: ein Element besteht aus einem oder mehreren anderen Konzepten (N221, K); Beispiel mit drei Teilfunktionen (Bizzdesign S. 8, H). **Keine Quelle nennt Min/Max.**

**Zählregel (A, lokal, nicht ArchiMate)** — fixiert im [Modell](../models/archimate-billing.json) unter `local_count_rule`:

| Merkmal | Festlegung |
|---|---|
| Zielidentität | `am:financial-processing` |
| Rolle | Ganzes (Quelle) der Composition |
| Gezählt | verschiedene Ziel-Elemente vom Typ Application Function |
| Grenzen | min 2, max 3 |
| Scope | `am:view/full` |
| Zeitpunkt | Modellstand 2026-11-01, statisch |
| Vollständigkeit | Vollsicht als vollständig deklariert; in der Service-Sicht ist die Anzahl unbekannt, nicht null |

Im Modell: drei Teile (Accounting, Billing, Payment) → Regel erfüllt.

## Cube-Ausdruck und Vertrag

Abbildung wie [ARC-01](ARC-01.md); Prädikat `composedOf` Tool → Tool.

| Lauf | Art | Erwartung (vorab, `3229dd3`) | Ergebnis |
|---|---|---|---|
| ARC-02-part | `rel("composedOf", Tool[financial-processing], Tool[billing])` | PASS | PASS |
| ARC-02-count-rule | `not_executable` | kein Fachstatus | `NOT_EXECUTED`, kein Aufruf |

Begründung der Nichtausführbarkeit (im Fall gespeichert): `cube_validate` prüft genau einen Ausdruck; binding-context/1 kennt keine Relationskardinalität. Die P1.6-Slots (binding-context/2) haben nur `one`/`many` (≥ 1), gelten nur für X-Endpunkte und dürfen von Aufrufern nicht erweitert werden ([P1.6-Spezifikation](../../../../P1/instantiation-profile-v1/P1_6_ACCEPTANCE_SPEC.md) §1.2). **Diese Slot-Arity löst die Populationsprüfung nicht.**

## Befunde

| Dimension | Befund |
|---|---|
| **Ausdruck** | Belegt für Einzelaussagen. Die Zählregel selbst ist nicht ausdrückbar: weder als Ausdruck noch als Vertragsfeld. |
| **Vertragsbindung** | Teilweise: `additional_constraints` kann die Regel als Freitext tragen — das ist kein Abdeckungsnachweis. |
| **Prüfung** | **Konkrete Lücke:** keine Prüfung über eine Menge von Aussagen (Population) mit Scope und Vollständigkeit. |
| **Darstellungsbedarf** | Anzahl je Ganzem mit Grenzen sichtbar; „unvollständige Sicht“ von „Unterbelegung“ unterscheiden. → MILE-003 |
| **Nutzen** | Mittel: Modellqualitätsregeln (Teile pro Funktion, Partner pro Service) sind in EA-Werkzeugen üblich. Messbar: Regelverletzungen je Sicht mit korrekter Unterscheidung unbekannt/verletzt. |

## Kleinster Eingriff und Unsicherheit

**Profil + LIB:** ein Populationsprofil (Ziel, Rolle, Relationstyp, Grenzen, Scope, Zeitpunkt, Vollständigkeitserklärung) und eine reine Zählfunktion über eine deklarierte Aussagenmenge, die bei unvollständigem Scope UNRESOLVED liefert. Vorbild für die Statuslogik: P1.10.1 D-2 („incomplete, not contradictory“ → UNRESOLVED). Kein Morphologiebedarf belegt.

Unsicherheit: Ob eine solche Prüfung in P1 (mehrere Aussagen pro Lauf) oder ausschließlich in LIB gehört, ist eine Architekturentscheidung für MILE-004.
