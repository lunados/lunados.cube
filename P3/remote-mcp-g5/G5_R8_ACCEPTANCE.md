# G5 R8 · MILE-013 TASK-074

Status: **bereitgestellt und live geprüft (33/33)**.

Der private Core `P3-MCP-REMOTE/0.9.1-proof` enthält den Printer VP-07.7 (Profil `P2-VP-MIGRATION/0.7.7`: Core, Connector, Toolbox, Adapter, Grant, Evidence, Content). Seit 2026-11-05 läuft das Konto auf Workers Paid; `python-core/wrangler.jsonc` setzt `limits.cpu_ms` ausdrücklich auf 30 000 ms (Standard von Workers Paid, deckelt zugleich die Kosten je Aufruf). Das Gateway bleibt `0.2.0-proof` mit zehn Tools; es wird nicht neu bereitgestellt.

## Erwartungen vor der Bereitstellung

`evidence/G5_R8_EXPECTATIONS.json` (aus den lokalen G4/G6-Funktionen, `scripts/r8_expectations.py`): 32 Aufrufe plus Discovery.

| Gruppe | Aufrufe | Zweck |
|---|---|---|
| R6 (HO-01…HO-12, OL-01…OL-12) | 25 | unverändert; Payload- und SVG-Digests gleich den R6-Erwartungen (25/25) |
| R5 schwer (P-K07-flow, P-K08-sequence) | 2 | brachen im freien CPU-Budget ab; Digests gleich den R5-Erwartungen |
| VP-07.7 (P77-01…P77-05) | 5 | Flow mit Herkunftslinien, Phasen, Aussagenpfad, 0.7.6 bleibt geschlossen, X-Endpunkt bleibt ungemappt |

Zusammen mit P-OL-07 (R6) prüft R8, ob die bisherigen `G5_CORE_UNAVAILABLE`-Abbrüche mit dem neuen CPU-Budget verschwinden. Host-Teilmenge: D-01, P-OL-07, P-K07-flow, P77-01, P77-02, P77-04.

## Offline-Gate

`scripts/verify_g5.py`: `PASS G5 OFFLINE … R8 core 0.9.1-proof`, Laufzeit-Assets geprüft, 24 Vertragstests OK.

## Schritte für den Nutzer (Repo-Wurzel, Branch `feature/mile013-g5-r8`)

```sh
P3/adapters/mcp-local/.venv/bin/python P3/remote-mcp-g5/scripts/verify_g5.py
cd P3/remote-mcp-g5/.g5-runtime && uv run pywrangler deploy && cd -
P3/adapters/mcp-local/.venv/bin/python P3/remote-mcp-g5/scripts/sdk_remote_smoke.py
P3/adapters/mcp-local/.venv/bin/python P3/remote-mcp-g5/scripts/r8_remote_acceptance.py
```

`AIAEAO_G5_URL` und `AIAEAO_G5_TOKEN` wie bisher aus einer sicheren lokalen Quelle. Das Live-Skript schreibt `evidence/G5_R8_LIVE_SCRIPT.json` (nur Digests und Codes). Erwartet: 33/33.

## Ergebnis (2026-11-05)

- Der Nutzer stellte den privaten Core `0.9.1-proof` bereit (Cloudflare-Version `999dc4af-37bf-41f2-9da6-296d8bb8797b`, Upload 8 887 KiB, gzip 2 043 KiB, Worker-Startzeit 690 ms; `limits.cpu_ms` wurde angenommen). Das Gateway blieb `0.2.0-proof`.
- Allgemeiner Remote-Smoke-Test: `PASS G5 ACTUAL REMOTE MCP: auth, Origin, 10 tools, 14 resources, P0, P1, VP06 byte parity`.
- R8-Live-Skript: **33/33**, Tools und Health wie erwartet ([Nachweis](evidence/G5_R8_LIVE_SCRIPT.json)). Die bisher abgebrochenen Aufrufe liefen vollständig: P-OL-07 (1,07 s), P-K07-flow (1,03 s), P-K08-sequence (0,15 s); alle Payload- und SVG-Digests gleich den lokalen Erwartungen.
- Grenzen nachgeführt in [KNOWN_LIMITS.md](KNOWN_LIMITS.md): ein einzelner vollständiger Lauf, keine Wiederholung und kein Monitoring.
