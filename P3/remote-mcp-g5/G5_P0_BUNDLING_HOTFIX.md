# G5 P0 snapshot bundling hotfix (R3 diagnostic P0_LOCK_UNAVAILABLE)

**Purpose:** The private Cloudflare Python Worker returns `P0_LOCK_UNAVAILABLE` when `p0_resources.py` attempts to read its pinned `p0_snapshot/lock.json` using ordinary `Path.read_bytes()`. The successful CPython assembly verified that the source file exists and its lock hash matches. The first Cloudflare module listing showed Python and TXT modules but not the P0 JSON assets; this hotfix explicitly includes the snapshot's JSON, Markdown, and EBNF as Wrangler Text modules.

**Scope:** Only `P3/remote-mcp-g5/python-core/wrangler.jsonc` and a dedicated offline rule check. No changes to frozen P0/P1/P2, local G4, existing Gateway, secrets, or domains. The Core remains private (`workers_dev:false`, `preview_urls:false`). Existing Source Manifest and existing G5 release SHA manifests remain historical evidence; record this hotfix separately.

## Apply: established Finder + rsync process

1. Finder-unpack the ZIP. Finder-copy its folder to `~/cube-patches/` outside Downloads.
2. From the existing repo root:

```sh
rsync -av "$HOME/cube-patches/AIAEAO_Cube_G5_P0_Bundling_Hotfix/P3/" ./P3/
python3 P3/remote-mcp-g5/scripts/check_p0_bundle_rules.py
python3 P3/remote-mcp-g5/scripts/verify_g5.py
```

`verify_g5.py` recreates `.g5-runtime` from the unchanged frozen sources and updated Worker configuration (the generated runtime directory is not checked in). Deploy **only the private Core**:

```sh
cd P3/remote-mcp-g5/.g5-runtime
uv run pywrangler deploy
```

Observe the Wrangler module list; in particular look for `P3/adapters/mcp-local/p0_snapshot/lock.json` and the v9.4 JSON/MD/EBNF assets. If absent, **stop** and report the output: do not treat the upload as P0-compatible.

The JS Gateway is already deployed with Service Binding `CORE` and does not need redeployment if the Core keeps its name. From the repo root with the existing MCP v2 virtualenv and existing `AIAEAO_G5_URL`/`AIAEAO_G5_TOKEN` environment variables, run:

```sh
python3 P3/remote-mcp-g5/scripts/sdk_remote_smoke.py
```

**Acceptance:** first `cube_discover_surface`, then `cube_read_reference` and 14 resources work, finally P1 and byte-identical P2 SVG. The local rule check is not sufficient proof; only an actual remote call establishes R3.

If Cloudflare's Python module loader still cannot read the packaged JSON files via Path, stop rather than modifying `p0_resources.py` or disabling hashes. Investigate explicit embedded snapshot materialization in the transient Worker bootstrap as a separate, independently verified hotfix.

Sources: https://developers.cloudflare.com/workers/wrangler/configuration/ and https://developers.cloudflare.com/workers/languages/python/examples/.
