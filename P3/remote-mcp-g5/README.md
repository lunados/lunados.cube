# AIAEAO Cube G5 – Consolidated Remote MCP Proof Candidate

Seven MCP tools and fourteen P0 Resources on a Cloudflare Streamable HTTP Gateway; separate private Python Core Worker via Service Binding. This release overlay is P3-only; P0/P1/P2 and the accepted local G4 functional core are unchanged.

Start with `RELEASE_FREEZE.md` and `G5_ACCEPTANCE.md`; for actual deployment and proof evidence use `DEPLOYMENT.md`. G5 is **not authorized for production**. The source is frozen as a candidate pending Mac lockfile and the post-MIME-fix remote smoke and host evidence.

Pinned P0 SHA-256 lock: `cb259c5962a61c507ace6260d37ae364cf6658794a115052e3bc4fefdca477a1`. Gateway production versions: MCP SDK `2.4.0`, Zod `4.6.7`. Regenerate and commit the npm lockfile in the target working tree after npm audit passes.
