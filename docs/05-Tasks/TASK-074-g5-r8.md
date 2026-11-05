# TASK-074 — G5 R8: Core 0.9.1-proof und CPU-Budget

Mile: [MILE-013](../02-Milestones/MILE-013-printer-module-bodies.md) (D-4) · Aufwand: 0,25–0,5 PT · Status: vorbereitet, Bereitstellung ausstehend

## Ziel und Arbeit

Privaten G5-Core mit VP-07.7 neu bauen (`P3-MCP-REMOTE/0.9.1-proof`), `limits.cpu_ms` auf 30 000 ms setzen (Workers Paid seit 2026-11-05), Erwartungen vor der Bereitstellung fixieren (R8: alle R6-Aufrufe, die zwei schweren R5-Aufrufe, fünf VP-07.7-Aufrufe), Live-Skript `r8_remote_acceptance.py`. Gateway unverändert.

## Ergebnis und Akzeptanz

- Offline: `verify_g5.py` PASS (24 Vertragstests), `verify_release.py` PASS (45 Dateien); Erwartungen 32 Aufrufe, R6- und R5-Digests unverändert.
- Live (ausstehend, Nutzer): Remote-Smoke PASS, R8 33/33 ohne `G5_CORE_UNAVAILABLE` ([R8](../../P3/remote-mcp-g5/G5_R8_ACCEPTANCE.md)); danach `KNOWN_LIMITS.md` nachführen.

## Abhängigkeiten und Grenze

[TASK-073](TASK-073-vp077-module-bodies.md). Keine Änderung an P0, P1, P2 oder am Gateway.
