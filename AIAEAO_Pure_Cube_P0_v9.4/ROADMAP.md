# Pure Cube — capability roadmap

This roadmap describes extension boundaries, not a commitment to implement
features on dates. The reference v9.4 is versioned separately from function
API versions.

## P0 — Reference Cube (this package)

Three static, read-only reference views (`core`, `time`, `observer`),
Machine-readable concept/relation/constraint catalogs, compositional notation
source grammar and structural AST interchange schema, 129 registered VG anchors,
four historical aliases, a public manifest, two foreign-domain examples and
release validation. No token, writable endpoint, runtime or server dependency.

Exit checks: complete and internally linked P0 files; 129 unique glyphs and
four aliases; no duplicate definition homes; consistent X Key Pairs;
source-bound uncertainty; both hypotheticals available without external repo.

## P1 — Validation Cube

Freeze an accepted parser/resolver profile; implement syntax, reference binding
and semantic type-checking with independent negative controls and error
addresses into the v9.4 reference. Distinguish structural, mathematical,
epistemic and admission judgments. Test actual ACG edge cases and preserve
observer/time witnesses. Do not claim external truth from a validated AST.

## P2 — Functional Cube

Offer optional, allowlisted, side-effect-free `describe`, `parse`, `validate`,
`derive` and `project` capabilities as separately versioned API methods with
scoped bearer tokens, secret storage, rate limits, audit logs and OpenAPI.
Reuse the Rust Cube only after actual parity tests. Never inherit Authority
from an API token over the unrelated AIAEAO server.

## P3 — Agent Integration

Optional natural-language-to-grammar Adapter with declared inference loss,
independent oracles, counterexamples, robust identity/source binding and
versioned external tool discovery (OpenAPI and optionally MCP).

## Release criteria

- No silent invention of adopted runtime contracts from research candidates.
- No replacement of the v9.4 reference by experimental EXP-023 fixtures.
- Every new capability has separate version/compatibility and negative tests.
- `/v9.4/` resources remain immutable after public release.
