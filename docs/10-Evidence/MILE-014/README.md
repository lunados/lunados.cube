# MILE-014 · Nachweis

Stand: 2026-11-05 · Branch `feature/mile014-vp078-x-endpoints`

## Regression und Tests

| Prüfung | Ergebnis |
|---|---|
| `scripts/pin_077_digests.py --write` auf dem unveränderten Stand | 3 Szenarien festgehalten |
| `pin_070…pin_077 --check` | 14/14, 16/16, 13/13, 14/14, 16/16, 16/16, 10/10, 3/3 byte-identisch |
| `scripts/run_vectors_ol.py` | 13/13 |
| P2 `visual-printer-migration-v1` | 131 Tests OK (Python 3.13; `server.py` mit Import-Stub für `mcp`) |
| P3 `mcp-local` | 250 Tests OK (ebenso) |
| G5 `verify_g5.py` | PASS, 24 Vertragstests (Core unverändert `0.9.1-proof`) |

Ein Lauf in der Adapter-venv auf dem Mac steht aus.

## Abnahmefälle (lunados.explorer, `scripts/print_sheet.py`)

| Fall | gedruckt mit 0.7.7 | gedruckt mit 0.7.8 | P1.14 (Pläne) | X-Referenten (P1.6) |
|---|---|---|---|---|
| F01 | 23 von 24 | 24 von 24 | PASS | 1 Admission UNRESOLVED |
| F02 | 42 von 42 | 42 von 42 | PASS | – |
| F03a | 56 von 61 | 61 von 61 | PASS | 3 Admissions UNRESOLVED |
| F04a | 38 von 39 | 39 von 39 | PASS | 1 Admission UNRESOLVED |
| F05 | 27 von 28 | 28 von 28 | PASS | 1 Admission UNRESOLVED |

Die X-Referenten melden `P1_INSTANTIATION_PROFILE_REQUIRED`: Eine Admission ist in P1.6 erst gebunden mit Policy-Scope, Anfrage (X Action), Principal, Entscheidung und Authority bzw. Refusal. Diese Angaben stehen in den Explorer-Blättern noch nicht; der Druck bleibt davon unberührt.
