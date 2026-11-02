# P1.14 rule coverage

| Rule or status row | Fixed vectors | Additional test |
|---|---|---|
| OR-1 predicate opt-in, absent contract unchanged | HO-10, HO-11 | `test_unopted_and_extra_parameters` |
| OR-2 missing, valid and invalid origin | HO-01, HO-02, HO-05, HO-07, HO-08 | `test_status_rows` |
| OR-3 basis requirement and prohibition | HO-04, HO-06 | `test_status_rows` |
| OR-4 statements/projection basis, missing basis declaration | HO-02, HO-03, HO-09 | `test_bad_contexts`, `test_status_rows` |
| OR-5 origin independent of predicate name | HO-02, HO-03, HO-08 | `test_no_hardcoded_predicate` |
| OR-6 plan dependencies | HO-12 | `test_plan_origin_rows` |
| OR-7 statement-set/2 shape (printer resolution is TASK-066) | — | `test_statement_set_schema` |
| `/10` strict superset, `/9` projection, old formats unchanged | HO-11 | `test_schemas_and_projection`, `test_prior_reports` |
| MCP config errors for malformed declarations and old format fields | — | `test_bad_contexts`, `test_old_format_rejects_new_fields` |
| Synthetic golden, both basis kinds | HO-02, HO-03, HO-07, HO-08 | `test_golden` |

`P1_ORIGIN_UNDECLARED`, `P1_ORIGIN_BASIS_MISSING`, and `P1_ORIGIN_INVALID` are P1.14 semantic diagnostics. Basis lookup retains `P1_BINDING_CONTEXT_REQUIRED`; unrelated parameters retain `P1_PREDICATE_PROFILE_MISSING`. No source set or projection record is opened, recomputed, or certified.
