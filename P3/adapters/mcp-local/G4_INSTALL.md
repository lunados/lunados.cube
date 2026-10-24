# G4 macOS installation and GitHub workflow

**Use the established Finder workflow. No command-line unzip or Python archive installer.**

1. Download `AIAEAO_Cube_MCP_G4_Consolidated_Local_Release.zip` and unpack it in Finder.
2. In Finder **copy the entire unpacked folder** into `~/cube-patches/` (create the directory if needed). macOS may prevent Terminal/rsync from traversing folders within Downloads.
3. In Terminal, from the real Git checkout (`~/Downloads/lunados.cube` in the current setup):

```sh
cd "$HOME/Downloads/lunados.cube"
rsync -av   "$HOME/cube-patches/AIAEAO_Cube_MCP_G4_Consolidated_Local_Release/P3/"   ./P3/
```

The trailing `/P3/` is **required**. `rsync` must copy the inner P3 directory contents, not the outer delivery folder.

To opt in to new GitHub CI only (not required for local tests), merge the workflow separately:

```sh
mkdir -p .github/workflows
rsync -av   "$HOME/cube-patches/AIAEAO_Cube_MCP_G4_Consolidated_Local_Release/.github/workflows/"   ./.github/workflows/
```

4. Keep using the existing Python environment:

```sh
cd P3/adapters/mcp-local
source .venv/bin/activate
python scripts/verify_g4.py
python scripts/sdk_g4_stdio_smoke.py
python scripts/sdk_g3_stdio_smoke.py
```

If the venv is not available, first create it and install `requirements-mcp.txt`; the SDK must be v2. No additional Python packages are required for ordinary printing, reading or validation beyond the host MCP SDK.

5. Restart Claude Desktop completely (Cmd+Q, relaunch), confirm `cube_discover_surface` exists; run `G4_CLAUDE_ACCEPTANCE.md`.
6. Only after macOS + Claude tests pass, stage the new release on a Git branch:

```sh
cd "$HOME/Downloads/lunados.cube"
git status --short
# Do NOT commit your .venv, secrets, temp prints or cache.
git switch -c release/p3-mcp-g4
 git add P3 .github/workflows/cube-p3-mcp-g4.yml
 git diff --cached --check
 git diff --cached --stat
 git commit -m "Release G4 consolidated local Cube MCP v0.2.0-rc1"
 git push -u origin release/p3-mcp-g4
```

**Important:** Because G1–G3 may still be uncommitted, do not `git switch` away if Git says it would overwrite local changes. Instead commit the already verified consolidated P3 state on a new branch created from the current clean/compatible checkout. Check that no P0/P1/P2 files were staged. Review changes before merging to `main`.

No Cloudflare or remote endpoint is created. Do not announce Remote MCP yet.
