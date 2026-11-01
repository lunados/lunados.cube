#!/usr/bin/env python3
"""Materialise K-01..K-21 (P1_12_ACCEPTANCE_SPEC.md §5) into explicit binding-context/8 vectors.

Source of every vector is its check case in docs/09-Research/completeness-instances/CHECK-CASES.json
(statements, declarations, claim, instance bindings, predicate properties), translated per the §5 notes.
Referents and predicate contracts come from the MILE-002 case contexts (same working mappings, synthetic).
Expected values are copied from oracles/independent_k01_k21.json, transcribed before any code.

input_text is one statement (P1 checks single statements); `statements` is the full statement set of the
check case, kept for the LIB entry (TASK-034). P1 never evaluates it.
"""
import copy, json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]; REPO = HERE.parents[1]
CASES = REPO/'docs/09-Research/grammar-sampling/cases'
CHECK = {c['case_id']: c for c in json.loads((REPO/'docs/09-Research/completeness-instances/CHECK-CASES.json').read_text('utf-8'))['cases']}
ORACLE = {c['id']: c for c in json.loads((HERE/'oracles/independent_k01_k21.json').read_text('utf-8'))['cases']}
F8, A = 'aiaeao.cube.binding-context/8', 'α'
INST, WI, EV = 'Y:identified-object:bounded-execution', 'Y:identified-object:work-item', 'Y:resource-object:evidence'
LABEL = {'Z:module-body:tool': 'Tool', 'Z:boundary:capability': 'Capability', 'Y:resource-object:artifact': 'Artifact',
         'Y:resource-object:evidence': 'Evidence', 'Y:identified-object:work-item': 'WorkItem'}
FLOW = {'f-stock-done': 'bpmn:f-stock-done', 'f-credit-done': 'bpmn:f-credit-done'}   # §5 translation note: flow referents


def base(name, cid):
    c = copy.deepcopy(json.loads((CASES/f'{name}.json').read_text('utf-8'))['arguments']['context'])
    c['format'] = F8
    c['context_id'] = 'p112-' + cid.lower()
    return c


def add_ref(c, ref, concept):
    if ref not in {r['ref'] for r in c['referents']}:
        c['referents'].append({'ref': ref, 'concept_id': concept, 'home': concept.split(':')[0], 'layers': [A],
                               'provenance_status': 'declared_unverified', 'scope_ref': c['scope_ref']})


def trace(cid, joins_flows):
    """Shared-scope trace context (BPMN-03 shared) with tokens, instances and, for join rules, flows + gateway + onFlow."""
    c = base('BPMN-03-join-cross-instance-shared', cid)
    add_ref(c, 'bpmn:i1/tok-credit', EV)
    add_ref(c, 'bpmn:i1', INST); add_ref(c, 'bpmn:i2', INST)
    if joins_flows:
        for f in (*FLOW.values(), 'bpmn:join'):
            add_ref(c, f, WI)
        c['predicate_contracts'].append({'predicate_id': 'onFlow', 'revision': 'p112:bpmn:pred/1', 'scope': c['scope_ref'],
                                         'origin': 'illustrative_fixture', 'subject_concept_ids': [EV], 'object_concept_ids': [WI],
                                         'direction': 'subject_to_object', 'required_qualifiers': [],
                                         'additional_constraints': ['Token liegt auf einem Sequence Flow (Spuraufzeichnung).']})
    return c


def context_for(cid, cc):
    m = cc['matrix_case']
    if m.startswith('ARC'):
        return base('ARC-02-part', cid)
    if m.startswith('DSM'):
        return base('DSM-03-marked', cid)
    if m == 'BPMN-01':
        return base('BPMN-01-routed', cid)
    if m == 'BPMN-02' and cc['claim']['rule'] != 'single_statement':   # CI-03 is a BPMN-02 statement but carries only its own bindings
        c = trace(cid, True)
        bind = {'bpmn:i1/tok-stock': 'bpmn:i1', 'bpmn:i1/tok-credit': 'bpmn:i1', 'bpmn:i2/tok-credit': 'bpmn:i2'}
        for r in c['referents']:                      # token membership for CV-4 evaluation in LIB; joins is not instance-constrained here
            if r['ref'] in bind:
                r['instance_ref'] = bind[r['ref']]
        return c
    if cid == 'CI-02':
        return base('BPMN-03-join-cross-instance-scoped', cid)
    return trace(cid, False)


def obj(ref):
    return FLOW.get(ref, ref)


def statements(cc):
    return [{'subject': s['subject'], 'predicate_id': s['predicate'], 'object': obj(s['object'])} for s in cc['statements']]


def render(st, ctx):
    concept = {r['ref']: r['concept_id'] for r in ctx['referents']}

    def term(ref):
        k = concept[ref]
        return f'{k.split(":")[0]}:{A}:{LABEL[k]}["{ref}"]'
    return f'rel("{st["predicate_id"]}",{term(st["subject"])},{term(st["object"])})'


def declarations(cc, rule):
    out = []
    for n, d in enumerate(cc['declarations'], 1):
        if d['scope'] == 'pair':
            out.append({'declaration_id': f'cv-{n}', 'scope': 'pair', 'subject': d['subject'], 'predicate_id': d['predicate'],
                        'object': d['object'], 'witness_ref': 'synthetic:coverage#' + d['source']})
        elif d['direction'] == 'incoming-to-join':     # §5 note: one declaration per incoming flow, restricted to the instance (CV-4)
            for f in rule['incoming_flows']:
                out.append({'declaration_id': f'cv-{n}-{f["flow"].split(":")[1]}', 'scope': 'referent_relation_direction', 'referent': f['flow'],
                            'predicate_id': d['predicate'], 'direction': 'incoming', 'instance_ref': d['referent'],
                            'witness_ref': 'synthetic:coverage#' + d['source']})
        else:
            out.append({'declaration_id': f'cv-{n}', 'scope': 'referent_relation_direction', 'referent': d['referent'], 'predicate_id': d['predicate'],
                        'direction': d['direction'], 'witness_ref': 'synthetic:coverage#' + d['source']})
    return out


def rule_of(cid, cl):
    w = 'synthetic:rule#' + cl.get('source', cid)
    if cl['rule'] == 'absence':
        r = {'rule_id': 'pr-' + cid.lower(), 'kind': 'absence', 'predicate_id': cl['predicate'], 'witness_ref': w}
        for f in ('subject', 'object'):
            if cl.get(f):
                r[f] = cl[f]
        return r
    if cl['rule'] == 'count':
        r = {'rule_id': 'pr-' + cid.lower(), 'kind': 'count', 'referent': cl['subject'], 'predicate_id': cl['predicate'],
             'direction': cl['direction'], 'min': cl['min'], 'witness_ref': w}
        if cl.get('max') is not None:
            r['max'] = cl['max']
        return r
    return {'rule_id': 'pr-' + cid.lower(), 'kind': 'join_activation', 'instance_ref': cl['instance'], 'gateway': cl['gateway'],
            'predicate_id': 'onFlow', 'incoming_flows': [{'flow': obj(f), 'min': b[0]} for f, b in cl['per_incoming_flow'].items()],
            'witness_ref': w}


NEUTRAL = {'ARC-03': ('am:financial-processing', 'composedOf', 'am:billing'), 'ARC-02': ('am:financial-processing', 'composedOf', 'am:billing')}

out = []
for k, o in sorted(ORACLE.items()):
    cid = o['check_case']; cc = CHECK[cid]
    ctx = context_for(cid, cc)
    sts = statements(cc)
    if cc['claim']['rule'] == 'single_statement':
        for ref, inst in (cc.get('instance_bindings') or {}).items():
            add_ref(ctx, inst, INST)
            for r in ctx['referents']:
                if r['ref'] == ref:
                    r['instance_ref'] = inst
        for p in ctx['predicate_contracts']:
            props = (cc.get('predicate_properties') or {}).get(p['predicate_id'], {})
            if 'requires_same_instance' in props:
                p['requires_same_instance'] = props['requires_same_instance']
    else:
        rule = rule_of(cid, cc['claim'])
        ctx['coverage_declarations'] = declarations(cc, rule)
        ctx['population_rules'] = [rule]
    first = sts[0] if sts else dict(zip(('subject', 'predicate_id', 'object'), NEUTRAL[cc['matrix_case']]))
    item = {'id': k, 'check_case': cid, 'question': cc['question'], 'input_text': render(first, ctx), 'input_format': 'acg_text', 'context': ctx}
    if cc['claim']['rule'] != 'single_statement':
        item['statements'] = sts
        item['lib_expected'] = o['lib_expected']
    item.update(expected_overall=o['expected_overall'], required_codes=o['required_codes'], forbidden_codes=o['forbidden_codes'])
    out.append(item)

(HERE/'fixtures').mkdir(exist_ok=True)
(HERE/'fixtures/k01_k21_materialized.json').write_text(json.dumps(
    {'format': 'aiaeao.cube.p1.12-vectors/1', 'reference_version': 'v9.4',
     'source': 'P1_12_ACCEPTANCE_SPEC.md §5; CHECK-CASES.json; contexts from MILE-002 case files; synthetic, no client data',
     'cases': out}, ensure_ascii=False, indent=1)+'\n', 'utf-8')
print('wrote', len(out), 'vectors')
