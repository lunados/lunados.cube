# AIAEAO Pure Cube — P1.4 Semantic Validator

**Local engineering deliverable:** `P1/semantic-validator-v1/`  
**Descriptive validation profile:** `P1-VC/1.0.0`  
**Semantic authority:** unmodified *AIAEAO Morphology v9.4*, human-adopted documentary reference 2026-10-23.

P1.4 is a **Python 3.11+ standard-library-only**, offline validator on top of the included P1.2 parser and P1.3 resolver. It does not deploy anything, invoke a tool, make an AIAEAO Core decision, or verify historical truth. The P0 v9.4 files remain immutable.

## Quick start

From this directory:

```bash
# P1.1/P1.2/P1.3/P1.4 joint regression checks
python3 -m unittest discover -s tests_parser -q
python3 -m unittest discover -s tests -q
python3 -m unittest discover -s tests_semantic -q

# Two published P0 examples: PASS only within these explicit, hypothetical contexts
python3 -m cube_semantic -i fixtures/migration.acg \
  --context fixtures/migration.binding-context.json
python3 -m cube_semantic -i fixtures/metaphysics.acg \
  --context fixtures/metaphysics.binding-context.json

# Nontrivial method-profile and T/O qualifier examples
python3 -m cube_semantic -i fixtures/semantic/example-method.acg \
  --context fixtures/semantic/migration-with-method.binding-context.json
python3 -m cube_semantic -i fixtures/semantic/example-qualified.acg \
  --context fixtures/semantic/migration-with-method.binding-context.json \
  --qualification-profiles fixtures/semantic/migration.qualifier-profiles.json

# Compact reproducible release check
python3 scripts/verify_semantic_release.py
```

CLI exit codes: `0` = descriptive **PASS**, `1` = **UNRESOLVED**, `2` = **FAIL**, `3` = invalid input, profile, or frozen reference files. Machine-readable output uses the **unchanged** P1.1 `contract/report.schema.json` shape. It intentionally omits a free-form AST-path member not allowed by that schema; a stable AST path is included in diagnostic messages.

## Eight stages

`syntax`, `structure`, `concept_resolution`, `referent_binding`, `predicate_typing`, `method_typing`, `qualifier_typing`, `scope_consistency`.

- **Predicate**: exact scoped, versioned caller-provided signature; direction and subject/object concept IDs; required relation-level qualifier coordinates. Without a typed signature, `UNRESOLVED`; wrong declared direction/type, `FAIL`. No universal signatures are invented from the ten P0 predicate **names**.
- **Method**: exact namespaced method ID, revisioned scoped declaration, argument count/type, pure-declarative effect class; effectful application **FAIL**, no tool execution. No return types or keyword-parameter contracts are inferred.
- **Qualifiers**: T uses v9.4's eight named facets; T/O witness requirements, F method binding, M descriptive/presentation-mode handling, order preserved; missing qualification contract or witness -> `UNRESOLVED`.
- **Scope**: enforce same declared scope between signature/referent/context and optional qualifier profile; untrusted declaration does not become Authority or real-world evidence.

## Optional P1.4 qualifier profiles

The P1.1 `binding-context/1` does **not** contain machine-readable T/F/M/O signatures. Rather than silently extending that frozen schema, P1.4 defines a **separate**, caller-supplied `qualification-profiles/1` fixture document. See `QUALIFIER_PROFILES.schema.json` and `fixtures/semantic/migration.qualifier-profiles.json`.

These profiles constrain parameter names, required fields, scoped values, and references to **declared, unverified** witness pointers. They **do not prove** occurrence times, message delivery, perception, operating mode admission, or source authenticity. A qualifier `PASS` is only a locally declared descriptive *shape* check. `Loose`/`Strict`/`Transitional` are still presentation labels, **not** authorized runtime MODE values. This P1.4-only extension and extra `P1_QUALIFIER_SIGNATURE` diagnostic require explicit review in P1.5; they do not modify P1.1 or v9.4.

## Reused snapshots

`baseline/P1_1_Contract_Freeze/` is the unmodified P1.1 contract snapshot; `baseline/P0_reference/` contains pinned machine files. The parser and resolver are copied directly from the P1.3 package. No external AIAEAO server or live registry is needed.

## Non-goals and explicit limitations

- No externally authenticated identity, causal truth, actual historical facts, authorization, governance Admission, proof of Verification/Satisfaction, or production Schema parity.
- Only **specified**, caller-scoped technical relation and method signatures are checked. `additional_constraints` narrative strings in P1.1 fixture profiles are preserved as *declarations*; they are **not** executed as formal constraint logic.
- Nested relation/function return types are **UNRESOLVED** when a signature would require them. Semantic keyword-parameter typing is also **UNRESOLVED** because the frozen P1.1 schemas define no signatures for those parameter values.
- Text grammar is not proven when input is a standalone JSON AST (`syntax: NOT_EVALUATED`). Valid structural and descriptive typing does not imply syntax provenance.
- The 32 P0 constraints are **not all executable**. `RULE_COVERAGE.json` distinguishes mechanically checked cases, noninference guards and uncovered conceptual rules.
- An independent P1.5 conformance oracle, CI/release packaging, and full coverage review are pending. This package contains many executable fixture regressions, **not** evidence of global semantic correctness.
- No Rust/WASM production implementation is claimed; this is a Python reference validator with actual executed tests.

## Deployment / GitHub

**Nothing is pushed or published by this package.** The user will publish after P1.1–P1.5 are reviewed. The existing `/v9.4/` static content at `cube.lunados.net` stays unchanged. A future published validator manifest should live in `/validation/v1/` only after P1.5.
