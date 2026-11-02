# MILE-010 — Abschlussnachweis

Stand: 2026-11-02 · Branch `feature/mile010-remote-plan-views` (lunados.cube) · Prüfung: [verification.json](verification.json), Skript [verify_mile010.py](verify_mile010.py) · Hashes: [MANIFEST.json](MANIFEST.json)

## Prüfung

| Kriterium | Ergebnis |
|---|---|
| Entscheidungen D-1–D-8 (`c44a89d`) vor dem Spezifikationsentwurf (`7cc8505`); Q-1–Q-10 (`d7ed25a`) vor den Erwartungen (`a29450a`); Erwartungen vor Kern- und Gateway-Code (`d5124d0`); Live-Läufe (`75eb528`) vor dem Host-Bericht (`31d9686`) | erfüllt |
| Erwartungen, Aufrufliste und Erwartungsskript seit `a29450a` unverändert | erfüllt |
| G5-Gates in einer Kopie von HEAD: Offline-Parität R5 88/88 (CPU höchstens 0,78 s, Regel < 2 s), `verify_g5` (21 Vertragstests, Asset-Prüfung), Gateway-Tests, `verify_release` (34 Dateien), Parität G4/G5 22/22, 10/10, 15/15, 21/21 | erfüllt |
| Live per Skript (vier Läufe, je 88 Aufrufe): 87, 87, 86, 87 wie erwartet; jede Abweichung nur `P-K07-flow` oder `P-K08-sequence` mit `isError` (`G5_CORE_UNAVAILABLE`, `exceededCpu`, [Spezifikation §10](../../../P3/remote-mcp-g5/G5_R5_ACCEPTANCE_SPEC.md)); Gateway-Tools und `/health`-Version wie erwartet | erfüllt (dokumentierte Grenze) |
| Host-Abnahme über den Connector: Teilmenge 7/7, 18/18 Prüfzeilen PASS ([Host-Bericht R5](../../../P3/remote-mcp-g5/evidence/G5_R5_HOST_REPORT.md)) | erfüllt |
| P0, P1, P2, lokaler Adapter, `scripts/` und `RELEASE_INDEX.md` seit `main` unverändert; geändert nur `P3/remote-mcp-g5`; alle Prüfsummenlisten halten | erfüllt |
| Relative Links in docs/, openspec/ und `P3/remote-mcp-g5` | keine kaputten (drei Links ins Nachbar-Repo lunados.lib hier nicht geprüft) |

## Chargen

| Mile | Abschlusskriterium | Nachweis |
|---|---|---|
| MILE-010-A | Entscheidungen aufgelöst; Erwartungen vor Code committet | [Spezifikation G5 R5](../../../P3/remote-mcp-g5/G5_R5_ACCEPTANCE_SPEC.md), [Erwartungen](../../../P3/remote-mcp-g5/evidence/G5_R5_EXPECTATIONS.json) |
| MILE-010-B | Offline grün, Remote = lokal für alle Vektoren, Laufzeit gemessen | [Offline-Parität](../../../P3/remote-mcp-g5/evidence/G5_R5_OFFLINE_PARITY.json), [TASK-060](../../05-Tasks/TASK-060-g5-core-gateway.md) |
| MILE-010-C | Live-Abnahme wie erwartet; Bericht R5; `all_ok` | [Skript-Lauf 4](../../../P3/remote-mcp-g5/evidence/G5_R5_LIVE_SCRIPT_RUN4.json), [Host-Bericht R5](../../../P3/remote-mcp-g5/evidence/G5_R5_HOST_REPORT.md), [verification.json](verification.json) |

## Ergebnis

- **`/9` remote (US-030):** `cube_validate` im G5-Kern `P3-MCP-REMOTE/0.8.0-proof` prüft `binding-context/9` mit dem unveränderten P1.13-Profil; die Discovery nennt `p113_control_flow` mit den vier Diagnosen und `false` für Spur- und Bedingungsauswertung.
- **Plansichten remote (US-031):** `cube_plan_source`, `cube_plan_views` und `cube_plan_check` im Gateway `0.2.0-proof`, mit VP-07 bis VP-11 und denselben Argumenten, Grenzen, Fehlercodes und Bytes wie lokal; die Discovery meldet `remote_available: true`.
- **Grenze:** Die CPU-Grenze des Cloudflare-Workers reicht nicht für die größte Plansicht (`cube_plan_check` auf 26 `cube.flow`-Panels). Ein solcher Aufruf endet sauber mit `G5_CORE_UNAVAILABLE`; nichts wird gekürzt oder verändert. D-6 wurde revidiert: alle Sichten bleiben remote.

## Grenzen

- G5 bleibt ein Proof (`G5_PROOF_NOT_PRODUCTION_AUTHORIZED`, Release `remote_proof_not_accepted`); keine Änderung an Authentifizierung oder `cube.lunados.net`.
- Rechenzeit offline mit CPython gemessen, nicht mit Pyodide; die Live-Läufe zeigen die tatsächliche Grenze nur für die geprüften Vektoren.
- Host-Abnahme nur mit Claude als Host und nur für die Teilmenge, deren Argumente sich im Host übergeben lassen (CL-3); die übrigen Aufrufe deckt das Abnahmeskript ab.
- Die Abschlussprüfung lief auf dem Mac des Nutzers mit der Adapter-venv (CPython 3.13.7); in der Agent-VM war sie bis auf die Rechenzeitregel ebenfalls grün, die dort an einer gedrosselten VM scheiterte (7,1 s bei identischem Code). Die Bereitstellung selbst wird nicht wiederholt.
- Alle Fälle synthetisch, ohne Kundendaten.

## Offen

VR-01 (Herkunftslinie in `cube.flow`); Produktionsfreigabe von G5 (OAuth, Mandantentrennung, Rate-Limits, CPU-Budget).
