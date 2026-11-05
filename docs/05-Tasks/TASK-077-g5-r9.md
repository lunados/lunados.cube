# TASK-077 — G5 R9: Core 0.9.2-proof mit P1.15 und VP-07.8

Mile: [MILE-015](../02-Milestones/MILE-015-scopes-and-admission-outcomes.md) (G5-Schritt; nimmt VP-07.8 aus MILE-014 mit) · Aufwand: 0,25–0,5 PT · Status: erledigt, 2026-11-05

## Ziel und Arbeit

Privaten G5-Core neu bauen (`P3-MCP-REMOTE/0.9.2-proof`): P1.15 und Referenz v2 stagen, Wrangler-Text-Regel und Asset-Prüfung ergänzen, Discovery `p115_scope_nesting`. Erwartungen vor der Bereitstellung fixieren (R9: alle R8-Aufrufe, SN-01…SN-14, vier VP-07.8-Aufrufe), Live-Skript `r9_remote_acceptance.py`. Gateway unverändert.

## Ergebnis und Akzeptanz

- Offline: `verify_g5.py` PASS (25 Vertragstests), 50 Erwartungen, R8-Digests 32/32 unverändert ([R9](../../P3/remote-mcp-g5/G5_R9_ACCEPTANCE.md)).
- Live (Nutzer, Cloudflare-Version `f4458919-…`): Remote-Smoke PASS, R9 **51/51** ([Nachweis](../../P3/remote-mcp-g5/evidence/G5_R9_LIVE_SCRIPT.json)); `KNOWN_LIMITS.md` nachgeführt.

## Abhängigkeiten und Grenze

[TASK-076](TASK-076-p115-scope-nesting.md), [TASK-075](TASK-075-vp078-x-endpoints.md). Keine Änderung an P0, P1, P2 oder am Gateway.
