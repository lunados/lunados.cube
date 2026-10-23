# P1 Extended — Basic Visual Grammar v1

## Scope
A display-only P1 extension: Form + Color on top of the **existing 129 Unicode symbols** from v9.4 Annex J. No SVG files, no identity or authority changes, no P1 validator behavior changes.

Static publication: `AIAEAO_Pure_Cube_P0_v9.4/validation/v1/visual/manifest.json`.

## Local validation

From a checkout of `lunados/lunados.cube`, after merging the full P1 release overlay:

```bash
python3 P1/visual-grammar-v1/scripts/verify_visual_grammar.py
python3 P1/release-v1/scripts/verify_p15.py
```

## Interpretation
- v9.4 Morphology is the single authority for symbols. P1.1 contractual validation is independent of this visual-only profile.
- Geometry and colors are **optional CSS/HTML primitives**, not new glyphs, SVGs or semantic truth signals.
- The source path `lunados.space/web/satellites/visual-grammar/index.html` refers to an earlier viewer (VG v0.9.3), not a v9.4 contract. See published `form-color.json` lineage for exact design source files.
- `P1-VG-basic/1.0.0` is a proposed display extension awaiting human signoff and deployment checks.

## Release note
Deploy by unpacking the ZIP **at the existing GitHub repository root** and merging the paths, not replacing the existing P0 folder. Current Cloudflare Pages Build Output remains `AIAEAO_Pure_Cube_P0_v9.4`.
