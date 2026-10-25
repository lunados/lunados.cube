# P1.6 decisions and boundaries — v1.1 candidate

**Status:** Ready for technical review, not an adopted morphology update and not a production release. P1.6 runtime is not implemented by Charge 1.

| Decision | Resolution | Boundary |
|---|---|---|
| D-1 | Unconditional missing slot = UNRESOLVED; explicit type contradiction = FAIL; conditionally missing `authority_ref`/`refusal_ref` = FAIL | Absence is not proof of invalidity; conditional contradiction is a declared inconsistency |
| D-2 | Reference slot table = P1 validator vocabulary | Morphology v9.4 unchanged; any §D.5 adoption is separate |
| D-3 | Defer Principal-to-holder authorization chain to P1.7 | No identity-equality shortcut or Authority proof |
| D-4 | Defer Z zones | P1.6 tests maintain their UNRESOLVED behaviour |

## Semantic gates

- Config-stage rejection occurs before runtime referent checks; it uses `P1_MCP_CONFIG_INVALID` rather than a P1 referent report.
- `canonical_admission`, `current_authority`, `epistemic_warrant` remain `NOT_EVALUATED`; `source_warrant` remains `declared_unverified`.
- `binding-context/1` must retain byte-identical results for the existing regression corpus.
- P1.6 success is **shape/type validity only**. The absence of runtime evidence is never upgraded by a declared profile.

## Boundary and versioning

New artifacts only in `P1/instantiation-profile-v1/`. No changes to P0, `P1/contract-v1/`, frozen baselines, G5/G4 runtime, MCP tool signatures, P2 or existing public plugin. `context-v2.schema.json` copies the existing `/1` schema fields and restricts the two new referent fields. Local JSON-Schema validation does not constitute full P1.6 runtime implementation.

## Acceptance priorities

1. Review schema/profile vocabulary and decisions.
2. Implement runtime validator with independent oracle in Charge 2.
3. Run local MCP parity then protected G5 proof deployment and actual remote R-01..R-13 in Charge 3. Do not infer operational authorization from host tool PASS.
