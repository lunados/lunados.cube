# P1.15 — Scope Nesting and Admission Outcomes Profile (`binding-context/11`)

**Status:** Implemented locally for TASK-076 (2026-11-05), MILE-015 B1–B3. G5 is a separate step.

P1.15 lets a context declare which X scope lies in which (`scope_nesting`), accepts an X endpoint whose scope reaches the validation scope through such a chain and checks it with P1.6 in its own pair scope. It widens the Authority resource scope by Revision and Artifact (P1.6 reference v2, `/11` only) and ties the outcomes of one Admission request to an exclusive P1.13 gateway. P1 checks the declaration only: whether an inner scope is actually narrower, which outcome holds, and any truth, authority or admission stay outside P1.

The validator projects `/11` to `/10` (drops `scope_nesting`, narrows profiles to reference v1), runs P1.14 unchanged, then recomputes the binding of every X endpoint in the input with reference v2, supersedes the scope conflict of endpoints nested by a valid chain, and adds the SN and AO checks. `/1…/10` delegate unchanged (byte-identical reports, tested).

## Contract (summary; rules in [P1_15_ACCEPTANCE_SPEC.md](P1_15_ACCEPTANCE_SPEC.md))

- `scope_nesting[]`: `{"inner", "outer"}`; one parent per inner scope; inner is a declared X scope (its own `scope_ref`), outer the context scope or such a scope; chains end in the context scope without cycle (SN-1…SN-3). Kinds may mix (Policy ⊃ Event).
- Nesting rescues only X endpoints used in relations (SN-4, SN-5); Y/Z placement such as *hosted-by* is not a scope chain.
- Reference v2: `instantiation_reference_v2.json`, pinned in `cube_p115/nesting.py`; differs from v1 only in Authority `resource_scope_ref` (SN-6).
- Admission outcomes: targets of one exclusive gateway that are Admissions share `request_ref`, at most one is admitted, each is instance-checked (AO-1…AO-3). A plan dependency points at the admitted outcome.
- New codes: `P1_SCOPE_NESTING_INVALID` (scope consistency), `P1_ADMISSION_OUTCOME_CONFLICT` (referent binding).

## Artifacts

| Path | Purpose |
|---|---|
| `P1_15_ACCEPTANCE_SPEC.md` | Rules SN-1…SN-7, AO-1…AO-3, vectors, acceptance |
| `oracles/independent_sn01_sn14.json` | Independent expectations, committed before runtime code (d9483ae) |
| `scripts/materialize_sn01_sn14.py`, `fixtures/sn01_sn14_materialized.json` | One synthetic base context, 14 vectors |
| `cube_p115/nesting.py`, `cube_p115/validator.py` | `/11` shape, reference v2, projection and checks |
| `instantiation_reference_v2.json` | P1.6 reference v2 |
| `context-v11.schema.json` (`scripts/build_schema.py`) | Strict `/10` schema plus `scope_nesting` |
| `DIAGNOSTIC_EXTENSION.json`, `RULE_COVERAGE.json` | Codes and rule coverage |
| `tests/test_p115.py` | Oracle, schema, regression `/1…/10`, configuration errors, reference v2, parallel gateways |

## Local verification

```bash
python3 P1/scope-nesting-profile-v1/scripts/materialize_sn01_sn14.py
python3 P1/scope-nesting-profile-v1/scripts/build_schema.py
python3 -m unittest discover -s P1/scope-nesting-profile-v1/tests -q
```

The local G4 adapter dispatches `/11` (`scope_nesting_profile`, `policy_narrowing_checked_by_cube: false`) and lists the two new codes in discovery.
