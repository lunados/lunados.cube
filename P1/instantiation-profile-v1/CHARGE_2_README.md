# AIAEAO Pure Cube P1.6 — Charge 2/3: additive validator overlay

**State:** IMPLEMENTED LOCALLY · OFFLINE CONFORMANCE CANDIDATE. **Not deployed to G5.**

P1.6 checks the **declared structural instantiation** of 10 X Key-Pair endpoints
with `binding-context/2`. It cannot authorize effects, prove Authority, assess
warrant or assert that an Admission happened. P0 Morphology v9.4, P1.1 contracts,
P1.2–P1.5 executable baselines, report schema and MCP surfaces remain unchanged.

## Files

- `cube_p16/instantiation.py`: SHA-pinned reference vocabulary, strict closed `/2`
  input/profile validation, typed slots, conditional Admission, endpoint reference
  cycles, missing/wrong-type/ambiguous diagnostics and β/ζ precedence.
- `cube_p16/validator.py`: additive dispatch. `/1` calls **the frozen P1.4
  validator directly and without rewriting its output**. `/2` projects the
  unchanged P1.1 shape into P1.4, retains all other semantic stages and overlays
  P1.6 `referent_binding` for X endpoints only. Z zones remain unchanged.
- `scripts/validate_p16.py`: standalone, reproducible CLI; exit codes 0/1/2/3.
- `tests/test_runtime.py` and `oracles/independent_r01_r13.json`: ten positive
  endpoints, error-class and no-promotion coverage, all thirteen locked
  experiment vectors. `tests/test_contracts.py` remains from Charge 1.
- `DIAGNOSTIC_EXTENSION.json` and `RULE_COVERAGE.json`: **new P1.6-only** files;
  never rewrite P1.4/P1.5 frozen registers.
- `scripts/verify_charge2.py`: runs P1.6 suite + **full P1.5 release integrity
  checks**, including P0 source locks and frozen P1.4 implementation hashes.

## Apply locally (from Finder-unpacked ZIP)

```bash
cd "$HOME/Downloads/lunados.cube"
rsync -av "$HOME/cube-patches/AIAEAO_Cube_P1_6_Charge_2_Validator_v1/P1/" ./P1/
python3 P1/instantiation-profile-v1/scripts/verify_charge2.py
```

The P1.6 contract preflight in Charge 1 uses `jsonschema>=4` for its tests.
The new runtime overlay itself uses only Python stdlib and installed P1.4.

## Real standalone `/2` validation (no G5)

```bash
python3 P1/instantiation-profile-v1/scripts/validate_p16.py \
  --input P1/semantic-validator-v1/fixtures/migration.acg \
  --context P1/instantiation-profile-v1/fixtures/valid_conclusion_context_v2.json
```

The above generic migration example does **not** refer to the v2 Conclusion
fixture and must not be used as a P1.6 positive proof. For a positive run, use:

```bash
printf 'X:α:Conclusion["c1"]' | python3 P1/instantiation-profile-v1/scripts/validate_p16.py \
  --input - --context P1/instantiation-profile-v1/fixtures/valid_conclusion_context_v2.json
```

Expected `overall_status=PASS`, three epistemic/governance fields
`NOT_EVALUATED`, no validated truth or authority.

## Charge 3 integration boundary

No changes to existing MCP tools, P3/worker, G5 protected Bearer gateway or
public `lunados-cube` MCP are part of this ZIP. **Charge 3** must explicitly
route `cube_validate` with context format `/2` to `P16Validator` in both local
MCP and G5 remote runtime, preserving `/1` unchanged. `cube_discover_surface`
should advertise the optional new context/profile vocabulary.

Perform local MCP parity, independent protected remote acceptance R-01…R-13,
and separate credential/log review **before** any production consideration.
Preserve `G5_PROOF_NOT_PRODUCTION_AUTHORIZED` throughout.

## Known bounded limitations

- `source_warrant=declared_unverified` is recorded in context/referents; no new
  report field can be added because `P1.1 report.schema.json` is frozen.
- The independent expected-status oracle is separate from the runtime checker,
  but the **fixture constructor** is shared across tests. Charge 3 should run
  separately materialized fixtures independently as a second oracle.
- Native MCP resource discovery and real runtime effect/permission proofs are
  not part of P1.6 validation.
