"""VP-09 input (AQ-1): a VP-07 migration source (0.7.1/0.7.2) or an axes input with method bindings."""
from __future__ import annotations
import copy

from vpmigration.source import validate_source as _validate_vp07
from vpmigration.adapter import from_plan as _from_plan
from .common import PROFILE, INPUT_FORMAT, P071, P072, SEMREF, CATALOG_ORDER, need, via07

CTX_FORMATS = ('aiaeao.cube.binding-context/5', 'aiaeao.cube.binding-context/6', 'aiaeao.cube.binding-context/7')


def normalize(doc):
    """Return (source, bindings) for either input form; validate the VP-07 source unchanged."""
    need(isinstance(doc, dict), 'VP09_SOURCE_INVALID', 'input must be an object')
    if doc.get('format') == INPUT_FORMAT:
        need(set(doc) == {'format', 'profile', 'source', 'method_bindings'} and doc['profile'] == PROFILE, 'VP09_SOURCE_INVALID',
             'axes input needs format, profile '+PROFILE+', source, method_bindings')
        src, bindings = doc['source'], doc['method_bindings']
    else:
        src, bindings = doc, []
    need(isinstance(src, dict) and src.get('profile') in (P071, P072), 'VP09_SOURCE_INVALID',
         'VP-09 reads VP-07 migration sources 0.7.1 or 0.7.2 (AQ-1)')
    v = via07(_validate_vp07, src, code='VP09_SOURCE_INVALID')
    items = {}
    for it in src['rows']+src['objects']:
        if it['id'] in items:
            continue
        m = SEMREF.match(it.get('semantic_ref', '') or '')
        need(m is not None, 'VP09_SOURCE_INVALID', 'item '+repr(it['id'])+' has no declared home (semantic_ref from from-plan, AX-2)')
        items[it['id']] = {'id': it['id'], 'label': it['label'], 'home': m.group(1), 'kind': m.group(2), 'anchor_id': it['anchor_id']}
    need(isinstance(bindings, list), 'VP09_SOURCE_INVALID', 'method_bindings must be an array')
    cells = {c['id'] for c in src['cells']}
    trs = {t['id'] for t in src['transitions']}
    for b in bindings:
        need(isinstance(b, dict) and set(b) == {'owner_kind', 'owner', 'method_id', 'arguments'}, 'VP09_SOURCE_INVALID', 'binding shape')
        need(b['owner_kind'] in ('transition', 'dependency'), 'VP09_SOURCE_INVALID', 'binding owner_kind')
        need(b['owner'] in (trs if b['owner_kind'] == 'transition' else cells), 'VP09_SOURCE_INVALID',
             'binding owner '+repr(b['owner'])+' not in source')
        need(isinstance(b['method_id'], str) and b['method_id'], 'VP09_SOURCE_INVALID', 'binding method_id')
        need(isinstance(b['arguments'], dict) and all(x in items for x in b['arguments'].values()), 'VP09_SOURCE_INVALID',
             'binding arguments must name source items')
    return src, bindings, items, v


def from_plan(context, plan_id, tracks=None, track=None, labels=None, steps=None, subjects=None, layers=None):
    """AQ-1: run the unchanged VP-07 adapter; transcribe P1.11 bindings (refs → display IDs) into an axes input."""
    need(isinstance(context, dict) and context.get('format') in CTX_FORMATS, 'VP09_ADAPTER_INPUT',
         'context must be binding-context /5, /6 or /7')
    view = copy.deepcopy(context)
    raw = []
    if view['format'].endswith('/7'):
        view['format'] = 'aiaeao.cube.binding-context/6'
        view.pop('method_profile_refs', None)
        for mp in view.get('migration_plans', []):
            if mp.get('plan_id') != plan_id:
                for t in mp.get('transitions', []):
                    t.pop('methods', None)
                for d in mp.get('dependencies', []):
                    d.pop('method', None)
                continue
            for t in mp.get('transitions', []):
                for b in t.pop('methods', []):
                    raw.append(('transition', t['transition_id'], b))
            for d in mp.get('dependencies', []):
                if 'method' in d:
                    raw.append(('dependency', d['dependency_id'], d.pop('method')))
    src, mapping = via07(_from_plan, view, plan_id, tracks, track, labels, steps, subjects, layers=layers, code='VP09_ADAPTER_INPUT')
    ids = {r['ref']: r['id'] for r in mapping['referents']}
    cells = {c['id'] for c in src['cells']}
    trs = {t['id'] for t in src['transitions']}
    bindings = []
    for kind, owner, b in raw:
        if owner not in (trs if kind == 'transition' else cells):
            continue                                         # owner outside the slice
        args = {role: ids[r] for role, r in sorted(b.get('arguments', {}).items()) if r in ids}
        if args and isinstance(b.get('method_id'), str):
            bindings.append({'owner_kind': kind, 'owner': owner, 'method_id': b['method_id'], 'arguments': args})
    return {'format': INPUT_FORMAT, 'profile': PROFILE, 'source': src, 'method_bindings': bindings}, mapping


def method_order(bindings):
    seen = []
    for b in bindings:
        if b['method_id'] not in seen:
            seen.append(b['method_id'])
    return [m for m in CATALOG_ORDER if m in seen]+[m for m in seen if m not in CATALOG_ORDER]

