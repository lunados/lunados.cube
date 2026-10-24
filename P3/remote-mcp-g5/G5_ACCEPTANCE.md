# G5 – consolidated acceptance ledger (2026-10-24)

**Scope:** P3 remote proof on two Cloudflare Workers. Proof access is controlled; **production is not authorized**.

| Gate | Grounded result | Evidence origin / next action |
|---|---|---|
| L0 frozen sources | PASS offline | 77 pinned input files; SHA256 manifest and P0 lock |
| L1 core parity | PASS offline | 17 Python tests and VP-06 exact SVG comparison |
| L2 gateway security/build | PASS user-reported | npm audit green, npm syntax/build, four security checks |
| R1 Python Worker upload | PASS user-reported | Cloudflare uploaded private core; functionality corroborated by R3 |
| R2 Remote ingress | PASS user-reported | HTTPS /health, bearer + Origin rejection in R3 |
| R3 Remote SDK conformance | PASS user-reported | Actual Python SDK client returned `PASS G5 ACTUAL REMOTE MCP: auth, Origin, 7 tools, 14 resources, P0, P1, VP06 byte parity` |
| R4 Independent Claude host | Functional PASS; FORMAL INCOMPLETE | Claude report: 27 remote calls plus earlier discovery, 7/7 tools, P0 hashes, P1 states, P2 renders; R4.8 missing persisted raw R3, R4.5 host did not hash SVG bytes himself, MIME divergence observed before fix |
| R5 Post-consolidation redeploy | PENDING | Redeploy private Core if source change included; deploy updated Gateway; repeat remote SDK and Claude MIME checks |
| R6 Production operations | NOT APPROVED | OAuth / tenant isolation, rate limiting, observability, rollback/secret rotation, cost controls require separate gate |

The old G5 prototype's `R3 Security / R4 Exact parity / R5 Host UX` were descriptive draft gate names. This ledger uses the user's operational R1–R4 naming. Do not merge them without mapping.

**No fabricated remote evidence:** The concise user-reported R3 success is preserved in `evidence/G5_R3_R4_USER_ATTESTATIONS.json`. This package contains no captured HTTP transcript from that run. `sdk_remote_smoke.py --evidence PATH` can collect a fresh sanitized R3 verification on the user's Mac. Secrets must not be committed.

**Frozen source boundary:** No changes to P0/P1/P2/G4. The G5 remote adapter is descriptive/discovery only, no automatic ACG→SVG, no Truth / Authority / Admission, and no cross-domain overall status.

**G5-R4 ACCEPTED** and **Production AUTHORIZED** are NOT claimed by this package. `Release Freeze` denotes a reviewed source candidate with explicit final gates, not the completion of those gates.
