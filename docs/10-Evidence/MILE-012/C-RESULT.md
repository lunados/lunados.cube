# MILE-012 — Abschlussnachweis

Stand: 2026-11-02 · Branch `feature/mile012-consolidation` (lunados.cube) · Prüfung: [verification.json](verification.json), Skript [verify_mile012.py](verify_mile012.py) · Hashes: [MANIFEST.json](MANIFEST.json)

## Prüfung

| Kriterium | Ergebnis |
|---|---|
| Plan (`f78497d`) vor Ledger und Grenzen-Seite (`0916995`), RELEASE_INDEX (`998943f`) und Ausgangswert (`548bc41`) | erfüllt |
| Seit MILE-011 (`0d15c4b`) nur Dokumente und Nachweise geändert; kein Code, keine Payloads | erfüllt |
| Jede Zahl in `G5_ACCEPTANCE.md` und `KNOWN_LIMITS.md` gegen die Nachweisdateien (Offline, Live, Host, CPU-Ereignisse, Ausgangswert) | 11/11 erfüllt |
| Live-Ausgangswert nur mit erwarteten Abweichungen (Versionsangabe in D-01, `G5_CORE_UNAVAILABLE`) | erfüllt |
| `RELEASE_INDEX.md`: Links lösen auf, alle 19 Versionsangaben stehen im Code | erfüllt |
| Alle Prüfsummenlisten halten; keine kaputten Links | erfüllt |

## Ergebnis

- **G5-Ledger:** [`G5_ACCEPTANCE.md`](../../../P3/remote-mcp-g5/G5_ACCEPTANCE.md) nennt R5 und R6 mit Offline-, Live- und Host-Ergebnissen; der Produktivbetrieb heißt R7 und ist nicht geplant.
- **Bekannte Grenzen:** [`KNOWN_LIMITS.md`](../../../P3/remote-mcp-g5/KNOWN_LIMITS.md) mit CPU-Abbrüchen, Abbruch ohne Ursache, Bearer-Token, Versionsangaben, Ausgangswert und dem lokalen Ausweg.
- **Gesamtüberblick:** [`RELEASE_INDEX.md`](../../../RELEASE_INDEX.md) für alle Schichten nach MILE-011.
- **Ausgangswert:** R5 86/88 und R6 25/26 gegen `0.9.0-proof`, Token unverändert; Abweichungen vom Nutzer als bekannte Grenzen hingenommen.

## Grenzen

- Die Abschlussprüfung liest Nachweise; sie wiederholt keine Live-Aufrufe und keine Code-Gates (kein Code geändert).
- Integration in `main` und Tag macht der Nutzer nach diesem Commit; vorgeschlagener Tag `cube-2026-11-02`.

## Offen

G5-Produktion (CPU-Budget, OAuth, Rate-Limits, Betrieb) als ungeplanter Kandidat nach dem Test des aktuellen Stands; Quellenabgleich mit Fremdmodellen durch den Nutzer.
