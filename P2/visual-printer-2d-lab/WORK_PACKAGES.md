# AIAEAO Visual Printer — work packages

**Reference:** Morphology v9.4 / P0; P1-VC/1.0.0; P1-VG-basic/1.0.0. All P1 files frozen. This is a separate, local, experimental P2 module. No deployment, GitHub mutation or Cloudflare change.

| Package | Deliverable | Status in this ZIP | Acceptance / gate |
| --- | --- | --- | --- |
| **VP-00 · Reference & boundaries** | P0/P1 byte-frozen snapshots, identity/visual split, deterministic 2D input plan, work package constraints | **Implemented** | Verify 129 glyphs, v9.4 order, SHA references, no semantic promotion |
| **VP-01 · 2D SVG lab** | Python stdlib CLI, four fixed SVG templates (pairs, relation, sequence, topology), four fixtures, render snapshots | **Implemented / experimental** | XML/SVG well formed, UTF-8 Unicode anchors preserved, identical input yields byte-identical output, no external assets or scripts |
| **VP-02 · Visual QA** | Open SVGs locally in Chrome/Firefox/Safari, capture screenshots, inspect typography, spacing, contrast, overflow, relation direction, meanings, monochrome / narrow viewport | **Initial automated inspection only; human review required** | All four templates legible and non-misleading, labels don't clip, user accepts diagrams; issues recorded |
| **VP-03 · 2D Contract & Conformance** | Hardening: schema, more fixtures, golden rendered regression artifacts, robust layout / viewBox, independent oracle and release workflow | **Not started** | Explicit acceptance of VP-02; no unverified proof/authority effects; independent agent interoperability |
| **VP-04 · Optional distribution** | Opt-in packaging in Pure Cube repository and local CLI install; static guide + template spec public | **Deferred** | VP-03 approved; no P0/P1 modification, compatibility verified |
| **VP-3D · Exploration only after VP-02/03** | Concept for natural axis order, 3D coordinate contract, SVG projection or genuine 3D renderer | **Not authorized / not in scope** | Requires proven 2D usability and explicit go/no-go decision |

## Recommended decision sequence

1. Run the 2D experiment. Inspect the four SVGs. Note misrendered Unicode and layout defects.
2. Determine whether a **fixed-layout** printer solves the agents' actual failure cases. Do not jump to 3D for failures caused by font fallback or ambiguous semantics.
3. Decide `2D_GO`, `2D_REVISE`, or `2D_STOP` with specific criteria from `GATE_2D.md`.
4. Only after reliable 2D results, decide whether morphology-grounded fixed-order spatial projection adds demonstrable value. No arbitrary X/Y/Z numeric embedding is assumed.

## A note on "natural order"

P0 v9.4 explicitly orders the five X dimensions and their endpoint pairs. **That does not automatically establish one canonical total order for all Y and Z entities.** The 2D experiment uses only the adopted X pair sequence; relation, thread and topology examples use explicit fixture ordering. A future spatial axis-order contract must be separately justified and approved, rather than inventing Y/Z coordinates.

## Main invariants

- The glyph registry is indexed by its stable anchor ID, never Unicode alone.
- A graphical edge may only depict a **declared** relation (P1 typing still separately required); the paired endpoints use neutral display-only connectors.
- Color/form cannot prove identity, authorization, admission, truth, completion or occurrence.
- Time labels and ordering are supplied as explicit fixture declarations, not inferred from chronology.
- Every SVG node exposes `data-anchor-id` and optional `data-semantic-ref` for inspecting provenance of **presentation binding** only.
- Generated SVGs are code artifacts, not SVG sources stored as normative P1 grammar. Renderer is independent of deployed P0 and P1.
