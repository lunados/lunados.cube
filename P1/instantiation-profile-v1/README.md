# P1.6 — Charge 1 of 3: additive specification and contracts

**State:** CONTRACT CANDIDATE / schema-preflight only. NOT implemented, NOT deployed, NOT a production authorization.

Contents:
- `P1_6_ACCEPTANCE_SPEC.md` — full revised acceptance v1.1 candidate, decisions resolved, edge cases clarified.
- `P1_6_DECISIONS.md` — explicit D-1..D-4 and safety gates.
- `context-v2.schema.json` — copied `/1` structure plus `/2` discriminant, caller profiles and typed referent additions.
- `INSTANTIATION_PROFILES.schema.json` — closed caller profile/descriptor schema.
- `instantiation_reference_v1.json` — ten exact X endpoints, five pair-scopes, type allowlists and conditions derived from Morphology v9.4 §§6.2.1–6.2.5 and existing P1.1 identifiers.
- `fixtures/valid_conclusion_context_v2.json` — full schema-valid fixture, **not** runtime validator proof.
- `tests/test_contracts.py` — schema-preflight checks and contracts invariants, without touching runtime.

## macOS copy from Finder-extracted ZIP

```bash
cd "$HOME/Downloads/lunados.cube"
rsync -av "$HOME/cube-patches/AIAEAO_Cube_P1_6_Charge_1_Contracts_v1_1/P1/" ./P1/
python3 -m unittest discover -s P1/instantiation-profile-v1/tests -v
```

The tests require `jsonschema>=4` in the active Python environment; the repo `.venv` may already supply it. No automatic dependency installation, deployment or Git push is performed by this package.

## Three charges

1. **Contracts and decisions (this package):** schema-valid additions, frozen semantics proposed, no changes to existing files.
2. **P1.6 validator implementation and independent local oracle:** implement `/2` instantiation logic, ten positives, negative status/diagnostic matrix, R-01–R-13 and byte-identical `/1` regression.
3. **Host/MCP & G5 proof parity and independent acceptance:** update local & remote version discovery without tool signature change; execute live R-01–R-13 and regress Claude/Codex. Gate deployment on local PASS; preserve `G5_PROOF_NOT_PRODUCTION_AUTHORIZED`.

Review Charge 1 before merging/deploying later charges. `P1/contract-v1`, P0 and legacy schema must stay byte-identical.
