# VP-12 — Landscape view (`P2-VP-LANDSCAPE/0.12.0`, `cube.landscape`)

MILE-016 B6 and B10. One page per plan: the Y and Z referents in declared layer columns, one band per declared step,
the dependencies holding at that step as edges with their predicate. Nothing new is asserted; the view arranges
declared statements. Everything shown stays `declared_unverified`. See `VP12_ACCEPTANCE_SPEC.md` (D-1…D-8 confirmed,
vectors L-01…L-14, oracle `oracles/independent_l01_l14.json` committed before the code).

- **Input** from the unchanged VP-07.8 source path (`binding-context/10`, origin lines on), optionally with a VP-07.2
  layer map. Errors of that path keep their VP-07 codes.
- **Columns:** the declared `layer_order` (empty layers included), plus `unassigned` with `VP12_LAYER_PARTIAL` for Y/Z
  referents without a layer. Without a layer map: anchor families in Morphology order (module bodies, boundaries,
  identity anchors, resources). At most 6 columns.
- **Bands:** default first and last declared step, at most 4, always in declared order.
- **Markers:** `introduced` / `retired at <next step>` from presence between shown bands; `declared_by` names the
  declared transitions (T-codes) that back the marker, empty when none does. Retired nodes are dashed.
- **Edges:** origin `declared` solid, `derived` dashed, `unknown` / `unbound` dotted; placement predicates
  (default `runs-on`, `hosted-by`) heavier. X endpoints are never nodes; their dependencies are listed in `x_outside`.
- **Status line (B10):** `Y × Z over T · derived · Morphology 01.3` (de: `Y × Z über T · abgeleitet · Morphologie 01.3`).
- **Budget:** 12 / 8 / 5 nodes per column and band (detail / standard / overview); overflow rejects with
  `VP12_BUDGET_EXCEEDED`, never truncates.

```sh
python3 -m vplandscape from-plan --context ctx.json --plan pm-1 [--layers layers.json] [--steps current,beta] \
        [--placement runs-on,hosted-by] [--locale de] --out landscape.json
python3 -m vplandscape print-panels --input landscape.json --out out/
python3 -m vplandscape check-panels --dir out/
python3 -m unittest tests.test_vp12
```

Codes: `VP12_INPUT`, `VP12_STEP_UNKNOWN`, `VP12_BUDGET_EXCEEDED`, `VP12_PANEL_COVERAGE`, `VP12_AUDIT`; warning
`VP12_LAYER_PARTIAL`. In-memory API `vplandscape.api` (`source`, `views`, `check`) has the `plan-views/1` shape; the
G6 registration (`cube_plan_views`) and the G5 delivery follow as their own step.
