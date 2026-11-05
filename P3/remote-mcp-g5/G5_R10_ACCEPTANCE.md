# G5 R10 · MILE-016 TASK-080

Status: **bereitgestellt und live geprüft (58/58)**.

Der private Core `P3-MCP-REMOTE/0.9.3-proof` bringt die Landschaftssicht VP-12 (`cube.landscape`, Profil `P2-VP-LANDSCAPE/0.12.0`) und die gepinnte deutsche Locale von VP-09.3 (`vpaxes/locales/de-0093.json`, X × Y) nach G5. Neu gestaged: `P2/visual-printer-landscape-v1/vplandscape`; die Wrangler-Text-Regel deckt jetzt auch `vpaxes/locales` und `vplandscape/locales` ab (Laufzeit-Assets 50 → 53, `P2LOC` 6 → 9). Ohne diese Regel würde VP-09.3 mit `--locale de` auf G5 die Locale nicht finden.

Das **Gateway** wird diesmal mit bereitgestellt: `0.3.0-proof`, weiterhin zehn Tools; `cube_plan_source` kennt den Printer `vplandscape` und die Option `placement_predicates`, `cube_plan_views` die Sicht `cube.landscape`. Ohne neues Gateway würde dessen Schema beides abweisen.

## Erwartungen vor der Bereitstellung

`evidence/G5_R10_EXPECTATIONS.json` (aus den lokalen G4/G6-Funktionen, `scripts/r10_expectations.py`): 57 Aufrufe plus Discovery.

| Gruppe | Aufrufe | Zweck |
|---|---|---|
| R9 | 50 | unverändert; alle Payload- und SVG-Digests gleich den R9-Erwartungen (50/50) |
| VP-12 (L10-01…L10-05) | 5 | Layer-Map mit Default-Schritten; drei Bänder auf Deutsch; Default-Spalten ohne Platzierungsprädikat; `VP12_STEP_UNKNOWN`; sieben Schichten → `VP12_BUDGET_EXCEEDED` |
| VP-09.3 (X10-01, X10-02) | 2 | X × Y:kind und X × Y:referent (leere Spalten aus) mit `locale de`, Statuszeile `X × Y · kanonisch · Morphologie §3.3` |

Host-Teilmenge: die von R9 und L10-01, L10-02, X10-01. Höchste lokale CPU-Zeit je Aufruf 1,38 s (ein R9-Aufruf); die neuen Aufrufe unter 0,05 s.

## Offline-Gate

`scripts/verify_g5.py`: `PASS G5 OFFLINE … R10 core 0.9.3-proof`; Assembly 168 Dateien, Landschaft und Check durch `dispatch`; Laufzeit-Assets 53 (`P2LOC=9`); 26 Vertragstests OK (neu `test_r10_landscape_parity`); Gateway-Tests 6 + 4 OK. Lokal P3 `mcp-local` 256 Tests grün (neu `test_mile016_landscape.py`), VP-12 19 Tests grün.

## Schritte für den Nutzer (Repo-Wurzel, Branch `feature/g5-r10`)

Beide Worker neu bereitstellen, **zuerst den privaten Core**; das Bearer-Secret bleibt.

```sh
P3/adapters/mcp-local/.venv/bin/python P3/remote-mcp-g5/scripts/verify_g5.py
P3/adapters/mcp-local/.venv/bin/python P3/remote-mcp-g5/scripts/verify_release.py --require-npm-lock
cd P3/remote-mcp-g5/.g5-runtime && uv run pywrangler deploy && cd -
cd P3/remote-mcp-g5/gateway && npm ci && npm run check:freeze && npm run deploy && cd -
P3/adapters/mcp-local/.venv/bin/python P3/remote-mcp-g5/scripts/sdk_remote_smoke.py
P3/adapters/mcp-local/.venv/bin/python P3/remote-mcp-g5/scripts/r10_remote_acceptance.py
```

`AIAEAO_G5_URL` und `AIAEAO_G5_TOKEN` wie bisher aus einer sicheren lokalen Quelle. Das Live-Skript schreibt `evidence/G5_R10_LIVE_SCRIPT.json` (nur Digests und Codes). Erwartet: 58/58 (57 Aufrufe und Discovery), Tools wie erwartet, Health `0.3.0-proof`. Danach den G5-Connector im Claude-Host neu verbinden (der Host hält die Tool-Schemas im Cache).

## Ergebnis (2026-11-05)

- Der Nutzer stellte den privaten Core `0.9.3-proof` und das Gateway `0.3.0-proof` bereit (Gateway-Version `296e448c-76d6-487e-8f74-527ce87d1722`; die Core-Versions-ID wurde nicht übermittelt, die Discovery meldet `P3-MCP-REMOTE/0.9.3-proof`).
- Allgemeiner Remote-Smoke-Test: `PASS G5 ACTUAL REMOTE MCP: auth, Origin, 10 tools, 14 resources, P0, P1, VP06 byte parity`.
- R10-Live-Skript: **58/58**, Tools und Health (`0.3.0-proof`) wie erwartet ([Nachweis](evidence/G5_R10_LIVE_SCRIPT.json)). Alle R9-Aufrufe wieder gleich, die Landschaft (L10-01…L10-03) byte-gleich mit lokal, beide Fehlerfälle mit dem erwarteten Code, X × Y mit deutscher Locale. Längste Aufrufe: P-OL-07 1,69 s, P-K07-flow 1,33 s; neue Aufrufe höchstens 0,22 s (L10-01).
- Grenzen nachgeführt in [KNOWN_LIMITS.md](KNOWN_LIMITS.md): ein einzelner vollständiger Lauf, keine Wiederholung und kein Monitoring.
