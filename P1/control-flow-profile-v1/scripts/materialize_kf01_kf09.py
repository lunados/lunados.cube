#!/usr/bin/env python3
"""Materialize the fixed CF-01..CF-09 inputs; expected values come only from the prior oracle."""
import copy
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parents[1]
CHECK = {c['case_id']: c for c in json.loads(
    (REPO / 'docs/09-Research/control-flow/CHECK-CASES.json').read_text('utf-8'))['cases']}
ORACLE = json.loads((HERE / 'oracles/independent_kf01_kf09.json').read_text('utf-8'))['cases']
SOURCE = json.loads((REPO / 'docs/09-Research/grammar-sampling/cases/BPMN-01-routed.json').read_text('utf-8'))
BASE = SOURCE['arguments']['context']
WI = 'Y:identified-object:work-item'
EV = 'Y:resource-object:evidence'
INSTANCE = 'Y:identified-object:bounded-execution'


def add_ref(ctx, ref, concept):
    if ref not in {r['ref'] for r in ctx['referents']}:
        ctx['referents'].append({'ref': ref, 'concept_id': concept, 'home': 'Y', 'layers': ['α'],
                                 'provenance_status': 'declared_unverified', 'scope_ref': ctx['scope_ref']})


def convert_gateway(g):
    return {'gateway': g['id'], 'type': g['type'], 'incoming': copy.deepcopy(g['incoming']),
            'outgoing': [{k: copy.deepcopy(v) for k, v in f.items() if k not in ('to', 'condition')}
                         | {'target': f['to']}
                         | ({'condition_ref': 'model:bpmn-order#' + f['condition']} if 'condition' in f else {})
                         for f in g['outgoing']]}


def make_vector(oracle):
    cid = oracle['check_case']
    case = CHECK[cid]
    ctx = copy.deepcopy(BASE)
    ctx['format'] = 'aiaeao.cube.binding-context/8' if cid == 'CF-08' else 'aiaeao.cube.binding-context/9'
    ctx['context_id'] = 'p113-' + cid.lower()
    add_ref(ctx, 'bpmn:i1', INSTANCE)
    for t in case['trace']:
        add_ref(ctx, t['token'], EV)
        ref = next(r for r in ctx['referents'] if r['ref'] == t['token'])
        ref['instance_ref'] = t['instance']
        if cid != 'CF-08' and 'at' in t:
            ref['at_gateway'] = t['at']
    model = case['control_flow'] or CHECK['CF-01']['control_flow']
    for g in model:
        add_ref(ctx, g['id'], WI)
        for flow in g['incoming']:
            add_ref(ctx, flow, WI)
        for flow in g['outgoing']:
            add_ref(ctx, flow['flow'], WI)
            add_ref(ctx, flow['to'], WI)
    if cid == 'CF-07':
        add_ref(ctx, 'bpmn:f-ghost', WI)
    if cid != 'CF-08':
        ctx['control_flow'] = {'gateways': [convert_gateway(g) for g in model]}
        for p in ctx['predicate_contracts']:
            if p['predicate_id'] == 'routedTo':
                p['control_flow_role'] = 'routing'
    if cid in ('CF-07', 'CF-08'):
        p = {'predicate_id': 'onFlow', 'revision': 'p113:bpmn:pred/1', 'scope': ctx['scope_ref'],
             'origin': 'illustrative_fixture', 'subject_concept_ids': [EV], 'object_concept_ids': [WI],
             'direction': 'subject_to_object', 'required_qualifiers': [], 'additional_constraints': []}
        if cid != 'CF-08':
            p['control_flow_role'] = 'on_flow'
        ctx['predicate_contracts'].append(p)
    t = case['trace'][0] if case['trace'] else CHECK['CF-01']['trace'][0]
    if not case['trace']:
        token_ref = next(r for r in ctx['referents'] if r['ref'] == t['token'])
        token_ref['instance_ref'] = t['instance']
        token_ref['at_gateway'] = t['at']
    if 'on_flow' in t:
        predicate, target = 'onFlow', t['on_flow']
    else:
        predicate, target = 'routedTo', t['routed_to']
    text = (f'rel("{predicate}",Y:α:Evidence["{t["token"]}"],'
            f'Y:α:WorkItem["{target}"])')
    return {'id': oracle['id'], 'check_case': cid, 'question': case['question'],
            'input_text': text, 'input_format': 'acg_text', 'context': ctx,
            'expected_overall': oracle['expected_overall'], 'required_codes': oracle['required_codes'],
            'forbidden_codes': oracle['forbidden_codes']}


vectors = [make_vector(o) for o in ORACLE]
out = {'format': 'aiaeao.cube.p1.13-vectors/1', 'reference_version': 'v9.4',
       'source': 'Fixed CF-01..CF-09, independent KF oracle, and synthetic MILE-002 context', 'cases': vectors}
(HERE / 'fixtures/kf01_kf09_materialized.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', 'utf-8')
print('wrote', len(vectors), 'vectors')
