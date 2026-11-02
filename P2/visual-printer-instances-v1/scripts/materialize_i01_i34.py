#!/usr/bin/env python3
"""Materialize the VP-11 vectors I-01…I-34 (TASK-054, before any printer code).

Sources: the lunados.lib cases of analyze.trace-conformance/v1 (sibling checkout ../lunados.lib, pinned by INDEX sha256)
for I-01…I-21 and the hand-built cases I-22…I-34. Each case gets a binding-context/9, a trace statement set
(aiaeao.cube.statement-set/1) and zero or more conformance records (aiaeao.cube.conformance-record/1). Record results are
the LIB cases' `expected` (I-01…I-18) or the pinned LIB evaluator's output (I-22, I-34); for the LIB cases the evaluator
is run as well and must equal `expected`. Every context is checked with the P1.13 context validator.

  python3 -I P2/visual-printer-instances-v1/scripts/materialize_i01_i34.py   (from the lunados.cube root)
All data synthetic.
"""
import copy, hashlib, json, subprocess, sys
from pathlib import Path

ROOT = Path.cwd(); HERE = ROOT/'P2/visual-printer-instances-v1'; LIB = ROOT.parent/'lunados.lib'
E = LIB/'entries/analyze.trace-conformance/v1'
sys.path[:0] = [str(ROOT/'P1'/p) for p in ('control-flow-profile-v1', 'coverage-instance-profile-v1', 'migration-methods-v1',
                                          'migration-profile-v2', 'migration-profile-v1', 'comparison-profile-v1', 'simulation-profile-v1',
                                          'instantiation-profile-v1', 'semantic-validator-v1')]
sys.dont_write_bytecode = True
from cube_p113.validator import P113Validator  # noqa: E402

INDEX = next(e for e in json.loads((LIB/'INDEX.json').read_text('utf-8'))['entries'] if e['entry_id'] == 'analyze.trace-conformance')
LIBREF = {'library_id': 'lunados.lib', 'entry_id': 'analyze.trace-conformance', 'revision': 1, 'sha256': INDEX['sha256']}
EV = 'Y:resource-object:evidence'; WI = 'Y:identified-object:work-item'; BE = 'Y:identified-object:bounded-execution'
LIMITS = ['Synthetische Versuchsabbildung MILE-002 BPMN-01..03: Token-Aufzeichnung→Y:resource-object:evidence, Aktivität, Gateway und '
          'Fluss→Y:identified-object:work-item (Arbeitsannahme A). Token sind keine X Events.',
          'Handgeschriebene Spur, keine Engine-Ausführung; keine Wahrheit, Autorität oder Zulassung behauptet.']


def pred(pid, role=None, obj=WI):
    p = {'predicate_id': pid, 'revision': 'mile009:vp11:pred/1', 'scope': 'bpmn:trace', 'origin': 'illustrative_fixture',
         'subject_concept_ids': [EV], 'object_concept_ids': [obj], 'direction': 'subject_to_object', 'required_qualifiers': [],
         'additional_constraints': []}
    if role:
        p['control_flow_role'] = role
    return p


def ref(r, concept, **kw):
    return {'ref': r, 'concept_id': concept, 'home': 'Y', 'layers': ['α'], 'provenance_status': 'declared_unverified', 'scope_ref': 'bpmn:trace', **kw}


def context(cid, cf, trace, coverage, extra_preds=(), extra_refs=()):
    seen, refs = set(), []

    def add(r, concept, **kw):
        if r not in seen:
            seen.add(r); refs.append(ref(r, concept, **kw))
    for g in cf['gateways']:
        add(g['gateway'], WI)
        for f in g['incoming']:
            add(f, WI)
        for o in g['outgoing']:
            add(o['flow'], WI); add(o['target'], WI)
    for row in trace:
        if row.get('instance'):
            add(row['instance'], BE)
    for row in trace:
        kw = {}
        if row.get('instance'):
            kw['instance_ref'] = row['instance']
        if row.get('at'):
            kw['at_gateway'] = row['at']
        add(row['token'], EV, **kw)
    for r in extra_refs:
        add(r['ref'], r['concept_id'], **{k: v for k, v in r.items() if k in ('instance_ref', 'at_gateway')})
    cov = [{k: d[k] for k in ('declaration_id', 'scope', 'referent', 'predicate_id', 'direction', 'instance_ref') if k in d}
           | {'witness_ref': f"synthetic:vp11#{cid}/{d['declaration_id']}"} for d in coverage]
    return {'format': 'aiaeao.cube.binding-context/9', 'reference_version': 'v9.4', 'context_id': f'vp11-{cid.lower()}',
            'source_kind': 'illustrative_fixture', 'scope_ref': 'bpmn:trace', 'referents': refs,
            'predicate_contracts': [pred('routedTo', 'routing'), pred('onFlow', 'on_flow'), *extra_preds],
            'method_contracts': [], 'profile_limitations': LIMITS, 'coverage_declarations': cov, 'control_flow': copy.deepcopy(cf)}


def trace_set(ctx, trace, extra=()):
    refs, stmts = [], []
    for row in trace:
        if row['token'] not in refs:
            refs.append(row['token'])
    for row in trace:
        for key, p in (('routed_to', 'routedTo'), ('on_flow', 'onFlow')):
            if row.get(key):
                stmts.append({'statement_id': f't-{len(stmts)+1}', 'subject': row['token'], 'predicate_id': p, 'object': row[key]})
    for s in extra:
        stmts.append(dict(s, statement_id=f't-{len(stmts)+1}'))
    for s in stmts:
        for e in (s['subject'], s['object']):
            if e not in refs:
                refs.append(e)
    return {'format': 'aiaeao.cube.statement-set/1', 'set_id': f"trace-{ctx['context_id']}", 'context_id': ctx['context_id'],
            'referents': refs, 'statements': stmts, 'witness_ref': f"synthetic:vp11#{ctx['context_id']}/trace"}


def evaluate(call):
    p = subprocess.run([sys.executable, '-I', str(E/'evaluator/evaluate.py')], input=json.dumps(call).encode(), capture_output=True)
    if p.returncode:
        raise SystemExit(f'LIB evaluator refused: {p.stderr.decode()[-300:]}')
    return json.loads(p.stdout)


def record(call, result):
    return {'format': 'aiaeao.cube.conformance-record/1', 'library_ref': dict(LIBREF), 'call': copy.deepcopy(call), 'result': copy.deepcopy(result)}


def libcase(cid):
    return json.loads((E/'cases'/f'{cid}.json').read_text('utf-8'))


cases, notes = [], []


def put(iid, source, ctx, trace, records, locale='en', note=''):
    cases.append({'id': iid, 'source': source, 'locale': locale, 'context': ctx, 'trace': trace, 'records': records, 'note': note})


LIBIDS = [f'CF-{n}' for n in (11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 24, 25, 26, 27, 28, 29)]
for n, cid in enumerate(LIBIDS, 1):
    c = libcase(cid); i = c['call']['inputs']
    got = evaluate(c['call'])
    if got != c['expected']:
        raise SystemExit(f'{cid}: evaluator != expected')
    ctx = context(cid, i['control_flow'], i['trace'], i['coverage'])
    put(f'I-{n:02d}', f'lunados.lib {cid}', ctx, trace_set(ctx, i['trace']), [record(c['call'], c['expected'])])
for iid, cid, note in (('I-19', 'CF-12', 'BPMN-01 two paths, no record'), ('I-20', 'CF-23', 'BPMN-02 waiting join, no record'),
                       ('I-21', 'CF-25', 'BPMN-03 foreign token, no record')):
    i = libcase(cid)['call']['inputs']
    ctx = context(cid, i['control_flow'], i['trace'], i['coverage'])
    put(iid, f'lunados.lib {cid} without record', ctx, trace_set(ctx, i['trace']), [], note=note)

# I-22: BPMN-02 model with two instances and six records (I-34: same, German)
CF = libcase('CF-21')['call']['inputs']['control_flow']
TR = [{'token': 'bpmn:i1/tok-route', 'instance': 'bpmn:i1', 'at': 'bpmn:xor', 'routed_to': 'bpmn:approve-auto', 'conditions': {'bpmn:f-manual': False}}]
TR += [{'token': f'bpmn:i1/{t}', 'instance': 'bpmn:i1', 'on_flow': f'bpmn:{f}'} for t, f in
       (('tok-ad', 'f-auto-done'), ('tok-ap', 'f-approved'), ('tok-s', 'f-stock'), ('tok-c', 'f-credit'), ('tok-sd', 'f-stock-done'),
        ('tok-cd', 'f-credit-done'), ('tok-ship', 'f-ship'))]
TR += [{'token': 'bpmn:i2/tok-route', 'instance': 'bpmn:i2', 'at': 'bpmn:xor', 'routed_to': 'bpmn:approve-manual', 'conditions': {'bpmn:f-manual': True}}]
TR += [{'token': f'bpmn:i2/{t}', 'instance': 'bpmn:i2', 'on_flow': f'bpmn:{f}'} for t, f in
       (('tok-md', 'f-manual-done'), ('tok-ap', 'f-approved'), ('tok-s', 'f-stock'), ('tok-c', 'f-credit'), ('tok-cd', 'f-credit-done'))]
COV = []
for inst in ('bpmn:i1', 'bpmn:i2'):
    COV.append({'declaration_id': f'cv-{len(COV)+1}', 'scope': 'referent_relation_direction', 'referent': f'{inst}/tok-route',
                'predicate_id': 'routedTo', 'direction': 'outgoing', 'instance_ref': inst, 'source': 'Leitentscheidung vollständig aufgezeichnet'})
    for f in ('f-manual-done', 'f-auto-done', 'f-approved', 'f-stock', 'f-credit', 'f-stock-done', 'f-credit-done', 'f-ship'):
        COV.append({'declaration_id': f'cv-{len(COV)+1}', 'scope': 'referent_relation_direction', 'referent': f'bpmn:{f}',
                    'predicate_id': 'onFlow', 'direction': 'incoming', 'instance_ref': inst, 'source': 'Token vollständig aufgezeichnet'})
ctx22 = context('I-22', CF, TR, COV)
recs = []
for check, gw, inst in (('exclusive', 'bpmn:xor', 'bpmn:i1'), ('condition_order', 'bpmn:xor', 'bpmn:i1'), ('merge', 'bpmn:merge', 'bpmn:i1'),
                        ('split', 'bpmn:split', 'bpmn:i1'), ('join', 'bpmn:join', 'bpmn:i1'), ('join', 'bpmn:join', 'bpmn:i2')):
    call = {'schema': 'lunados.lib/call/v1', 'method_id': 'analyze.trace-conformance/v1', 'parameters': {},
            'inputs': {'control_flow': CF, 'trace': TR, 'coverage': COV, 'claim': {'check': check, 'gateway': gw, 'instance': inst}}}
    recs.append(record(call, evaluate(call)))
put('I-22', 'BPMN-02 model, i1 complete, i2 waiting', ctx22, trace_set(ctx22, TR), recs)

# I-23…I-30: errors (§6), built on I-01 (CF-11) and I-10 (CF-21)
b, j = cases[0], cases[9]


def variant(iid, base, note, ctx=None, trace=None, records=None):
    put(iid, f"variant of {base['id']}", copy.deepcopy(ctx or base['context']), copy.deepcopy(trace or base['trace']),
        copy.deepcopy(base['records'] if records is None else records), note=note)


c8 = copy.deepcopy(b['context']); c8['format'] = 'aiaeao.cube.binding-context/8'; del c8['control_flow']
variant('I-23', b, 'context /8 without control_flow → VP11_ADAPTER_INPUT', ctx=c8, records=[])
t = copy.deepcopy(b['trace']); t['context_id'] = 'other-context'
variant('I-24', b, 'trace for another context_id → VP11_TRACE_INVALID', trace=t, records=[])
t = copy.deepcopy(b['trace']); t['statements'][0]['object'] = 'bpmn:ghost'; t['referents'].append('bpmn:ghost')
variant('I-25', b, 'trace endpoint not in the context → VP11_TRACE_REF_UNKNOWN', trace=t, records=[])
t = copy.deepcopy(b['trace']); t['statements'][0]['predicate_id'] = 'flowsTo'
variant('I-26', b, 'trace predicate not in the context → VP11_TRACE_PREDICATE_INVALID', trace=t, records=[])
r = copy.deepcopy(b['records']); r[0]['library_ref']['sha256'] = 'abc'
variant('I-27', b, 'library_ref sha256 malformed → VP11_RECORD_INVALID', records=r)
variant('I-28', b, 'record of CF-12 (other trace) → VP11_RECORD_MISMATCH', records=cases[1]['records'])
variant('I-29', b, 'same record twice → VP11_RECORD_DUPLICATE', records=b['records']*2)
r = copy.deepcopy(j['records']); r[0]['call']['inputs']['claim']['check'] = 'split'; r[0]['result']['check'] = 'split'
variant('I-30', j, 'check split at a parallel join → VP11_RECORD_INVALID', records=r)

# I-31…I-33: warnings
extra_refs = [{'ref': 'bpmn:tok-loose', 'concept_id': EV}]
ctx = context('I-31', CF, libcase('CF-21')['call']['inputs']['trace'], [], extra_preds=[pred('joins', obj=EV)], extra_refs=extra_refs)
tr = trace_set(ctx, libcase('CF-21')['call']['inputs']['trace'],
               extra=[{'subject': 'bpmn:i1/tok-stock', 'predicate_id': 'joins', 'object': 'bpmn:i1/tok-credit'},
                      {'subject': 'bpmn:tok-loose', 'predicate_id': 'onFlow', 'object': 'bpmn:f-ship'}])
put('I-31', 'CF-21 trace plus a joins statement and a token without instance_ref', ctx, tr, [],
    note='VP11_STATEMENT_NOT_DRAWN, VP11_INSTANCE_UNDECLARED')
i = libcase('CF-23')['call']['inputs']
cf = copy.deepcopy(i['control_flow'])
cf['gateways'].append({'gateway': 'bpmn:or', 'type': 'inclusive', 'incoming': ['bpmn:f-x'], 'outgoing': [{'flow': 'bpmn:f-y', 'target': 'bpmn:ship'}]})
ctx = context('I-32', cf, i['trace'], i['coverage'])
put('I-32', 'CF-23 plus an inclusive gateway', ctx, trace_set(ctx, i['trace']), [], note='VP11_GATEWAY_NOT_DRAWN')
t = copy.deepcopy(b['trace']); t['referents'] = []; t['statements'] = []
variant('I-33', b, 'empty trace → VP11_TRACE_EMPTY', trace=t, records=[])
c22 = next(c for c in cases if c['id'] == 'I-22')
put('I-34', 'I-22 in German', copy.deepcopy(c22['context']), copy.deepcopy(c22['trace']), copy.deepcopy(c22['records']), locale='de')

# P1.13: every trace statement through the P1.13 validator, as cube_validate does (validity comes from P1.13, not the printer)
v = P113Validator(); LABEL = {EV: 'Evidence', WI: 'WorkItem', BE: 'BoundedExecution'}
for c in cases:
    try:
        v.validate_context(copy.deepcopy(c['context']))
    except Exception as x:  # I-23: a /8 context with P1.13 fields is refused by P1 as well
        c['p113'] = {'status': 'REFUSED', 'codes': [type(x).__name__]}
        continue
    concept = {r['ref']: r['concept_id'] for r in c['context']['referents']}
    statuses, codes = [], set()
    for st in c['trace']['statements']:
        lab = lambda r: LABEL.get(concept.get(r), 'WorkItem')  # noqa: E731
        text = f'rel("{st["predicate_id"]}",Y:α:{lab(st["subject"])}["{st["subject"]}"],Y:α:{lab(st["object"])}["{st["object"]}"])'
        rep = v.validate_bytes(text.encode(), input_format='acg_text', context=copy.deepcopy(c['context']))
        statuses.append(rep['overall_status']); codes |= {d['code'] for d in rep.get('diagnostics', [])}
    order = ['PASS', 'UNRESOLVED', 'FAIL']
    c['p113'] = {'status': max(statuses, key=order.index) if statuses else 'NO_STATEMENTS', 'statements': len(statuses), 'codes': sorted(codes)}
cases.sort(key=lambda c: c['id'])
out = {'format': 'aiaeao.p2.vp11-vectors/1', 'profile': 'P2-VP-INSTANCES/0.12.0', 'pinned_before': 'any VP-11 printer code (TASK-054)',
       'lunados_lib': {'entry': LIBREF, 'cases_sha256': {cid: hashlib.sha256((E/'cases'/f'{cid}.json').read_bytes()).hexdigest() for cid in LIBIDS}},
       'cases': cases}
(HERE/'fixtures').mkdir(exist_ok=True)
(HERE/'fixtures/i01_i34_materialized.json').write_text(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True)+'\n', 'utf-8')
print(len(cases), 'cases;', {c['id']: (c['p113']['status'], c['p113']['codes']) for c in cases if c['p113']['status'] != 'PASS'})
