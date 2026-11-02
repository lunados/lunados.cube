# MILE-009 — Abschlussnachweis

Stand: 2026-11-02 · Branch `feature/mile009-instance-view` (lunados.cube) · Prüfung: [verification.json](verification.json), Skript [verify_mile009.py](verify_mile009.py) · Hashes: [MANIFEST.json](MANIFEST.json)

## Prüfung

| Kriterium | Ergebnis |
|---|---|
| Entscheidungen D-1–D-8 (`25133a0`) vor der Spezifikation (`0b5b114`); Q-1–Q-10 (`5ab75cc`) vor den Vektoren; Vektoren, Orakel und Pins (`e842081`) vor dem Printer-Code (`ba33c79`) und vor der G6-Änderung (`bf678a9`) | erfüllt |
| Vektoren, Orakel und Pins seitdem unverändert | erfüllt |
| VP-11: I-01–I-34 34/34 wie das Orakel; 15 Tests, darunter Abgleich der Ergebnisprüfung mit dem LIB-Schema und Farbfreiheit | erfüllt |
| G6: alle Vektoren gleich dem Printer, I-22 deutsch byte-gleich zur CLI; Adapter-Suiten grün (vollständige G6-Suite mit K-17 in TASK-056) | erfüllt |
| VP-10 unverändert: 0.11.0 15/15, 0.10.1 9/9, 0.10.0 16/16 byte-gleich, S-Vektoren 16/16 | erfüllt |
| Sichtprüfung nach [Anleitung](SICHTPRUEFUNG.md): 5/5 ja | erfüllt |
| P0, P1, die übrigen P2-Pakete und G5 seit `main` unverändert; alle Prüfsummenlisten halten | erfüllt |
| Relative Links in docs/, openspec/, VP-11 und Adapter | keine kaputten |

## Chargen

| Mile | Abschlusskriterium | Nachweis |
|---|---|---|
| MILE-009-A | Entscheidungen aufgelöst; Vektoren, Orakel und Pins vor Code | [Spezifikation](../../../P2/visual-printer-instances-v1/VP11_ACCEPTANCE_SPEC.md), [Paket](../../../P2/visual-printer-instances-v1/README.md) |
| MILE-009-B | Vektoren wie das Orakel; vorhandene Printer byte-gleich | [TASK-055](../../05-Tasks/TASK-055-vp11-printer.md) |
| MILE-009-C | G6 = CLI; Sichtprüfung beantwortet | [TASK-056](../../05-Tasks/TASK-056-vp11-g6.md), [Renderings](task057/README.md), [Sichtprüfung](SICHTPRUEFUNG.md) |

## Ergebnis

- **VR-12, V-10, V-11, V-12:** `cube.instances` zeigt eine deklarierte Spur je Instanz in einem eigenen Rahmen: am exklusiven Split je Aktivierung „genommen“ oder „nicht genommen“, am parallelen Join jeden Eingang mit „angekommen“ oder „fehlt“; ein Token einer anderen Instanz steht am fehlenden Eingang als „nicht Teil“. Das Prozessmodell steht getrennt, ohne Spur.
- **Urteile:** nur aus Datensätzen von lunados.lib `analyze.trace-conformance/v1`, gegen Kontext, Spur und Abdeckung geprüft und nie nachgerechnet; ohne Datensatz „nicht geprüft“, nie ein Urteil aus der Zeichnung.
- Zustände unterscheiden sich durch Text und Linienart (durchgezogen, gepunktet, gestrichelt, schraffiert), nicht durch Farbe.

## Grenzen

- Nur lokal (CLI und G6); kein G5, keine Plansichten remote.
- Nur exklusive und parallele Gateways (Grenzen von P1.13); keine Zeitachse, keine Engine-Logs.
- Spezifikation, Orakel und Printer vom selben Autor; die Übereinstimmung kontrolliert Implementierungsunterschiede, nicht die Lesart der Spezifikation. Die LIB-Urteile stammen aus MILE-008.
- Kein bestätigter Prozess-Anwendungsfall; Prüffälle nur aus BPMN-01/02/03 und den MILE-008-Fällen, synthetisch, ohne Kundendaten.

## Offen

`/9` und Plansichten remote (G5), VR-01 (Herkunftslinie in `cube.flow`).
