# P1.12 — Declared Coverage and Instance Profile (`binding-context/8`)

**Status:** IMPLEMENTED locally 2026-11-01 (TASK-033).

Available through the local MCP since 2026-11-02 (TASK-036): `cube_validate` with `/8`, and local discovery. The LIB entry is lunados.lib `analyze.population/v1` (TASK-034), and the cell-state printer is VP-10 (TASK-035). G5 and host acceptance are the follow-up step.

Gaps G-01 (completeness and population) and G-08 (instance correlation) from the MILE-002 grammar comparison. `/8` is a strict superset of `/7`. P1.12 runs P1.11 unchanged on a `/7` projection and adds three things:

- declared **coverage**: what was surveyed completely, per referent × predicate × direction or per ordered pair;
- declared **population rules**: `absence`, `count`, `join_activation`;
- typed **instance membership**: `instance_ref` on referents, `requires_same_instance` on predicate contracts.

P1 checks declarations and single statements. It never counts statements, never infers coverage and never evaluates a rule; that evaluation is the LIB entry's job (D-6). See `P1_12_ACCEPTANCE_SPEC.md` (D-1…D-6 and Q-1…Q-6 resolved, all as proposed).

## Diagnostics

| Code | Status | Rule |
|---|---|---|
| `P1_COVERAGE_UNDECLARED` (new) | UNRESOLVED | CV-3: a population rule has no covering declaration. Absence or count stays unknown, not zero. |
| `P1_INSTANCE_MISMATCH` (new) | FAIL | IN-3: a `requires_same_instance` predicate has endpoints in different instances. |
| `P1_INSTANCE_UNDECLARED` (new) | UNRESOLVED | IN-3: a `requires_same_instance` predicate has an endpoint without `instance_ref`. |
| `P1_BINDING_CONTEXT_REQUIRED` (reused, frozen stage) | UNRESOLVED | IN-1, Q-4: an `instance_ref`, a declaration or a rule names an unknown or wrongly typed referent or predicate. |
| `P1_MCP_CONFIG_INVALID` (reused) | MCP error | Malformed declaration or rule, or P1.12 fields in `/1…/7`. |

An incomplete declaration is never FAIL (P1.10.1 D-2).

## Layout

| Path | Purpose |
|---|---|
| `cube_p112/coverage.py` | `/8` shape checks (CV-1, PR-1, IN-1, IN-2), `/7` projection, coverage fit (CV-3, CV-4) |
| `cube_p112/validator.py` | `P112Validator`: wraps P1.11 and adds the CV/PR context checks and the IN statement check |
| `context-v8.schema.json` | strict superset of `context-v7.schema.json` (`scripts/build_schema.py`) |
| `DIAGNOSTIC_EXTENSION.json`, `RULE_COVERAGE.json` | 3 new codes, 7 rules |
| `oracles/independent_k01_k21.json` | expectations from spec §5 and `CHECK-CASES.json`, committed before code (`8297b82`) |
| `fixtures/k01_k21_materialized.json` | 21 synthetic vectors (`scripts/materialize_k01_k21.py`) |
| `fixtures/golden_coverage_instance.json` | one trace context with all three blocks, plus a mixed variant (`scripts/build_golden.py`) |
| `scripts/run_vectors.py` | runs the K vectors against the oracle |
| `tests/test_p112.py` | oracle, `/1…/7` regression, §2 rows, coverage and instance details, projection, golden, schema |

## How the vectors are built

Each vector comes from its check case: statements, declarations, claim, instance bindings and predicate properties. Referents and predicate contracts come from the MILE-002 case contexts.

`input_text` is one statement of the check case, because P1 checks single statements. The full statement set is kept as `statements`, next to `lib_expected`, for the LIB entry. CC-01 and CC-09 have no statements, so K-01 and K-09 use a neutral `composedOf` statement from the same model.

Following the spec §5 translation note, the "incoming to join" declaration of CC-14 and CC-15 becomes one `onFlow`/`incoming` declaration per flow referent, restricted to the instance (CV-4). Flows and the gateway use the working mapping `Y:identified-object:work-item`. Instances use `Y:identified-object:bounded-execution`.

## Run

```bash
python3 P1/coverage-instance-profile-v1/scripts/build_schema.py
python3 P1/coverage-instance-profile-v1/scripts/materialize_k01_k21.py
python3 P1/coverage-instance-profile-v1/scripts/build_golden.py
python3 P1/coverage-instance-profile-v1/scripts/run_vectors.py        # 21/21
python3 P1/coverage-instance-profile-v1/tests/test_p112.py
```

## Local results (2026-11-01)

- **Vectors:** K-01…K-21 match the independent oracle (21/21) on the first run.
- **Unit tests:** 28/28 pass.
- **Regression:** the M, C, G and F vector suites and the P1.11 golden produce reports byte-identical to P1.11. Every `/7` context lifted to `/8` without P1.12 fields reports exactly like its `/7` twin.
- **Earlier profiles:** the P1.1…P1.11 test suites pass unchanged, and P1.11 `run_vectors` gives 16/16. The `SHA256SUMS` checks for P0 and P1 hold. No tracked file outside this directory changed.
- **Golden:** GC-pos gives PASS. GC-mixed gives FAIL with exactly one `P1_INSTANCE_MISMATCH` and one `P1_COVERAGE_UNDECLARED`.

## Not part of this stage

- Rule evaluation over statement sets: `lunados.lib` `analyze.population/v1`, TASK-034.
- Cell-state display: P2, TASK-035.
- G5 (remote) delivery and host acceptance: follow-up step (MILE-005 D-5).
