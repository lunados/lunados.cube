"""VP-10 0.11.0 input: a declared statement set (SS-1…SS-4), optionally aggregated by lunados.lib (PR-1…PR-6).

`from_statements` resolves the set against a binding-context/8, reads the chosen predicate (or the aggregation
record) and writes a self-contained matrix input. It checks resolution only; it never judges the statements
(D-3) and never recomputes an aggregation (Q-10). Coverage applies to plain sets only (Q-9).
"""
from __future__ import annotations
import re

from .common import (PROFILE_110, MATRIX_FORMAT, SET_FORMAT, RECORD_FORMAT, V8, need, sha_json)

AGG_METHOD = 'project.aggregate-relations/v1'
RESULT_SCHEMA = 'aiaeao.projection-result/v1'
HEX64 = re.compile(r'^[0-9a-f]{64}$')
MATRIX_KEYS = {'format', 'profile', 'set_id', 'predicate', 'home', 'axis', 'entries', 'coverage', 'aggregation', 'sources'}


def _set_shape(s):
    """SS-2 and the first step of SS-4: shape and unique IDs."""
    ok = (isinstance(s, dict) and s.get('format') == SET_FORMAT and isinstance(s.get('set_id'), str) and s['set_id']
          and isinstance(s.get('referents'), list) and s['referents'] and all(isinstance(r, str) and r for r in s['referents'])
          and isinstance(s.get('statements'), list))
    need(ok, 'VP10_STATEMENT_SET_INVALID', f'statement set must be {SET_FORMAT} with set_id, referents (non-empty) and statements')
    need(len(set(s['referents'])) == len(s['referents']), 'VP10_STATEMENT_SET_INVALID', 'a referent is listed twice')
    for st in s['statements']:
        need(isinstance(st, dict) and all(isinstance(st.get(k), str) and st[k] for k in ('statement_id', 'subject', 'predicate_id', 'object'))
             and ('label' not in st or isinstance(st['label'], str)), 'VP10_STATEMENT_SET_INVALID',
             'every statement needs statement_id, subject, predicate_id and object (strings); label is optional text')
    ids = [st['statement_id'] for st in s['statements']]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    need(not dup, 'VP10_STATEMENT_SET_INVALID', 'statement_id used twice: '+', '.join(dup))


def _resolve(s, ctx):
    """SS-1 and SS-4 in order: resolution → predicate and concepts → endpoints in referents."""
    refs = {r['ref']: r for r in ctx.get('referents', []) if isinstance(r, dict) and 'ref' in r}
    contracts = {p['predicate_id']: p for p in ctx.get('predicate_contracts', []) if isinstance(p, dict) and 'predicate_id' in p}
    missing = [x for x in s['referents'] if x not in refs]
    missing += [x for st in s['statements'] for x in (st['subject'], st['object']) if x not in refs and x not in missing]
    need(not missing, 'VP10_STATEMENT_REF_UNKNOWN', 'not a referent of the context: '+', '.join(missing))
    for st in s['statements']:
        p = contracts.get(st['predicate_id'])
        need(p is not None, 'VP10_STATEMENT_PREDICATE_INVALID', f"{st['statement_id']}: predicate {st['predicate_id']!r} is not in the context")
        need(refs[st['subject']].get('concept_id') in p.get('subject_concept_ids', [])
             and refs[st['object']].get('concept_id') in p.get('object_concept_ids', []), 'VP10_STATEMENT_PREDICATE_INVALID',
             f"{st['statement_id']}: {st['predicate_id']} does not allow {refs[st['subject']].get('concept_id')} → {refs[st['object']].get('concept_id')}")
    listed = set(s['referents'])
    outside = sorted({x for st in s['statements'] for x in (st['subject'], st['object']) if x not in listed})
    need(not outside, 'VP10_STATEMENT_SET_INVALID', 'statement endpoint not listed in referents: '+', '.join(outside))
    return refs, contracts


def _axis(ids, refs):
    homes = sorted({refs[i].get('home') for i in ids})
    need(len(homes) == 1 and homes[0] in ('Y', 'Z'), 'VP10_PAIR_INVALID',
         'a statement-set matrix draws one home on both axes, Y × Y or Z × Z (Q-2); got '+', '.join(str(h) for h in homes))
    return homes[0], [{'id': i, 'concept_id': refs[i].get('concept_id')} for i in ids]


def _record(rec, s, refs):
    """PR-3, PR-6: the Cube checks the record, it never recomputes the aggregation."""
    ok = isinstance(rec, dict) and rec.get('format') == RECORD_FORMAT and set(rec) == {'format', 'library_ref', 'call', 'result'}
    need(ok, 'VP10_PROJECTION_INVALID', f'projection must be a {RECORD_FORMAT} record with library_ref, call and result')
    lr, call, res = rec['library_ref'], rec['call'], rec['result']
    need(isinstance(lr, dict) and lr.get('library_id') == 'lunados.lib' and lr.get('entry_id') == 'project.aggregate-relations'
         and lr.get('revision') == 'v1' and isinstance(lr.get('sha256'), str) and HEX64.match(lr['sha256']),
         'VP10_PROJECTION_INVALID', 'library_ref must name lunados.lib project.aggregate-relations v1 with a SHA-256')
    need(isinstance(call, dict) and call.get('method_id') == AGG_METHOD and isinstance(res, dict) and res.get('method_id') == AGG_METHOD
         and res.get('schema') == RESULT_SCHEMA and res.get('status') == 'declared_unverified', 'VP10_PROJECTION_INVALID',
         f'record must carry a successful {RESULT_SCHEMA} of {AGG_METHOD}')
    need(res.get('input_set_sha256') == sha_json(s), 'VP10_PROJECTION_INVALID',
         'the aggregation was computed for another statement set (input_set_sha256 does not match)')
    try:
        par = res['parameters']; ok = all(isinstance(par[k], str) for k in ('strategy', 'source_predicate', 'derived_predicate', 'membership_predicate'))
        ok = ok and all(r in refs for r in res['referents'])
        ok = ok and all(st['subject'] in res['referents'] and st['object'] in res['referents'] for st in res['statements'])
        ok = ok and isinstance(res['loss'], dict) and isinstance(res['internal'], list) and isinstance(res['suppressed'], list)
    except (KeyError, TypeError):
        ok = False
    need(ok, 'VP10_PROJECTION_INVALID', 'aggregation result is malformed (parameters, referents, statements, loss)')
    return res


def from_statements(context, statement_set, predicate=None, projection=None):
    """Statement set (+ optional aggregation record) → matrix input of profile 0.11.0."""
    need(isinstance(context, dict) and context.get('format') == V8, 'VP10_ADAPTER_INPUT', 'context must be binding-context/8')
    _set_shape(statement_set)
    refs, contracts = _resolve(statement_set, context)
    raw = context.get('coverage_declarations')
    entry = lambda st, **kw: {'statement_id': st['statement_id'], 'row': st['subject'], 'col': st['object'],  # noqa: E731
                              'predicate_id': st['predicate_id'], **({'label': st['label']} if 'label' in st else {}), **kw}
    if projection is None:
        need(isinstance(predicate, str) and predicate, 'VP10_PREDICATE_INVALID', 'a predicate must be chosen (--predicate, D-3)')
        need(predicate in contracts, 'VP10_STATEMENT_PREDICATE_INVALID', f'predicate {predicate!r} is not in the context')
        home, axis = _axis(statement_set['referents'], refs)
        entries = [entry(st, origin='declared') for st in statement_set['statements'] if st['predicate_id'] == predicate]
        ids = {a['id'] for a in axis}
        decls, ignored = [], []
        for d in raw or []:
            did = d.get('declaration_id')
            if d.get('predicate_id') != predicate:
                ignored.append({'declaration_id': did, 'reason': 'other_predicate'}); continue
            if 'instance_ref' in d:
                ignored.append({'declaration_id': did, 'reason': 'instance_ref'}); continue
            if d.get('scope') == 'pair':
                if d.get('subject') in ids and d.get('object') in ids:
                    decls.append({'declaration_id': did, 'scope': 'pair', 'row': d['subject'], 'col': d['object']})
                else:
                    ignored.append({'declaration_id': did, 'reason': 'ref_unknown'})
            elif d.get('referent') in ids:
                decls.append({'declaration_id': did, 'scope': 'row', 'row': d['referent']} if d.get('direction') == 'outgoing'
                             else {'declaration_id': did, 'scope': 'column', 'col': d['referent']})
            else:
                ignored.append({'declaration_id': did, 'reason': 'ref_unknown'})
        coverage = {'declared': bool(raw), 'projected': False, 'declarations': decls, 'ignored': ignored}
        aggregation = None
    else:
        res = _record(projection, statement_set, refs)
        par = res['parameters']
        need(predicate in (None, par['derived_predicate']), 'VP10_STATEMENT_PREDICATE_INVALID',
             f"an aggregation view shows its derived_predicate {par['derived_predicate']!r} (DR-7)")
        predicate = par['derived_predicate']
        home, axis = _axis(res['referents'], refs)
        entries = [entry(st, origin=st['origin'], **({'derived_from': list(st['derived_from']), 'labels_dropped': st.get('labels_dropped', 0)}
                                                    if st['origin'] == 'derived' else {}))
                   for st in res['statements']]
        coverage = {'declared': bool(raw), 'projected': True, 'declarations': [],
                    'ignored': [{'declaration_id': d.get('declaration_id'), 'reason': 'not_projected'} for d in raw or []]}
        aggregation = {'method_id': AGG_METHOD, 'library_ref': projection['library_ref'], 'parameters': dict(par),
                       'input_set_sha256': res['input_set_sha256'], 'loss': dict(res['loss']), 'internal': list(res['internal']),
                       'suppressed': [dict(x) for x in res['suppressed']]}
    return {'format': MATRIX_FORMAT, 'profile': PROFILE_110, 'set_id': statement_set['set_id'], 'predicate': predicate, 'home': home,
            'axis': axis, 'entries': entries, 'coverage': coverage, 'aggregation': aggregation,
            'sources': {'context_id': context.get('context_id'), 'context_sha256': sha_json(context), 'statement_set_sha256': sha_json(statement_set)}}


def normalize_matrix(doc):
    need(isinstance(doc, dict) and doc.get('format') == MATRIX_FORMAT and doc.get('profile') == PROFILE_110 and set(doc) == MATRIX_KEYS,
         'VP10_SOURCE_INVALID', f'VP-10 0.11.0 reads {MATRIX_FORMAT} with profile {PROFILE_110} ('+', '.join(sorted(MATRIX_KEYS))+')')
    need(doc['home'] in ('Y', 'Z') and isinstance(doc['axis'], list) and doc['axis'], 'VP10_SOURCE_INVALID', 'matrix axis')
    ids = [a['id'] for a in doc['axis']]
    for e in doc['entries']:
        need(e['row'] in ids and e['col'] in ids and e['origin'] in ('declared', 'derived'), 'VP10_SOURCE_INVALID', 'matrix entry')
    c = doc['coverage']
    need(isinstance(c, dict) and set(c) == {'declared', 'projected', 'declarations', 'ignored'}, 'VP10_SOURCE_INVALID', 'coverage shape')
    return doc
