# VP-11 — Instance view · Acceptance specification

**Status:** SPECIFIED. MILE-009 decisions D-1…D-8 apply (2026-11-02); detail questions Q-1…Q-10 resolved 2026-11-02 (all as proposed). IMPLEMENTED locally 2026-11-02 (TASK-055, TASK-056): I-01…I-34 34/34, G6 = CLI, visual check 5/5.
**Profile:** `P2-VP-INSTANCES/0.12.0`, package `vpinstances` in `P2/visual-printer-instances-v1/`, view `cube.instances` (D-2). VP-07, VP-08, VP-09 and VP-10 (0.10.0, 0.10.1, 0.11.0) stay byte-identical.
**Requirement:** VR-12 (MILE-003 handover) with V-10, V-11, V-12 (MILE-002 gap ledger, MILE-003 inventory); MILE-009 US-028, US-029, TASK-053…057.
**Basis:**
- Mockup [M-12B](../../docs/09-Research/visual-check/mockups/M-12B.svg): instance frames, join statement with its inputs, foreign input "not part of", model field "Prozessmodell · keine Spur"; blind correct in the agent pre-check (MILE-003). M-12A suggested an execution of ship and is not followed.
- P1.13 (`binding-context/9`, control flow, `at_gateway`, `control_flow_role`) and lunados.lib `analyze.trace-conformance/v1` (MILE-008, [C-RESULT](../../docs/10-Evidence/MILE-008/C-RESULT.md)).
- VP-10 0.11.0: statement set `aiaeao.cube.statement-set/1` and the LIB record pattern (PR-6, Q-10).

All examples are synthetic.

## 0. Scope

| In scope | Out of scope |
|---|---|
| A declared trace for a `binding-context/9`, drawn per instance | Checking the trace; any verdict not taken from a LIB record (D-5) |
| Exclusive split (taken / not taken path), exclusive merge, parallel split and join (inputs with status) | Inclusive, event-based, complex gateways (P1.13: UNRESOLVED) |
| Reading `aiaeao.trace-conformance-result/v1` records computed by lunados.lib | Recomputing or re-checking them; condition values |
| CLI and G6, local (D-7) | G5; time axis, engine logs, animation, BPMN notation |

## 1. Design summary

1. **Inputs.** A `binding-context/9` with `control_flow` (structure), a **trace** as statement set (Q-1) and zero or more **conformance records** (Q-2).
2. **Drawing.** One named, solid frame per instance; inside it one block per gateway the instance touches, in declared order; each block lists its flows as rows with the tokens of the instance. A separate field "Prozessmodell · keine Spur" lists the declared model (Q-4).
3. **Verdicts.** Each block carries one verdict line per record for that gateway and instance: checked, rule violation (with hatched mark) or not checkable with reason; without a record "not checked" (D-5). The printer never derives a verdict from the drawing.
4. **No colour.** States differ by text, line style and hatching (D-6). Ledger and report as in VP-10.

### 1.1 Shape (illustrative, synthetic; CF-25)

```json
{"format": "aiaeao.cube.statement-set/1", "set_id": "trace-bpmn-02", "context_id": "<context_id of the binding-context/9>",
 "referents": ["bpmn:i1/tok-stock", "bpmn:i2/tok-credit", "bpmn:i1/tok-ship", "bpmn:f-stock-done", "bpmn:f-credit-done", "bpmn:f-ship"],
 "statements": [
   {"statement_id": "t-1", "subject": "bpmn:i1/tok-stock", "predicate_id": "onFlow", "object": "bpmn:f-stock-done"},
   {"statement_id": "t-2", "subject": "bpmn:i2/tok-credit", "predicate_id": "onFlow", "object": "bpmn:f-credit-done"},
   {"statement_id": "t-3", "subject": "bpmn:i1/tok-ship", "predicate_id": "onFlow", "object": "bpmn:f-ship"}],
 "witness_ref": "synthetic:bpmn-02#trace"}
```

```json
{"format": "aiaeao.cube.conformance-record/1",
 "library_ref": {"library_id": "lunados.lib", "entry_id": "analyze.trace-conformance", "revision": 1, "sha256": "<INDEX value>"},
 "call": {"schema": "lunados.lib/call/v1", "method_id": "analyze.trace-conformance/v1", "parameters": {},
          "inputs": {"control_flow": {"…": "as in the context"}, "trace": ["…"], "coverage": ["…"],
                     "claim": {"check": "join", "gateway": "bpmn:join", "instance": "bpmn:i1"}}},
 "result": {"schema": "aiaeao.trace-conformance-result/v1", "check": "join", "gateway": "bpmn:join", "instance": "bpmn:i1",
            "status": "FAIL", "value": "join_incomplete", "missing": ["bpmn:f-credit-done"], "foreign": ["bpmn:i2/tok-credit"], "…": "…"}}
```

→ Frame "Instanz bpmn:i1", block "bpmn:join · parallel join": `bpmn:f-stock-done · arrived · bpmn:i1/tok-stock`; `bpmn:f-credit-done · missing · token of instance bpmn:i2 present · not part (bpmn:i2/tok-credit)` (dashed); `bpmn:f-ship → bpmn:ship · token bpmn:i1/tok-ship`; verdict `rule violation · join without all inputs · missing bpmn:f-credit-done` with hatched mark. Frame "Instanz bpmn:i2" shows its own token on `bpmn:f-credit-done` and "not checked".

## 2. Inputs

**Context (IN).**
- IN-1: `format` is `aiaeao.cube.binding-context/9` with a `control_flow` object; otherwise `VP11_ADAPTER_INPUT`. The printer reads the context structurally; its P1 validity comes from `cube_validate` (P1.13), not from the printer (D-3).
- IN-2: Gateway roles follow from the structure: exclusive with more than one outgoing flow = exclusive split; exclusive with one outgoing flow = exclusive merge; parallel with one incoming flow = parallel split; parallel with one outgoing flow = parallel join. A gateway that fits none, or a `type` outside {`exclusive`, `parallel`}, is drawn in the model field only, with `VP11_GATEWAY_NOT_DRAWN` (warning).

**Trace (TR, Q-1).** A statement set `aiaeao.cube.statement-set/1` whose `context_id` is the context's.
- TR-1: Resolution as VP-10 SS-1, SS-2, SS-4 (referents, predicates, concepts, unique IDs, endpoints listed).
- TR-2: A statement is a trace statement if its predicate has `control_flow_role` `routing` (subject = token, object = a target) or `on_flow` (subject = token, object = a flow). Other statements are not drawn; they are listed in the ledger and reported once as `VP11_STATEMENT_NOT_DRAWN` (warning).
- TR-3: A token's instance is its `instance_ref`, its position its `at_gateway` (P1.13 Q-3). A token without `instance_ref` is drawn in a frame "instance undeclared" with `VP11_INSTANCE_UNDECLARED` (warning).

**Records (RC, Q-2, Q-3).** Zero or more `aiaeao.cube.conformance-record/1` objects `{format, library_ref, call, result}`.
- RC-1: `library_ref` has `library_id` `lunados.lib`, `entry_id` `analyze.trace-conformance`, `revision` 1 and a 64-hex `sha256`; `call.method_id` = `result.method_id` = `analyze.trace-conformance/v1`; `result` matches the result schema of the entry (field shape and value/status pairs); `call.inputs.claim` equals `result.check`, `result.gateway`, `result.instance`. Otherwise `VP11_RECORD_INVALID`.
- RC-2: The record must belong to this context and trace: `call.inputs.control_flow` equals the context's `control_flow`; `call.inputs.trace` without `conditions` equals the trace derived from the set (§2.1); `call.inputs.coverage` equals the coverage derived from the context (§2.1). Compared as canonical JSON, rows as sets. Otherwise `VP11_RECORD_MISMATCH`.
- RC-3: At most one record per claim (`check`, `gateway`, `instance`); otherwise `VP11_RECORD_DUPLICATE`. The check must fit the gateway's role (`exclusive` and `condition_order` at an exclusive split, `merge` at an exclusive merge, `split` at a parallel split, `join` at a parallel join); otherwise `VP11_RECORD_INVALID`.
- RC-4: Nothing is recomputed. The printer reads `status`, `value`, `details`, `missing`, `foreign`, `excess`, `paths`, `taken`, `first_true` and `missing_scope` as given.

### 2.1 Derived LIB inputs (for RC-2 only)

- Trace rows: per token in the set, `{token, instance}` from the referent, `at` from `at_gateway` if present, `routed_to` per routing statement, `on_flow` per on-flow statement; one row per statement, identical rows merged (LIB: set-like).
- Coverage: the context's `coverage_declarations` of scope `referent_relation_direction` whose predicate has a `control_flow_role`, with `predicate_id` written as `routedTo` (routing) or `onFlow` (on_flow) and the fields `declaration_id`, `scope`, `referent`, `predicate_id`, `direction` and, if present, `instance_ref`; `witness_ref` and the LIB field `source` are not compared.

## 3. Drawing (`cube.instances`, Q-4…Q-9)

- **DR-1 Frames:** one solid frame per instance with the ⬠ anchor and the title `Instanz <ref>` / `instance <ref>`, in order of first appearance in the trace; frames stack vertically.
- **DR-2 Blocks:** inside a frame one block per gateway the instance touches — a token of the instance at the gateway or on one of its flows, or a record for (gateway, instance) — in the declared order of `control_flow.gateways`. Block header: `<gateway> · <role>` (e.g. `bpmn:xor · exclusive split`).
- **DR-3 Exclusive split:** one row per outgoing flow, in `order`, default last: `<flow> → <target> · order <n>` or `· default`, then `taken · <token>` (solid) or `not taken` (dotted). With several tokens of the instance at the gateway, one sub-row per token (activation, Q-9). Two targets for one token: both rows read `taken · <token>`. Conditions are not drawn (P1.13 Q-6).
- **DR-4 Parallel join:** one row per incoming flow: `arrived · <token>` (solid) or `missing` (dotted); a missing row lists tokens of other instances on the same flow as `token of instance <i> present · not part (<token>)`, dashed (Q-6). One row for the outgoing flow: `<flow> → <target> · token <token>` or `no token`. A step counts as started only if a token on its flow shows it.
- **DR-5 Parallel split, exclusive merge:** one row per flow (split: incoming, then outgoing; merge: incoming, then outgoing) with `token <token>` or `no token`.
- **DR-6 Verdict lines:** one line per record of the block, in check order `exclusive`, `condition_order`, `join`, `split`, `merge`:
  - PASS → `checked · <value text>`;
  - FAIL → `rule violation · <value text>` with a hatched mark next to the line (VP-07 PV-5);
  - UNRESOLVED → `not checkable · <reason>`, reason `coverage missing: <referent> <predicate> <direction>[, …]` or `condition outcomes not recorded`;
  - no record → `not checked`.
  Value texts are fixed per `value` (§3.1) and add `missing <flows>`, `paths <targets>` or `foreign <tokens>` from the record.
- **DR-7 Model field:** below the frames, a field `Prozessmodell · keine Spur` / `process model · no trace` lists every gateway with role, incoming flows and outgoing flows with targets, order and default, without tokens and without verdicts. Targets that no token reaches appear only here.
- **DR-8 Legend:** line styles (solid = token in the trace, dotted = no token, dashed = other instance), the hatched mark (= rule violation from a LIB record) and the sentence "Verdicts are read from lunados.lib records, not computed by the view."
- **DR-9 No colour, no active content:** the colour-free audit and `NO_ACTIVE_SVG_CONTENT_NO_PATTERN` apply as in VP-10; hatching is drawn from lines.

### 3.1 Value texts

| `value` | en | de |
|---|---|---|
| `exclusive_one_path` | one path | ein Pfad |
| `exclusive_two_paths` | more than one path for one activation | mehr als ein Pfad für eine Aktivierung |
| `exclusive_no_path` | no path | kein Pfad |
| `condition_first_true` | first true condition taken | erste wahre Bedingung genommen |
| `default_without_true` | default without true condition | Default ohne wahre Bedingung |
| `default_with_true_condition` | default although a condition was true | Default trotz wahrer Bedingung |
| `not_first_true` | not the first true condition | nicht die erste wahre Bedingung |
| `join_complete` | all inputs | alle Eingänge |
| `join_waiting` | waiting | wartet |
| `join_incomplete` | continued without all inputs | ohne alle Eingänge weiter |
| `split_complete` | all outputs | alle Ausgänge |
| `split_incomplete` | not all outputs | nicht alle Ausgänge |
| `merge_pass_through` | passed through | durchgereicht |
| `merge_mismatch` | inputs and outputs differ | Ein- und Ausgänge ungleich |
| `coverage_undeclared` | coverage missing | Abdeckung fehlt |
| `conditions_unrecorded` | condition outcomes not recorded | Bedingungsergebnisse nicht aufgezeichnet |

## 4. Ledger and report

- **LG-1:** `<metadata id="vp11-instances-ledger">` holds the frames, blocks, rows with their tokens and statement IDs, the records (`library_ref`, claim, `status`, `value`) and the statements not drawn. Labels from the set appear in the ledger only.
- **LG-2:** The report lists `profile`, frames, blocks, rows with states, verdict lines, `warnings`, `notices` and `invariants_passed`, including `STATES_DIFFER_WITHOUT_COLOUR`, `NO_ACTIVE_SVG_CONTENT_NO_PATTERN`, `EMBEDDED_LEDGER_MATCH`, `VERDICTS_FROM_RECORDS_ONLY` and `MODEL_SEPARATE_FROM_TRACE`.
- **LG-3:** Output is deterministic: same inputs and locale → same bytes.

## 5. Interfaces

| Surface | Call |
|---|---|
| CLI | `python3 -m vpinstances from-trace --context ctx9.json --trace set.json [--record r.json …] --out in.json`, then `print-instances --input in.json --out <dir> [--locale de]` and `check-instances --input <dir>` |
| G6 | `cube_plan_source` with `printer: vpinstances`, the context, `statements` (the trace) and an optional `records` list (Q-10); `cube_plan_views` view `cube.instances`; `cube_plan_check` |

## 6. Status and diagnostic rules

| Situation | Result | Code |
|---|---|---|
| Context not `/9` or without `control_flow` | error | `VP11_ADAPTER_INPUT` |
| Trace set malformed, wrong `context_id`, duplicate IDs, endpoint not in `referents` | error | `VP11_TRACE_INVALID` |
| Trace referent not in the context | error | `VP11_TRACE_REF_UNKNOWN` |
| Trace predicate not in the context, or concepts not allowed | error | `VP11_TRACE_PREDICATE_INVALID` |
| Record malformed, wrong `library_ref`, method, result shape, claim ≠ result, check does not fit the gateway | error | `VP11_RECORD_INVALID` |
| Record for another control flow, trace or coverage | error | `VP11_RECORD_MISMATCH` |
| Two records for one claim | error | `VP11_RECORD_DUPLICATE` |
| Statement without `control_flow_role` in the trace | drawn without it; listed | `VP11_STATEMENT_NOT_DRAWN` (warning) |
| Token without `instance_ref` | frame "instance undeclared" | `VP11_INSTANCE_UNDECLARED` (warning) |
| Gateway with unsupported type or role | model field only | `VP11_GATEWAY_NOT_DRAWN` (warning) |
| Empty trace | model field only | `VP11_TRACE_EMPTY` (warning) |

Errors use the VP-10 error shape (`format`, `profile`, `status: FAIL`, `code`, `stage`, `message`).

## 7. Acceptance criteria and vectors (planned, fixed in TASK-054)

| AC | Requirement | Evidence |
|---|---|---|
| VP11-01 | VP-07…VP-10 unchanged; the 0.11.0 outputs pinned before the G6 change and byte-identical afterwards | pins, SHA256SUMS |
| VP11-02 | DR-1…DR-9 for each LIB case CF-11…CF-19, CF-21…CF-29 with its record: rows, states and verdict line as in the oracle | vectors |
| VP11-03 | Without records: "not checked" everywhere, no hatched mark (D-5) | vectors |
| VP11-04 | Several instances, gateways and records in one view (BPMN-02 model, i1 and i2) | vector |
| VP11-05 | Every §6 row | vectors |
| VP11-06 | Colour-free audit, no active content, ledger match, determinism | tests |
| VP11-07 | G6 equals CLI; `cube_plan_check` | adapter test |

Planned vectors: I-01…I-18 the LIB cases CF-11…CF-19 and CF-21…CF-29 as context, trace and record (record result = the case's `expected`, `library_ref` from the lunados.lib INDEX); I-19…I-21 BPMN-01 two paths, BPMN-02 waiting join and CF-25 foreign token without records; I-22 BPMN-02 model with i1 and i2 and several records; I-23…I-30 the §6 rows; I-31 German locale. All synthetic, derived from `docs/09-Research/control-flow/CHECK-CASES.json`.

## 8. Detail questions (resolved 2026-11-02, all as proposed)

| ID | Question | Decision | Reason |
|---|---|---|---|
| **Q-1** | Where does the trace come from? A `binding-context/9` holds no statements; MILE-008 checked them one by one through `cube_validate` | A **statement set** `aiaeao.cube.statement-set/1` for the `/9` context (as VP-10 0.11.0 for `/8`); trace statements are those with a `control_flow_role` predicate | one existing format for declared statements; precises D-3 without changing it |
| **Q-2** | Form of a LIB result as input? | **Record** `aiaeao.cube.conformance-record/1` `{format, library_ref, call, result}`, zero or more | same pattern as the projection record (VP-10 PR-6); the evaluator cannot know its INDEX hash |
| **Q-3** | How much does the printer check of a record? | Shape, `library_ref`, method, result schema, claim = result (RC-1); **call inputs equal context and trace** (RC-2); no recomputation | a record for another trace must not be drawn as the verdict for this one |
| **Q-4** | Layout? | **Frames stacked vertically**, blocks in declared gateway order, flows as rows; model field below; no free graph layout | deterministic and readable; M-12B structure without BPMN geometry |
| **Q-5** | Texts and locale? | English default and German (`--locale de`) as in VP-10; fixed value texts (§3.1) | same convention as VP-10 |
| **Q-6** | Where do foreign tokens appear? | **Only on a missing join input** of the instance, dashed, as "token of instance … present · not part"; "rule violation" only from a FAIL record | answers "why missing?" without listing every other instance; verdict stays with LIB (D-5) |
| **Q-7** | Which gateways appear in a frame? | Those the instance touches (token at the gateway or on its flows) or that have a record for the instance; all gateways in the model field | a frame shows the instance, the model field the model |
| **Q-8** | Several records per block? | One per check; `exclusive` and `condition_order` may both stand at an exclusive split; duplicates and unfitting checks are errors | the LIB result is per claim |
| **Q-9** | Several activations of one gateway in one instance? | One sub-row per activation token; per-activation verdicts from `result.details` | an instance can pass a gateway more than once (P1.13 Q-9) |
| **Q-10** | G6 arguments? | `cube_plan_source` gets an **optional `records` argument**; `statements` carries the trace; printer `vpinstances`, view `cube.instances`; discovery lists the printer with `P2-VP-INSTANCES/0.12.0` | additive; same tools as VP-10 0.11.0 |

## 9. Precisions fixed with the vectors (TASK-054, before any code)

These close gaps in §2–§6 without changing a decision.

- **TR-4 Tokens:** a token is a set referent that carries `instance_ref` or `at_gateway` in the context, or is the subject of a trace statement. A token without trace statement still counts (CF-13: a token at the gateway with no routing) and yields the derived row `{token, instance[, at]}` (§2.1).
- **TR-5 Check order:** context (IN-1) → trace set shape, `context_id`, duplicate IDs (`VP11_TRACE_INVALID`) → resolution of referents (`VP11_TRACE_REF_UNKNOWN`) → predicates and concepts (`VP11_TRACE_PREDICATE_INVALID`) → endpoints in `referents` (`VP11_TRACE_INVALID`) → per record RC-1, RC-3 (fit), RC-2 → duplicates across records (`VP11_RECORD_DUPLICATE`). The first error stops.
- **DR-1a Order:** frames follow the first token of each instance in the set's `referents`; the frame "instance undeclared" comes last. Inside a block, tokens are listed in `referents` order, joined by ", ".
- **DR-2a Touching (Q-7):** a flow that is outgoing at one gateway and incoming at another (`bpmn:f-approved`: merge → split) touches both. A routing target does not touch a gateway.
- **DR-3a Rows of an exclusive split:** per activation token a header row `activation <token>` / `Aktivierung <token>`, then one row per outgoing flow `<flow> → <target> · order <n>` (default: `· default`), then `· taken` or `· not taken` (de: `Reihenfolge <n>`, `Default`, `genommen`, `nicht genommen`).
- **DR-4a Rows of join, split, merge:** join input `<flow> · arrived · <tokens>` or `<flow> · missing`; a missing input appends, per token of another instance on that flow, ` · token of instance <i> present · not part (<token>)`. Split and merge inputs `<flow> · token <tokens>` or `<flow> · no token`. Outgoing rows `<flow> → <target> · token <tokens>` or `· no token`. The frame "instance undeclared" shows no foreign notes. de: `angekommen`, `fehlt`, `Token aus Instanz <i> vorhanden · nicht Teil (<token>)`, `Token`, `kein Token`.
- **DR-6a Verdict line:** `<check>: <state> · <value text>`, then in this order ` · paths <targets>` (only with more than one path), ` · taken <flow>`, ` · first true <flow>`, ` · missing <flows>`, ` · foreign <tokens>`, ` · excess <flow> <n>` and ` · undeclared <referent> <predicate> <direction>[ <instance>]`, each only when present and not empty, items joined by ", " in record order. The verdict uses the record's top-level `status` and `value`; per-activation details go to the ledger. Check names `exclusive`, `condition order`, `join`, `split`, `merge`; states `checked`, `rule violation`, `not checkable`; without record `not checked`. de: `Exklusivität`, `Bedingungsreihenfolge`, `Join`, `Split`, `Merge`; `geprüft`, `Regelverstoß`, `nicht prüfbar`, `nicht geprüft`; `Pfade`, `genommen`, `erste wahre`, `fehlt`, `fremd`, `Überschuss`, `nicht erklärt`.
- **DR-7a Model field:** per gateway `<gateway> · <role>`, then `in <flows>` / `ein <flows>`, then one line per outgoing flow `<flow> → <target>` (exclusive split: `· order <n>` / `· default`, default last). A gateway not drawn reads `<gateway> · <type> · not drawn` / `nicht gezeichnet` with no further lines.
- **Vectors:** the planned list in §7 is fixed as I-01…I-34 in `fixtures/i01_i34_materialized.json` (materialized by `scripts/materialize_i01_i34.py` from the lunados.lib cases, INDEX `bf59c17e…`) and `oracles/independent_i01_i34.json` (`scripts/write_oracle_i01_i34.py`): I-01…I-18 the LIB cases CF-11…CF-19, CF-21…CF-29 with their record; I-19…I-21 CF-12, CF-23, CF-25 without record; I-22 BPMN-02 with i1 and i2 and six records; I-23…I-30 the errors; I-31…I-33 the warnings; I-34 = I-22 in German. Every trace statement of a valid context passes P1.13 (`cube_validate`); I-25, I-26 and I-32 are UNRESOLVED there as intended. The VP-10 0.11.0 outputs are pinned in `fixtures/regression_vp10_0110_digests.json` (VP11-01).
