# P1.1 Decision Register — P1-VC/1.0.0

| ID | Freeze decision | Origin / boundary |
|---|---|---|
| D01 | Morphology v9.4 is the *only* semantic documentary reference. | Morphology header / §1; P1-VC is a separate validator profile. |
| D02 | Keep `reference`, `qualified`, `relation`, `application`; no invented AST root. | P0 AST 2020-12 schema. |
| D03 | One `.acg` expression per UTF-8 file; token, WS, JSON scalars and limits frozen in P1 notation profile. | P1 engineering decision, not morphology. |
| D04 | Exact key registry 80 P0 concepts + 5 Greek semantic notation aliases; no glyph/ID coercion. | Morphology §2.9, P0 catalog. |
| D05 | Distinguish known concept, eligible instantiation, identified referent, semantic assertion, attested truth and authority. | Morphology §§2.9, 3.5, 5.14, 6.1. |
| D06 | Abstract layers α/β/ζ never prove concrete admission or witness retention. | Morphology §§3.12, 7.37. |
| D07 | Documented predicate names have *no default universal type signature*. | Morphology §7.6.1; P0 relations.json. |
| D08 | Additional scoped predicate contracts must carry revision, direction, endpoints, provenance and scope. | P1 profile implementing REL-01 candidate discipline; not Core adoption. |
| D09 | T/F/M/O remain qualifications. No automatic time conversion, observer perception, runtime MODE or tool activation. | Morphology §§3.6, 3.7, 3.10, 4.9, 5.8. |
| D10 | Four outcome words: PASS/FAIL/UNRESOLVED/NOT_EVALUATED *per stage*; tri-state aggregate. | P1 report API contract only; not a v9.4 ontology enum. |
| D11 | Descriptive PASS is not epistemic warrant, actual effect, canonical admission, external conformance or satisfaction. | Morphology §§2.3, 5.14, 7.38. |
| D12 | All diagnostics have stable codes, rule references, deterministic ordering and byte-based source spans. | P1 engineering decision. |
| D13 | P0 published files and manifest stay immutable; P1 lives in separate package/version. | P0 publication boundary. |
| D14 | The two domain fixtures provide local evidence of *declared* referents and narrowly typed relations, not independent truth. | Hypothetical use cases + Morphology §§5.17, 5.19. |
| D15 | No new canonical entity, Event-envelope field, production schema or server integration. | Morphology v9.4 adoption boundary. |

## Do not settle without new evidence or explicit future profile

- General relations for arbitrary concept-kind pairs; truth-bearing typed inference; signature completeness.
- Real, authenticated external referent resolution or Principal grants.
- Missing time clocks/transforms and Observer delivery records.
- An authoritative mode lifecycle; method invocation or execution privileges.
- Whether P1 fixture tests prove real-world mappings (they do not).
- Semantics of an unknown concept in a foreign vocabulary (mark unresolved).

## Acceptance boundary

Adoption freezes **validator behavior** as a local engineering contract.
It does **not** retroactively adopt `REL-01`, `TIME-*`, `PAT-*`, `MEAS-01`,
`FUNC-01` or universal α/β/ζ conformance into the v9.4 production schema.
