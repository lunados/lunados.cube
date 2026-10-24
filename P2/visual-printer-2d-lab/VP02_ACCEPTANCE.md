# VP-02 — Acceptance and visual evaluation

| Gate | Criterion | Automated state | Human state |
|---|---|---|---|
| V02-01 | Exact, disjoint `cube.flow`, `cube.diagramm`, `cube.tree` namespace; no Planner aliases | PASS | — |
| V02-02 | Two authored fixtures + golden SVG and report for **each** view | PASS | Review required |
| V02-03 | `cube.flow` edges retain declaration pointers and explicit direction; no causality/time inference | PASS | Direction arrows to inspect |
| V02-04 | `cube.diagramm` measures require nonnegative finite numbers, one unit, source pointer and declared-unverified status | PASS | Axis labels to inspect |
| V02-05 | `cube.tree` rejects disconnected, cyclic, multi-parent and undeclared roots | PASS | Hierarchical routing to inspect |
| V02-06 | Re-rendering is byte-identical; SVG is valid XML without scripts, external assets or font payload | PASS | Cross-browser glyph QA open |
| V02-07 | P0/P1 frozen snapshots unchanged, 129 anchors preserved | PASS | — |
| V02-08 | Semantic conformance, epistemic warrant, authority and admission always `NOT_EVALUATED` | PASS | — |
| V02-09 | Explicit complexity cut; no silent dropped nodes/edges/series | PASS for enforced budgets | Future granularity work |
| V02-10 | Browser typography at full size, contrast and clipping, independent agent usage | NOT_EVALUATED | Open |
| V02-11 | VP-03 lens behaviors / VP-04 adjustable granularity | NOT_IMPLEMENTED | Out of scope |
| V02-12 | 3D | NOT_IMPLEMENTED | Out of scope |

**Local decision for VP-02**: `AUTOMATED_PASS / HUMAN_VISUAL_REVIEW_OPEN`. This is *not* the same as accepted visual quality on every Mac or browser.

## Manual review checklist

- [ ] Open `view_preview.html` in Safari and Chrome; inspect each SVG with actual local font rendering.
- [ ] Verify relation arrowheads represent `from`→`to` even when layout order differs.
- [ ] Inspect two chart types for tick readability, labels, unit and provenance caveats.
- [ ] Verify that no multirooted or multi-parent graph has been silently depicted as a tree.
- [ ] Re-open original VP-01 `preview.html`, confirm original four SVG examples still work.
- [ ] Try a fixture with long but allowed labels; note clipping or insufficient vertical spacing.
- [ ] Review the output from Claude/Grok using the same JSON fixture, not newly invented relations.

Recommended follow-up: `VP-02_GO`, `VP-02_REVISE`, or `VP-02_STOP`, with screenshot-level evidence. Lens and granularity packages start after this gate, not as a hidden part of VP-02.
