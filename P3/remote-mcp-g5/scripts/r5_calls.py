"""G5 R5 call list (MILE-010 TASK-059): every remote call of the R5 acceptance, with wire arguments as the tools take them.

A call is a chain of steps {op, args, from?}; `from` = {'arg': name, 'path': [...]} feeds a part of the previous step's
result into this step (the source of cube_plan_source into cube_plan_views, the whole result into cube_plan_check).
A chain stops at the first error. `live`: 'host' = also checked by hand through the connector; every call runs in the
offline parity (core) and in the scripted live acceptance.

Groups: D discovery; V cube_validate with binding-context/9; P plan tools (K-, O-, S-, I-vectors, limits, arguments).
All data synthetic. Import from the lunados.cube root or via the scripts directory.
"""
from __future__ import annotations
import copy
import glob
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
CHECK = {'arg': 'result', 'path': []}
SRC = {'arg': 'source', 'path': ['source']}


def _j(rel):
    return json.loads((REPO/rel).read_text('utf-8'))


def _drop_none(d):
    return {k: v for k, v in d.items() if v is not None}


def chain(cid, group, steps, live=None):
    return {'id': cid, 'group': group, 'live': live, 'steps': steps}


def views_chain(cid, source_step, view_args, check=True, live=None):
    steps = [source_step, {'op': 'cube_plan_views', 'args': _drop_none(view_args), 'from': SRC}] if source_step['op'] == 'cube_plan_source' \
        else [{'op': 'cube_plan_views', 'args': _drop_none(view_args)}]
    if check:
        steps.append({'op': 'cube_plan_check', 'args': {}, 'from': CHECK})
    return chain(cid, 'P', steps, live)


def source(context, plan_id, printer, **kw):
    return {'op': 'cube_plan_source', 'args': {'context': context, 'plan_id': plan_id, 'printer': printer, **_drop_none(kw)}}  # plan_id stays, may be null


def big_instances(n=400):
    """A trace with n instances waiting at the join: small rules, an SVG over 512 KiB (P3_PLAN_SVG_TOO_LARGE)."""
    base = {c['id']: c for c in _j('P2/visual-printer-instances-v1/fixtures/i01_i34_materialized.json')['cases']}['I-20']
    ctx, tr = copy.deepcopy(base['context']), copy.deepcopy(base['trace'])
    proto = next(r for r in ctx['referents'] if r['ref'] == 'bpmn:i2/tok-credit')
    inst = next(r for r in ctx['referents'] if r['ref'] == 'bpmn:i2')
    for i in range(3, n+3):
        ctx['referents'].append(dict(inst, ref=f'bpmn:i{i}'))
        ctx['referents'].append(dict(proto, ref=f'bpmn:i{i}/tok-credit', instance_ref=f'bpmn:i{i}'))
        tr['referents'].insert(len(tr['referents'])-1, f'bpmn:i{i}/tok-credit')
        tr['statements'].append({'statement_id': f't-{len(tr["statements"])+1}', 'subject': f'bpmn:i{i}/tok-credit', 'predicate_id': 'onFlow',
                                 'object': 'bpmn:f-credit-done'})
    return ctx, tr


def calls():
    out = [chain('D-01', 'D', [{'op': 'cube_discover_surface', 'args': {}}], live='host')]
    # V: binding-context/9 (P1.13): KF-01…KF-09 and the seven BPMN re-run cases of MILE-008
    for c in _j('P1/control-flow-profile-v1/fixtures/kf01_kf09_materialized.json')['cases']:
        out.append(chain(f"V-{c['id']}", 'V', [{'op': 'cube_validate', 'args': _drop_none(
            {'input_text': c['input_text'], 'input_format': c.get('input_format'), 'context': c['context']})}],
            live='host' if c['id'] == 'KF-08' else None))
    for f in sorted(glob.glob(str(REPO/'docs/09-Research/control-flow/rerun/cases/*.json'))):
        c = json.loads(Path(f).read_text('utf-8'))
        a = c['arguments']
        out.append(chain(f"V-{c['case_id']}", 'V', [{'op': 'cube_validate', 'args': _drop_none(
            {'input_text': a['input_text'], 'input_format': a.get('input_format'), 'context': a['context']})}],
            live='host' if c['case_id'] in ('BPMN-01-routed-to-ship-v9', 'BPMN-01-token-position-v9') else None))
    # P: G6 vectors K-* (VP-07, VP-08, VP-09)
    g6 = _j('P3/adapters/mcp-local/tests/g6/k01_k18_materialized.json')
    fx = {k: _j(v['path']) for k, v in g6['fixtures'].items()}
    out.append(views_chain('P-K01-phases', source(fx['g73']['context'], fx['g73']['plan_id'], 'vpmigration'),
                           {'view': 'cube.phases', 'granularity': 'standard', 'partition': 'subject'}))
    k07 = {c['id']: c for c in g6['cases']}['K-07']['input']
    out.append(views_chain('P-K07-flow', source(fx['g74']['context'], fx['g74']['plan_id'], 'vpmigration', profile=k07['source_from']['profile']),
                           {**{k: v for k, v in k07['view'].items()}}))
    out.append(views_chain('P-K08-sequence', {'op': 'cube_plan_views'},
                           {'source': fx['gseq']['sequence_source'], 'view': 'cube.sequence', 'granularity': 'standard', 'partition': 'trigger'},
                           live='host'))
    k09 = {c['id']: c for c in g6['cases']}['K-09']['input']
    out.append(views_chain('P-K09-axes', source(fx['gax']['context'], fx['gax']['plan_id'], 'vpaxes', profile=k09['source_from']['profile']),
                           dict(k09['view'])))
    out.append(chain('P-K11-context9', 'P', [source({'context_id': 'k11', 'format': 'aiaeao.cube.binding-context/9'}, 'mp-x', 'vpmigration')]))
    out.append(chain('P-K12-view-unknown', 'P', [source(fx['g73']['context'], fx['g73']['plan_id'], 'vpmigration'),
                                                 {'op': 'cube_plan_views', 'args': {'view': 'cube.matrix', 'granularity': 'standard'}, 'from': SRC}]))
    a18 = {c['id']: c for c in fx['avec']['cases']}['A-18']['input']
    out.append(views_chain('P-K13-axes-detail', source(a18['context'], a18['plan_id'], 'vpaxes'),
                           {'view': 'cube.axes', 'granularity': 'detail', 'rows': 'Z:referent', 'cols': 'T'}))
    k14 = {c['id']: c for c in g6['cases']}['K-14']['input']
    out.append(views_chain('P-K14-axes-context', source(k14['context'], k14['plan_id'], k14['printer']), dict(k14['view'])))
    out.append(chain('P-K16-sequence-source', 'P', [source({'format': 'aiaeao.cube.binding-context/7'}, 'mp-x', 'vpsequence')]))
    # P: VP-10 0.10.1 (O-*), 0.11.0 (S-*) and VP-11 (I-*)
    for c in _j('P2/visual-printer-cells-v1/fixtures/o01_o10_materialized.json')['cases']:
        if c['via'] != 'cli':
            continue
        out.append(views_chain(f"P-{c['id']}", source(c['context'], c['plan_id'], 'vpcells', predicate=c['predicate'], steps=c['steps']),
                               {'view': 'cube.cells', 'granularity': 'standard', 'rows': c['rows'], 'cols': c['cols'], 'hide_empty': c['hide_empty'],
                                'locale': c['locale'], 'axis_order': c['axis_order']}))
    for c in _j('P2/visual-printer-cells-v1/fixtures/s01_s16_materialized.json')['cases']:
        out.append(views_chain(f"P-{c['id']}", source(c['context'], None, 'vpcells', predicate=c['predicate'], statements=c['statements'],
                                                      projection=c['projection']),
                               {'view': 'cube.cells', 'granularity': 'standard', 'locale': c['locale'], 'axis_order': c['axis_order']}))
    for c in _j('P2/visual-printer-instances-v1/fixtures/i01_i34_materialized.json')['cases']:
        out.append(views_chain(f"P-{c['id']}", source(c['context'], None, 'vpinstances', statements=c['trace'], records=c['records']),
                               {'view': 'cube.instances', 'granularity': 'standard', 'locale': None if c['locale'] == 'en' else c['locale']},
                               live='host' if c['id'] == 'I-14' else None))
    # P: limits and arguments
    ctx, tr = big_instances()
    out.append(views_chain('P-LIMIT-svg', source(ctx, None, 'vpinstances', statements=tr), {'view': 'cube.instances', 'granularity': 'standard'},
                           check=False))
    i14 = {c['id']: c for c in _j('P2/visual-printer-instances-v1/fixtures/i01_i34_materialized.json')['cases']}['I-14']
    out.append(chain('P-ARG-plan-id', 'P', [source(i14['context'], 'mp-x', 'vpinstances', statements=i14['trace'])], live='host'))
    out.append(chain('P-ARG-view-option', 'P', [source(i14['context'], None, 'vpinstances', statements=i14['trace']),
                                                {'op': 'cube_plan_views', 'args': {'view': 'cube.instances', 'granularity': 'standard', 'rows': 'Y:referent'},
                                                 'from': SRC}]))
    return out


def run_chain(call, invoke):
    """invoke(op, args) -> (is_error, payload). Returns [(is_error, payload)] up to the first error."""
    res, prev = [], None
    for st in call['steps']:
        args = copy.deepcopy(st['args'])
        if 'from' in st:
            v = prev
            for k in st['from']['path']:
                v = v[k]
            args[st['from']['arg']] = copy.deepcopy(v)
        err, payload = invoke(st['op'], args)
        res.append((err, payload))
        if err:
            break
        prev = payload
    return res
