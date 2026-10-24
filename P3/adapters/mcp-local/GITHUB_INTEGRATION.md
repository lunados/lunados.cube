# GitHub integration — P3-MCP-LOCAL/0.1.1

This archive is a **P3-only release overlay**, not a standalone P2 copy. The existing `lunados/lunados.cube` checkout must already contain VP-06 at `P2/visual-printer-release-v1`. This release does **not** modify P0, P1, P2, `.github`, Cloudflare or public endpoints.

1. In your clean checkout, branch from `main` (`git switch -c release/p3-mcp-local-0.1.1`).
2. Copy the extracted release `P3/` directory into the repository root (not a wrapper folder); no `--delete` and no `.venv`.
3. Run `python3 -m venv P3/adapters/mcp-local/.venv`, activate it, `python -m pip install -r P3/adapters/mcp-local/requirements-mcp.txt`.
4. From `P3/adapters/mcp-local`: `python scripts/verify_local.py`, `python scripts/sdk_smoke.py`, `python scripts/sdk_stdio_smoke.py`.
5. Stage **only P3**. Inspect `git diff --cached --name-status`. Commit and push the feature branch, then merge through PR after CI/review.
6. After merge, regenerate the Claude Desktop config using the **permanent checkout path**. Confirm all four tools in Claude Desktop and record host acceptance; only then promote Gate A.

Do not commit `.venv`, `__pycache__`, environment secrets or host-specific Claude Desktop configuration. A successful GitHub PR publishes source code; it does not deploy an online MCP endpoint.
