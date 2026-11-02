# Sichtprüfung VP-10 (MILE-006-C)

Dauer etwa 10 Minuten. Zwei synthetische Renderings, sieben Prüfpunkte, Antwort je Punkt ja oder nein. Keine Kundendaten. Geprüft wird nur, ob die Darstellung beim Hinsehen richtig ankommt; die Funktion ist durch Vektoren und Tests abgedeckt.

## Öffnen

```bash
cd /Users/johannesklapproth/SitesHeroku/lunados.cube
open -a Safari docs/10-Evidence/MILE-005/task035/GC-de.svg docs/10-Evidence/MILE-006/task040/O-09.svg
```

Zuerst nur die Matrix ansehen, danach die Legende lesen.

## Bild 1 — `GC-de.svg`: Zellzustände

Matrix resolver, validator, parser; die Spalte printer ist ausgeblendet.

1. **Vier Arten unterscheidbar:** Eintrag (dünner Rahmen mit Text), „keine · geprüft“ (fetter Rahmen), Schraffur und „Element“ auf der Diagonale sind ohne Legende auseinanderzuhalten.
2. **Schraffur:** Sie liest sich als „nicht erhoben“, nicht als „leer“ oder „keine Abhängigkeit“.
3. **Fetter Rahmen:** Er liest sich als „geprüft, nichts gefunden“, nicht als Fehler oder Hervorhebung.
4. **Ausgeblendete Spalte:** Dass printer fehlt, steht in der Legende und fällt dort auf.

## Bild 2 — `O-09.svg`: deklarierte Reihenfolge

Deklariert ist nur parser, validator; resolver und printer folgen ungeordnet.

5. **Reihenfolge:** Es ist klar, dass resolver und printer nicht deklariert wurden („nicht geordnet“ unter dem Namen).
6. **Rückkopplung:** Die beiden Zellen mit „Rückkopplung“ über der Diagonale lesen sich als Hinweis aus der Reihenfolge, nicht als Fehler oder Befund über das System.

## Beide Bilder

7. **Text und Überschriften:** Nichts überlappt oder ist abgeschnitten, die Schrift ist bei normalem Zoom lesbar, und die Überschriften passen. Ein bekannter Kandidat: Die Abschnittsüberschrift heißt noch „CUBE.AXES · …“ aus VP-09, die Fußzeile „cube.cells“.

## Rückmeldung

Im Chat, zum Beispiel: `1 ja, 2 ja, 3 nein – wirkt wie Warnung, 4 ja, 5 ja, 6 ja, 7 nein – Überschrift`. Jedes „nein“ wird in TASK-042 behoben (neue Printer-Revision, 0.10.0 bleibt byte-gleich) oder als offen benannt.

## Ergebnis (2026-11-02)

Nutzer: 1–7 ja. Keine Mängel; die Überschrift „CUBE.AXES · …“ bleibt.
