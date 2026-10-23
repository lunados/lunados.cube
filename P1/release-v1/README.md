# P1.5 — Conformance & Release

This directory is a *release gate* for the sibling `P1/semantic-validator-v1` package and frozen `P1/contract-v1`. It does not add a runtime API or modify v9.4 ontology.

## Run from repository root

```bash
python3 P1/release-v1/scripts/verify_p15.py
```

For strict JSON Schema verification install the test-only package locally:

```bash
python3 -m pip install 'jsonschema>=4.22,<5'
```

The CLI oracle (`scripts/conformance_cli.py`) has **no imports** of the implementation packages; it executes `python3 -m cube_semantic` in fresh processes and checks behavior against predefined expected cases, plus invariant/metamorphic controls.

## Files in this overlay

- `P1/contract-v1/`: frozen P1.1 snapshot.
- `P1/semantic-validator-v1/`: complete offline implementation containing P1.2, P1.3 and P1.4, their tests, and P0 machine-file snapshots.
- `P1/release-v1/`: independent CLI oracle, release checks, notes and disposition.
- `.github/workflows/cube-p1-validation.yml`: Python 3.11, 3.12, 3.13 CI matrix.
- `AIAEAO_Pure_Cube_P0_v9.4/`: **only overlay additions**, not a replacement of P0 directory. Contains updated root manifest/checksums, two P0 dotfiles absent from the inspected GitHub tree, and new `validation/v1` public metadata.

## Publication

Unzip at the root of the existing `lunados/lunados.cube` working tree (so paths merge). Review the modified P0 root `manifest.json`; do not delete the existing P0 files. Commit on a branch, run CI, then merge to `main` for Cloudflare Pages to automatically publish the static validation metadata. Use `P1_5_ACCEPTANCE.md` to record human signoff and live checks. No secret or token is required for static GET.

GitHub has **not** been changed by this package.
