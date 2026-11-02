# G5 – consolidated acceptance ledger (2026-10-24, updated 2026-11-02)

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
| R5 Post-consolidation redeploy | SUPERSEDED | Core and gateway were redeployed for R5.PV (`0.8.0-proof`, `0.2.0-proof`) and R6 (`0.9.0-proof`); the general remote SDK smoke passed in R6 ([R6](G5_R6_ACCEPTANCE.md)). The Claude MIME check was not repeated separately |
| R5.PV Control flow and plan views (MILE-010) | OFFLINE PASS 88/88; LIVE 87/88, 87/88, 86/88, 87/88 (CPU limit documented); HOST PASS 7/7 | Core `P3-MCP-REMOTE/0.8.0-proof`, gateway `0.2.0-proof`: `/9` and the three plan tools ([spec](G5_R5_ACCEPTANCE_SPEC.md) §10). Offline parity ([report](evidence/G5_R5_OFFLINE_PARITY.json)); every live deviation is `G5_CORE_UNAVAILABLE` on P-K07-flow or P-K08-sequence, run 4 with `exceededCpu` at 139 ms CPU ([runs](evidence/G5_R5_LIVE_SCRIPT_RUN4.json), [core tail](evidence/G5_R5_CORE_CPU_EVENT.json)); host subset over the Claude connector ([report](evidence/G5_R5_HOST_REPORT.md)) |
| R6 Relation origin (MILE-011) | OFFLINE PASS 26/26 and R5 legacy 87/87; LIVE 25/26 in three runs; HOST PASS 9/9 | Core `P3-MCP-REMOTE/0.9.0-proof` (Cloudflare version `445c6d50-…`), gateway `0.2.0-proof` with the additional `origin_lines` argument: P1.14 `/10` and VP-07.6 ([acceptance](G5_R6_ACCEPTANCE.md), [offline](evidence/G5_R6_OFFLINE_PARITY.json), [legacy](evidence/G5_R6_LEGACY_PARITY.json)). Live deviations `G5_CORE_UNAVAILABLE`: P-OL-07 twice, with `CpuLimitExceeded` at 522 ms CPU ([core tail](evidence/G5_R6_CORE_CPU_EVENT.json)), V-HO-11 once without a cause in the core tail ([runs](evidence/G5_R6_LIVE_SCRIPT.json)); host subset over the Codex connector, P-OL-02 after one repeat ([report](evidence/G5_R6_HOST_REPORT.md)) |
| R7 Production operations (formerly listed as R6) | NOT PLANNED | CPU budget (Workers Paid, `limits.cpu_ms`), OAuth / tenant isolation, rate limiting, observability, rollback/secret rotation, cost controls require a separate gate; candidate after testing the current state ([roadmap](../../docs/01-roadmap/ROADMAP.md)) |

**Known limits** of the current remote state, with evidence and the local way out: [`KNOWN_LIMITS.md`](KNOWN_LIMITS.md).

The old G5 prototype's `R3 Security / R4 Exact parity / R5 Host UX` were descriptive draft gate names. This ledger uses the user's operational R1–R4 naming. Do not merge them without mapping.

**No fabricated remote evidence:** The concise user-reported R3 success is preserved in `evidence/G5_R3_R4_USER_ATTESTATIONS.json`. This package contains no captured HTTP transcript from that run. `sdk_remote_smoke.py --evidence PATH` can collect a fresh sanitized R3 verification on the user's Mac. Secrets must not be committed.

**Frozen source boundary:** No changes to P0/P1/P2/G4. The G5 remote adapter is descriptive/discovery only, no automatic ACG→SVG, no Truth / Authority / Admission, and no cross-domain overall status.

**G5-R4 ACCEPTED** and **Production AUTHORIZED** are NOT claimed by this package. `Release Freeze` denotes a reviewed source candidate with explicit final gates, not the completion of those gates.
