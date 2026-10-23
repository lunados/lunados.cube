# AIAEAO Pure Cube — P1.1 Contract Freeze

**Validator Profile:** `P1-VC/1.0.0`  
**Semantic Source:** Morphology v9.4, human-adopted documentary reference of 2026-10-23  
**Existing P0:** static reference published at `cube.lunados.net`  
**Disposition:** specification drafted and statically checked; **awaits explicit project acceptance before implementation freeze**.

## 1. Purpose and non-goals

Define a deterministic, implementable **descriptive conformance** contract for P1.2–P1.5.
A validator tests a *bounded input under a declared context*, not the completeness of
AIAEAO philosophy, existence of an external system, authenticated empirical truth,
correctness of a production Core/Tool, or operational Admission. No new v9.4 root,
reference definition, canonical Event field or real AIAEAO server dependency is created.

No dynamic functions, API tokens, Cloudflare Workers, natural-language inference,
foreign-system import or executable actions are in P1.1. The public P0 remains unchanged.

## 2. Authority and contract layers

1. **Morphology v9.4** — one documentary conceptual source of truth, especially §§2.9,
   3.1, 3.6, 3.10, 3.12, 5.6–5.14, 6.1–6.4, 7.6.1, 7.37–7.38.
2. **P0 machine projections** — catalog, relation names, constraints, EBNF and structural
   AST schema, all pinned by SHA-256 in `contract/source_lock.json`.
3. **P1-VC** — a new *local, separately versioned validator behavior and interchange
   profile*, never an alternative morphology or accepted Core/Event contract.
4. **Caller-provided binding context** — untrusted subject declarations and scope-bounded
   predicate signatures; may permit descriptive type checks, not external truth or Authority.

Any discovered contradiction between P1 projections and v9.4 must **stop that claim**,
not let the implementation silently rewrite v9.4. Altering P1 semantics requires a new
P1-VC version and corresponding tests; altering Morphology requires a separate adoption.

## 3. Freeze: syntax and text processing

`contract/notation_p1.ebnf` is the normative P1.1 syntax proposal, constrained by the
existing P0 `notation/grammar.ebnf` and `notation/ast.schema.json`. Preserve exactly the
four P0 AST kinds: `reference`, `qualified`, `relation`, `application`.

- Input may be `acg_text` or P0-compatible `json_ast`. One source expression only.
- Decode strict UTF-8, without BOM. No comments, Markdown fences or infix arrows.
- Whitespace is limited to ASCII space, TAB, LF and CR between tokens.
- `String`/`Number`/`true`/`false`/`null` follow strict JSON lexical rules; no NaN,
  Infinity, unescaped control character or unpaired Unicode surrogate escape.
- Method IDs match `^[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*/v[1-9][0-9]*$`;
  parameter keys match `^[A-Za-z_][A-Za-z0-9_]*$`; no duplicate keys.
- Relation call syntax is `rel("predicate", subject, object [; k=value,...])`;
  accepted predicate names alone do **not** confer signature validity.
- Concept keys come **only** from `contract/concept_keys.json`; do not resolve from
  rendered Unicode glyphs, font appearance or NFKC normalization. Five explicit Greek
  semantic aliases `Ψ Γ Σ Ξ Π` resolve solely to non-instantiable X dimensions.
- Preserve qualifier order and multiplicity: never commute O/T, collapse repetitions
  or infer an authoritative mode from presentation order.
- Engineering input limits are frozen in `validation_profile.json` (1 MiB source,
  64 depth, 10,000 AST nodes, 64 parameters and 64 qualifiers per expression).

**Future printer rule:** P1.2 may emit a canonical display form only after explicitly
specifying decimal-number serialization and deciding whether comparison is byte- or
AST-value-based. The freeze does not falsely promise byte-identical numeric roundtrips.

## 4. Freeze: identity and referent binding

A reference expression `home:layer:concept_key["referent"]` passes syntax if well
formed; it has not thereby referenced any existent thing.

1. Resolve `(home, concept_key)` exactly to one P0 catalog concept ID. Pairing the
   right concept key to an explicitly wrong home => **FAIL**; an unknown key =>
   **UNRESOLVED** until a legitimate versioned catalog extension exists.
2. Dimensions, X logic relations and Y relation-arrow symbols are not instantiable
   reference types. `X:α:Σ["q"]` => **FAIL**.
3. X Scopes; Y identity anchors/resource/identified objects; Z module/boundary
   concepts are *eligible for qualified instance binding*, **not auto-instances**.
   X endpoints and Z presentation zones require a more specific binding profile.
4. A `referent_ref` must match a declared object of compatible concept ID, home,
   selected layer and (where declared) scope in `binding-context/1`.
5. No context or no evidence of actual referent identity => **UNRESOLVED**. Inconsistent
   explicit bindings => **FAIL**. A foreign Actor string is not an authenticated
   Principal. Source declarations remain untrusted until independently assured.
6. α = descriptive freedom; β = observer-rule-bound; ζ = historically instantiated
   with temporal witnesses. The spelling `ζ` never proves recording, Admission,
   authorized effects or surviving T/O witnesses. A missing witness remains **UNRESOLVED**.

## 5. Freeze: relations and predicates

The existing P0 `relations.json` names ten technical relation kinds (`parent`,
`child`, `references`, `related`, `sameAs`, `supersedes`, `derivedFrom`, `causedBy`,
`resultOf`, `fulfills`). These are **vocabulary**, not universal accepted domain/
range signatures. X logic and Y arrows remain distinct vocabularies.

- Without a versioned, scoped predicate contract: `predicate_typing = UNRESOLVED`.
- A caller-declared predicate contract must specify name, revision, scope, provenance,
  direction and allowed subject/object concept IDs. A known mismatch => **FAIL**.
- A profile declared by a fixture can establish local *descriptive admissibility*
  for its declared world only. It never authenticates either operand or assertion.
  *Descriptive PASS* requires no independent authentication; a separate request
  for external/empirical trust without attestation is UNRESOLVED, not PASS.
- `resultOf` does not establish Verification, `related` does not establish causality,
  `sameAs` does not erase separate provenance, and path composition does not infer a
  new predicate. Constraint IDs C005, C008, C017–C020, C026–C030 apply where relevant.

The two example profiles freeze only these **hypothetical** relation signatures:

| Fixture | Predicate | Subject | Object | Evidence level |
|---|---|---|---|---|
| Migration | `references` | Y Artifact | Y Resource | declared, unverified |
| Metaphysics | `related` | Y Annotation | Y Annotation | declared, unverified |

No generalized entailment for these named predicates is derived from two examples.

## 6. Freeze: T/F/M/O and layer conformance

T/F/M/O are **qualifiers, not definition homes**. P1.1 preserves:

- **T:** 8 named facets; role and clock origin/unit/precision/source/validity are
  independently qualified when relevant. Occurrence order/partial logical order is
  neither a scheduling command nor causation (§3.6 D.1/D.2).
- **F:** method name, version and activation/effect preconditions are distinct;
  a changed parameter alone is not changed output (MR-03).
- **M:** Loose/Transitional/Strict remain optional VG interpretations, not an
  adopted runtime MODE enum or grant.
- **O:** eligible, permitted, selected, visible, delivered, perceived and concluded
  are different claims. A value flag cannot independently establish delivery or
  human/AI perception (§4.9).

A missing qualifier profile/witness produces **UNRESOLVED** on the relevant stage,
not a fabricated historical state. Unknown or invalid enumerated built-in T roles
without any declared extension profile produce **FAIL**.

## 7. Freeze: validation report and determinism

Report JSON schema: `contract/report.schema.json`. Stage order:

1. `syntax` — lexical and grammar compliance.
2. `structure` — conforms to the published P0 structural AST schema.
3. `concept_resolution` — exact home and semantic concept-key resolution.
4. `referent_binding` — declared identity, scope and layer witness checks.
5. `predicate_typing` — versioned predicate contract matching (if relation).
6. `method_typing` — versioned method identity, argument signature, effect-class declaration (if application).
7. `qualifier_typing` — T/F/M/O applicability, required witness/profile.
8. `scope_consistency` — constraints of declared scope and cross-qualification.

Each stage reports `PASS`, `FAIL`, `UNRESOLVED`, or `NOT_EVALUATED` with reason.
`NOT_EVALUATED` is appropriate for skipped stages (e.g., after malformed syntax),
not a synonym of success. For *applicable* mandatory stages:
**FAIL > UNRESOLVED > PASS**; non-applicable stages excluded. First errors do not
rewrite unknown evidence into negative reality.

Every diagnostic provides a stable `P1_*` code, stage, severity and reference rule.
When an input span exists, use zero-based UTF-8 byte offsets `[start,end)`, plus
one-based line/Unicode-scalar column. Sort by source start, code, stage ordinal;
report order is not dependent on hash-map iteration. Keep deterministic error messages.

**Always separate from the aggregate:** `epistemic_warrant`, `current_authority`
and `canonical_admission` are `NOT_EVALUATED` for the P1 validator. Even descriptive
PASS asserts no source truth, real-world operation, Completion or Satisfaction.

## 8. Failure semantics and compatibility

- `FAIL` = violation of a *specified* lexeme, shape, home, binding, typed contract
  or scope condition supported by the input/context.
- `UNRESOLVED` = insufficient declared profile, source identity, clock or witness
  to complete a requested check; **not** empirical falsification.
- `PASS` = only the declared, bounded descriptive check succeeded.
- The aggregate `overall_status` is **only** PASS/FAIL/UNRESOLVED; `NOT_EVALUATED`
  is reserved for individual stages and explicitly excluded from aggregate results.
- `NOT_EVALUATED` = not applicable or not attempted; requires explanation.

The proposed P1 profile is compatible with the P0 AST *shape*, but P0 examples
will only attain full descriptive PASS when a compatible scenario context is
explicitly supplied. Without that context they correctly remain UNRESOLVED.

## 9. Acceptance and implementation handoff

P1.1 exit: `AC-01`–`AC-12` in `ACCEPTANCE_MATRIX.md`, plus explicit project
acceptance of this profile. The included executable script checks the *contract
package and schemas*, not a parser. The 25 fixture entries are implementation
obligations for P1.2–P1.5, **not passed behavior tests**.

P1.2 implements syntax/AST handling; P1.3 implements resolution; P1.4 applies
versioned scoped predicate/qualifier contracts; P1.5 runs independent negative
controls and publishes reproducible conformance. No operation performs effects.

**Deployment principle:** keep `AIAEAO_Pure_Cube_P0_v9.4/v9.4` immutable;
create a separate `P1/contract-v1` package now and a separate future
`validation/v1` public release only after conformance checks.
