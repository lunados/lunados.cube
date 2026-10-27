# P1.11 — Migration method catalog (`binding-context/7`)

Requirement C-10. P1.10 / P1.10.1 and `/5`, `/6` stay frozen; `/7` runs P1.10.1 unchanged on a `/6`
projection and adds a pinned, reusable method catalog plus method bindings in migration plans.
Imported catalog methods are scoped to the importing context, so `@F(method="migrate.…/v1")` resolves
through the unchanged P1.4 F-qualifier check without a hand-written contract. Bindings on transitions
and dependencies are checked for typing and plan fit. The Cube never runs, schedules, ranks or admits a
method. See `P1_11_ACCEPTANCE_SPEC.md` (D-1…D-9 resolved, all as proposed; §6 relation to the
morphology F families).

## Catalog `P1.11/migration-methods-v1`

| Method | Roles | Binding point |
|---|---|---|
| `migrate.import/v1` | `source`, `target` | transition |
| `migrate.rebuild/v1` | `target` | transition |
| `migrate.retire/v1` | `retired` | transition |
| `migrate.rewrite/v1` | `dependant`, `new_object` | dependency |
| `migrate.reconfigure/v1` | `target` | transition |

Admissible concept IDs per role: spec §3.5. File pinned by SHA-256 (`SHA256SUMS.txt`, `cube_p111/methods.py`).

## Layout

| Path | Purpose |
|---|---|
| `cube_p111/profiles/migration-methods-v1.json` | pinned catalog (MC-1…MC-4) |
| `cube_p111/methods.py` | `/7` config validation, catalog import, `/6` projection (MI-1…MI-3) |
| `cube_p111/validator.py` | `P111Validator`: wraps P1.10.1; bindings MB/MP/MV |
| `context-v7.schema.json` | strict superset of `context-v6.schema.json` (`scripts/build_schema.py`) |
| `DIAGNOSTIC_EXTENSION.json`, `RULE_COVERAGE.json` | 3 new codes, 6 rules |
| `oracles/independent_f01_f16.json` | expectations from spec §5 before code (commit `dd6cfde`) |
| `fixtures/f01_f16_materialized.json` | 16 synthetic vectors (`scripts/materialize_f01_f16.py`) |
| `fixtures/golden_methods_synthetic.json` | VP-07.1 golden plan as `/7`, every transition and successor bound; one misfit (`scripts/build_golden.py`) |
| `scripts/run_vectors.py` | F vectors directly or `--adapter` |
| `scripts/parity_g4_g5.py` | offline parity G4 adapter vs. staged G5 core |
| `tests/test_p111.py` | oracle, `/1…/6` regression (M, C, G), §2 rows, projection, golden, schema |

## Run

```bash
python3 P1/migration-methods-v1/tests/test_p111.py
python3 P1/migration-methods-v1/scripts/run_vectors.py --adapter          # 16/16
python3 P3/remote-mcp-g5/scripts/verify_g5.py
python3 P1/migration-methods-v1/scripts/parity_g4_g5.py                   # 15/15 (F-03 patches the pin, local only)
```

## Local results (2026-10-27)

- F-01…F-16: 16/16 against the independent oracle, directly and through the G4 adapter.
- 21/21 unit tests; M-01…M-22, C-01…C-20 and G-01…G-10 reports byte-identical to P1.10.1.
- G4 suite 193/193; G5 offline verification PASS (assembly smoke incl. P1.11, packaging coverage with the
  catalog as Text asset, contract tests 18/18); G4/G5 parity 15/15, P1.10.1 parity unchanged 10/10.
- Golden: every transition (7 bindings) and every successor-bearing dependency (16 rewrites) bound → PASS;
  one retire on a referent the transition does not retire → FAIL `P1_MIGRATION_METHOD_PLAN` (exactly one).

## Not part of this stage

VP-07 transcription of bindings and
VP-09 F axes (P2).
