# P1.3 — Acceptance matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-13-01 | Exact 80 canonical keys + five explicit Greek aliases, no implicit glyph/NFKC mapping | source-lock hash, all key-map tests, Unicode negative controls | PASS |
| AC-13-02 | Wrong Home rejects, unknown Concept does not fabricate identity | `test_wrong_home_failure`, `test_unknown_key_unresolved` | PASS |
| AC-13-03 | All non-instantiable X/Y viewpoints reject instantiation | dimensions, logic relation, Y arrow negatives | PASS |
| AC-13-04 | Concept lookup never implies matching referent identity | missing and mismatched contexts | PASS |
| AC-13-05 | Explicit referent concept, home, layer and scope must agree | mismatch tests | PASS |
| AC-13-06 | β and ζ layer no longer silently imply T/O witnesses | no-witness + unverified-pointer cases | PASS (declared pointer only) |
| AC-13-07 | Unknown instantiation profiles remain unresolved | X endpoints and Z zones | PASS |
| AC-13-08 | Nesting traversed deterministically; AST not mutated | nested methods/relations and order tests | PASS |
| AC-13-09 | Invalid or ambiguous caller context rejected before interpretation | invalid source, version, duplicated referents/keys, scope, layer tests | PASS |
| AC-13-10 | Golden migration and metaphysics examples pass *only resolution stages* | text and AST parity with declared fixture context | PASS |
| AC-13-11 | Parser regressions retained | vendored P1.2 26-group suite | PASS |
| AC-13-12 | Result semantics separate from the complete P1 report | resolution-report schema + tests | PASS |
| AC-13-13 | Reproducible file hashes + isolated offline CLI | release manifest, `verify_release.py`, CLI smoke | PASS |

## Explicit deferrals (NOT P1.3 failures)

- P1.4: scoped relation signatures, method signatures, T/F/M/O profiles and witness interpretation; cross-scope consistency across references.
- P1.5: integrated eight-stage validation report, diagnostic UTF-8 spans for semantic nodes, full 25-fixture conformance and independent Rust parity (if Rust implementation is adopted).
- Neither this implementation nor declared fixture origin asserts external proof, real-world truth, Admission or execution.
