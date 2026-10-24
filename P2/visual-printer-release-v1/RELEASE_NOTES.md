# Release Notes — VP-06

**Version:** `P2-VP/1.0.0-rc1` (local release candidate) · **Date:** 2026-10-24.

## Scope completed

VP-01 basic SVG; VP-02 named Cube views; VP-03 five explicit Lens Profiles; VP-04 three granularity levels and exact omission ledger; VP-05 90-case conformance and advisory splitting; VP-06 unified agent CLI, public metadata and reproducible release gate.

The last step uses composition, not rewrites: unchanged VP-05 ConformanceAuditor + unchanged VP-04/VP-03/VP-02 printers. All sample claims and measurements remain `declared_unverified`.

## Agent-facing integration

`prepare` can lock an already authored VP-03 bundle to an explicit VP-04 print job without manual SHA calculation. `check` performs full in-memory rendering/auditing and returns JSON. `print` creates SVG and report together. Every failure produces a stable `VP06_*` diagnostic JSON on stderr. A single capabilities document keeps selection deterministic.

## Delivery

Full P2 source snapshots, golden samples, preview page, acceptance matrix, source lock, file checksums, and a separately opt-in public Cube metadata overlay + CI workflow. Neither GitHub nor Cloudflare has been changed.

## Open limits

- No generic ACG→view-plan translator or semantic reasoning engine.
- No observed-in-production Agent compatibility evidence; Claude/Grok usage needs their host to execute the local CLI.
- Platform-specific Unicode glyph fallback.
- Layout caps and no automatic multi-SVG / scene graph / interactive app / 3D.
- Production CI, Cloudflare and public URL verification pending user-controlled publication.
