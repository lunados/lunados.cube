# DSM-02 — Zwei Domänen mit domänenübergreifender Zuordnung

Status: ausgeführt 2026-11-01 · Normalfall · Matrix: [DSM-02](../CASE-MATRIX.md) · Lauf: [task013-dsm-report.json](../../../10-Evidence/MILE-002/task013-dsm-report.json) · Bewertung: **teilweise**

## Aufgabe und Fremdreferenz

**Nutzeraufgabe:** „Welches Team pflegt welche Module — und wie hängen Teamzuständigkeit und Modulkopplung zusammen?“ DSM- und DMM-Beziehungen mit expliziten Domänen verbinden; heterogene Relationstypen nicht zu einer universellen Kante verflachen.

**Regeln:** R-DSM-3 (DMM: rechteckig, bildet eine Domäne auf eine andere ab), R-DSM-4 (MDM: DSMs auf der Diagonale, DMMs außerhalb; mehrere Relationstypen je Teilmatrix möglich). Stufe D.

**Modell:** [dsm-modules.json](../models/dsm-modules.json): Domänen `modules` und `teams`, DMM teams × modules („Zeilenteam pflegt Spaltenmodul“). Die Team-DSM ist nicht modelliert (unbekannt).

## Cube-Ausdruck und Vertrag

**Versuchsabbildung (A):** Teams → `Y:identity-anchor:actor`, Module → `Y:resource-object:artifact`. Domäne = Konzeptmenge; Relationstyp je Teilmatrix = eigenes Prädikat (`dependsOn` Artifact→Artifact, `maintains` Actor→Artifact).

| Lauf | Ausdruck (gekürzt) | Erwartung (vorab, `fa50ee9`) | Ergebnis |
|---|---|---|---|
| DSM-02-dmm-cell | `rel("maintains", Actor[t:core], Artifact[m:parser])` | PASS | PASS |
| DSM-02-ctrl-cross-type | `rel("dependsOn", Actor[t:core], Artifact[m:parser])` | FAIL / P1_PREDICATE_SIGNATURE | wie erwartet |
| DSM-02-ctrl-flattened | `rel("related", Actor[t:core], Artifact[m:parser])` mit breitem Vertrag | PASS | PASS |

## Befunde

| Dimension | Befund |
|---|---|
| **Ausdruck** | Belegt: Beide Teilmatrizen sind als typisierte Aussagen ausdrückbar; die Domäne ergibt sich aus den Konzepten. |
| **Vertragsbindung** | Teilweise: Eine *Domäne* ist kein eigenes Objekt; sie existiert nur implizit über Konzepte. Zwei Domänen mit demselben Konzept (z. B. zwei Modulgruppen) wären nicht unterscheidbar. |
| **Prüfung** | Belegt: Ein domänenfremder Relationstyp wird abgewiesen. **Konkrete Lücke:** Ein bewusst breiter Vertrag (`related`) lässt die Abflachung zu; die Trennung hängt allein an der Profildisziplin. |
| **Darstellungsbedarf** | MDM-Blockstruktur mit Domänenbeschriftung; Relationstyp je Block in der Legende; unmodellierte Blöcke (Team-DSM) als „unbekannt“, nicht leer. → MILE-003 |
| **Nutzen** | Mittel bis hoch: Fragen wie „Kreuzt diese Kopplung eine Teamgrenze?“ verbinden DSM und DMM. Messbar: Anzahl der Modul-Abhängigkeiten zwischen Modulen unterschiedlicher Teams. |

## Analysefunktions-Kandidaten (nicht implementiert)

| Kandidat | Eingabe | Ausgabe | Nicht-Implikation |
|---|---|---|---|
| `project.mdm/v1` | Domänendeklaration (Name → Konzeptmenge bzw. Referentenliste), Prädikat je Block, Konvention | Blockmatrix mit Zellzustand und Quellaussage | Unmodellierter Block ≠ leerer Block |
| `analyze.cross-domain-coupling/v1` | DSM-Aussagen + DMM-Aussagen | Kopplungen über Zuordnungsgrenzen mit Quellkanten | Strukturelle Kopplung ≠ Abstimmungsbedarf |

## Kleinster Eingriff und Unsicherheit

**Profil:** eine Domänendeklaration (benannte Referentenmengen) und eine Regel „ein Relationstyp je Block“, die breite Prädikate über Domänengrenzen hinweg ablehnt. **LIB:** die oben genannten Projektionen. Keine Morphologieänderung.

Unsicherheit: Die Teamabbildung auf Actor ist eine Arbeitsannahme; Rollen- oder Gruppenkonzepte (Role Binding) wurden nicht geprüft.
