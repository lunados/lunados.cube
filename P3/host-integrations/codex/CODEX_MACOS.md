# Codex macOS App — AIAEAO G5 remote integration

**Scope:** Host adapter only. Server identity, seven tools, 14 P0 Resources, G5 Bearer gate unchanged. No repository, Cloudflare or Claude deployment is modified by this package.

**Remote:** `https://aiaeao-cube-g5-gateway.jo-885.workers.dev/mcp` (Streamable HTTP)

**Credential source:** login Keychain, service `aiaeao-g5-mcp-token`; no plaintext in Codex config or repo.

## Recommended for Codex GUI: Keychain-backed stdio credential bridge

Codex officially supports Streamable HTTP and the `bearer_token_env_var` setting. However, macOS GUI processes do not necessarily inherit variables exported in Terminal. We therefore supply a *host-side* stdio-to-Streamable-HTTP bridge, which reads the token from Keychain immediately before each HTTPS request and forwards MCP JSON-RPC. It is not a new Cube server or new G5 tool. It creates no files during execution, does not expose a listening port, and does not require packages beyond macOS Python.

The local Codex MCP server will appear as `aiaeao_cube_g5` with stdio transport; the *upstream* connection from the bridge to Cloudflare is still Streamable HTTP. This distinction must be stated in acceptance evidence.

1. Unpack ZIP in Finder, copy extracted folder under `~/cube-patches/`; rsync the `P3/` directory onto repo (see root README).
2. Check Keychain **without printing** a secret:

   ```bash
   security find-generic-password -a "$USER" -s aiaeao-g5-mcp-token >/dev/null
   echo "Keychain status: $?"  # expect 0
   ```

3. Preview non-destructive Codex installation:

   ```bash
   cd "$HOME/Downloads/lunados.cube"
   python3 P3/host-integrations/codex/scripts/install_codex_g5.py
   ```

4. Install only after reviewing preview:

   ```bash
   python3 P3/host-integrations/codex/scripts/install_codex_g5.py --install
   ```

   This saves a *no-secrets* bridge at `~/.local/share/aiaeao/codex/g5_stdio_bridge.py`, backs up an existing `~/.codex/config.toml` once, and adds only this one named Codex MCP stanza. Other configured MCP servers are preserved. No other configuration file is edited. The installer requires Python >=3.11 to validate the TOML.

5. Fully quit and restart the **Codex macOS App**. In its MCP/server settings or tool listing, confirm `aiaeao_cube_g5`. Optional CLI sanity check: `codex mcp list` and `codex mcp get aiaeao_cube_g5` if the CLI is installed. CLI listing alone **does not prove authentication**.
6. Issue the acceptance prompt from `CODEX_ACCEPTANCE_PROMPT.md` inside the real Codex App.

### Fallback: native Streamable HTTP (CLI and GUI only when environment is available)

If your installed Codex App reliably injects an environment variable into the Codex MCP process, the native configuration is preferable:

```toml
[mcp_servers.aiaeao_cube_g5]
url = "https://aiaeao-cube-g5-gateway.jo-885.workers.dev/mcp"
bearer_token_env_var = "AIAEAO_G5_TOKEN"
enabled = true
startup_timeout_sec = 30
tool_timeout_sec = 120
```

**Never paste the token into `config.toml`.** For a CLI session only, launch it from a shell that has read the Keychain value:

```bash
export AIAEAO_G5_TOKEN="$(security find-generic-password -a "$USER" -s aiaeao-g5-mcp-token -w)"
codex
unset AIAEAO_G5_TOKEN
```

An app launched from Finder typically **will not inherit** this Terminal variable. The provided installer deliberately selects the Keychain-backed bridge to avoid an insecure global `launchctl setenv` approach. Do not combine both configurations using the same server name.

### Credential security and limits

- The bridge never prints the bearer token, stores it on disk or passes it as an argv argument. It exists briefly in the bridge process memory and in the HTTPS header, which is required to authenticate.
- `security` may request Keychain permission. No cleartext exposure in normal logs, config or repository; the usual macOS process-memory/Keychain trust boundaries still apply.
- It hardcodes the single approved HTTPS endpoint, refuses redirects, sets 90-second network timeout and 2 MiB request/8 MiB response limits. It handles JSON and SSE MCP response framing; **does not implement long-lived unsolicited notifications, reconnect/replay or subscriptions**. These features are outside the current seven-tool proof scope.
- If Codex does not support the stdio adapter or the tool/resource protocol is incompatible, record `HOST_UNSUPPORTED`; **do not relax G5 bearer authentication**.
- Existing Claude connector is unaffected; do not change or rotate the shared G5 token for this test.
- Manual rollback: remove only the marked stanza from `~/.codex/config.toml`, delete `~/.local/share/aiaeao/codex/g5_stdio_bridge.py`, quit/restart Codex. Backup `~/.codex/config.toml.aiaeao-g5.backup` was created on first install; do not blindly restore if other settings changed meanwhile.

### Source and evidence

- Official Codex MCP guide: https://learn.chatgpt.com/docs/extend/mcp
- Configuration reference: https://learn.chatgpt.com/docs/config-file/config-reference
- Evidence template: `CODEX_HOST_ACCEPTANCE.md`
- Offline host-adapter check: `python3 -m unittest discover -s P3/host-integrations/codex/tests -v`
- Existing remote SDK parity test (different host): `python3 P3/remote-mcp-g5/scripts/sdk_remote_smoke.py` with the prior environment setup. This is not a Codex App acceptance substitute.
