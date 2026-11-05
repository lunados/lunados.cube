# G5 R9 · MILE-015 TASK-077

Status: **bereitgestellt und live geprüft (51/51)**.

Der private Core `P3-MCP-REMOTE/0.9.2-proof` enthält P1.15 (`binding-context/11`: deklarierte X-Scope-Ketten, P1.6-Referenz v2, Ausgänge einer Admission am exklusiven Gateway; MILE-015) und den Printer VP-07.8 (Profil `P2-VP-MIGRATION/0.7.8`: zehn X-Endpunkte, Source, Cache, Revision; MILE-014). Neu gestaged: `P1/scope-nesting-profile-v1/cube_p115` und die gepinnte Referenz `instantiation_reference_v2.json` (Wrangler-Text-Regel ergänzt). Die Discovery meldet `p115_scope_nesting`. Das Gateway bleibt `0.2.0-proof` mit zehn Tools: Profil und Kontext reicht es unverändert durch, es wird nicht neu bereitgestellt.

## Erwartungen vor der Bereitstellung

`evidence/G5_R9_EXPECTATIONS.json` (aus den lokalen G4/G6-Funktionen, `scripts/r9_expectations.py`): 50 Aufrufe plus Discovery.

| Gruppe | Aufrufe | Zweck |
|---|---|---|
| R8 (R6, R5 schwer, VP-07.7) | 32 | unverändert; alle Payload- und SVG-Digests gleich den R8-Erwartungen (32/32) |
| P1.15 (V-SN-01…V-SN-14) | 14 | alle Vektoren gegen das vorab committete Oracle: Scope-Ketten, Lücken in P1.6, Referenz v2, Ausgänge |
| VP-07.8 (P78-01…P78-04) | 4 | Flow und Phasen mit Admission als Objekt, Flow ohne X-Endpunkt, 0.7.7 bleibt für den X-Endpunkt geschlossen (`VP07_ADAPTER_MAPPING`) |

Host-Teilmenge: die sechs von R8 und V-SN-02, V-SN-08, V-SN-10, V-SN-11, P78-01, P78-02. Höchste lokale CPU-Zeit je Aufruf 0,91 s.

## Offline-Gate

`scripts/verify_g5.py`: `PASS G5 OFFLINE … R9 core 0.9.2-proof`; Assembly 158 Dateien, alle SN-Vektoren durch `dispatch`; Laufzeit-Assets 50 (neu `P115=1`); 25 Vertragstests OK (neu `test_p115_scope_nesting`).

## Schritte für den Nutzer (Repo-Wurzel, Branch `feature/g5-r9`)

```sh
P3/adapters/mcp-local/.venv/bin/python P3/remote-mcp-g5/scripts/verify_g5.py
cd P3/remote-mcp-g5/.g5-runtime && uv run pywrangler deploy && cd -
P3/adapters/mcp-local/.venv/bin/python P3/remote-mcp-g5/scripts/sdk_remote_smoke.py
P3/adapters/mcp-local/.venv/bin/python P3/remote-mcp-g5/scripts/r9_remote_acceptance.py
```

`AIAEAO_G5_URL` und `AIAEAO_G5_TOKEN` wie bisher aus einer sicheren lokalen Quelle. Das Live-Skript schreibt `evidence/G5_R9_LIVE_SCRIPT.json` (nur Digests und Codes). Erwartet: 51/51 (50 Aufrufe und Discovery).

## Ergebnis (2026-11-05)

- Der Nutzer stellte den privaten Core `0.9.2-proof` bereit (Cloudflare-Version `f4458919-1b94-462e-8dc9-2cb95c51ff86`, Upload 8 914 KiB, gzip 2 048 KiB, Worker-Startzeit 1 010 ms). Das Gateway blieb `0.2.0-proof`.
- Allgemeiner Remote-Smoke-Test: `PASS G5 ACTUAL REMOTE MCP: auth, Origin, 10 tools, 14 resources, P0, P1, VP06 byte parity`.
- R9-Live-Skript: **51/51**, Tools und Health wie erwartet ([Nachweis](evidence/G5_R9_LIVE_SCRIPT.json)). Alle R8-Aufrufe wieder gleich, alle SN-Vektoren mit dem erwarteten Status und Code, VP-07.8 druckt die Admission. Längste Aufrufe: P-OL-07 1,08 s, P-K07-flow 1,06 s, P78-01 0,22 s.
- Grenzen nachgeführt in [KNOWN_LIMITS.md](KNOWN_LIMITS.md): ein einzelner vollständiger Lauf, keine Wiederholung und kein Monitoring.
