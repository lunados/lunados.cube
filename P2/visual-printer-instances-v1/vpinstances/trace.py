"""VP-11 input: a binding-context/9, a declared trace (statement set) and lunados.lib conformance records.

`from_trace` checks in the order of §9 TR-5 and writes a self-contained instances input. It resolves the trace against
the context (TR-1…TR-4) and checks each record against the context and the trace (RC-1…RC-3). It never judges the
trace and never recomputes a record (D-3, D-5, RC-4).
"""
from __future__ import annotations
import re

from .common import (PROFILE, INPUT_FORMAT, V9, SET_FORMAT, RECORD_FORMAT, METHOD, RESULT_SCHEMA, CHECKS, FIT, STATUS_OF, need, cjson, sha_json)

HEX64 = re.compile(r'^[0-9a-f]{64}$')
INPUT_KEYS = {'format', 'profile', 'set_id', 'context_id', 'gateways', 'tokens', 'statements', 'not_drawn', 'records', 'sources'}
RESULT_KEYS = {'activations', 'check', 'details', 'effectful_execution_authorized', 'excess', 'first_true', 'foreign', 'gateway', 'incoming',
               'instance', 'method_id', 'missing', 'missing_scope', 'outgoing', 'paths', 'runtime_authority', 'schema', 'status', 'taken', 'value'}
RESULT_REQUIRED = {'schema', 'method_id', 'check', 'gateway', 'instance', 'status', 'value', 'details', 'missing_scope', 'runtime_authority',
                   'effectful_execution_authorized'}
DETAIL_KEYS = {'activation', 'first_true', 'missing', 'paths', 'status', 'taken', 'value'}
ROLE_PRED = {'routing': 'routedTo', 'on_flow': 'onFlow'}


def _str(v):
    return isinstance(v, str) and bool(v)


def _strs(v):
    return isinstance(v, list) and all(_str(x) for x in v) and len(set(v)) == len(v)


def role_of(g):
    """IN-2: the role follows from the structure; None = drawn in the model field only."""
    n_in, n_out = len(g.get('incoming', [])), len(g.get('outgoing', []))
    if g.get('type') == 'exclusive':
        return 'xs' if n_out > 1 else 'xm' if n_out == 1 else None
    if g.get('type') == 'parallel':
        return 'ps' if n_in == 1 and n_out >= 1 else 'pj' if n_out == 1 and n_in >= 1 else None
    return None


def _context(ctx):
    need(isinstance(ctx, dict) and ctx.get('format') == V9 and isinstance(ctx.get('control_flow'), dict)
         and isinstance(ctx['control_flow'].get('gateways'), list), 'VP11_ADAPTER_INPUT', 'context must be binding-context/9 with control_flow (IN-1)')
    refs = {r['ref']: r for r in ctx.get('referents', []) if isinstance(r, dict) and _str(r.get('ref'))}
    contracts = {p['predicate_id']: p for p in ctx.get('predicate_contracts', []) if isinstance(p, dict) and _str(p.get('predicate_id'))}
    gws = []
    for g in ctx['control_flow']['gateways']:
        ok = isinstance(g, dict) and _str(g.get('gateway')) and _str(g.get('type')) and _strs(g.get('incoming', []))
        ok = ok and isinstance(g.get('outgoing'), list) and all(isinstance(o, dict) and _str(o.get('flow')) and _str(o.get('target')) for o in g['outgoing'])
        need(ok, 'VP11_ADAPTER_INPUT', 'control_flow gateways need gateway, type, incoming and outgoing {flow, target}')
        out = [{k: o[k] for k in ('flow', 'target', 'order', 'default') if k in o} for o in g['outgoing']]
        gws.append({'gateway': g['gateway'], 'type': g['type'], 'role': role_of(g), 'incoming': list(g.get('incoming', [])), 'outgoing': out})
    return refs, contracts, gws


def _trace(s, ctx, refs, contracts):
    """TR-1, TR-5: shape and context_id → resolution → predicates and concepts → endpoints in referents."""
    ok = (isinstance(s, dict) and s.get('format') == SET_FORMAT and _str(s.get('set_id')) and isinstance(s.get('referents'), list)
          and all(_str(r) for r in s['referents']) and isinstance(s.get('statements'), list))
    need(ok, 'VP11_TRACE_INVALID', f'trace must be {SET_FORMAT} with set_id, referents and statements')
    need(s.get('context_id') == ctx.get('context_id'), 'VP11_TRACE_INVALID', 'trace belongs to another context (context_id)')
    need(len(set(s['referents'])) == len(s['referents']), 'VP11_TRACE_INVALID', 'a referent is listed twice')
    for st in s['statements']:
        need(isinstance(st, dict) and all(_str(st.get(k)) for k in ('statement_id', 'subject', 'predicate_id', 'object'))
             and ('label' not in st or isinstance(st['label'], str)), 'VP11_TRACE_INVALID',
             'every statement needs statement_id, subject, predicate_id and object (strings); label is optional text')
    ids = [st['statement_id'] for st in s['statements']]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    need(not dup, 'VP11_TRACE_INVALID', 'statement_id used twice: '+', '.join(dup))
    missing = [x for x in s['referents'] if x not in refs]
    missing += [x for st in s['statements'] for x in (st['subject'], st['object']) if x not in refs and x not in missing]
    need(not missing, 'VP11_TRACE_REF_UNKNOWN', 'not a referent of the context: '+', '.join(missing))
    for st in s['statements']:
        p = contracts.get(st['predicate_id'])
        need(p is not None, 'VP11_TRACE_PREDICATE_INVALID', f"{st['statement_id']}: predicate {st['predicate_id']!r} is not in the context")
        need(refs[st['subject']].get('concept_id') in p.get('subject_concept_ids', [])
             and refs[st['object']].get('concept_id') in p.get('object_concept_ids', []), 'VP11_TRACE_PREDICATE_INVALID',
             f"{st['statement_id']}: {st['predicate_id']} does not allow {refs[st['subject']].get('concept_id')} → {refs[st['object']].get('concept_id')}")
    listed = set(s['referents'])
    outside = sorted({x for st in s['statements'] for x in (st['subject'], st['object']) if x not in listed})
    need(not outside, 'VP11_TRACE_INVALID', 'statement endpoint not listed in referents: '+', '.join(outside))


def _tokens(s, refs, contracts):
    """TR-2…TR-4: trace statements, tokens in referents order, statements not drawn."""
    stmts, not_drawn = [], []
    for st in s['statements']:
        role = contracts[st['predicate_id']].get('control_flow_role')
        if role in ROLE_PRED:
            stmts.append({'statement_id': st['statement_id'], 'subject': st['subject'], 'predicate_id': st['predicate_id'], 'object': st['object'],
                          'role': role, **({'label': st['label']} if 'label' in st else {})})
        else:
            not_drawn.append(st['statement_id'])
    subjects = {st['subject'] for st in stmts}
    tokens = []
    for r in s['referents']:
        ref = refs[r]
        if 'instance_ref' in ref or 'at_gateway' in ref or r in subjects:
            tokens.append({'token': r, 'instance': ref.get('instance_ref'), 'at': ref.get('at_gateway')})
    return tokens, stmts, not_drawn


def derived_trace(tokens, stmts):
    """§2.1: the LIB trace rows that this context and trace stand for (without condition outcomes)."""
    rows = []
    for t in tokens:
        base = {'token': t['token'], **({'instance': t['instance']} if t['instance'] else {}), **({'at': t['at']} if t['at'] else {})}
        mine = [st for st in stmts if st['subject'] == t['token']]
        for st in mine:
            rows.append({**base, ('routed_to' if st['role'] == 'routing' else 'on_flow'): st['object']})
        if not mine:
            rows.append(base)
    return rows


def derived_coverage(ctx, contracts):
    out = []
    for d in ctx.get('coverage_declarations') or []:
        role = contracts.get(d.get('predicate_id'), {}).get('control_flow_role') if isinstance(d, dict) else None
        if isinstance(d, dict) and d.get('scope') == 'referent_relation_direction' and role in ROLE_PRED:
            out.append({**{k: d[k] for k in ('declaration_id', 'scope', 'referent', 'direction', 'instance_ref') if k in d}, 'predicate_id': ROLE_PRED[role]})
    return out


def _as_set(rows, drop=()):
    return sorted({cjson({k: v for k, v in r.items() if k not in drop}) for r in rows}) if isinstance(rows, list) and all(isinstance(r, dict) for r in rows) else None


def _result_shape(res):
    """RC-1: the result schema of analyze.trace-conformance/v1 (fields, enums, status/value pairs), checked by hand."""
    if not (isinstance(res, dict) and RESULT_REQUIRED <= set(res) <= RESULT_KEYS):
        return False
    ok = (res['schema'] == RESULT_SCHEMA and res['method_id'] == METHOD and res['check'] in CHECKS and _str(res['gateway']) and _str(res['instance'])
          and res['value'] in STATUS_OF and res['status'] == STATUS_OF[res['value']] and res['runtime_authority'] == 'not-evaluated'
          and res['effectful_execution_authorized'] is False and isinstance(res['details'], list))
    for k in ('missing', 'foreign', 'paths'):
        ok = ok and (k not in res or _strs(res[k]))
    for k in ('taken', 'first_true'):
        ok = ok and (k not in res or _str(res[k]))
    for k in ('activations', 'incoming', 'outgoing'):
        ok = ok and (k not in res or (isinstance(res[k], int) and not isinstance(res[k], bool) and res[k] >= 0))
    ok = ok and ('excess' not in res or (isinstance(res['excess'], dict)
                                         and all(isinstance(v, int) and not isinstance(v, bool) and v >= 1 for v in res['excess'].values())))
    for d in res['details'] if ok else []:
        ok = ok and isinstance(d, dict) and {'activation', 'status', 'value'} <= set(d) <= DETAIL_KEYS and _str(d['activation'])
        ok = ok and d.get('value') in STATUS_OF and d['status'] == STATUS_OF[d['value']]
        ok = ok and all(k not in d or _strs(d[k]) for k in ('missing', 'paths')) and all(k not in d or _str(d[k]) for k in ('taken', 'first_true'))
    ms = res.get('missing_scope') if ok else None
    if ok and ms is not None:
        decl = ms.get('declarations') if isinstance(ms, dict) else None
        ok = (isinstance(ms, dict) and set(ms) == {'needs', 'declarations'} and ms['needs'] == 'all' and isinstance(decl, list) and decl
              and all(isinstance(x, dict) and set(x) == {'scope', 'referent', 'predicate_id', 'direction', 'instance_ref'}
                      and x['scope'] == 'referent_relation_direction' and x['predicate_id'] in ('routedTo', 'onFlow')
                      and x['direction'] in ('incoming', 'outgoing') and _str(x['referent']) and _str(x['instance_ref']) for x in decl))
    return bool(ok)


def _record(rec, ctx, gws, trace_rows, coverage):
    """RC-1 → RC-3 (fit) → RC-2, per record."""
    ok = isinstance(rec, dict) and rec.get('format') == RECORD_FORMAT and set(rec) == {'format', 'library_ref', 'call', 'result'}
    need(ok, 'VP11_RECORD_INVALID', f'record must be a {RECORD_FORMAT} with library_ref, call and result')
    lr, call, res = rec['library_ref'], rec['call'], rec['result']
    need(isinstance(lr, dict) and set(lr) == {'library_id', 'entry_id', 'revision', 'sha256'} and lr['library_id'] == 'lunados.lib'
         and lr['entry_id'] == 'analyze.trace-conformance' and lr['revision'] == 1 and isinstance(lr['sha256'], str) and HEX64.match(lr['sha256']),
         'VP11_RECORD_INVALID', 'library_ref must name lunados.lib analyze.trace-conformance revision 1 with a SHA-256')
    inp = call.get('inputs') if isinstance(call, dict) else None
    need(isinstance(call, dict) and call.get('method_id') == METHOD and isinstance(inp, dict)
         and {'control_flow', 'trace', 'coverage', 'claim'} <= set(inp), 'VP11_RECORD_INVALID', f'call must be a {METHOD} call with its four inputs')
    need(_result_shape(res), 'VP11_RECORD_INVALID', f'result is not a valid {RESULT_SCHEMA} (fields, values or status)')
    claim = inp['claim']
    need(isinstance(claim, dict) and set(claim) == {'check', 'gateway', 'instance'}
         and (claim['check'], claim['gateway'], claim['instance']) == (res['check'], res['gateway'], res['instance']),
         'VP11_RECORD_INVALID', 'claim of the call and check, gateway, instance of the result differ')
    role = {g['gateway']: g['role'] for g in gws}.get(res['gateway'])
    need(role is not None and FIT[res['check']] == role, 'VP11_RECORD_INVALID',
         f"check {res['check']} does not fit gateway {res['gateway']} (RC-3)")
    need(cjson(inp['control_flow']) == cjson(ctx['control_flow']), 'VP11_RECORD_MISMATCH', 'the record was computed for another control flow (RC-2)')
    need(_as_set(inp['trace'], drop=('conditions',)) == _as_set(trace_rows), 'VP11_RECORD_MISMATCH', 'the record was computed for another trace (RC-2)')
    need(_as_set(inp['coverage'], drop=('source',)) == _as_set(coverage), 'VP11_RECORD_MISMATCH', 'the record was computed for other coverage (RC-2)')
    return {'library_ref': dict(lr), 'claim': dict(claim), 'result': res}


def from_trace(context, trace, records=None):
    """Context, trace and records → instances input of profile 0.12.0."""
    refs, contracts, gws = _context(context)
    _trace(trace, context, refs, contracts)
    tokens, stmts, not_drawn = _tokens(trace, refs, contracts)
    rows, coverage = derived_trace(tokens, stmts), derived_coverage(context, contracts)
    need(records is None or isinstance(records, list), 'VP11_RECORD_INVALID', 'records must be a list')
    recs = [_record(r, context, gws, rows, coverage) for r in records or []]
    claims = [(r['claim']['check'], r['claim']['gateway'], r['claim']['instance']) for r in recs]
    dup = sorted({' · '.join(c) for c in claims if claims.count(c) > 1})
    need(not dup, 'VP11_RECORD_DUPLICATE', 'two records for one claim: '+', '.join(dup))
    return {'format': INPUT_FORMAT, 'profile': PROFILE, 'set_id': trace['set_id'], 'context_id': context.get('context_id'), 'gateways': gws,
            'tokens': tokens, 'statements': stmts, 'not_drawn': not_drawn, 'records': recs,
            'sources': {'context_sha256': sha_json(context), 'trace_sha256': sha_json(trace), 'records_sha256': [sha_json(r) for r in records or []]}}


def normalize(doc):
    need(isinstance(doc, dict) and doc.get('format') == INPUT_FORMAT and doc.get('profile') == PROFILE and set(doc) == INPUT_KEYS,
         'VP11_SOURCE_INVALID', f'VP-11 reads {INPUT_FORMAT} with profile {PROFILE} ('+', '.join(sorted(INPUT_KEYS))+')')
    need(all(isinstance(g, dict) and g.get('role') in (None, 'xs', 'xm', 'ps', 'pj') for g in doc['gateways'])
         and all(isinstance(t, dict) and _str(t.get('token')) for t in doc['tokens']) and isinstance(doc['records'], list),
         'VP11_SOURCE_INVALID', 'instances input is malformed')
    return doc
