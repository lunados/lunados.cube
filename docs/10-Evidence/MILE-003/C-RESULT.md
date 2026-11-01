# MILE-003 — Abschlussnachweis (TASK-023)

Stand: 2026-11-01 · Branch `feature/mile003-visual-check` · Prüfung: [verification.json](verification.json), Skript [verify_mile003.py](verify_mile003.py) · Hashes: [MANIFEST.json](MANIFEST.json)

## Prüfung

| Kriterium | Ergebnis |
|---|---|
| Inventur: alle zwölf Anforderungen V-01–V-12 mit Urteil und Nachweisart | erfüllt (0 × trägt, 9 × teilweise, 3 × Lücke) |
| Render-Läufe über den lokalen MCP-Pfad, `plan_check` PASS, SVG-Hashes wie protokolliert | erfüllt, 6 Läufe |
| Je vorrangige Unterscheidung (V-01, V-05, V-09, V-12) ein Printer-Paar oder ein markiertes Mockup | erfüllt |
| Mockups: Kennzeichnung „MOCKUP — kein Printer-Output“, keine aktiven SVG-Inhalte, Glyphen nur aus `symbols.json`, Hashes wie dokumentiert, Generator reproduziert alle neun | erfüllt |
| Erwartung bzw. Prüfplan vor dem Lauf committet und seitdem unverändert (Spezifikations-Commit ist echter Vorfahre des Nachweis-Commits) | erfüllt für alle sechs Spezifikationen und Pläne |
| Vorprüfung: neun Einheiten mit C1–C6, Antworten als Proxy markiert; blinde Zweitprüfung mit 15 Antworten | erfüllt |
| P0, P1, P2 und P3 seit Beginn von MILE-003 ohne Commit; P0–P2 im Arbeitsbaum unverändert | erfüllt |
| Relative Links in docs/ und openspec/ | keine kaputten |

## Chargen

| Mile | Abschlusskriterium | Nachweis |
|---|---|---|
| MILE-003-A | Inventurtabelle mit Nachweisart je Zeile; MILE-002-Material gerendert, wo ein Eingabeformat existiert | [INVENTORY](../../09-Research/visual-check/INVENTORY.md), [RENDER-RESULTS](../../09-Research/visual-check/RENDER-RESULTS.md); R-1a/b, R-2a/b |
| MILE-003-B | Paare aus Printer-Output oder markiertem Mockup, mit Eingabe, Hash und Fallbezug | [PAIRS](../../09-Research/visual-check/PAIRS.md) (P-01, P-09), [MOCKUPS](../../09-Research/visual-check/MOCKUPS.md) (M-01A, M-05A–C, M-09A–C, M-12A–B) |
| MILE-003-C | Prüfbericht je Paar, Übergabe an MILE-004, Menschentest-Skript, ehrliche Grenzen | [PRECHECK](../../09-Research/visual-check/PRECHECK.md), [HANDOVER](../../09-Research/visual-check/HANDOVER.md), [HUMAN-TEST-SCRIPT](../../09-Research/visual-check/HUMAN-TEST-SCRIPT.md) |

## Ergebnis in einem Satz je Unterscheidung

- **V-01:** Der Mechanismus existiert (`edge_styles` + Legende); es fehlt die Herkunftsbindung (G-02). M-01A erfüllt alle Kriterien.
- **V-05:** Heute fallen „geprüft leer“ und „unbekannt“ zusammen; M-05C trennt vier Zustände, setzt aber eine Erhebungserklärung je Zelle voraus (G-01).
- **V-09:** Heute nur eine von Hand deklarierte, farbabhängige Hervorhebung; M-09C zeigt die Zyklenkomponente und setzt eine berechnete Zyklusprüfung voraus (G-05).
- **V-12:** Keine Sicht vorhanden; M-12B zeigt Instanz, Paarung und Regelverstoß und setzt eine typisierte Instanzbindung voraus (G-08).

## Grenzen

- **Kein menschlicher Lesbarkeitsnachweis** (D-1). Beide Prüfungen sind Agenten-Proxy, mit demselben Modell; die erste ist nicht blind, die zweite blind per Anweisung.
- Die korrigierten Varianten entstanden nach der ersten Prüfung und wurden nur blind geprüft.
- Acht der zwölf Anforderungen sind nur inventarisiert bzw. gerendert.
- Rendering lief aus einem Arbeitsbaum mit nicht committeten P3-Änderungen; Laufprotokolle nennen den Stand.
- Erratum zum DAG-Modell aus MILE-002: zwei Zyklen statt einem ([HANDOVER §4](../../09-Research/visual-check/HANDOVER.md)).

## Wiederholen

```sh
python3 -I docs/10-Evidence/MILE-003/verify_mile003.py         # Abschlussprüfung, schreibt verification.json
python3 -I docs/09-Research/visual-check/mockups/mockups.py /tmp/m   # Mockups neu erzeugen, Hashes vergleichen
```

Renders: Spezifikationen unter `docs/09-Research/visual-check/renders/` und `pairs/` mit `plan_source` → `plan_views` → `plan_check` (P3-MCP-LOCAL/0.3.0-rc1) in der Agent-Umgebung (`scripts/dev/agent_env.sh`). Rasterung der Vorprüfung: `precheck/raster.js` (Playwright/Chromium).
