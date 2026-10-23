# P1.1 Acceptance Matrix and Handover

## P1.1 freeze checks

| AC | Verifiable result | Evidence |
|---|---|---|
| AC-01 | Source attribution binds to Morphology v9.4 (hash) and P0 published reference files | `contract/source_lock.json` |
| AC-02 | 80 concept IDs resolve via exactly one `(home,key)` per entry; 5 Greek aliases are non-instantiable | `contract/concept_keys.json`; script |
| AC-03 | No automatic Unicode glyph/case/NFKC coercion | `contract/validation_profile.json` |
| AC-04 | Parser grammar has one expression, four AST forms, JSON scalars, explicit lexical bounds | `contract/notation_p1.ebnf` |
| AC-05 | Referential identity is checked only with explicit typed context; ζ requires witness | `contract/context.schema.json`; D05–D06 |
| AC-06 | Predicate names are not universal signatures | `contract/predicate_registry.json`; D07–D08 |
| AC-07 | T/F/M/O qualifications and method applications are typed separately with no inferred authority or truth | `contract/validation_profile.json`; D09 |
| AC-08 | Deterministic stage reports/diagnostics with PASS/FAIL/UNRESOLVED/NOT_EVALUATED | `contract/report.schema.json`; `diagnostics.json` |
| AC-09 | Every positive fixture explicitly says *illustrative*; no external truth/effect | `fixtures/*.binding-context.json` |
| AC-10 | Positive, negative and unresolved fixtures documented, not falsely reported executed | `fixtures/conformance_cases.json` |
| AC-11 | P0 assets left untouched; dedicated P1 profile version and no deployment | package README |
| AC-12 | Static contract package passes its own consistency tests | `checks/check_result.json` |

## P1.2 parser exit (not implemented here)

- Parse all four forms from exactly one document; build P0-compatible AST; reject malformed JSON
  scalars, duplicate parameter keys, unclosed text and unsupported syntax.
- Canonical printing may be implemented only after specifying **numeric rendering** and
  byte/semantic equivalence. Do not promise byte-identical roundtrip for all JSON numbers.
- Diagnostics use frozen byte span/line rules; impose resource limits.
- Run independent oracle/counterexamples; P1.1 fixtures are test design, not test passes.

## P1.3 resolver exit (not implemented here)

- Exact home/concept_key crosswalk and legal semantic aliases; non-instantiable dimensions fail.
- Reference binding must be attested against a supplied context; absent binding => UNRESOLVED.
- Foreign IDs are never authenticated Principals by mere spelling.

## P1.4 validator exit (not implemented here)

- Enforce explicit scoped predicate-signature profiles; nonexistent profile => UNRESOLVED.
- Recognize T time facets without claiming valid clocks; independently check Observer evidence.
- For `application`, require an explicit method signature; otherwise UNRESOLVED. No effect invocation.
- Separate distinct judgment channels; never infer path-derived predicates or current admission.

## P1.5 conformance/release exit (not implemented here)

- Execute and version fixtures, add independent mutations, CI, differential tests and published reports.
- External review if claiming real schema or foreign mapping conformance.
- Do not modify the immutable `/v9.4/` documentation or quietly backfill runtime contracts.
