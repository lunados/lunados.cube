# P1.3 Contract notes / binding boundary

1. **Reference immutable:** Morphology v9.4 remains the single adopted source. The P1.1 `concept_keys.json` is a *validator vocabulary profile*, not a new morphological catalog or Semantic ID authority.
2. **Exact key resolution:** `(Home, concept_key)` is looked up in the P1.1 table. The five aliases Ψ Γ Σ Ξ Π are semantic notation aliases for non-instantiable dimensions. Unknown key -> `P1_UNKNOWN_CONCEPT` UNRESOLVED; known wrong Home -> `P1_WRONG_HOME` FAIL.
3. **Instantiability:** `not_instantiable` -> `P1_NON_INSTANTIABLE` FAIL. `requires_binding_profile` -> `P1_INSTANTIATION_PROFILE_REQUIRED` UNRESOLVED. `eligible_with_declared_referent` proceeds to context identity checks.
4. **Declared referents only:** caller context `referents[].ref` must exactly match lexical `referent_ref`. Home/concept/layer/scope are checked; no inference from display glyphs, textual similarity or provenance claims. No context / absent entry -> `P1_BINDING_CONTEXT_REQUIRED` UNRESOLVED (for β/ζ, prioritize `P1_LAYER_WITNESS_MISSING` as in fixture F17).
5. **Witness pointers:** β/ζ require declared `witness_ref` (absence UNRESOLVED). Presence can satisfy *reference declaration shape*, but cannot prove historical witness availability, validity, O/T qualification or Core admission; `witness_truth=NOT_EVALUATED`. P1.4 will need separate witness profile/typed provenance rules.
6. **Consistency and ambiguity:** any contradictory declared concept, home, layer or explicit scope -> `P1_REFERENT_MISMATCH` FAIL. Duplicate referent IDs and malformed contexts are rejected as **invalid inputs**. This input-error category is distinct from P1.1 semantic diagnostic codes.
7. **Other expressions:** `relation`, `application`, `qualified` are only recursively walked to find references. Recognition of `references`/`causedBy` etc is not a domain/range type PASS. This phase intentionally makes no predicate, method, qualifier or cross-expression scope decisions.
8. **Report boundary:** `resolution_status` is for the concept/resolver component only; future P1.5 `overall_status` spans all applicable mandatory stages. `NOT_EVALUATED` is not PASS. For original JSON AST inputs, source grammar is also `NOT_EVALUATED` (P1.2 provenance limit).
9. **Diagnostics and AST location:** source lexical diagnostics from P1.2 retain precise UTF-8 offsets; new P1.3 errors use deterministic JSON Pointer paths, **not guessed text spans**. Completeness of semantics and full span diagnostics are deferred to P1.5.
10. **No runtime claims:** no foreign ID becomes a Principal, no Capability becomes Authority, and no Result becomes Outcome/Verification/Completion/Satisfaction.

## Integration contract for P1.4

P1.4 may depend on `Resolver.resolve_bytes(...).bindings`, the 8 named `checks`, `context_id`, and the **declared concept IDs**. It MUST NOT treat `resolution_status=PASS` as global conformance. It should use the P1.1 reference type registry and scoped predicate/method contracts supplied in caller context, without inventing production REL-01 signatures. It must preserve the untrusted `source_kind` and the non-authoritative `witness_ref` boundary.
