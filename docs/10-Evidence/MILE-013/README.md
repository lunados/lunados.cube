# MILE-013 · Nachweis

Stand: 2026-11-05 · Branch `feature/mile013-vp077-module-bodies` auf `3d424ce`

## Regression und Tests

| Prüfung | Ergebnis |
|---|---|
| `scripts/pin_076_digests.py --write` auf dem unveränderten Stand (Worktree von `3d424ce`) | 10 Szenarien festgehalten |
| `pin_070…pin_076 --check` auf dem Branch | 14/14, 16/16, 13/13, 14/14, 16/16, 16/16, 10/10 byte-identisch |
| `scripts/run_vectors_ol.py` | 13/13 Status, Codes und Kanten wie das Orakel |
| `python3 -m unittest discover -s tests` in `P2/visual-printer-migration-v1` | 123 Tests OK (Python 3.13) |
| `python3 -m unittest discover -s tests` in `P3/adapters/mcp-local` | 250 Tests OK (Python 3.13) |

Bestätigt in der Adapter-venv auf dem Mac (echtes `mcp`, Python 3.13, 2026-11-05, Nutzer): P2 `visual-printer-migration-v1` 123 Tests OK, P3 `mcp-local` 250 Tests OK. Die ersten Läufe in der Prüfumgebung luden `server.py` mangels `mcp` mit einem Import-Stub.

## Abnahmefall F02 (lunados.explorer)

Funktionsblatt `cases/case-02/F02-relay-metriken.flow.json`, exportiert mit `scripts/print_sheet.py` als `binding-context/10` (Kontext `explorer.F02`, 28 Referenten, 7 lokale Prädikate mit `origin_binding: required`).

| | VP-07.6 | VP-07.7 |
|---|---|---|
| druckbare Abhängigkeiten | 5 von 42 | 42 von 42 |
| P1.14 | PASS | PASS (alle sechs Pläne) |
| `cube.flow` / `cube.phases` | 6 / 1 Panels | 35 / 6 Panels (fünf Druckpläne) |
| `check-panels` | PASS | PASS, Abdeckung vollständig |

Der Explorer packt die Kanten in fünf Druckpläne, weil der Relay in einer Phase an bis zu sieben Objekten hängt und ein Flow-Panel im Budget `detail` höchstens vier Knoten zeigt (VP-04, unverändert).

Sichtprüfung: Core (K), Connector (C) und Toolbox (B) erscheinen mit ihren Typbuchstaben als Modulblöcke; Relay und Connector teilen im Explorer bewusst die Rolle Connector.

## G5 (R8, TASK-074)

Core `P3-MCP-REMOTE/0.9.1-proof` auf Workers Paid (`limits.cpu_ms` 30 000), Cloudflare-Version `999dc4af-37bf-41f2-9da6-296d8bb8797b`; Gateway `0.2.0-proof` unverändert. Remote-Smoke PASS; R8-Live-Skript 33/33 ([Nachweis](../../../P3/remote-mcp-g5/evidence/G5_R8_LIVE_SCRIPT.json), [R8](../../../P3/remote-mcp-g5/G5_R8_ACCEPTANCE.md)). Die bisher am CPU-Budget gescheiterten Aufrufe P-OL-07, P-K07-flow und P-K08-sequence liefen vollständig.
