# P1.5 — Conformance & Release Gate

## Gate matrix

| Gate | Test | Acceptance requirement |
|---|---|---|
| G01 | P0 `scripts/test_release.py` | All v9.4 reference assets and hashes unchanged |
| G02 | P1.1 source SHA lock | Morphology + P0 reference digests identical |
| G03 | P1.2–P1.4 unit suites | 26 + 41 + 73 regressions passing |
| G04 | Independently authored CLI oracle | All 25 P1.1 cases and 22 new independent controls passing |
| G05 | Adversarial lexical inputs | All 10 malformed inputs rejected |
| G06 | Metamorphic checks | Whitespace invariance; no magical referent/causality/witness |
| G07 | Report schema | JSON Schema 2020-12 check of each black-box report (with `jsonschema`) |
| G08 | Scope/truth/authority boundary | All reports keep empirical proof, Authority and Admission NOT_EVALUATED |
| G09 | Version/distribution integrity | Public manifests, immutability of `/v9.4`, checksums |
| G10 | CI | GitHub Actions on 3.11/3.12/3.13 (must be confirmed once repository has workflow) |
| G11 | Remote post-deploy | Live `GET`s/headers on custom domain (must be confirmed after publishing) |
| G12 | Human contract approval | Reviewer expressly adopts contract/extension after examination |

## Disposition

Offline candidate may be called **release candidate** after G01–G09 succeed.
**Do not** assert GitHub Actions success, public HTTP availability, or human adoption before G10–G12 are actually completed.
No Rust parity, authenticated source truth, full rule coverage or real AIAEAO Core compliance is claimed.

## Semantics of extension

The P1.4 `P1_QUALIFIER_SIGNATURE` diagnostic is accepted as an **engineering extension** (not silently added to the 21-code P1.1 registry); the separate `qualification-profiles/1` type remains a scoped, unverified, optional caller input. See `DIAGNOSTIC_DISPOSITION.json`.

## Why black-box?

The P1.5 oracle invokes the CLI in a **subprocess** and reads the output without importing `cube_parser`, `cube_resolver` or `cube_semantic`. Expectations were written from P1.1 contract clauses / fixture conditions. This is implementation-independent *testing*, not a proof of universal semantic correctness or a separately implemented validator.
