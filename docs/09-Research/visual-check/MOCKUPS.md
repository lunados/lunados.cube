# MILE-003-B — Handmockups für nicht darstellbare Unterscheidungen (TASK-021)

Stand: 2026-11-01 · Entscheidung D-2 · Generator: [mockups/mockups.py](mockups/mockups.py) (deterministisch, ohne `<pattern>`, `<use>`, `<image>`, `href`, Skript)

**Jedes Bild ist ein Kandidat, kein Printer-Output** und trägt das sichtbar im Kopf. Verwendete VG-Anker: `⌹` resource, `⌼` evidence, `⬠` boundary, `𝗜` integration, `𝗥` runtime, `𝗣` provider — dieselben, die die Printer für das Material verwenden. Alles Weitere ist Text, Linienart oder Schraffur aus expliziten Linien (wie VP-07 PV-5). Keine Farbe trägt Bedeutung.

| Mockup | Anforderung · Fall | Kandidatenregel | Setzt voraus | Wiederverwendet |
|---|---|---|---|---|
| [M-05A](mockups/M-05A.svg) | V-05 · DSM-03, ARC-03 | Vier Zellzustände **textlich**: Eintrag, „keine · geprüft“ (fett umrandet), „offen (nicht erhoben)“, ausgeblendete Spalte als **benannter** Streifen; Diagonale als Element | Vollständigkeitserklärung je Zeile/Relationstyp (G-01); deklarierte Reihenfolge | M-5 Legendenformel, M-4 Offenlegung |
| [M-05B](mockups/M-05B.svg) | V-05 · DSM-03, ARC-03 | wie A, aber **unbekannt = schraffiert**, geprüft leer weiß mit Vermerk | wie A | M-3 Schraffur |
| [M-01A](mockups/M-01A.svg) | V-01 · C4-02, C4-03 | Linienart folgt der **gebundenen Herkunft**, nicht dem Prädikat: deklariert durchgezogen, abgeleitet gestrichelt, **nicht gebunden gepunktet** — nie durchgezogen | typisierte Relationsherkunft (G-02) | M-1 Linienarten-Satz (solid/dashed/dotted), neutrale Pfeilspitze |
| [M-09A](mockups/M-09A.svg) | V-09 · DAG-03, DAG-01 | Zyklenkanten **doppelt + Z-Nummer**, berechneter Zeuge als Statuszeile „Plan nicht abarbeitbar“; Layout wie Printer (gemeinsame Stränge) | berechnete Zyklusprüfung (G-05) | M-1 `double` |
| [M-09B](mockups/M-09B.svg) | V-09 · DAG-03, DAG-01 | wie A, aber **direkte Kanten ohne gemeinsame Stränge**; Hinweis, dass die Darstellung von keiner Nummerierung abhängt | wie A; anderes Layout als VP-02 | M-1 `double` |
| [M-12A](mockups/M-12A.svg) | V-12 · BPMN-03 | Instanz als **benannte Grenze** (`⬠`); instanzübergreifende Kante gestrichelt mit **schraffierter, benannter Marke** | typisierte Instanzbindung (G-08) | M-3 Schraffur, Grenzanker |

Hashes (SHA-256, erste 16 Zeichen): M-01A `00de9a63db4e354f` · M-05A `74caad87019766a7` · M-05B `858754fef20e4cd4` · M-09A `270bd293f67d9367` · M-09B `9415e83f49fcf5a6` · M-12A `522ac60830a2bbc0` · Generator `75714c1a11b96df9`. Vollständig im MANIFEST bei TASK-023.

## Bewusste Entscheidungen beim Zeichnen

- **V-05:** Die gesamte Spalte printer ist als ausgeblendet gezeigt (wie R-1b), nicht nur die Modellzelle (resolver, printer); der Streifen nennt den Namen, den R-1b nur im Bericht führt.
- **V-01:** Zwei Felder nebeneinander, weil dieselbe Kante api → db in C4-02 mit gebundener und in C4-03 mit ungebundener Herkunft auftritt.
- **V-09A** übernimmt absichtlich die Kantenführung der Printer (gemeinsame Senkrechten), damit TASK-022 prüfen kann, ob doppelte Linien allein genügen; **V-09B** trennt Darstellung und Layoutproblem.
- **V-12:** Der Join ist als beschriftete Box gezeichnet, nicht in BPMN-Notation — die VG hat dafür keinen Anker.

## Offene Fragen für TASK-022

1. Ist „doppelt“ in V-09A bei überlagerten Strängen noch eindeutig einer Kante zuzuordnen?
2. Reicht in M-05A der Text allein, oder braucht „unbekannt“ eine Fläche (M-05B)?
3. Ist „gepunktet = Herkunft unbekannt“ in M-01A gegen „gestrichelt = abgeleitet“ ausreichend verschieden?
4. Überdeckt in M-12A die Schraffurmarke die Kante so, dass ihre Richtung unklar wird?

Keine Printer-, Anker- oder Morphologieänderung. Kein Lesbarkeitsnachweis.
