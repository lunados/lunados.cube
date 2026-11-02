# P1.13 — Control Flow Profile (`binding-context/9`)

**Status:** Implemented locally for TASK-050 (2026-11-02). The local MCP adapter and discovery are TASK-052; trace conformance over a statement set is TASK-051 in lunados.lib.

P1.13 is additive over P1.12. A `/9` context is projected to `/8`, validated by the unchanged P1.12 path, then checked for control-flow declarations (CF-1…CF-5) and single-statement trace binding (TB-1…TB-3). `/1…/8` dispatches directly to P1.12. No condition is evaluated and no process is executed.

## Contract

- `control_flow.gateways[]` declares a gateway referent, `type`, incoming flow referents and outgoing `flow`/`target` pairs. Exclusive branches may carry `order`, `condition_ref` and one default. Parallel branches carry none of those fields.
- `at_gateway` on a token referent locates it for routing. `control_flow_role` on a predicate contract identifies `routing` or `on_flow`; predicates without a role are unchanged.
- Unresolved referents, absent token positions and unsupported gateway types remain UNRESOLVED. Invalid declarations or statements bound outside the declared flow are FAIL. Malformed `/9` fields are configuration errors.
- Earlier contexts reject P1.13 fields. P0, P1.1…P1.12, P2 and existing LIB entries are untouched.

The acceptance rules are in [P1_13_ACCEPTANCE_SPEC.md](P1_13_ACCEPTANCE_SPEC.md). The schema is `context-v9.schema.json`.

## Artifacts

| Path | Purpose |
|---|---|
| `oracles/independent_kf01_kf09.json` | Independent expectations transcribed from the fixed CF-01…CF-09 cases and specification before runtime code |
| `cube_p113/control_flow.py` | `/9` shape checks and `/8` projection |
| `cube_p113/validator.py` | Additive CF and TB checks over the unchanged P1.12 validator |
| `scripts/build_schema.py` | Generates the strict `/8` superset schema |
| `scripts/materialize_kf01_kf09.py` | Builds nine synthetic, explicit vectors from fixed CF cases |
| `scripts/build_golden.py` | Builds one synthetic control-flow, trace-binding and coverage golden |
| `scripts/run_vectors.py` | Compares vector results with the independent oracle |
| `tests/test_p113.py` | Oracle, every status row, CF/TB details, schema, golden and regression checks |
| `DIAGNOSTIC_EXTENSION.json`, `RULE_COVERAGE.json` | Additive diagnostic and rule vocabulary |

## Local verification

```bash
python3 P1/control-flow-profile-v1/scripts/build_schema.py
python3 P1/control-flow-profile-v1/scripts/materialize_kf01_kf09.py
python3 P1/control-flow-profile-v1/scripts/build_golden.py
python3 P1/control-flow-profile-v1/scripts/run_vectors.py
python3 P1/control-flow-profile-v1/tests/test_p113.py
```

On 2026-11-02: KF-01…KF-09 matched 9/9; P1.13 tests passed 18/18. Nine earlier P1 test suites (236 tests) and six earlier vector suites passed. All five P0/P1 `SHA256SUMS.txt` manifests verified. The P1.13 regression test compares earlier reports byte-for-byte with P1.12, including all 21 P1.12 K vectors. No tracked P0 or earlier P1 file was changed.

The local `cube_validate` adapter, discovery, MCP repeat and G5 checks are outside TASK-050.
