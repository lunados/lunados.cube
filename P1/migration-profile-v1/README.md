# P1.10 — Declared Migration Profile (`binding-context/5`)

Additive to P1.9. Declares **migration plans** in the Cube domain — phases,
transitions (retire / introduce), the dependency inventory as data — and checks
their **structural consistency**. It never checks a live system, never discovers a
dependency, never compares a date and never decides an order. See
`P1_10_ACCEPTANCE_SPEC.md` (decisions D-1…D-8 resolved in §6).

## Layout

| Path | Purpose |
|---|---|
| `cube_p110/migration.py` | /5 config validation (profile import, plan shapes), /4 projection with scope-bound imported contracts |
| `cube_p110/validator.py` | `P110Validator`: wraps P1.9; plan checks after all P1.9 checks |
| `cube_p110/profiles/migration-predicates-v1.json` | pinned predicate profile, eight predicates (D-1); SHA-256 in code and `SHA256SUMS.txt` |
| `context-v5.schema.json` | strict superset of `context-v4.schema.json` (`scripts/build_schema.py`) |
| `DIAGNOSTIC_EXTENSION.json`, `RULE_COVERAGE.json` | 9 new codes, 4 reused codes, 10 rules with Morphology references |
| `oracles/independent_m01_m22.json` | expectations transcribed from spec §5 before code (commit `a258252`) |
| `fixtures/m01_m22_materialized.json` | 22 synthetic vectors (`scripts/materialize_m01_m22.py`) |
| `fixtures/golden_migration_synthetic.json` | synthetic golden plan, 24 dependencies, 3 phases, negative control + corrected PASS (`scripts/build_golden.py`) |
| `scripts/run_vectors.py` | vectors directly or `--adapter` through G4; `--with-c`, `--with-s`, `--with-r` add regression vectors |
| `scripts/parity_g4_g5.py` | P1.10-12 offline parity: G4 adapter vs. staged G5 core, M-01…M-22 |
| `tests/test_p110.py` | 25 unit tests: oracle, /1…/4 regression, config, §2 rows, ordering, golden, schema |

## Run

```bash
python3 P1/migration-profile-v1/tests/test_p110.py
python3 P1/migration-profile-v1/scripts/run_vectors.py --adapter --with-c --with-s --with-r   # 72/72
python3 P3/remote-mcp-g5/scripts/verify_g5.py                                              # assembly incl. P1.10 smoke
python3 P3/remote-mcp-g5/scripts/check_runtime_assets.py
python3 P1/migration-profile-v1/scripts/parity_g4_g5.py                                    # 22/22
```

## Local results (2026-10-26, implementation stage)

- 25/25 unit tests (schema test skipped where `jsonschema` < 4.18; checked separately with a Draft-7 fallback: all M vectors except M-20 and both golden cases valid against /5, M-20 rejected by /4, all /4 C vectors valid as /5).
- M-01…M-22 match the independent oracle; C-01…C-20, S-01…S-17, R-01…R-13 byte-identical to P1.9.
- Golden: `G-neg` FAIL `P1_MIGRATION_DANGLING_DEPENDENCY` (recovery via the provider retired first), `G-pos` PASS.
- No frozen file changed; P1.9 suite unchanged.

- G4 adapter: explicit `/5` dispatch (`P1_MCP_P110_UNAVAILABLE` if the module is missing); envelope adds
  `migration_profile: "P1.10/migration-profile-v1"` and keeps `binding_context_profile`, `simulation_profile`,
  `comparison_profile` and `evaluation_performed_by_cube: false`. 72/72 vectors through the adapter.
- G4 suite 192/193 here; the one error (`test_report_json_schema`) is environmental (`jsonschema` 3.2 in this
  workspace) and occurs identically without the P1.10 change. All 21 non-error M/golden reports are valid
  against the frozen `report.schema.json` (Draft-7 fallback).
- G5: `p110_migration` descriptor in `cube_discover_surface`, version `P3-MCP-REMOTE/0.4.0-proof`;
  `cube_p110` staged incl. the pinned profile as Wrangler Text asset (42 non-Python assets, P110=1).
  Assembly 91 files with P1.10 smoke (M-01, M-18, M-17, M-10, M-02, both goldens), G5 contract 18/18,
  `verify_g5.py` PASS, offline G4/G5 parity 22/22.
- Not yet done: G5 re-deployment and host acceptance (P1.10-13, live parity P1.10-12).
- `P3/remote-mcp-g5/SHA256SUMS.txt` (Charge 2 freeze) already disagreed for `core_runtime.py`,
  `wrangler.jsonc`, `assemble_core.py` and `check_runtime_assets.py` before P1.10 (superseded by
  P1.6/P1.8/P1.9); it is left unchanged here, as in P1.9.

## Notes

- Imported contracts are bound to the context `scope_ref` (D-8). On the /4 projection they carry
  `external_declaration_unverified`, because the frozen /1 origin enum does not know
  `profile_declaration_unverified`; the report exposes no contract origin.
- Plan diagnostics follow the P1.9 diagnostics, ordered by plan, then section, then item index.
- `PASS` means a consistent **declaration**, not a safe, complete or executed migration.
