# MILE-011 — Abschlussnachweis

Stand: 2026-11-02 · Branch `feature/mile011-relation-origin` (lunados.cube) · Prüfung: [verification.json](verification.json), Skript [verify_mile011.py](verify_mile011.py) · Hashes: [MANIFEST.json](MANIFEST.json)

## Prüfung

| Kriterium | Ergebnis |
|---|---|
| Entscheidungen D-1–D-8 (`79da657`) vor den Spezifikationen (`64cf9c0`); Q (`e2cf8e3`) vor Orakeln, Vektoren und Pins (`bfe5308`); diese vor dem Code von P1.14 (`8dd8b94`) und VP-07.6 (`177e24d`); R6-Erwartungen (`58ae4a8`) vor dem G5-Code (`c120c3c`); Live (`4d18689`) vor der Sichtprüfung (`e860778`) | erfüllt |
| Orakel HO und OL, Pins 0.7.0–0.7.5 und R6-Erwartungen seit dem Festschreiben unverändert | erfüllt |
| P1.14: 11 Tests einschließlich Orakel HO-01–HO-12; P1.13 9/9, P1.12 21/21; P1.13-Regeln unter `/10` wie unter `/9`; Adapter 250 Tests | erfüllt |
| VP-07: Pins 0.7.0–0.7.5 byte-gleich (89 Szenarien); VP-07.6 13/13 mit Prüfung je Kante (Herkunft, Linienart, Text) gegen das Orakel, 11 Tests | erfüllt |
| G5 offline: `verify_g5`, Gateway-Tests, `verify_release` (40 Dateien), R6-Parität 26/26, 87 R5-Aufrufe byte-gleich | erfüllt |
| G5 live (Kern `0.9.0-proof`, Cloudflare-Version `445c6d50-…`): drei Skriptläufe je 25/26, jede Abweichung `G5_CORE_UNAVAILABLE`; Host-Teilmenge 9/9 mit 16 Payload-Digests ([Host-Bericht R6](../../../P3/remote-mcp-g5/evidence/G5_R6_HOST_REPORT.md)) | erfüllt mit dokumentierter Grenze |
| Sichtprüfung S-1–S-6 durch den Nutzer: alle **ja** ([Sichtprüfung](visual-check/SICHTPRUEFUNG.md)) | erfüllt |
| P0, P1.1–P1.13, P2 außer `vpmigration`, `scripts/` und `RELEASE_INDEX.md` seit `ec18401` unverändert; geändert nur P1.14, `vpmigration`, lokaler Adapter und G5; alle Prüfsummenlisten halten | erfüllt |
| Relative Links in docs/, openspec/, P1.14, `vpmigration` und G5 | keine kaputten (Links ins Nachbar-Repo lunados.lib hier nicht geprüft) |

## Chargen

| Mile | Abschlusskriterium | Nachweis |
|---|---|---|
| MILE-011-A | Entscheidungen aufgelöst; Orakel, Vektoren und Pins vor Code | [P1.14-Spezifikation](../../../P1/relation-origin-profile-v1/P1_14_ACCEPTANCE_SPEC.md), [VP-07.6-Spezifikation](../../../P2/visual-printer-migration-v1/VP07_6_ACCEPTANCE_SPEC.md), [Vorher-Lauf](../../../P1/relation-origin-profile-v1/fixtures/baseline_p113.json) |
| MILE-011-B | Prüffälle wie das Orakel; P1.1–P1.13 unverändert | [TASK-065](../../05-Tasks/TASK-065-p114-profile.md), [Regelabdeckung](../../../P1/relation-origin-profile-v1/RULE_COVERAGE.md) |
| MILE-011-C | Vektoren wie das Orakel, ältere Profile byte-gleich, G5 = lokal, Sichtprüfung, `all_ok` | [TASK-066](../../05-Tasks/TASK-066-vp076-printer.md), [G5 R6](../../../P3/remote-mcp-g5/G5_R6_ACCEPTANCE.md), [verification.json](verification.json) |

## Ergebnis

- **Herkunft prüfen (US-032):** P1.14 mit `binding-context/10`. Für Prädikate mit `origin_binding: required` ergibt eine Beziehung ohne Herkunft UNRESOLVED (`P1_ORIGIN_UNDECLARED`), eine Ableitung ohne Grundlage ebenso (`P1_ORIGIN_BASIS_MISSING`), ein fremder Wert FAIL (`P1_ORIGIN_INVALID`). C4-03 (`api → db`) besteht nicht mehr stillschweigend; mit `origin="derived"` und Grundlage besteht es.
- **Herkunftslinie (US-033):** `cube.flow` 0.7.6 zeichnet jede Kante nach ihrer gebundenen Herkunft (durchgezogen, gestrichelt, gepunktet), schreibt die Herkunft als Text an die Kante und liest auch Aussagenmengen und Verdichtungen aus lunados.lib. Lokal (CLI, G4, G6) und remote (G5).
- **Befunde bei der Prüfung in TASK-068:** `VP07_SHA256SUMS.txt` deckte acht geänderte Dateien nicht mehr und wurde nachgezogen; der Orakel-Lauf prüfte nur Status und Codes und prüft jetzt auch jede Kante. Ein Fehler aus TASK-064 (HO-12 und OL-07 setzten `origin_binding` nicht, weil GM-pos seine Prädikate importiert) wurde in TASK-065 an der Eingabe behoben, nicht am Orakel.

## Grenzen

- Ein Profil verhindert keine falsche Angabe `origin=declared`; dafür fehlt der Abgleich mit dem Quellmodell.
- G5: kein vollständiger Live-Lauf ohne Abbruch. P-OL-07 überschritt die CPU-Grenze des Workers (522 ms); einmal brach auch V-HO-11 ab, ohne Ursache im Core-Log. Die Host-Abnahme lief über den Codex-Connector; P-OL-02 traf erst nach Wiederholung.
- Unter `locale de` bleibt die Legendenüberschrift englisch (`VP07_LOCALE_FALLBACK`); in der Sichtprüfung angenommen.
- Alle Fälle synthetisch, ohne Kundendaten; alles bleibt `declared_unverified`.

## Offen

Quellenabgleich mit Fremdmodellen; Host-Vergleich (ChatGPT, Grok); Produktionsfreigabe von G5 einschließlich CPU-Budget (`limits.cpu_ms`).
