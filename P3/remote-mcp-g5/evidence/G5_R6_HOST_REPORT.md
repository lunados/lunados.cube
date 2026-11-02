# G5 R6 — Host-Abnahme: relation origin und origin lines

**Datum:** 2026-11-02. **Host:** Codex-G5-Connector über die macOS-Keychain-Bridge. **Bereitgestellt:** privater Core `P3-MCP-REMOTE/0.9.0-proof`, Cloudflare-Version `445c6d50-8d06-4d67-acdd-c246419357c8`; Gateway `0.2.0-proof`. **Erwartungen:** `G5_R6_EXPECTATIONS.json`, vor dem Remote-Code in Commit `58ae4a8` fixiert. **Umfang:** die neun in `scripts/r6_calls.py` als `host` markierten Fälle. Die Argumente wurden aus diesen Fällen unverändert über den Connector übertragen; Folgeaufrufe erhielten das unveränderte Ergebnis des vorherigen Schritts.

## Ergebnisse

| Fall | Host-Beobachtung | Ergebnis |
|---|---|---|
| D-01 | Discovery: Core `0.9.0-proof`, P1.14 `/10`, VP-07.6, zehn Tools; alle fixierten Discovery-Felder gleich | PASS |
| V-HO-01 | `UNRESOLVED`, `P1_ORIGIN_UNDECLARED`; Payload-Digest gleich | PASS |
| V-HO-03 | `PASS`; Payload-Digest gleich | PASS |
| V-HO-05 | `FAIL`; Payload-Digest gleich | PASS |
| P-OL-02 | Source → Views → Check; drei Payload-Digests und SVG-Digest gleich; Check `PASS` | PASS nach Wiederholung |
| P-OL-04 | Source → Views → Check; drei Payload-Digests und SVG-Digests gleich; Check `PASS` | PASS |
| P-OL-06 | Source → Views → Check; drei Payload-Digests und SVG-Digests gleich; Check `PASS` | PASS |
| P-OL-08 | Fixierter Fehler `VP07_ORIGIN_STYLE_CONFLICT`; Payload-Digest gleich | PASS |
| P-OL-11 | Source → Views → Check; drei Payload-Digests und SVG-Digests gleich; Check `PASS` | PASS |

Die 16 Payload-Digests wurden aus den strukturierten Connector-Ergebnissen als kanonisches JSON neu berechnet und mit den fixierten SHA-256-Werten verglichen ([Host-Ergebnisse](G5_R6_HOST_RESULTS.json)). Bei `cube_validate` wurde für diesen Vergleich allein das Transportfeld auf den lokalen Erwartungswert gesetzt, wie im Live-Skript. Die vier `cube_plan_views`-Ergebnisse hatten zusätzlich dieselben SVG-Digests. Das absichtlich fehlerhafte P-OL-08 hatte genau den fixierten Fehlercode.

Beim ersten Host-Aufruf von P-OL-02 stimmte `cube_plan_source`; `cube_plan_views` gab `G5_CORE_UNAVAILABLE` zurück. Die unveränderte Kette wurde unmittelbar wiederholt und traf alle drei fixierten Digests. Dieser erste Abbruch bleibt eine Remote-Abweichung und wird nicht als PASS umgedeutet.

## Live-Skript und Laufzeitgrenze

Das authentifizierte R6-Live-Skript prüfte Discovery, zwölf HO-Validierungen und dreizehn OL-Ketten. Drei vollständige Läufe erreichten jeweils **25/26**:

| Lauf | Abbruch | Übrige Fälle |
|---|---|---|
| `G5_R6_LIVE_SCRIPT.json` | P-OL-07, `cube_plan_views`: `G5_CORE_UNAVAILABLE` | fixierte Ergebnisse |
| `G5_R6_LIVE_SCRIPT_RUN2.json` | V-HO-11, `cube_validate`: `G5_CORE_UNAVAILABLE` | fixierte Ergebnisse |
| `G5_R6_LIVE_SCRIPT_RUN3.json` | P-OL-07, `cube_plan_check`: `G5_CORE_UNAVAILABLE` | fixierte Ergebnisse |

P-OL-07 traf bei zwei gezielten Wiederholungen alle drei Digests und den Check-Status `PASS` ([erster Wiederholungslauf](G5_R6_OL07_RECHECK.json); der zweite liegt nur temporär lokal). Eine weitere gezielte Wiederholung brach bei `cube_plan_views` ab. Der gleichzeitig gelesene Core-Tail belegt für diesen Abbruch `introspection.CpuLimitExceeded` bei 522 ms CPU in der Cloudflare-Version `445c6d50-…`; der sanitisierte Befund steht in `G5_R6_CORE_CPU_EVENT.json`. Für die anderen `G5_CORE_UNAVAILABLE`-Antworten liegt keine eigene Ursache aus dem Core-Tail vor.

Der allgemeine Remote-Smoke-Test bestand: Authentifizierung, Origin-Sperre, zehn Tools, 14 P0-Resources, P1 und bytegleiche VP-06-Ausgabe. **Host-Teilmenge 9/9 wie erwartet nach Wiederholung; kein vollständiger R6-Live-Lauf ohne Remote-Abbruch.** Die CPU-Grenze und die sporadische Core-Nichtverfügbarkeit sind als Abweichung offengelegt. Die Ergebnisse verleihen weder Wahrheit noch Autorität oder Admission.
