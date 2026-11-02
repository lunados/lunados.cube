# Sichtprüfung VP-10 0.11.0 (MILE-007, TASK-047)

Dauer etwa 5 Minuten. Zwei synthetische Renderings, fünf Prüfpunkte, Antwort je Punkt ja oder nein. Keine Kundendaten. Geprüft wird nur, ob die Darstellung beim Hinsehen richtig ankommt; die Funktion ist durch Vektoren und Tests abgedeckt.

## Öffnen

```bash
cd /Users/johannesklapproth/SitesHeroku/lunados.cube
open -a Safari docs/10-Evidence/MILE-007/task046/S-02.svg docs/10-Evidence/MILE-007/task046/S-05-de.svg
```

## Bild 1 — `S-02.svg`: DSM-Module als Aussagenmenge, ohne Plan

1. **Ohne Umweg:** Titel, Achsen und Einträge sprechen von Modulen und `dependsOn`; nichts erinnert an Migration, Phasen oder Schritte.
2. **Lesrichtung:** Mit der Legende ist klar, dass die Zeile vom Spalten-Element abhängt (Zeile = Subjekt, Spalte = Objekt).

## Bild 2 — `S-05-de.svg`: C4-Komponenten auf Container verdichtet

In der Zelle API × DB stehen eine deklarierte Container-Beziehung (`s-4 · uses`) und eine abgeleitete (`d-1 · uses.derived · abgeleitet · 2 Quellen`).

3. **Unterscheidbar:** Deklarierte und abgeleitete Aussage sind in derselben Zelle klar auseinanderzuhalten.
4. **Verlust:** Die Zeile „Verdichtung all: Quellen 4 → abgeleitet 1; …“ in der Legende macht verständlich, was die verdichtete Sicht nicht zeigt (interne Beziehung, verworfene Beschreibung).

## Beide Bilder

5. **Text:** Nichts überlappt oder ist abgeschnitten; die Schrift ist bei normalem Zoom lesbar.

## Rückmeldung

Im Chat, zum Beispiel `1–5 ja` oder `1 ja, 2 ja, 3 nein – …`. Jedes „nein“ wird behoben (neue Revision, 0.10.x bleibt byte-gleich) oder als offen benannt.
