# AIAEAO Pure Cube P1 — Validation Cube release candidate

Reference: unchanged Morphology v9.4. Validator: `P1-VC/1.0.0` (engineering candidate, subject to human acceptance).

### Delivered
- Frozen P1.1 validation contract and 25 designed conformance cases.
- P1.2 text parser and canonical AST-value printer.
- P1.3 catalog/referent resolver against declared binding contexts.
- P1.4 typed, caller-scoped descriptive semantic validation and optional `qualification-profiles/1`.
- P1.5 independent CLI acceptance oracle, SHA-lock validation, reproducible Python CI matrix and static discoverability metadata.

### Compatibility
- All published `/v9.4/` assets remain byte-identical.
- Public `/validation/v1/` provides *static profile metadata*, not callable validation endpoints. The implementation is **offline/local**.
- P0 dotfiles `.nojekyll` and `.github/workflows/verify.yml` are restored in the overlay because they are referenced by the original P0 SHA256SUMS but absent from the inspected GitHub tree; the GitHub Actions workflow that actually runs resides in the repository-root `.github/workflows/cube-p1-validation.yml`.
- Root `/manifest.json` gains `validation_profiles.P1-VC/1.0.0` and asset descriptors. No existing P0 field removed.
- Existing `P1-VC/1.0.0` report schema shape remains unchanged. `P1_QUALIFIER_SIGNATURE` is a formally documented P1.4/P1.5 code extension; 21 original codes remain as published.

### Limitations
No real-world existence proof, identity attestation, empirical truth, logic theorem verification, source-of-truth authority, tool effect or Governance Admission. Missing predicate/method profiles and T/O witnesses remain `UNRESOLVED`. Not all 32 reference constraints are executable. The package uses Python 3.11+; Rust/WASM parity is not established.

### Shipping gates still outside offline build
Human signoff on profile, first run of GitHub Actions, deployment on Cloudflare and a live GET/header check.
