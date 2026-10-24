# G3 Host Acceptance — PENDING

**Local core gate (this package):** PASS (41 independent G3 tests; G2 137 tests and frozen P1.5 gate).  
**Official MCP SDK on macOS:** PENDING user-run.  
**Claude cross-domain host test:** PENDING user-run.  
**GitHub/Cloudflare:** UNCHANGED.

| Acceptance criterion | Evidence to enter | Result |
|---|---|---|
| Tools still exactly the six G2 tools | `tools/list` | PENDING |
| P0 index and pinned concept reference through `cube_read_reference` | URI, digest, bytes, paging | PENDING |
| P0 transferred bytes independently hashed if supported | computed checksum, not merely server field | PENDING |
| P1 PASS for migration fixture + context | report status, input digest, eight checks | PENDING |
| P1 FAIL and UNRESOLVED are successful MCP calls | status, isError=false | PENDING |
| No automatically inferred ACG→VP03 conversion | agent explicitly refuses no-bundle mapping | PENDING |
| Independently supplied VP03 bundle prepared and checked | job hash, report status | PENDING |
| SVG/report identical to frozen VP-06 sample | SHA-256, byte count, full report parity | PENDING |
| Contradictory P1 FAIL + P2 PASS not merged into verdict | explicitly separate P1 and P2 outcomes | PENDING |
| Truth, authority, admission NOT_EVALUATED | report values | PENDING |
| MCP Resources if host supports; otherwise `HOST_RESOURCE_UNAVAILABLE` | bridge limitation recorded | PENDING |

**Final G3 decision:** PENDING / ACCEPTED / BLOCKED

Do not mark as ACCEPTED based on offline tests or this blank form. The user's earlier G1/G2 host evidence is distinct from this cross-domain workflow.
