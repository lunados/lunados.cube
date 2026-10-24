# Optional Publication — Explicitly NOT performed

This ZIP includes an **overlay candidate** for `lunados/lunados.cube`. Its structure starts from the GitHub repository root:

```
P2/visual-printer-2d-lab/
P2/visual-printer-granularity-v1/
P2/visual-printer-conformance-v1/
P2/visual-printer-release-v1/
AIAEAO_Pure_Cube_P0_v9.4/validation/v1/visual/printer/v1/
.github/workflows/cube-vp06-conformance.yml
```

`P2` stores the Python runtime and all frozen laboratory snapshots; it is **not** served by Cloudflare if the output directory remains `AIAEAO_Pure_Cube_P0_v9.4`. The tiny public overlay contains machine-readable metadata, schemas and agent instructions only. It offers no API and cannot print SVGs over HTTP.

## Before publishing

1. Run `python3 P2/visual-printer-release-v1/scripts/verify_vp06.py` locally **from the repository root** after merging files. Check no tracked `/v9.4` asset changed.
2. Confirm that `.github/workflows/cube-vp06-conformance.yml` landed at repository ROOT, **not** inside the Cloudflare webroot.
3. Commit to a branch, open a PR into `main`, wait for the CI matrix (Python 3.11–3.13) and inspect diff. Merge only after results are green.
4. Keep the Cloudflare build output directory `AIAEAO_Pure_Cube_P0_v9.4` unchanged. Once the deployment succeeds, the manifest should be available at `https://cube.lunados.net/validation/v1/visual/printer/v1/manifest.json`.
5. Validate published digest values and links; publicly hosting the JSON **does not** make an SVG printing service available. Agents require local Python execution/installation.

No parent P0/P1 manifest is edited by this extension. Discovery can be added **separately**, once the publication URL is verified, without redefining or mutating the frozen Morphology v9.4. The static document's `status` remains `local_release_candidate_unpublished` until that step.

**Avoid copying the entire archive over an existing unrelated checkout without reviewing the diff.** `rsync -av` merges without deletion; verify all changes before committing. Never push automatically from this local experiment.
