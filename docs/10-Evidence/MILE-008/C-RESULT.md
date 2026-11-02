# MILE-008 — Abschlussnachweis

Stand: 2026-11-02 · Branches `feature/mile008-control-flow` (lunados.cube), `codex/task-051-trace-conformance` (lunados.lib) · Prüfung: [verification.json](verification.json), Skript [verify_mile008.py](verify_mile008.py) · Hashes: [MANIFEST.json](MANIFEST.json)

## Prüfung

| Kriterium | Ergebnis |
|---|---|
| Entscheidungen D-1–D-8 (`460592a`) vor den Prüffällen; 27 Prüffälle vor der Spezifikation (`aefe6aa` vor `ff31bd5`); KF-Orakel vor dem Profilcode (`d33f22c` vor `9222424`); LIB-Orakel und Fälle vor dem Evaluator (`ebb3110` vor `d823a4a`); Wiederholungserwartung vor dem Adapter (`76e5ac1` vor `70d0469`) | erfüllt |
| Erwartungen seitdem unverändert; LIB-Orakel nach dem Evaluator in einer Zeile korrigiert (`5511574`), Erwartungen unverändert, offengelegt | erfüllt, mit Befund |
| P1.13: KF-01–KF-09 9/9, 18 Tests; alle früheren P1-Suiten und -Vektoren grün | erfüllt |
| lunados.lib `analyze.trace-conformance/v1`: 18/18, Differenzprüfung 471, `verify.py --cube` 159/159 | erfüllt |
| Adapter: `/9` in `cube_validate` und Discovery, MILE-005–008-Adapter- und Discovery-Tests grün; G5 unverändert (`/9` dort geschlossen) | erfüllt |
| Wiederholung: 7/7 über lokales MCP in zwei Verbindungen, Readiness bestanden; LIB-Teil 3/3 | erfüllt |
| P0, P1.1–P1.12, P2 und G5 seit `main` unverändert; alle Prüfsummenlisten halten | erfüllt |
| Relative Links in docs/, openspec/, P1.13 und Adapter (ohne eingefrorene P0-Kopie) | keine kaputten |

## Chargen

| Mile | Abschlusskriterium | Nachweis |
|---|---|---|
| MILE-008-A | Fälle und Erwartungen vor der Spezifikation; Detailfragen entschieden | [Prüffälle](../../09-Research/control-flow/CHECK-CASES.md), [Baseline 27/27](task048-baseline-check.json), [Spezifikation](../../../P1/control-flow-profile-v1/P1_13_ACCEPTANCE_SPEC.md) |
| MILE-008-B | Orakel vor Code; Profil und LIB grün | [Prüfung der Fremdumsetzung](TASK-052-REVIEW.md), [LIB-Nachweis](TASK-051-LIB.md) |
| MILE-008-C | `/9` lokal; BPMN-Fälle wie vorab erwartet | [Wiederholung](task052-rerun/README.md) |

## Ergebnis

- **G-07:** Ein `binding-context/9` deklariert exklusive und parallele Gateways mit Flüssen, Bedingungsreihenfolge und Default. P1.13 lehnt fehlerhafte Deklarationen ab und meldet Spur-Aussagen an nicht deklarierte Flüsse (`P1_FLOW_UNDECLARED`); `/8` bleibt unverändert.
- **BPMN-01:** Die Leitung an Ship und der unbekannte Fluss bestanden in MILE-002 mit PASS, jetzt FAIL. Zwei Pfade für eine Aktivierung meldet die LIB-Prüfung als FAIL `exclusive_two_paths`.
- **BPMN-02:** Startet Ship, obwohl am Join ein Eingang fehlt, ist das FAIL `join_incomplete`; wartet der Join noch, ist es PASS `join_waiting`. Beide nennen den fehlenden Eingang.
- Bedingungen werden nirgends ausgewertet; LIB liest nur aufgezeichnete Ergebnisse, fehlt eines, ist das Ergebnis UNRESOLVED.

## Befunde aus der Prüfung

1. und 2. CF-2 deckte einen einzelnen unbedingten Ausgang und `condition_ref` am Default nicht ab: als CF-2a/2b in §8 der Spezifikation präzisiert, so wie beide Umsetzungen und die Fälle es schon verlangen.
3. LIB-Orakel nach dem Evaluator korrigiert, ohne Einfluss auf die Erwartungen: offengelegt.
4. 31 Sekunden zwischen KF-Orakel und Profilcode: Reihenfolge formal eingehalten, Unabhängigkeit aus der Historie nicht belegbar.
5. Dokumentationslücken: nachgezogen (Task-Ergebnisse, Nachverfolgung, LIB-README `f9dfb20`, Pfad in TASK-051-LIB.md). Die Läufe von TASK-050 sind in [verification.json](verification.json) wiederholt.
6. Fremdcommits ohne Angabe zum ausführenden Agenten: festgehalten.

## Grenzen

- Nur lokal (G4 und LIB); G5, Host-Abnahme und Darstellung fehlen.
- Nur exklusive und parallele Gateways; keine inklusiven, ereignisbasierten oder komplexen Gateways, kein Instanzabschluss, keine Kompensation.
- Handgeschriebene, synthetische Spuren ohne Kundendaten; Engine-Logs (Korrelation, Zeitstempel) ungeprüft.
- Profil und LIB von zwei externen Agenten umgesetzt, Prüffälle und Spezifikation von mir; die Übereinstimmung kontrolliert Unterschiede zwischen den Umsetzungen, nicht die Fälle selbst.
- Der Prozessnutzen bleibt laut Lernbilanz an einen bestätigten Anwendungsfall gebunden.

## Offen

VR-12 (Instanzsicht mit Join-Status je Eingang und genommenem Pfad), `/9` remote (G5), VR-01 (Herkunftslinie in `cube.flow`), Plansichten remote.
