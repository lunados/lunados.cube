# Codex App G5 Host Acceptance — PENDING

Host: Codex macOS App, version: NOT RECORDED
Date: NOT RUN
Server: `aiaeao_cube_g5` (host-side Keychain credential bridge; remote HTTPS upstream)
Protected Cloudflare URL: `https://aiaeao-cube-g5-gateway.jo-885.workers.dev/mcp`

| AC | Expected | Observed | Status |
|---|---|---|---|
| AC-01 | Codex lists registered G5 MCP | not executed in user's host | NOT TESTED |
| AC-02 | HTTP bearer handshake succeeds | not executed | NOT TESTED |
| AC-03 | `cube_discover_surface` called | not executed | NOT TESTED |
| AC-04 | all 7 tools available | not executed | NOT TESTED |
| AC-05 | 14 resources actually discovered/read | not executed | NOT TESTED |
| AC-06 | no secrets persisted/exposed | adapter static checks only, host not checked | INCOMPLETE |
| AC-07 | Claude-G5 unchanged | no server changes in this package, host not rechecked | INCOMPLETE |
| AC-08 | independent Codex calls + report | not executed | NOT TESTED |

**HOST STATUS: PENDING.** Neither the Mac GUI host nor the live Cloudflare server was accessible from the package build runtime. Fill the actual evidence; never convert static expectations into PASS.
