# AIAEAO Pure Cube — P1.1 Contract Freeze

**Engineering handover:** `P1-VC/1.0.0` · **Reference:** Morphology v9.4 · **Date:** 2026-10-23

This is the specification package for **P1.1 only**. No parser, resolver, or runtime
validator is claimed or deployed. **No GitHub changes have been made.**

## Read in this order

1. `P1_1_CONTRACT_FREEZE.md` — semantics, binding policy, error states and boundaries.
2. `DECISIONS.md` — fixed engineering choices vs still intentionally unresolved semantics.
3. `ACCEPTANCE_MATRIX.md` — stage-by-stage acceptance and P1.2–P1.5 handoff.
4. `contract/*.json` — machine-readable profile, key registry, signature policy, schemas, diagnostics.
5. `fixtures/` — deliberately scoped reference contexts and 25 prospective test cases.
6. `scripts/check_contract.py` — checks *this contract package* without pretending to execute P1 validation.

## Proposed repository location

`P1/contract-v1/` next to `AIAEAO_Pure_Cube_P0_v9.4/`.
Do **not** overwrite `/v9.4/` or modify the deployed P0 manifest yet.

## Gate

Contract freeze requires explicit project adoption. On adoption, protect this
profile from semantic edits; later changes require an incremented `P1-VC` version,
not modifications to Morphology v9.4. The package deliberately leaves unknown
actual foreign referents, universal predicate signatures, active grants,
independent empirical truth and runtime conformance **unresolved**.

```bash
python3 scripts/check_contract.py
```
