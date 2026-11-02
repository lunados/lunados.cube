# P1.14 — Relation Origin Profile (`binding-context/10`)

**Status:** Implemented locally for TASK-065 (2026-11-02). Printer VP-07.6 and G5 integration are TASK-066/067.

P1.14 validates caller-declared relation origin in a `/10` context. A predicate opts in with `origin_binding: "required"`. Its relations then need `origin="declared"`, `origin="derived"` with a named basis, or `origin="unknown"`. Bases are declarations referencing source statement IDs or a `project.aggregate-relations/v1` record. P1 checks their shape and reference only; it does not open or recompute them.

The validator projects `/10` to `/9`, runs the unchanged P1.13 validator, then adds origin checks. For opted-in relations, only the former P1.4 diagnostic for typed `origin`/`basis` parameters is superseded. Other relation parameters remain unresolved. `/1…/9` delegate unchanged. Migration-plan dependencies use the same origin rules. `statement-set/2` has a schema here; its resolution and rendering belong to TASK-066.

## Artifacts

| Path | Purpose |
|---|---|
| `P1_14_ACCEPTANCE_SPEC.md` | Fixed acceptance rules and HO oracle contract |
| `oracles/independent_ho01_ho12.json` | Independent expectations committed in TASK-064 before code |
| `cube_p114/origin.py`, `cube_p114/validator.py` | `/10` shape, projection and additive semantic checks |
| `context-v10.schema.json` | Strict `/9` superset schema |
| `statement-set-v1.baseline.schema.json`, `statement-set-v2.schema.json` | Local schema transcription of VP-10 `/1` and additive `/2` shape |
| `DIAGNOSTIC_EXTENSION.json`, `RULE_COVERAGE.json`, `RULE_COVERAGE.md` | Diagnostic and rule coverage descriptions |
| `fixtures/ho01_ho12_materialized.json`, `fixtures/golden_relation_origin.json` | Synthetic vectors and declared/derived/unknown golden |
| `tests/test_p114.py` | Oracle, status rows, schema, golden and old-report regression |

The HO-12 vector materializes the pinned P1.10 predicate profile as equivalent local contracts to set `origin_binding` on `sends-via`. This corrects the TASK-064 materializer's empty local contract list; the independent oracle and old baseline results are unchanged.

## Local verification

```bash
python3 P1/relation-origin-profile-v1/scripts/materialize_ho01_ho12.py --baseline
python3 P1/relation-origin-profile-v1/scripts/build_schema.py
python3 P1/relation-origin-profile-v1/scripts/build_golden.py
python3 -m unittest discover -s P1/relation-origin-profile-v1/tests -q
```

The local G4 adapter dispatches `/10` and lists it with the three new diagnostic codes in discovery. No truth, origin verification, authority or admission is inferred.
