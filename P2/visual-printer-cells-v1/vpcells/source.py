"""VP-10 input: the unchanged VP-09.2 axes input plus a `coverage` block from a binding-context/8 (D-2, D-4, D-7)."""
from __future__ import annotations
import copy

from vpaxes.source import from_plan as _axes_from_plan, _items
from .common import (INPUT_FORMAT, PROFILE, BASE_PROFILE, CTX_FORMATS, V8, SCOPES, need)

V8_TOP = ('coverage_declarations', 'population_rules')


def project(context):
    """/8 → the view VP-07/VP-09 read: P1.12 fields removed; /7 without a method catalog reads as /6 (nothing to transcribe)."""
    view = copy.deepcopy(context)
    if view['format'] == V8:
        view['format'] = 'aiaeao.cube.binding-context/7'
        for k in V8_TOP:
            view.pop(k, None)
        for r in view.get('referents', []) if isinstance(view.get('referents'), list) else []:
            if isinstance(r, dict):
                r.pop('instance_ref', None)
        for p in view.get('predicate_contracts', []) if isinstance(view.get('predicate_contracts'), list) else []:
            if isinstance(p, dict):
                p.pop('requires_same_instance', None)
    if view['format'].endswith('/7') and 'method_profile_refs' not in view:
        view['format'] = 'aiaeao.cube.binding-context/6'
    return view


def from_plan(context, plan_id, predicate, tracks=None, track=None, labels=None, steps=None, subjects=None, layers=None):
    need(isinstance(context, dict) and context.get('format') in CTX_FORMATS, 'VP10_ADAPTER_INPUT',
         'context must be binding-context /5, /6, /7 or /8')
    need(isinstance(predicate, str) and predicate, 'VP10_PREDICATE_INVALID', 'a predicate must be chosen (--predicate, D-3)')
    axes, mapping = _axes_from_plan(project(context), plan_id, tracks, track, labels, steps, subjects, layers, profile=BASE_PROFILE)
    ids = {r['ref']: r['id'] for r in mapping['referents']}
    items = _items(axes['source'])
    plan = next(p for p in context['migration_plans'] if isinstance(p, dict) and p.get('plan_id') == plan_id)
    deps = [d for d in plan.get('dependencies', []) if d.get('predicate_id') == predicate]
    need(deps, 'VP10_PREDICATE_INVALID', f'no dependency of plan {plan_id!r} uses predicate {predicate!r}')
    yy = lambda i: i is not None and items.get(i, {}).get('home') == 'Y'  # noqa: E731
    pairs = []
    for d in deps:                                           # D-4: the full plan, every phase, not the slice
        s, o = ids.get(d['subject']), ids.get(d['object'])
        if yy(s) and yy(o):
            pairs.append({'row': s, 'col': o, 'dependency_id': d['dependency_id']})
    raw = context.get('coverage_declarations') if context['format'] == V8 else None
    decls, ignored = [], []
    for d in raw or []:
        did = d.get('declaration_id')
        if d.get('predicate_id') != predicate:
            ignored.append({'declaration_id': did, 'reason': 'other_predicate'}); continue
        if 'instance_ref' in d:                              # D-7
            ignored.append({'declaration_id': did, 'reason': 'instance_ref'}); continue
        if d.get('scope') == 'pair':
            s, o = ids.get(d.get('subject')), ids.get(d.get('object'))
            if not (yy(s) and yy(o)):
                ignored.append({'declaration_id': did, 'reason': 'ref_unknown'}); continue
            decls.append({'declaration_id': did, 'scope': 'pair', 'row': s, 'col': o})
        else:
            r = ids.get(d.get('referent'))
            if not yy(r):
                ignored.append({'declaration_id': did, 'reason': 'ref_unknown'}); continue
            if d.get('direction') == 'outgoing':
                decls.append({'declaration_id': did, 'scope': 'row', 'row': r})
            else:
                decls.append({'declaration_id': did, 'scope': 'column', 'col': r})
    coverage = {'predicate': predicate, 'declared': bool(raw), 'declarations': decls, 'ignored': ignored, 'plan_pairs': pairs}
    return {'format': INPUT_FORMAT, 'profile': PROFILE, 'axes': axes, 'coverage': coverage}, mapping


def normalize(doc):
    need(isinstance(doc, dict) and doc.get('format') == INPUT_FORMAT and doc.get('profile') == PROFILE
         and set(doc) == {'format', 'profile', 'axes', 'coverage'}, 'VP10_SOURCE_INVALID',
         f'VP-10 reads {INPUT_FORMAT} with profile {PROFILE} (format, profile, axes, coverage)')
    c = doc['coverage']
    need(isinstance(c, dict) and set(c) == {'predicate', 'declared', 'declarations', 'ignored', 'plan_pairs'}, 'VP10_SOURCE_INVALID', 'coverage shape')
    need(isinstance(doc['axes'], dict) and doc['axes'].get('profile') == BASE_PROFILE, 'VP10_SOURCE_INVALID', f'axes input must be {BASE_PROFILE}')
    for d in c['declarations']:
        need(isinstance(d, dict) and d.get('scope') in SCOPES, 'VP10_SOURCE_INVALID', 'declaration scope')
    for x in c['ignored']:
        need(isinstance(x, dict) and x.get('reason') in ('other_predicate', 'instance_ref', 'ref_unknown'), 'VP10_SOURCE_INVALID', 'ignored reason')
    return doc
