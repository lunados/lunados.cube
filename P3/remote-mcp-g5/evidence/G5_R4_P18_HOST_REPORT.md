# G5 R4 — AIAEAO Cube P1.8 Host-Abnahme (Simulation Profile)

**Gesamtstatus: PASS**

| Feld | Wert |
|---|---|
| Datum | 2026-10-25, ca. 20:38–20:45 MEZ |
| Connector | ausschließlich `AIAEAO Cube G5 Remote` (`transport: remote_mcp_streamable_http`) |
| Remote-Release | `P3-MCP-REMOTE/0.2.0-proof`, `remote_proof_not_accepted`, `G5_PROOF_NOT_PRODUCTION_AUTHORIZED` |
| Quellstand | `feature/p18-simulation-profile` @ `b94a5a8`, in `main` gemergt; nur Python-Core neu deployt, Gateway unverändert |
| Vektoren | `P1/simulation-profile-v1/fixtures/s01_s17_materialized.json`, unverändert gesendet; Erwartungen aus `oracles/independent_s01_s17.json` (vor dem Code festgeschrieben) |

## 1. Oberfläche (P1.8-14)

`cube_discover_surface`: `release.version` und `remote_adapter.version` = `P3-MCP-REMOTE/0.2.0-proof`; neuer Deskriptor `p18_simulation` mit `profile P1.8/simulation-profile-v1`, `activation explicit_context_format_3_only`, `scenario_modes [simulation, replay]`, `evaluation_performed_by_cube false`, `library_resolution format_check_only`, Warrant, Authority und Admission `NOT_EVALUATED`. `p16_instantiation` unverändert. **PASS**

## 2. S-01 … S-17 (19 `cube_validate`-Aufrufe inkl. Regression)

| ID | Erwartet | Beobachtet | `declared_context_sha256` | Status |
|---|---|---|---|---|
| S-01 | PASS | PASS | `f52d1922…d98e` | PASS |
| S-02 | UNRESOLVED · `METHOD_RETURN_UNDECLARED` | ✓ | `8dc73279…9363` | PASS |
| S-03 | FAIL · `METHOD_RETURN_TYPE` | ✓ | `c3bd73d7…7c29` | PASS |
| S-04 | UNRESOLVED · `PREDICATE_PROFILE_MISSING` | ✓ (nested `rel` bleibt untypisiert) | `f52d1922…d98e` | PASS |
| S-05 | PASS | PASS | `13600f1a…986f` | PASS |
| S-06 | FAIL · `SCENARIO_WORLD_VIOLATION` | ✓ (`/subject/arguments/0`, `a1`) | `0ab0865a…010f` | PASS |
| S-07 | FAIL · `SCENARIO_MODE` | ✓ (+ `P1_METHOD_SIGNATURE`) | `cdcfb415…db17` | PASS |
| S-08 | FAIL · `SCENARIO_MODE` | ✓ (`operative`) | `24af0bab…7069` | PASS |
| S-09 | PASS, `evaluation_performed_by_cube: false` | ✓ | `e210b074…aa3b` | PASS |
| S-10 | UNRESOLVED · `EVALUATION_WITNESS_MISSING` | ✓ | `e8203dd8…2bf0` | PASS |
| S-11 | UNRESOLVED · `EVALUATOR_UNDECLARED` | ✓ | `13e2ea0f…f108` | PASS |
| S-12 | FAIL · `EVALUATION_OUTPUT_TYPE` | ✓ (X Conclusion als Output) | `f975727e…5e29` | PASS |
| S-13 | FAIL · `EVALUATION_RECORD_INCONSISTENT` | ✓ (`md5:` Digest) | `74edeff3…244a` | PASS |
| S-14 | MCP-Fehler · `P1_MCP_CONFIG_INVALID` | ✓ (/3-Felder in /2) | — | PASS |
| S-15 | UNRESOLVED · `SCENARIO_REQUIRED` | ✓ | `265b41f8…0335` | PASS |
| S-16 | PASS (X Result via P1.6, EV-3a) | PASS | `34c63e4f…947a` | PASS |
| S-17 | UNRESOLVED · `INSTANTIATION_SLOT_MISSING` | ✓ (`action_ref` fehlt) | `3c03b239…d969` | PASS |

Bei allen 16 semantischen Reports: `epistemic_warrant`, `current_authority` und `canonical_admission` = `NOT_EVALUATED`, `source_warrant: declared_unverified`, Envelope `simulation_profile: P1.8/simulation-profile-v1`, `evaluation_performed_by_cube: false`. Kein PASS leitet Ausführung, Wahrheit oder Admission ab.

## 3. Regression P1.6 auf dem neuen Deploy

| ID | Ergebnis | `declared_context_sha256` | Vergleich mit Lauf 18:50 | Status |
|---|---|---|---|---|
| R-01 (/2) | PASS | `ee6eb8c1…5fa0` | identisch, kein P1.8-Envelope | PASS |
| R-12 (/1) | UNRESOLVED · `PROFILE_REQUIRED` | `56aafc49…1e5f` | identisch, kein P1.6/P1.8-Envelope | PASS |

## 4. Lokale Belege (nicht von diesem Host erhoben)

30/30 Unit-Tests, S+R 30/30 direkt und durch den G4-Adapter, 16/16 Reports gültig gegen das eingefrorene `report.schema.json`, G5-Assemble PASS (siehe `P1/simulation-profile-v1/README.md`).

## 5. Bekannte Abweichungen

- **Gateway-Version:** MCP-`serverInfo.version` meldet weiter `0.1.0-proof`, weil `gateway/src/index.mjs` unverändert bleibt (Charge-3-Freeze-Anker).
- **Charge 3 überholt:** Die Quell-Prüfsummen von Charge 3 und `test_08` passen nicht mehr zu HEAD. Das ist erwartet. Folgeschritt ist ein Charge-4-Freeze.
- **Unabhängigkeit:** Die Vektoren und das Oracle stammen aus dem Projekt-Repo.

Dieses PASS bestätigt das beobachtete Host-Verhalten für die genannten Fälle. Es ist keine Production Authorization.
