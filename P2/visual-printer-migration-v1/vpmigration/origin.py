"""VP-07.6 origin declarations and post-render flow marks (display only)."""
from __future__ import annotations

import copy
from xml.etree import ElementTree as ET

from .adapter import from_plan
from .common import (P076, V76UP, METHOD_PROFILE_REF, HEX64, KEY, NS, STROKE, MUTED,
                     VP07Error, need, clean, sha_bytes, sha_json, style_line,
                     add, rect, line, text, no_active_content)

SET1 = 'aiaeao.cube.statement-set/1'
SET2 = 'aiaeao.cube.statement-set/2'
RECORD = 'aiaeao.cube.projection-record/1'
METHOD = 'project.aggregate-relations/v1'
HEADER = 'CUBE.FLOW · FIXTURE ASSERTIONS · no inferred chronology or causality'
OLD_HEADERS = ('CUBE.FLOW · DECLARED RELATIONSHIPS · no inferred chronology or causality',
               'CUBE.FLOW · DEKLARIERTE BEZIEHUNGEN · keine erschlossene Chronologie oder Kausalität')
LEGENDS = {
    'en': [('solid', 'solid · declared'), ('dashed', 'dashed · derived from sources'),
           ('dotted', 'dotted · origin unknown or not bound')],
    'de': [('solid', 'durchgezogen · deklariert'), ('dashed', 'gestrichelt · abgeleitet aus Quellen'),
           ('dotted', 'gepunktet · unbekannt / ungebunden')],
}


def _set_check(ctx, s):
    need(isinstance(ctx, dict) and ctx.get('format') == 'aiaeao.cube.binding-context/10',
         'VP07_ADAPTER_INPUT', 'statement path needs binding-context/10')
    need(isinstance(s, dict) and s.get('format') in (SET1, SET2) and
         clean(s.get('set_id'), 100) and s.get('context_id') == ctx.get('context_id') and
         isinstance(s.get('referents'), list) and s['referents'] and
         all(isinstance(x, str) and x for x in s['referents']) and
         len(s['referents']) == len(set(s['referents'])) and isinstance(s.get('statements'), list),
         'VP07_STATEMENT_SET_INVALID', 'statement set has invalid shape or context_id')
    refs = {r['ref']: r for r in ctx.get('referents', []) if isinstance(r, dict) and isinstance(r.get('ref'), str)}
    contracts = {p['predicate_id']: p for p in ctx.get('predicate_contracts', []) if isinstance(p, dict) and isinstance(p.get('predicate_id'), str)}
    missing = [x for x in s['referents'] if x not in refs]
    ids = set()
    for st in s['statements']:
        need(isinstance(st, dict) and all(isinstance(st.get(k), str) and st[k] for k in
             ('statement_id', 'subject', 'predicate_id', 'object')) and
             ('label' not in st or isinstance(st['label'], str)),
             'VP07_STATEMENT_SET_INVALID', 'statement needs ID, subject, predicate and object')
        sid = st['statement_id']
        need(sid not in ids, 'VP07_STATEMENT_SET_INVALID', 'duplicate statement_id '+sid)
        ids.add(sid)
        missing += [x for x in (st['subject'], st['object']) if x not in refs and x not in missing]
        need(st['subject'] in s['referents'] and st['object'] in s['referents'],
             'VP07_STATEMENT_SET_INVALID', 'statement endpoint not listed in referents')
        if s['format'] == SET2:
            need('origin' not in st or st['origin'] in ('declared', 'derived', 'unknown'),
                 'VP07_STATEMENT_SET_INVALID', 'invalid statement origin')
            need('basis' not in st or isinstance(st['basis'], str),
                 'VP07_STATEMENT_SET_INVALID', 'invalid statement basis')
        else:
            need(not set(st) & {'origin', 'basis'}, 'VP07_STATEMENT_SET_INVALID',
                 'origin and basis need statement-set/2')
    need(not missing, 'VP07_STATEMENT_REF_UNKNOWN', 'referent is not in context: '+', '.join(missing))
    for st in s['statements']:
        p = contracts.get(st['predicate_id'])
        need(p is not None and refs[st['subject']].get('concept_id') in p.get('subject_concept_ids', [])
             and refs[st['object']].get('concept_id') in p.get('object_concept_ids', []),
             'VP07_STATEMENT_PREDICATE_INVALID', 'unknown or mistyped predicate '+st['predicate_id'])
    return refs


def _record(rec, s, refs):
    need(isinstance(rec, dict) and rec.get('format') == RECORD and
         set(rec) == {'format', 'library_ref', 'call', 'result'},
         'VP07_ORIGIN_RECORD_INVALID', 'projection record shape is invalid')
    lr, call, res = rec['library_ref'], rec['call'], rec['result']
    need(isinstance(lr, dict) and lr.get('library_id') == 'lunados.lib' and
         lr.get('entry_id') == 'project.aggregate-relations' and lr.get('revision') == 'v1' and
         isinstance(lr.get('sha256'), str) and HEX64.fullmatch(lr['sha256']) and
         isinstance(call, dict) and call.get('method_id') == METHOD and isinstance(res, dict) and
         res.get('method_id') == METHOD and res.get('schema') == 'aiaeao.projection-result/v1' and
         res.get('status') == 'declared_unverified' and res.get('input_set_sha256') == sha_json(s),
         'VP07_ORIGIN_RECORD_INVALID', 'projection record does not match the statement set')
    try:
        par = res['parameters']
        ok = all(isinstance(par[k], str) for k in ('strategy', 'source_predicate', 'derived_predicate', 'membership_predicate'))
        ok = ok and isinstance(res['referents'], list) and all(r in refs for r in res['referents'])
        ok = ok and isinstance(res['statements'], list) and isinstance(res['loss'], dict) and isinstance(res['internal'], list) and isinstance(res['suppressed'], list)
        ok = ok and all(isinstance(st, dict) and all(isinstance(st.get(k), str) and st[k] for k in
                        ('statement_id', 'subject', 'predicate_id', 'object')) and
                        st['subject'] in res['referents'] and st['object'] in res['referents'] and
                        st.get('origin') == 'derived' and isinstance(st.get('derived_from'), list) and st['derived_from'] and
                        all(isinstance(x, str) and x for x in st['derived_from']) for st in res['statements'])
    except (KeyError, TypeError):
        ok = False
    need(ok, 'VP07_ORIGIN_RECORD_INVALID', 'projection result is malformed')
    return res['statements']


def _basis(origin, basis, bases, records):
    if origin in ('declared', 'unknown'):
        return origin, [], None
    if origin != 'derived':
        return 'unbound', [], None
    b = bases.get(basis) if isinstance(basis, str) else None
    if b is None:
        return 'unbound', [], 'VP07_ORIGIN_UNRESOLVED'
    if b['kind'] == 'statements':
        return 'derived', list(b['statement_ids']), None
    for rec in records:
        if sha_json(rec) == b['record_sha256']:
            for st in rec['result']['statements']:
                if st['statement_id'] == b['statement_id']:
                    return 'derived', list(st['derived_from']), None
    return 'unbound', [], 'VP07_ORIGIN_UNRESOLVED'


def _ledger(st, ref, bases, records, direct=False, bound=True):
    if direct:
        origin, ids, warning = 'derived', list(st['derived_from']), None
    elif not bound:
        origin, ids, warning = 'unbound', [], None
    else:
        origin, ids, warning = _basis(st.get('origin'), st.get('basis'), bases, records)
    return {'cell_id': st['statement_id'] if 'statement_id' in st else st['dependency_id'],
            'declaration_ref': ref, 'predicate_id': st['predicate_id'],
            'origin': origin, 'style': {'declared': 'solid', 'derived': 'dashed',
                                       'unknown': 'dotted', 'unbound': 'dotted'}[origin],
            'source_ids': ids, **({'warning': warning} if warning else {})}


def from_statements(context, statements, records=None, origin_lines=False, profile=P076):
    need(profile in V76UP, 'VP07_ADAPTER_INPUT', 'statement path requires profile '+' or '.join(V76UP))
    refs = _set_check(context, statements)
    need(records is None or isinstance(records, list), 'VP07_ORIGIN_RECORD_INVALID', 'records must be an array')
    records = records or []
    selected = []
    for rec in records:
        selected += [(st, True) for st in _record(rec, statements, refs)]
    if not records:
        selected = [(st, False) for st in statements['statements']]
    need(selected, 'VP07_STATEMENT_SET_INVALID', 'statement set yields no edges')
    ids = [st['statement_id'] for st, _ in selected]
    need(len(ids) == len(set(ids)), 'VP07_STATEMENT_SET_INVALID', 'duplicate edge statement_id')
    for st, _ in selected:
        need(st['subject'] in refs and st['object'] in refs, 'VP07_STATEMENT_REF_UNKNOWN', 'projection endpoint not in context')
    # Use the frozen from-plan mapping and panel geometry with one descriptive
    # synthetic phase. No migration plan or dependency is inferred in the source.
    synthetic = copy.deepcopy(context)
    synthetic['format'] = 'aiaeao.cube.binding-context/7'
    synthetic['method_profile_refs'] = [METHOD_PROFILE_REF]
    synthetic['migration_plans'] = [{'plan_id': statements['set_id'],
        'phases': [{'phase_id': 'input', 'role': 'current'},
                   {'phase_id': 'statements', 'role': 'target'}], 'transitions': [],
        'dependencies': [{'dependency_id': st['statement_id'], 'subject': st['subject'],
                          'object': st['object'], 'predicate_id': st['predicate_id'],
                          'holds_in': ['statements']} for st, _ in selected]}]
    shown = list(dict.fromkeys(x for st, _ in selected for x in (st['subject'], st['object'])))
    labels = {'format': 'aiaeao.cube.vp07-label-map/1', 'labels':
              {ref: {'id': 'n'+str(i+1), 'label': ref[:60]} for i, ref in enumerate(shown)}}
    src, mapping = from_plan(synthetic, statements['set_id'], labels=labels, profile=profile)
    src['title'] = statements['set_id']
    src['source_kind'] = 'statement_set'
    src['plan_id'] = None
    src['statement_set_id'] = statements['set_id']
    for i, cell in enumerate(src['cells']):
        cell['declaration_ref'] = f"decl:{context['context_id']}#/statement_sets/{statements['set_id']}/statements/{i}"
        need(len(cell['declaration_ref']) <= 140, 'VP07_ADAPTER_MAPPING', 'statement declaration_ref exceeds 140 chars')
    src['source_context_sha256'] = sha_json(context)
    src['origin_lines'] = bool(origin_lines)
    opted = {p['predicate_id'] for p in context.get('predicate_contracts', [])
             if p.get('origin_binding') == 'required' and p.get('scope') == context.get('scope_ref')}
    src['origin_ledger'] = [_ledger(st, src['cells'][i]['declaration_ref'],
                            {b['basis_id']: b for b in context.get('origin_bases', [])}, records, direct,
                            bound=st['predicate_id'] in opted)
                            for i, (st, direct) in enumerate(selected)]
    src['statement_set_sha256'] = sha_json(statements)
    _semantics_bindings(src)
    mapping['source_context_sha256'] = src['source_context_sha256']
    mapping['statement_set_sha256'] = src['statement_set_sha256']
    mapping['source_kind'] = 'statement_set'
    mapping['plan_id'] = None
    mapping['statements'] = [{'statement_id': c['id'], 'declaration_ref': c['declaration_ref']}
                             for c in src['cells']]
    mapping.pop('dependencies', None)
    mapping['p1_validation_performed'] = False
    return src, mapping


def from_origin_plan(context, plan_id, **options):
    origin_lines = bool(options.pop('origin_lines', False))
    profile = options.pop('profile', None) or P076
    need(profile in V76UP, 'VP07_ADAPTER_INPUT', 'origin plan path requires profile '+' or '.join(V76UP))
    src, mapping = from_plan(context, plan_id, profile=profile, **options)
    bases = {b['basis_id']: b for b in context.get('origin_bases', [])}
    opted = {p['predicate_id'] for p in context.get('predicate_contracts', [])
             if p.get('origin_binding') == 'required' and p.get('scope') == context.get('scope_ref')}
    deps = next(p['dependencies'] for p in context['migration_plans'] if p['plan_id'] == plan_id)
    byid = {d['dependency_id']: d for d in deps}
    src['origin_lines'] = origin_lines
    src['source_kind'] = 'migration_plan'
    src['origin_ledger'] = [_ledger(byid[c['id']], c['declaration_ref'], bases, [],
                                    bound=byid[c['id']]['predicate_id'] in opted) for c in src['cells']]
    _semantics_bindings(src)
    return src, mapping


def _semantics_bindings(src):
    for c in src['cells']:
        src['facet_bindings'].append({'lens': 'cube.lens.semantics', 'target_kind': 'cell',
            'target_id': c['id'], 'declaration_ref': c['declaration_ref'],
            'note': c['predicate_id'][:80], 'basis': 'declared_unverified'})


def display_entry(entry, locale='en'):
    origin, ids = entry['origin'], entry['source_ids']
    if origin == 'derived':
        short = ', '.join(ids[:3]) + (f' +{len(ids)-3}' if len(ids) > 3 else '')
        suffix = ('abgeleitet aus ' if locale == 'de' else 'derived from ') + short
    elif locale == 'de':
        suffix = {'declared': 'deklariert', 'unknown': 'Herkunft unbekannt',
                  'unbound': 'Herkunft nicht gebunden'}[origin]
    else:
        suffix = {'declared': 'declared', 'unknown': 'origin unknown',
                  'unbound': 'origin not bound'}[origin]
    return {**entry, 'text': '· '+suffix}


def post_flow(svg, entries, locale='en', active=True):
    root = ET.fromstring(svg)
    headers = [t for t in root.iter(f'{{{NS}}}text') if t.text in OLD_HEADERS]
    need(len(headers) == 1, 'VP07_AUDIT', '0.7.6 flow header not found exactly once', 'audit')
    headers[0].text = HEADER
    ledger = [display_entry(e, locale) for e in entries]
    if active:
        byref = {e['declaration_ref']: e for e in ledger}
        seen = set()
        for g in root.iter(f'{{{NS}}}g'):
            if not g.get('data-edge-id'):
                continue
            ref = g.get('data-declaration-ref')
            need(ref in byref, 'VP07_AUDIT', 'drawn edge has no origin ledger entry', 'audit')
            e = byref[ref]; seen.add(ref)
            g.set('data-vp07-origin', e['origin'])
            g.set('data-vp07-edge-style', e['style'])
            for el in g.findall(f'{{{NS}}}line'):
                style_line(el, e['style'])
            label = g.find(f'{{{NS}}}text')
            need(label is not None, 'VP07_AUDIT', 'drawn edge has no text label', 'audit')
            label.text = e['predicate_id']+' '+e['text']
            title = g.find(f'{{{NS}}}title')
            if title is not None:
                title.text = (title.text or '')+' | '+e['text']+' | sources: '+', '.join(e['source_ids'])
        need(seen == set(byref), 'VP07_AUDIT', 'origin ledger does not match drawn edges', 'audit')
        h0 = int(float(root.get('height')))
        extra = 161
        root.set('height', str(h0+extra)); root.set('viewBox', f'0 0 1200 {h0+extra}')
        for ch in root:
            if ch.tag == f'{{{NS}}}rect' and ch.get('x') == '0' and ch.get('width') == '1200':
                ch.set('height', str(h0+extra)); break
        lg = add(root, 'g', **{'data-vp07-origin-legend': 'display-only', 'aria-label': 'Origin line legend'})
        rect(lg, 48, h0+8, 1104, extra-16, '#94A3B8', '#F8FAFC', 9)
        text(lg, 65, h0+31, 'ORIGIN · declared assertions · no truth or authority claim', 13, '#334155', 'bold')
        for i, (style, label) in enumerate(LEGENDS[locale]):
            y = h0+57+i*23
            sample = line(lg, 70, y-4, 130, y-4, STROKE)
            style_line(sample, style)
            text(lg, 142, y, label, 12, '#334155')
        separate = ('Herkunft unbekannt', 'Herkunft nicht gebunden') if locale == 'de' else (
            'origin unknown', 'origin not bound')
        text(lg, 142, h0+130, separate[0], 11, MUTED)
        text(lg, 440, h0+130, separate[1], 11, MUTED)
    out = ET.tostring(root, encoding='utf-8', xml_declaration=True, short_empty_elements=True)+b'\n'
    need(no_active_content(ET.fromstring(out)), 'VP07_AUDIT', 'origin SVG contains active content', 'audit')
    return out, ledger
