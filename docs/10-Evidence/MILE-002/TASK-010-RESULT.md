# TASK-010 — Ergebnis: Fallvertrag v2 und erster lokaler Lauf

Stand: 2026-11-01 · Ausgeführt durch den Agenten in der Linux-VM der Claude-Desktop-App mit der [Offline-Agent-Umgebung](../../../scripts/dev/README.md).

## Umgebung

| Angabe | Wert |
|---|---|
| Repository HEAD beim Lauf | `cf2abce` (Branch `feature/mile002-grammar-sampling`) |
| Nicht committete P3-Adapteränderungen | `server.py`, `surface.py` (+5/−2), neue `validation_discovery.py`; Diff-SHA-256 `b71ba683a0844dc2fd4f6c3e89d727a72eb9bbf44c3d06259bfc89a6e0beeafb`. Im Bericht über `snapshot.files` erfasst. |
| Python / MCP-SDK | 3.13.16 (python-build-standalone, Linux x86_64) / mcp 2.0.0, Pakete nach `scripts/dev/requirements-agent.lock` |
| Adapter laut Discovery | `P3-MCP-LOCAL/0.3.0-rc1`, 10 Tools |
| Quellsnapshot | `files_sha256` `bafa210dfccc…`, 836 Dateien, während beider Läufe unverändert |

Die Mac-Adapter-venv (Python 3.13.7) wurde nicht verwendet; Paketversionen sind identisch gepinnt, die Patchversion von Python weicht ab.

## Läufe

| Lauf | Bericht | Fälle | Ergebnis |
|---|---|---|---|
| Pilot v2 | [task010-pilot-report.json](task010-pilot-report.json) (`research-run/2`) | A-PILOT-01-relation-declared | PASS, keine Diagnosen; Erwartung erfüllt in 2/2 frischen Verbindungen |
| v1-Wiederholung | [task010-v1-replay-report.json](task010-v1-replay-report.json) (`research-run/1`) | P1-method-arity-negative, P1-mode-display, P1-mode-unbound | FAIL/P1_METHOD_SIGNATURE, PASS, UNRESOLVED/P1_QUALIFIER_PROFILE_MISSING — identisch mit MILE-001 |

Beide Läufe: `readiness_checks_passed: true`, Wiederholungen semantisch gleich, Konfigurationsfehler-Kontrolle `TOOL_ERROR`/`P1_MCP_CONFIG_INVALID`, Nichtverfügbarkeitskontrolle `UNAVAILABLE`.

Pilot-Stufen: syntax, structure, concept_resolution, referent_binding, predicate_typing, scope_consistency PASS; method_typing und qualifier_typing NOT_EVALUATED (nicht anwendbar). Gegenüber der historischen Probe mit identischem Ausdruck wechselt nur predicate_typing von UNRESOLVED zu PASS — allein durch den deklarierten Prädikatvertrag.

## Einordnung

Das PASS belegt die deklarative Typisierung dieses Ausdrucks im gebundenen Kontext und die Funktionsfähigkeit des v2-Herkunftsvertrags. Es belegt keine Wahrheit der Beziehung, keinen Vergleichsbefund und keine Grammatikabdeckung. Unit-Tests: 22/22 in der Agent-Umgebung.

Wiederholen: siehe [Fälle im Fallvertrag v2](../../09-Research/grammar-sampling/cases/README.md#ausführen).
