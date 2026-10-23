# P1 extended — Basic Visual Grammar for AI agents

**Display grammar, not semantic authority.** Apply only after reading the v9.4 Unicode registry and, where appropriate, P1 parser/resolver results. This extension does not change `/v9.4/` or assert runtime conformance.

## Three visual layers

1. **Symbol:** Use the exact registered single-codepoint Unicode character from `/v9.4/visual/symbols.json`, looked up by `anchor_id` in `anchors.json`. Never use glyphs as semantic IDs, never normalize IDs using NFKC. Include a readable label.
2. **Form:** Use `form-color.json` `forms[]` and the suggested `form_id` in `anchors.json`. Forms are **optional** HTML/CSS carriers. `form.glyph-only` is always a valid fallback. If rendering primitives are unavailable, display Unicode plus text.
3. **Color:** Prefer neutral. Five X lenses and their ten endpoints MAY use a historical domain accent; status accents require an explicit declared state witness. An arrow/operator gets **no forced color or shape**. Color is never the sole information carrier.

## Recommended shape reference (CSS-only, no SVG)

| Role | Optional carrier | Note |
|---|---|---|
| Five X dimensions | Circle/halo | One registered Unicode anchor at center |
| X complementary endpoints | Rounded anchor card | Preserve pair distinction by label/glyph |
| Y resources | Simple rectangle | Object presence is not evidence |
| Y identities | Pill/chip | Actor, Principal, Role Binding remain distinct |
| Z boundaries | Outline/frame | No admission or tier inferred |
| Z modules | Labeled rounded block | Does not imply deployed runtime |
| Z zones | Neutral band | No automatic trust/authority boundary |
| State | Badge/pill | State color requires witness |
| Y relation arrows | Unicode glyph on line | Never infer symmetry or causation |
| UI elements | Plain surface | Never ontology home |

## Rendering algorithm

- Resolve display `anchor_id` against `anchors.json`; reject arbitrary Unicode substitutions.
- Choose `form_suggestion` or `form.glyph-only`; forms are not forced on the registered glyph.
- Choose optional `domain.*` accent ONLY where `domain_accent_token` matches the registry; otherwise omit color.
- For `status.*`, require `qualified_state_witness_ref` and a state-marker anchor; even then present as an attributed statement rather than verified truth.
- For `relation_operator`, never apply a forced chromatic token.
- Show the `label` in both colored and monochrome modes. Test keyboard/screen-reader fallback in the host renderer.
- Emit a `render-plan.schema.json`-compatible plan. SVGs, images, icon libraries and external fonts are not needed.

## Illustrative, not factual

`examples.json` uses a **fixture** running state and a deliberately scoped witness. It does not prove that anything actually ran. Shape and color do not establish truth, verification, Permission, Authority, Admission, Completion or Satisfaction.

## Source alignment

Source example: `lunados/lunados.space/web/satellites/visual-grammar/index.html` (historical VG v0.9.3), together with its symbolic registry, pair grammar and earlier CSS form/color design. The index is a historical standalone (over 3 MB), not copied into this package. Morphology v9.4 Annex J remains the sole canonical Unicode symbol selection; old registries remain design provenance, not a second authority.
