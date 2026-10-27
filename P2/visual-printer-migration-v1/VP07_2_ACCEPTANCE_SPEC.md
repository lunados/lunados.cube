# VP-07.2 — Declared layers as row order · Acceptance specification

**Status:** SPECIFIED, decisions D-1…D-8 resolved 2026-10-27 (all as proposed) — ready for oracle transcription and implementation.
**Profile:** `P2-VP-MIGRATION/0.7.2`, follow-up to `0.7.1` (VP-07.1, PR #15) in the same package (profile dispatch as VP-07.1 PD-1…PD-4).
**Requirement:** C-9 from the running migration field test (2026-10-27; about 37 referents, 56 dependencies, steps p0–p3, several workstreams; client details withheld).
**Basis:** `VP07_ACCEPTANCE_SPEC.md` PV-6 ("row order = declared order; no sorting by inferred importance"), AD-5 (declared track map), PE-2 (packing); `VP07_1_ACCEPTANCE_SPEC.md` NP-1…NP-5 (nested partition), PD-1…PD-4; VP-02 `VIEW_GRAMMAR.md` ("`cube.flow` requires an explicit, order-preserving full `order` … display order only, never derived chronology"); Morphology v9.4 §3.8 (presentation order is a derived projection and may vary without redefining canon; it never reassigns homes).
**Motivation:** In 0.7.1 rows follow the order of the dependency inventory in the context. In the field test this order looks random and hides the functional chain (platform → DNS → provider → account → system → actor). The author knows the chain but cannot declare it to the printer.

| Finding | Effect in 0.7.1 |
|---|---|
| Row order = first appearance in the dependency list | Related subjects are scattered over panels; the chain is not readable top to bottom |
| `cube.flow` panels order nodes rows-first, then objects | Platform and DNS objects land on the right, actors on the left: the left-to-right reading runs against the chain |
| The only declared grouping is `track` (workstream) | Layers cut across workstreams; using tracks as layers would lose the workstream partition |

VP-07.2 adds a **declared layer map** as optional input. Layers are declared, never derived from `concept_id`, anchors, labels or the dependency graph.

## 0. Scope

| In scope | Out of scope |
|---|---|
| Declared layer map `aiaeao.cube.vp07-layer-map/1`: ordered layer names plus an assignment of referents to layers | Deriving layers from `concept_id`, P0 axis order, names or graph structure |
| `from-plan --layers <file>` writes `layer_order` and per-item `layer` into a 0.7.2 source | Changes to VP-01…VP-06 (`cube.flow` stays one declared `order` list) |
| `cube.phases`: rows sorted by layer, then by the declared order within the layer; layer bands at the left edge | Automatic crossing minimisation as a default (D-5) |
| `cube.flow` panels: node `order` follows the layer order (left to right) | New colours; any status or risk meaning of a layer |
| Partition key `layer` (single or nested with `track`, `subject`, `object`, `step`) | P1 changes; the layer map is a display input, not a context field (D-2) |
| 0.7.0 / 0.7.1 documents byte-identical | MCP tool |

## 1. Design summary

1. **Layer map.** A separate file, like the track map (AD-5): `layer_order` lists layer names top to bottom; `layers` assigns referent refs to exactly one layer, in a declared order within the layer (D-3).
2. **Transcription.** `from-plan --layers` copies the declaration into the source: `layer_order` at source level, `layer` on each row and object. The source stays self-contained; `print-panels` needs no extra input.
3. **`cube.phases`.** Rows are sorted by `(layer index, order within layer)`. A thin band with the layer name is drawn left of the row cards; layer boundaries get a rule. Within a row, lane order follows the declared cell order unchanged (D-6).
4. **`cube.flow`.** The panel bundle's `order` lists nodes by `(layer index, order within layer)`, subjects and objects interleaved; the VP-02 printer stays unchanged. An optional caption line under the cards names the layers shown (post-processing, as VP-07 Path F).
5. **Partition.** `--partition layer` and nested `layer,subject`, `track,layer` etc. (NP-1 rules); coverage and outer ledger unchanged.
6. **Unassigned referents.** Handled by D-4.

### 1.1 Shape (illustrative, synthetic)

```json
{
  "format": "aiaeao.cube.vp07-layer-map/1",
  "layer_order": ["platform", "dns", "provider", "account", "system", "actor"],
  "layers": {
    "platform": ["acme:hosting"],
    "dns": ["acme:dns-zone"],
    "provider": ["acme:legacy-mail", "acme:new-mail"],
    "account": ["acme:admin-mailbox", "acme:billing-mailbox"],
    "system": ["acme:shop", "acme:crm-sync"],
    "actor": ["acme:support-team"]
  }
}
```

```text
vpmigration from-plan --context ctx.json --plan mp-acme --tracks tracks.json --layers layers.json --out src.json
vpmigration print-panels --source src.json --view cube.phases --partition track,layer --granularity standard --out panels/
```

## 2. Status and diagnostic rules

| Situation | Result | Diagnostic |
|---|---|---|
| Layer map with wrong format, empty or duplicate layer names, a layer not in `layer_order`, a ref in two layers | FAIL | `VP07_ADAPTER_INPUT` (existing) |
| Layer map names a ref that is not a referent of the context | FAIL | `VP07_ADAPTER_INPUT` (existing) |
| A referent shown in the slice has no layer | per D-4 | `VP07_LAYER_UNASSIGNED` (new warning) or `VP07_ADAPTER_INPUT` |
| `--partition layer` on a source without `layer_order` | FAIL | `VP07_PANEL_PARTITION` (existing) |
| Source 0.7.2 with `layer` on an item whose value is not in `layer_order` | FAIL | `VP07_SOURCE_INVALID` (existing) |
| Layer fields in a 0.7.0 / 0.7.1 source | FAIL | `VP07_SOURCE_INVALID` (existing) |

## 3. Rules in detail

### 3.1 Layer map (LM)

- LM-1: `layer_order`: 1…12 distinct clean names (≤ 24 chars); order is top to bottom in `cube.phases` and left to right in `cube.flow`.
- LM-2: `layers`: every key is in `layer_order`; values are arrays of context refs; a ref appears at most once in the whole map.
- LM-3: The map is a declared presentation input. It is recorded in `mapping.json` by SHA-256 (as the track map) and never written back into the P1 context.

### 3.2 Ordering (LO)

- LO-1: Sort key for rows and flow nodes: `(index of layer in layer_order, index within the layer's list)`; ties cannot occur because a ref appears once.
- LO-2: Without a layer map, 0.7.2 behaves exactly like 0.7.1 (declared inventory order).
- LO-3: Steps, transitions, codes, gap marks and coverage are unaffected by layers.
- LO-4: Any order not given by LO-1 (D-5) must be named in the panel ledger as `presentation_order: derived:<method>` and never changes IDs, coverage or reports other than the order fields.

### 3.3 Drawing (LD)

- LD-1: `cube.phases`: a 14 px band left of the row cards spans the rows of one layer, with the layer name rotated or abbreviated; layer boundaries get a 1 px rule across the grid. No fill colour per layer.
- LD-2: `cube.flow`: one caption line `layers: platform · dns · provider` under the node row (only the layers present in the panel).
- LD-3: The panel index lists the layers of each panel.

### 3.4 Source fields and profile selection (LS)

Clarification transcribed together with the oracle (no decision changed).

- LS-1: `from-plan` without `--layers` emits a 0.7.1 source exactly as before (LO-2, L-08); with `--layers` it emits a 0.7.2 source. `--profile` still forces a profile; `--layers` with `--profile` 0.7.0 or 0.7.1 FAILs with `VP07_ADAPTER_INPUT`.
- LS-2: A 0.7.2 source carries `layer_order` (layer names; the reserved name `unassigned` may only appear last, D-4), `layer_sequence` (display IDs of all layered rows and objects in declared map order, each once) and `layer` on every row and object. The layer index along `layer_sequence` never decreases.
- LS-3: The layer map may not use the name `unassigned`. Referents shown without a map entry get `layer: unassigned`; `mapping.json` and the panel report list one `VP07_LAYER_UNASSIGNED` warning per such item.
- LS-4: Rows and cells of a 0.7.2 source are ordered by LO-1 before packing (stable within a row); `cube.flow` bundle `order` follows `layer_sequence`.

## 4. Acceptance criteria

| AC | Requirement | Evidence |
|---|---|---|
| VP072-01 | 0.7.0 and 0.7.1 outputs byte-identical (pinned digests extended by the 0.7.1 golden before code) | regression run |
| VP072-02 | Layer map validation LM-1…LM-3 | L-01…L-05 |
| VP072-03 | Ordering LO-1…LO-4 in `cube.phases` and `cube.flow` | L-06…L-10 |
| VP072-04 | Partition `layer`, nested, coverage | L-11…L-13 |
| VP072-05 | Every row in §2 yields exactly the stated result and code | one test per row |
| VP072-06 | Synthetic golden: 6 layers, 3 tracks, `--partition track,layer` covers everything; flow panel reads platform → actor left to right | fixture |
| VP072-07 | No client data in fixtures, examples or previews | review |

## 5. Alignment vectors (exit check)

| ID | Case | Expected |
|---|---|---|
| L-01 | Valid map, 6 layers | PASS |
| L-02 | Ref in two layers | FAIL · `VP07_ADAPTER_INPUT` |
| L-03 | Layer key not in `layer_order` | FAIL · `VP07_ADAPTER_INPUT` |
| L-04 | Map names an undeclared ref | FAIL · `VP07_ADAPTER_INPUT` |
| L-05 | Shown referent without layer | per D-4 |
| L-06 | Inventory order differs from layer order | PASS, rows in layer order |
| L-07 | Two rows in one layer, map lists them reversed to the inventory | PASS, map order wins |
| L-08 | No layer map | PASS, byte-identical to 0.7.1 output of the same source |
| L-09 | Flow panel with nodes from 3 layers | PASS, `order` follows layers; caption lists them |
| L-10 | Layer bands and rules present; no `fill` other than the 0.7.1 palette | PASS |
| L-11 | `--partition layer` | PASS, no panel mixes layers |
| L-12 | `--partition track,layer` | PASS, outer ledger COMPLETE |
| L-13 | `--partition layer` on a source without layers | FAIL · `VP07_PANEL_PARTITION` |

## 6. Decisions (resolved 2026-10-27, all as proposed)

| Decision | Options | Resolution | Consequence |
|---|---|---|---|
| D-1 Placement | (a) VP-07.2 in `vpmigration` (profile `0.7.2`, dispatch) · (b) separate package | **(a)** | One CLI; same pattern as VP-07.1. |
| D-2 Where layers are declared | (a) separate layer map file (like the track map) · (b) new P1 context field · (c) both | **(a)** | No P1 change; a context can be shown with different layer maps for different audiences. |
| D-3 Order within a layer | (a) the order of the refs in the layer's list · (b) the inventory order of the context | **(a)** | The author controls the chain completely; (b) keeps the "random" order the field test complains about. |
| D-4 Unassigned referents | (a) collected in a trailing layer `unassigned` + warning `VP07_LAYER_UNASSIGNED` · (b) FAIL · (c) leading layer | **(a)** | Nothing disappears; the gap in the map is visible. `--strict-layers` could turn it into FAIL. |
| D-5 Barycentre / crossing reduction within a layer | (a) not in 0.7.2: the declared list order is final · (b) opt-in `--within-layer barycenter` for `cube.flow` only, deterministic, ledger states `presentation_order: derived:barycenter` · (c) default | **(a)**; (b) remains a possible follow-up | `cube.phases` has no edges between rows, so crossings do not arise there; in `cube.flow` panels (≤ 4 nodes) the gain is small. Morphology §3.8 would allow (b) as a presentation order, but PV-6 and the VP-02 rule favour declared order. |
| D-6 Objects in `cube.phases` | (a) layers order rows only; lanes keep declared cell order · (b) also order lanes by object layer | **(a)** | Lanes stay stable between 0.7.1 and 0.7.2; (b) changes bar positions for every layer change. |
| D-7 Layer bands | (a) left band + rules · (b) rules only · (c) none, order only | **(a)** | The chain is readable without a legend entry. |
| D-8 Golden | (a) synthetic, 6 layers × 3 tracks · (b) field-test inventory | **(a)** | Client data stays out. |

## 7. Not part of VP-07.2

- Deriving layers from P0 axis order (Z: Core → … → Third-party Dependency) — would be a declared P0 order, but it classifies concept kinds, not the author's functional chain; possible as a helper that *writes* a layer map for review, never applied silently.
- Layer-aware routing in `cube.flow` (VP-02 frozen).
- Layers in VP-08 sequence views (participants already have a declared order).
