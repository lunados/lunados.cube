# P1.10.1 — Migration profile revision: dependency gap (`binding-context/6`)

Revision of P1.10 (C-7). P1.10 and `/5` stay frozen; `/6` runs P1.10 unchanged on a
lossless `/5` projection and adds one rule: a dependency that ends before the target phase
must be explained by a declaration — retirement of its object or subject at the next phase,
`successor_ref`, `dropped` or `ends_reason` — otherwise `P1_MIGRATION_DEPENDENCY_GAP`
(UNRESOLVED). See `P1_10_1_ACCEPTANCE_SPEC.md` (D-1…D-7 resolved, all as proposed).

## Layout

| Path | Purpose |
|---|---|
| `cube_p1101/migration.py` | `/6` config validation (`ends_reason` shape), lossless `/5` projection |
| `cube_p1101/validator.py` | `P1101Validator`: wraps P1.10; DG-1…DG-8 |
| `context-v6.schema.json` | strict superset of `context-v5.schema.json` (`scripts/build_schema.py`) |
| `DIAGNOSTIC_EXTENSION.json`, `RULE_COVERAGE.json` | 1 new code, 5 rules |
| `oracles/independent_g01_g10.json` | expectations from spec §5 before code (commit `2919e0c`) |
| `fixtures/g01_g10_materialized.json` | 10 synthetic vectors (`scripts/materialize_g01_g10.py`) |
| `fixtures/golden_gap_synthetic.json` | P1.10 golden as `/6` (PASS) plus one unexplained end (`scripts/build_golden.py`) |
| `scripts/run_vectors.py` | G vectors directly or `--adapter`; `--with-m` re-runs M-01…M-22 as `/6` |
| `scripts/parity_g4_g5.py` | offline parity G4 adapter vs. staged G5 core for G-01…G-10 |
| `tests/test_p1101.py` | oracle, `/1…/5` regression, M as `/6`, rules, golden, schema |

## Run

```bash
python3 P1/migration-profile-v2/tests/test_p1101.py
python3 P1/migration-profile-v2/scripts/run_vectors.py --adapter --with-m      # 32/32
python3 P3/remote-mcp-g5/scripts/verify_g5.py
python3 P1/migration-profile-v2/scripts/parity_g4_g5.py                         # 10/10
```

G4 adapter dispatches `/6` explicitly (envelope `migration_profile: P1.10.1/migration-profile-v2`).
G5 core: descriptor `p1101_migration`, version `P3-MCP-REMOTE/0.5.0-proof`; host acceptance after redeploy.
