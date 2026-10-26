# VP-08 — Sequence Views per trigger · Acceptance specification

**Status:** DRAFT 2026-10-26 — decisions D-1…D-10 open, no code.
**Profile (proposed):** `P2-VP-SEQUENCE/0.8.0`, additive to the frozen `P2-VP/1.0.0-rc1` facade (VP-06) and independent of `P2-VP-MIGRATION/0.7.x` (VP-07, VP-07.1).
**Basis:** Morphology v9.4 visual anchors (`module-bodies.*`, `identity-anchors.*`, `relation-arrows.*`); VP-01 printer primitives; VP-05 audit rules (`NO_ACTIVE_SVG_CONTENT`); VP-06 budgets and publish rules; VP-07 panel export with (unit) coverage ledger, text index and declaration ledger; P1.8 `method_contracts` (optional reference only).
**Motivation:** `cube.flow` shows *who depends on whom* in a use case, but not *in which order* modules talk to each other when a user presses a button. Edges have no order, no call/return distinction and no alternative paths. VP-08 adds a sequence view: modules as lifelines, declared messages as numbered arrows, `alt`/`opt`/`loop` frames, one sequence per declared trigger (button, schedule, webhook …). Everything shown stays `declared_unverified`: order is the declared list order, never a measured time, and an arrow never asserts causation, success or authority.

## 0. Scope

| In scope | Out of scope |
|---|---|
| View `cube.sequence`: lifelines, numbered messages (call, return, async, self), activation bars | Durations, timestamps, latency, any time axis (D-8) |
| Declared triggers (entry points) with a closed kind set; one sequence per trigger | Interactive or clickable SVG (VP-05 forbids active content); HTML wrappers are a separate decision |
| Fragments `alt`, `opt`, `loop` with declared guard text, nesting depth bounded (D-5) | `par`, `break`, `critical`, `ref` fragments; flowchart view (separate follow-up) |
| Budgets per granularity; deterministic panel export per trigger with coverage and a text index | Automatic layout optimisation; inferring messages from `cube.flow` edges, code or logs |
| Source format `aiaeao.cube.vp08-sequence-source/1`, hand-written or produced by a later adapter (D-2) | Running, tracing or validating the sequence against real systems; P1 semantic validation |
| Optional reference from a message to a P1.8 `method_id` (display only) | Changes to VP-01…VP-07.1, G4/G5 or the MCP surface (D-10) |

## 1. Design summary

1. **Source.** A sequence source declares participants (display items with canonical anchors), triggers, and per trigger an ordered list of messages and fragments. Each message carries a `declaration_ref` (`decl:` / `fixture:`), like VP-07 cells.
2. **View.** `cube.sequence` draws participants as columns with a header card (anchor glyph + label) and a dashed lifeline. Messages are horizontal arrows top to bottom in declared order, numbered `1, 2, 3 …` (fragment-local numbering is not used). The trigger is drawn as message 0 entering the first participant from the left margin.
3. **Message kinds** (closed set): `call` (solid line, filled head), `return` (dashed line, open head), `async` (solid line, open head), `self` (loop back onto the same lifeline). Returns are drawn only when declared — never implied (D-4).
4. **Fragments.** `alt` (two or more operands with guards), `opt` (one operand with guard), `loop` (one operand with a declared bound text). A frame spans the participants its messages touch; guards are declared text, never evaluated.
5. **Panels.** `print-panels --view cube.sequence --partition trigger` writes one panel per trigger (and splits over-long sequences by message windows, D-7), an index that lists every trigger like a button list, and a report whose coverage unit is `(trigger_id, message_id)`. `check-panels` re-verifies a directory as in VP-07 PE-6.
6. **Ledger.** Each panel embeds a declaration ledger (message number → `declaration_ref`, optional `method_id`) and lists omitted or continued messages explicitly.

### 1.1 Shape (illustrative, synthetic)

```json
{
  "format": "aiaeao.cube.vp08-sequence-source/1",
  "profile": "P2-VP-SEQUENCE/0.8.0",
  "reference_version": "v9.4",
  "source_id": "fixture-shop",
  "title": "Acme shop · order flows",
  "participants": [
    {"id": "user", "anchor_id": "identity-anchors.actor", "form_id": "form.identity-chip", "label": "customer"},
    {"id": "web", "anchor_id": "module-bodies.adapter", "form_id": "form.module-block", "label": "web shop UI"},
    {"id": "orders", "anchor_id": "module-bodies.core", "form_id": "form.module-block", "label": "order service"},
    {"id": "pay", "anchor_id": "module-bodies.third-party-dependency", "form_id": "form.module-block", "label": "payment provider"},
    {"id": "mail", "anchor_id": "module-bodies.provider", "form_id": "form.module-block", "label": "mail service"}
  ],
  "triggers": [
    {"id": "btn-checkout", "kind": "ui_button", "label": "Checkout", "enters": "web", "use_case": "uc-order",
     "declaration_ref": "fixture:vp08/btn-checkout",
     "sequence": [
       {"id": "m1", "kind": "call", "from": "web", "to": "orders", "label": "create order", "declaration_ref": "fixture:vp08/m1"},
       {"fragment": "alt", "id": "f1", "operands": [
         {"guard": "payment accepted", "sequence": [
           {"id": "m2", "kind": "call", "from": "orders", "to": "pay", "label": "charge", "method_id": "pay.charge/v1", "declaration_ref": "fixture:vp08/m2"},
           {"id": "m3", "kind": "return", "from": "pay", "to": "orders", "label": "receipt", "declaration_ref": "fixture:vp08/m3"},
           {"id": "m4", "kind": "async", "from": "orders", "to": "mail", "label": "send confirmation", "declaration_ref": "fixture:vp08/m4"}]},
         {"guard": "payment declined", "sequence": [
           {"id": "m5", "kind": "return", "from": "orders", "to": "web", "label": "decline notice", "declaration_ref": "fixture:vp08/m5"}]}]},
       {"id": "m6", "kind": "return", "from": "orders", "to": "web", "label": "order status", "declaration_ref": "fixture:vp08/m6"}
     ]},
    {"id": "sched-reminder", "kind": "schedule", "label": "daily reminder", "enters": "orders", "use_case": "uc-remind",
     "declaration_ref": "fixture:vp08/sched-reminder", "sequence": ["…"]}
  ],
  "declaration_status": "declared_unverified"
}
```

Index (synthetic): a drawn table — `Checkout (ui_button) · uc-order · 6 messages · panel-01`, `daily reminder (schedule) · uc-remind · … · panel-02`.

## 2. Status and diagnostic rules (proposed codes)

| Situation | Result | Diagnostic |
|---|---|---|
| Source not `aiaeao.cube.vp08-sequence-source/1`, wrong profile, unknown keys, limits exceeded | FAIL | `VP08_SOURCE_INVALID` |
| Participant with unknown canonical anchor or non-recommended form; duplicate IDs | FAIL | `VP08_SOURCE_INVALID` |
| Message references an unknown participant; `self` message with `from ≠ to`; non-self message with `from = to` | FAIL | `VP08_SEQUENCE_REFERENCE` |
| Trigger kind outside the closed set, or `enters` not a participant | FAIL | `VP08_TRIGGER_INVALID` |
| Fragment malformed: `alt` with < 2 operands, `opt`/`loop` with ≠ 1 operand, empty operand, missing guard/bound text, nesting deeper than D-5 | FAIL | `VP08_FRAGMENT_INVALID` |
| Participants, messages or fragment depth over the granularity budget and overflow `reject` (or `detail`) | FAIL | `VP08_SEQUENCE_BUDGET` |
| Over budget with overflow `summarize` | Rendered as message windows with continuation markers; ledger lists them | `VP08_SEQUENCE_CONTINUED` (warning) |
| A declared `return` without an earlier open `call` on the same pair in the same operand | Rendered as declared | `VP08_RETURN_UNMATCHED` (warning, not a verdict) |
| A declared `call` without a declared `return` (when the source marks returns as expected, D-4) | Rendered as declared | `VP08_RETURN_UNDECLARED` (warning, not a verdict) |
| `method_id` given and a `method_contracts` list supplied, but the ID is not in it | Rendered | `VP08_METHOD_UNKNOWN` (warning; never P1 validation) |
| Panel directory: files, digests, units or ledger differ from a deterministic re-render | FAIL | `VP08_PANEL_COVERAGE` |
| SVG contains active content, or the embedded ledger differs from the report | FAIL | `VP08_AUDIT` |

## 3. Rules in detail

### 3.1 Participants and lifelines (SP)

- SP-1: Participants are display items like VP-07 rows (`id`, `anchor_id`, `form_id`, `label`, optional `semantic_ref`); column order is the declared participant order, never re-sorted.
- SP-2: Only participants touched by the trigger's messages (plus `enters`) are drawn in a panel; omitted participants are listed.
- SP-3: Lifelines are dashed vertical lines; an activation bar is drawn from a `call` to its matching `return` (D-4); without a matching return the bar ends at the operand end.

### 3.2 Messages (SM)

- SM-1: Numbering `1…n` in declared order across all operands (depth-first); the trigger arrow is `0`.
- SM-2: Labels ≥ 11 px, wrapped to two lines, never truncated; the full text, `declaration_ref` and `method_id` are in `<title>` and in the declaration ledger.
- SM-3: Line styles carry only the kind (legend); no colour carries status, success, risk or causality.
- SM-4: Vertical pitch is fixed per granularity; panels never compress pitch to fit.

### 3.3 Fragments (SF)

- SF-1: Frames are rectangles with a corner tag (`alt`, `opt`, `loop`), guard text in brackets per operand, dashed operand separators.
- SF-2: Guards and loop bounds are declared text (≤ 60 chars); they are never parsed or evaluated.
- SF-3: Nesting depth limit per D-5; frames span exactly the participants their messages touch (plus one column margin).

### 3.4 Triggers and panels (ST)

- ST-1: Trigger kinds (closed set, D-3): `ui_button`, `schedule`, `webhook`, `cli`, `event`, `manual`.
- ST-2: `print-panels --partition trigger` (default) or `--partition use_case` (all triggers of one use case on consecutive panels).
- ST-3: Coverage unit `(trigger_id, message_id)`; every unit is shown in at least one panel; continued windows repeat the participant header and show a continuation marker (`… continued from 12`).
- ST-4: The index is text-only: per trigger its label, kind, use case, message count and panel names (VP-07 PE-5 style, no thumbnails).

## 4. Acceptance criteria

| AC | Requirement | Evidence |
|---|---|---|
| VP08-01 | VP-01…VP-07.1 unchanged (SHA-256 ledgers and pinned digests) | regression run |
| VP08-02 | Source validation and limits (§2 rows 1–5) | S-01…S-06 |
| VP08-03 | Message kinds, numbering, labels (SM-1…SM-4) | S-07…S-11 |
| VP08-04 | Fragments (SF-1…SF-3) | S-12…S-15 |
| VP08-05 | Budgets, continuation, panels and coverage (ST-1…ST-4) | S-16…S-20 |
| VP08-06 | Every row in §2 yields exactly the stated result and code | one test per row |
| VP08-07 | Synthetic golden: 5 participants, 4 triggers (3 buttons, 1 schedule), one `alt` with nested `loop`, one sequence long enough to continue at standard | `fixtures/golden_sequence.json` |
| VP08-08 | No client data in fixtures, examples or previews | review |

## 5. Alignment vectors (exit check, draft)

| ID | Case | Expected |
|---|---|---|
| S-01 | Minimal valid source, one button, two participants, one call + return | PASS |
| S-02 | Unknown anchor for a participant | FAIL · `VP08_SOURCE_INVALID` |
| S-03 | Message to an undeclared participant | FAIL · `VP08_SEQUENCE_REFERENCE` |
| S-04 | `self` message with `from ≠ to` | FAIL · `VP08_SEQUENCE_REFERENCE` |
| S-05 | Trigger kind `cron` (not in set) | FAIL · `VP08_TRIGGER_INVALID` |
| S-06 | Source over the hard limits | FAIL · `VP08_SOURCE_INVALID` |
| S-07 | Call, return, async and self in one sequence | PASS, four distinct line/head styles, legend lists each kind once |
| S-08 | Numbering across two `alt` operands | PASS, numbers 1…n depth-first, no reuse |
| S-09 | Label of 90 characters | PASS, wrapped to two lines, full text in `<title>` |
| S-10 | `return` without an open call | PASS + `VP08_RETURN_UNMATCHED` |
| S-11 | `method_id` not in supplied contracts | PASS + `VP08_METHOD_UNKNOWN` |
| S-12 | `alt` with one operand | FAIL · `VP08_FRAGMENT_INVALID` |
| S-13 | `loop` with bound text, two messages | PASS, frame spans exactly the touched participants |
| S-14 | Nesting one level deeper than D-5 | FAIL · `VP08_FRAGMENT_INVALID` |
| S-15 | `opt` without guard | FAIL · `VP08_FRAGMENT_INVALID` |
| S-16 | Messages over standard budget, overflow `reject` | FAIL · `VP08_SEQUENCE_BUDGET` |
| S-17 | Same, overflow `summarize` | PASS + `VP08_SEQUENCE_CONTINUED`, windows cover every message |
| S-18 | Four triggers, `--partition trigger` | PASS, 4+ panels, coverage COMPLETE, index lists 4 triggers |
| S-19 | `check-panels` after deleting one message from a panel input | FAIL · `VP08_PANEL_COVERAGE` |
| S-20 | SVG audit: no `<script>`, `<a>`, `<use>`, `<pattern>`, event attributes | PASS · `NO_ACTIVE_SVG_CONTENT` |

## 6. Decisions (open)

| Decision | Options | Proposal | Consequence |
|---|---|---|---|
| D-1 Package and profile | (a) new package `P2/visual-printer-sequence-v1`, profile `P2-VP-SEQUENCE/0.8.0`, own CLI `python3 -m vpsequence` · (b) extend `vpmigration` | **(a)** | VP-07.x stays untouched; shared helpers are imported, not copied (as VP-07 imports VP-01…VP-06). |
| D-2 Where sequences come from | (a) declared VP-08 source only (hand-written or exported by a later tool) · (b) first a P1 interaction profile (`binding-context/7`, "P1.11") with an adapter · (c) derive from `cube.flow` edges or code | **(a)** now, (b) as a possible follow-up | No P1 change; (c) is excluded because it would infer order. |
| D-3 Trigger model | (a) one sequence per trigger, closed kind set (ST-1), optional `use_case` grouping · (b) one sequence per use case with several entry points | **(a)** | "Sequence per button" is the unit of the index and of coverage. |
| D-4 Returns | (a) drawn only when declared; optional per-trigger flag `returns: expected` enables `VP08_RETURN_UNDECLARED` · (b) implied returns drawn automatically | **(a)** | Nothing is inferred; missing returns are visible as a warning only where the author asked for it. |
| D-5 Fragments | (a) `alt`, `opt`, `loop`, nesting depth ≤ 2 · (b) also `par`, `break`, `critical`, `ref` · (c) none in 0.8.0 | **(a)** | Covers decision paths and repetition; `ref` (sub-sequence) is the most likely 0.8.x addition. |
| D-6 Budgets (participants / messages / fragment depth) | (a) overview 4/8/1, standard 7/16/2, detail 10/30/2 · (b) single budget | **(a)** | Same three-level scheme as VP-04/VP-07; detail never omits. |
| D-7 Long sequences | (a) `summarize` splits into message windows with continuation markers and repeated headers · (b) reject only | **(a)** | Real button flows stay printable; coverage stays provable per message. |
| D-8 Time | (a) none: order is declared, never a time axis; no durations · (b) optional declared durations as text | **(a)** | Consistent with VP-07 ("step order is declared, not a time axis"); measured timing belongs to an evaluator, not the printer. |
| D-9 Lens | (a) `neutral` plus `cube.lens.provenance` (witness per message) · (b) neutral only · (c) all VP-03 lenses | **(b)** for 0.8.0 | Declaration ledger already shows `declaration_ref`; lens facets can follow. |
| D-10 Transport | (a) local CLI only, MCP tool later · (b) G5 tool in the same step | **(a)** | No G4/G5 change, no deploy; follows VP-07 D-6. |

## 7. Not part of VP-08

- Flowchart view (decision/branch diagram per use case) — possible VP-09.
- Clickable index (HTML wrapper around static panels).
- Link between a sequence and a migration step (`valid_in_step`) — candidate for 0.8.x once VP-07.1 is in use.
- Time, duration or performance views; trace import.
