# VP-03 — Acceptance criteria and test scope

| Gate | Acceptance condition | Local state |
| --- | --- | --- |
| L03-01 | Exact five namespaced lens IDs, Planner and view IDs rejected | Automated PASS |
| L03-02 | 3 unchanged source plans × 5 lens profiles; 15 golden SVGs / reports | Automated PASS |
| L03-03 | All P0/P1 symbols, palette and VP-02 view contracts unchanged | Automated PASS |
| L03-04 | Same source-plan digest across all five perspectives; no modified data | Automated PASS |
| L03-05 | Only explicit `declared_unverified` facet bindings highlighted; unknown/ambiguous rejected | Automated PASS |
| L03-06 | Every underlying node, directed edge, sample, value, annotation and relation pointer preserved | Automated PASS |
| L03-07 | Source view unchanged; output byte-identical on re-render; SVG XML safe; all SHA-256 match | Automated PASS |
| L03-08 | Semantics, warrant, authority and admission remain NOT_EVALUATED | Automated PASS |
| L03-09 | P1 schema validates bundles/reports; no external runtime dependency | Automated PASS in bundled environment; jsonschema is optional |
| L03-10 | Mac/Safari Unicode fallback, lens legibility and subjective distinction | **Human QA pending** |

**Critical warning:** A semantically chosen emphasis is not derived from AIAEAO by this printer: the emphasis is *authored* in `facet_bindings`. Without it, printing fails. This is intentional to prevent model-driven factual claims. The 3×5 view matrix is the evaluation artifact, not a shipped browser application.

**VP-04 hold:** No focus pruning, aggregation, budget management, automated lenses or 3D should be introduced until this focused evaluation is accepted.
