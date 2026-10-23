# P1.4 — Acceptance matrix

| AC | Requirement | Evidence | Status |
|---|---|---|---|
| P1.4-01 | No change to v9.4 or P1.1 frozen files | Reused `baseline/` hash snapshot, original P1.3 code | PASS |
| P1.4-02 | Both Golden-Examples yield descriptive PASS in matching fixtures | `test_01_migration_golden`, `test_02_metaphysics_golden` | PASS |
| P1.4-03 | Known relation name cannot confer universal signature | `test_03`, `test_fixture_F09` | PASS |
| P1.4-04 | Directed relation concept types enforced | `test_04`, `test_05` | PASS |
| P1.4-05 | No automatic selection of ambiguous revisions/signatures | `test_06`, `test_23` | PASS |
| P1.4-06 | Conflicting scopes rejected; missing scopes unresolved | `test_07`–`test_10`, `test_36` | PASS |
| P1.4-07 | Relation-level required qualifiers, parameter typing limitations | `test_11`–`test_14` | PASS |
| P1.4-08 | Method typing: arguments, count, purity, no effects | `test_15`–`test_24` | PASS |
| P1.4-09 | T eight facets and mandatory local qualification contract | `test_25`–`test_29` | PASS |
| P1.4-10 | O witness and distinct observational status | `test_27`, `test_30` | PASS |
| P1.4-11 | M presentation-only; F scoped descriptive method | `test_31`–`test_35` | PASS |
| P1.4-12 | Qualified profile schema, duplicate protection | `test_37`–`test_41` | PASS |
| P1.4-13 | JSON-AST provenance not mistaken for parsed source | `test_38`, `test_42` | PASS |
| P1.4-14 | FAIL/UNRESOLVED precedence and external truth exclusions | `test_43`–`test_48` | PASS |
| P1.4-15 | All 25 frozen P1.1 fixture expectations actually executed | `test_fixture_F01`–`F25` | PASS |
| P1.4-16 | P1.2/P1.3 regression | `tests_parser` / `tests` | PASS |
| P1.4-17 | Report validates against unchanged P1.1 report.schema.json | `scripts/check_semantic_schema.py` | PASS (with optional `jsonschema`) |
| P1.4-18 | P1.5 independent oracle and CI/release readiness | P1.5, explicitly pending | OPEN |

`PASS` in this matrix means **the listed test ran successfully**. It does not imply a mathematically complete interpreter of all 32 P0 interpretative constraints.
