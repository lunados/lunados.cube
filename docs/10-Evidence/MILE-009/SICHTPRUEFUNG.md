# Sichtprüfung VP-11 Instanzsicht (MILE-009, TASK-057)

Dauer etwa 5 Minuten. Zwei synthetische Renderings, fünf Prüfpunkte, Antwort je Punkt ja oder nein. Keine Kundendaten. Geprüft wird nur, ob die Darstellung beim Hinsehen richtig ankommt; die Funktion ist durch Vektoren und Tests abgedeckt.

## Öffnen

```bash
cd /Users/johannesklapproth/SitesHeroku/lunados.cube
open -a Safari docs/10-Evidence/MILE-009/task057/I-02-de.svg docs/10-Evidence/MILE-009/task057/I-34-de.svg
```

## Bild 1 — `I-02-de.svg`: ein Token, zwei Pfade

Instanz i1 wurde am exklusiven Gateway an zwei Ziele geleitet; der LIB-Datensatz meldet FAIL.

1. **Verstoß:** Es ist sofort zu sehen, dass hier etwas nicht stimmt — beide Pfade stehen als „genommen“, die Urteilszeile sagt „Regelverstoß“ und trägt die schraffierte Marke.

## Bild 2 — `I-34-de.svg`: zwei Instanzen, Join wartet

i1 lief vollständig durch; i2 hat die Kreditprüfung, aber nicht die Lagerprüfung.

2. **Instanzen:** Die beiden Rahmen „Instanz bpmn:i1“ und „Instanz bpmn:i2“ trennen klar, was zu welcher Instanz gehört.
3. **Join:** Bei i2 ist am Join erkennbar, welcher Eingang fehlt, dass ein Token von i1 dort nicht zählt (gestrichelt, „nicht Teil“) und dass i2 wartet; Ship erscheint für i2 nicht als gestartet.
4. **Ohne Urteil:** Wo „nicht geprüft“ steht (i2 an XOR, Merge, Split), wirkt die Zeile nicht wie bestanden oder verletzt.

## Beide Bilder

5. **Text:** Nichts überlappt oder ist abgeschnitten; Linienarten (durchgezogen, gepunktet, gestrichelt) sind bei normalem Zoom unterscheidbar.

## Rückmeldung

Im Chat, zum Beispiel `1–5 ja` oder `1 ja, 2 ja, 3 nein – …`. Jedes „nein“ wird behoben oder als offen benannt.

## Ergebnis (2026-11-02)

Nutzer: 1–5 ja (Antwort `1 - 5 ja`). Keine Mängel; nichts offen.
