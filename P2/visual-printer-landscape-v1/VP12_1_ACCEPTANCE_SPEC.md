# VP-12.1 — VG anchor of the layer column (`P2-VP-LANDSCAPE/0.12.1`) · Acceptance specification

**Status:** SPECIFIED for MILE-018 E18-1 (B13), 2026-11-05. Decision D-1 by the user; vectors LA-01…LA-06, oracle `oracles/independent_la01_la06.json` and the 0.12.0 regression digests (`fixtures/regression_0120_digests.json`) committed before code.
**Profile:** `P2-VP-LANDSCAPE/0.12.1`, opt-in; `0.12.0` stays the default and byte-identical.

## 1. Decision

| ID | Question | Decision (user, 2026-11-05) |
|---|---|---|
| D-1 | Which VG anchor carries the layer column? | **`skeleton-shell.section`** (◲, UI marker, `form.shell-surface`). The column is a caller-declared presentation grouping (VP-07.2 layer map, "presentation input only") or an anchor family; a UI anchor makes no Cube statement. `resource-zones.*` (Z:zone) is not used, because it would claim each layer is a resource zone. |

## 2. Design

1. `from-plan --profile P2-VP-LANDSCAPE/0.12.1` (CLI) / `profile=` (API, G6 source option `profile`) writes the landscape input with that profile; everything else as 0.12.0.
2. Under 0.12.1 every column header is a group `data-vp12-column-header="<column>"` with `data-anchor-id="skeleton-shell.section"`, a `<title>` naming the anchor, and the anchor glyph `◲` before the label. This holds for every declared column, empty layers and `unassigned` included.
3. The ledger and report carry `column_anchor: "skeleton-shell.section"`; an audit invariant `COLUMN_ANCHOR_EACH_COLUMN` checks one anchored header per column.
4. Nodes, edges, bands, markers and budgets are unchanged.

## 3. Vectors (synthetic, the VP-12 context of L-01…L-14)

| ID | Case | Expected |
|---|---|---|
| LA-01 | L-01 under 0.12.1 | 4 column headers (actor, module, data, platform), each with `data-anchor-id="skeleton-shell.section"` and glyph ◲; ledger `column_anchor` = `skeleton-shell.section`; invariant `COLUMN_ANCHOR_EACH_COLUMN` |
| LA-02 | L-03 under 0.12.1 (partial layer map) | 5 anchored headers including `unassigned` |
| LA-03 | L-02 under 0.12.1 (default families) | 3 anchored headers (`module-bodies`, `identity-anchors`, `resource-objects`) |
| LA-04 | L-01 under 0.12.1, units | units, bands, x_outside identical to 0.12.0 |
| LA-05 | every 0.12.0 case (default profile) | SVG and panel files byte-identical to `fixtures/regression_0120_digests.json`; no `data-vp12-column-header` |
| LA-06 | unknown profile `P2-VP-LANDSCAPE/0.12.9` | `VP12_INPUT` |

## 4. Acceptance

| ID | Criterion |
|---|---|
| VP121-01 | LA-01…LA-06 against the oracle committed before code |
| VP121-02 | 0.12.0 byte-identical (LA-05); VP-07…VP-11 untouched |
| VP121-03 | lunados.explorer prints the landscapes under 0.12.1; `check-panels` PASS |
| VP121-04 | G6 `cube_plan_source` accepts `profile` for `vplandscape`; G5 as its own step (E18-7) |
