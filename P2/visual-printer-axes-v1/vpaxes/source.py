"""VP-09 input (AQ-1): a VP-07 migration source (0.7.1/0.7.2) or an axes input with method bindings.

0.9.1 (VP-09.1) adds to the axes input: `local_methods`, per binding `declaration_ref` (+ `witness_ref`,
dependency `step` / `step_rule`), and `dropped_arguments` for bindings or arguments outside the slice.
"""
from __future__ import annotations
import copy

from vpmigration.source import validate_source as _validate_vp07
from vpmigration.adapter import from_plan as _from_plan
from vpmigration.common import P078
from .common import tag_profile, PROFILE, P090, P091, P092, P093, V91UP, V92UP, INPUT_FORMAT, P071, P072, SEMREF, CATALOG_ORDER, METHOD_PROFILE_REF, DIM_OF, need, via07

CTX_FORMATS = ('aiaeao.cube.binding-context/5', 'aiaeao.cube.binding-context/6', 'aiaeao.cube.binding-context/7')
CTX_FORMATS_093 = ('aiaeao.cube.binding-context/7', 'aiaeao.cube.binding-context/8', 'aiaeao.cube.binding-context/9',
                   'aiaeao.cube.binding-context/10')  # VP-09.3: the source comes from VP-07.8, which maps X endpoints


KEYS_091 = {'format', 'profile', 'source', 'method_bindings', 'local_methods', 'dropped_arguments'}
KEYS_092 = KEYS_091 | {'step_roles'}  # VP-09.2: declared step roles travel with the input so the printer can translate them
KEYS_093 = KEYS_092 | {'x_instances', 'x_report'}  # VP-09.3: declared P1.6 instances of the X endpoints in and around the slice
BKEYS_091 = {'owner_kind', 'owner', 'method_id', 'arguments', 'declaration_ref'}
STEP_RULES = ('successor_first', 'own_last')


def profile_of(doc):
    """Profile an input renders under: the axes input's declared profile; a bare VP-07 source renders as 0.9.0."""
    return doc.get('profile') if isinstance(doc, dict) and doc.get('format') == INPUT_FORMAT else P090


def normalize(doc):
    """Return (source, bindings) for either input form; validate the VP-07 source unchanged."""
    need(isinstance(doc, dict), 'VP09_SOURCE_INVALID', 'input must be an object')
    if doc.get('format') == INPUT_FORMAT and doc.get('profile') in V91UP:
        return _normalize_091(doc)
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


def _items(src):
    items = {}
    for it in src['rows']+src['objects']:
        if it['id'] in items:
            continue
        m = SEMREF.match(it.get('semantic_ref', '') or '')
        need(m is not None, 'VP09_SOURCE_INVALID', 'item '+repr(it['id'])+' has no declared home (semantic_ref from from-plan, AX-2)')
        items[it['id']] = {'id': it['id'], 'label': it['label'], 'home': m.group(1), 'kind': m.group(2), 'anchor_id': it['anchor_id']}
    return items


def check_method(mid, local, where):
    """FM-1/FM-2 (D-5): a method is a catalog ID or a declared local method contract; anything else is not drawn."""
    need(isinstance(mid, str) and (mid in CATALOG_ORDER or mid in local), 'VP09_METHOD_UNKNOWN',
         f'method {mid!r} at {where} is neither in {METHOD_PROFILE_REF} nor a local method contract of the context; '
         'P1.11 reports it as P1_MIGRATION_METHOD_UNKNOWN (VP-09.1 FM-1, D-5)')


def _normalize_091(doc):
    keys = KEYS_093 if doc['profile'] == P093 else KEYS_092 if doc['profile'] == P092 else KEYS_091
    need(set(doc) == keys, 'VP09_SOURCE_INVALID', f"axes input {doc['profile'].rsplit('/', 1)[1]} needs exactly "+', '.join(sorted(keys)))
    if doc['profile'] == P093:
        _check_x(doc)
    if doc['profile'] in V92UP:
        sr = doc['step_roles']
        need(isinstance(sr, dict) and isinstance(doc['source'], dict) and isinstance(doc['source'].get('steps'), list)
             and set(sr) == {x.get('id') for x in doc['source']['steps'] if isinstance(x, dict)}
             and all(isinstance(r, str) and len(r) <= 24 for r in sr.values()), 'VP09_SOURCE_INVALID',
             'step_roles must map every source step to its declared role (VP-09.2)')
    src, bindings, local, dropped = doc['source'], doc['method_bindings'], doc['local_methods'], doc['dropped_arguments']
    need(isinstance(src, dict) and src.get('profile') in ((P078,) if doc['profile'] == P093 else (P071, P072)), 'VP09_SOURCE_INVALID',
         'VP-09.3 reads VP-07 migration sources 0.7.8' if doc['profile'] == P093 else 'VP-09 reads VP-07 migration sources 0.7.1 or 0.7.2 (AQ-1)')
    v = via07(_validate_vp07, src, code='VP09_SOURCE_INVALID')
    items = _items(src)
    need(isinstance(local, list) and all(isinstance(m, str) and m for m in local) and len(set(local)) == len(local),
         'VP09_SOURCE_INVALID', 'local_methods must be distinct method IDs')
    need(isinstance(bindings, list) and isinstance(dropped, list), 'VP09_SOURCE_INVALID', 'method_bindings / dropped_arguments must be arrays')
    cells = {c['id'] for c in src['cells']}
    trs = {t['id'] for t in src['transitions']}
    for b in bindings:
        need(isinstance(b, dict) and BKEYS_091 <= set(b) <= BKEYS_091 | {'witness_ref', 'step', 'step_rule'}, 'VP09_SOURCE_INVALID', 'binding shape')
        need(isinstance(b['declaration_ref'], str) and b['declaration_ref'], 'VP09_SOURCE_INVALID', 'binding declaration_ref')
        check_method(b['method_id'], local, b['declaration_ref'])
        need(b['owner_kind'] in ('transition', 'dependency'), 'VP09_SOURCE_INVALID', 'binding owner_kind')
        need(b['owner'] in (trs if b['owner_kind'] == 'transition' else cells), 'VP09_SOURCE_INVALID',
             'binding owner '+repr(b['owner'])+' not in source')
        dep = b['owner_kind'] == 'dependency'
        need(dep == ('step' in b) == ('step_rule' in b), 'VP09_SOURCE_INVALID', 'dependency bindings carry step and step_rule (D-3)')
        need(not dep or (isinstance(b['step'], str) and b['step_rule'] in STEP_RULES), 'VP09_SOURCE_INVALID', 'binding step / step_rule')
        need(isinstance(b['arguments'], dict) and all(x in items for x in b['arguments'].values()), 'VP09_SOURCE_INVALID',
             'binding arguments must name source items')
    for x in dropped:
        need(isinstance(x, dict) and set(x) == {'owner_kind', 'owner', 'method_id', 'role', 'ref', 'reason', 'declaration_ref'}
             and x['reason'] in ('owner_out_of_slice', 'ref_out_of_slice'), 'VP09_SOURCE_INVALID', 'dropped argument shape')
        check_method(x['method_id'], local, x['declaration_ref'])
    return src, bindings, items, v


def from_plan(context, plan_id, tracks=None, track=None, labels=None, steps=None, subjects=None, layers=None, profile=None):
    """AQ-1: run the unchanged VP-07 adapter; transcribe P1.11 bindings (refs → display IDs) into an axes input.

    profile None or 0.9.0 keeps the 0.9.0 transcription byte for byte; 0.9.1 adds paths, slice accounting and steps (VP-09.1).
    """
    need(profile in (None, P090, P091, P092, P093), 'VP09_ADAPTER_INPUT', f'profile must be {P090}, {P091}, {P092} or {P093}')
    if profile in V91UP:
        return _from_plan_091(context, plan_id, tracks, track, labels, steps, subjects, layers, profile)
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


def _from_plan_091(context, plan_id, tracks, track, labels, steps, subjects, layers, profile=P091):
    v93 = profile == P093
    need(isinstance(context, dict) and context.get('format') in (CTX_FORMATS_093 if v93 else CTX_FORMATS), 'VP09_ADAPTER_INPUT',
         'context must be binding-context /7…/10' if v93 else 'context must be binding-context /5, /6 or /7')
    ctx_id = context.get('context_id')
    view = copy.deepcopy(context)
    local = [m['method_id'] for m in view.get('method_contracts') or [] if isinstance(m, dict) and isinstance(m.get('method_id'), str)]
    raw, plan = [], None
    if view['format'] in CTX_FORMATS_093 if v93 else view['format'].endswith('/7'):
        refs = view.get('method_profile_refs') if v93 else view.pop('method_profile_refs', None)
        need(refs == [METHOD_PROFILE_REF], 'VP09_ADAPTER_INPUT', f'method_profile_refs must be [{METHOD_PROFILE_REF!r}] (VP-09.1 §2)')
        if not v93:
            view['format'] = 'aiaeao.cube.binding-context/6'
        for i, mp in enumerate(view.get('migration_plans', [])):
            mine = mp.get('plan_id') == plan_id
            plan = copy.deepcopy(mp) if mine else plan
            for j, t in enumerate(mp.get('transitions', [])):
                for n, b in enumerate(t.pop('methods', [])):
                    if mine:
                        raw.append(('transition', t['transition_id'], b, f'/migration_plans/{i}/transitions/{j}/methods/{n}'))
            for j, d in enumerate(mp.get('dependencies', [])):
                if 'method' in d:
                    b = d.pop('method')
                    if mine:
                        raw.append(('dependency', d['dependency_id'], b, f'/migration_plans/{i}/dependencies/{j}/method'))
    for kind, owner, b, ptr in raw:
        need(isinstance(b, dict) and isinstance(b.get('arguments'), dict), 'VP09_ADAPTER_INPUT', f'binding at {ptr} is not a P1.11 binding')
        check_method(b.get('method_id'), local, f'decl:{ctx_id}#{ptr}')
    src, mapping = via07(_from_plan, view, plan_id, tracks, track, labels, steps, subjects, layers=layers, code='VP09_ADAPTER_INPUT',
                         **({'profile': P078} if v93 else {}))
    ids = {r['ref']: r['id'] for r in mapping['referents']}
    cells = {c['id'] for c in src['cells']}
    trs = {t['id'] for t in src['transitions']}
    deps = {d['dependency_id']: d for d in (plan or {}).get('dependencies', [])}
    bindings, dropped = [], []
    for kind, owner, b, ptr in raw:
        ref = f'decl:{ctx_id}#{ptr}'
        inside = owner in (trs if kind == 'transition' else cells)
        args = {}
        for role, r in sorted(b['arguments'].items()):
            if inside and r in ids:
                args[role] = ids[r]
            else:
                dropped.append({'owner_kind': kind, 'owner': owner, 'method_id': b['method_id'], 'role': role, 'ref': r,
                                'reason': 'ref_out_of_slice' if inside else 'owner_out_of_slice', 'declaration_ref': ref})
        if not inside:
            continue
        x = {'owner_kind': kind, 'owner': owner, 'method_id': b['method_id'], 'arguments': args, 'declaration_ref': ref}
        if isinstance(b.get('witness_ref'), str):
            x['witness_ref'] = b['witness_ref']
        if kind == 'dependency':                                 # D-3: both values are declared in the context
            d = deps[owner]
            succ = deps.get(d.get('successor_ref')) if isinstance(d.get('successor_ref'), str) else None
            if succ and succ.get('holds_in'):
                x['step'], x['step_rule'] = succ['holds_in'][0], 'successor_first'
            else:
                x['step'], x['step_rule'] = d['holds_in'][-1], 'own_last'
        bindings.append(x)
    doc = {'format': INPUT_FORMAT, 'profile': profile, 'source': src, 'local_methods': local, 'method_bindings': bindings,
           'dropped_arguments': dropped}
    if profile in V92UP:  # VP-09.2: declared roles of the shown steps (from the plan's phases)
        mp = plan or next((x for x in context.get('migration_plans', []) if isinstance(x, dict) and x.get('plan_id') == plan_id), {})
        role = {ph.get('phase_id'): ph.get('role', '') for ph in mp.get('phases', []) if isinstance(ph, dict)}
        doc['step_roles'] = {s['id']: role.get(s['id'], '') for s in src['steps']}
    if v93:
        doc['x_instances'], doc['x_report'] = x_instances(context, ids)
    return doc, mapping


def _kind(concept):
    return ''.join(p.capitalize() for p in concept.split(':')[2].split('-'))


def x_instances(context, ids):
    """VP-09.3 §1: the X endpoints a dependency of the slice names, and those reached from them through slots; per endpoint
    its slots naming a Y referent and its required Y-typed slots that the instance leaves absent (descriptor of its profile)."""
    refs = {r['ref']: r for r in context.get('referents', []) if isinstance(r, dict) and isinstance(r.get('ref'), str)}
    is_x = lambda ref: refs.get(ref, {}).get('concept_id', '').startswith('X:endpoint:')  # noqa: E731
    todo = [ref for ref in ids if is_x(ref)]
    seen = []
    while todo:
        ref = todo.pop(0)
        if ref in seen:
            continue
        seen.append(ref)
        for v in (refs[ref].get('slots') or {}).values():
            for t in (v if isinstance(v, list) else [v]):
                if isinstance(t, str) and is_x(t) and t not in seen:
                    todo.append(t)
    profiles = {p.get('profile_ref'): p for p in context.get('instantiation_profiles', []) if isinstance(p, dict)}
    out, missing = [], []
    for ref in seen:
        r = refs[ref]
        c = r['concept_id']
        slots = r.get('slots') or {}
        prof = profiles.get(r.get('instantiation_profile_ref')) or next(
            (p for p in profiles.values() if p.get('concept_id') == c and p.get('scope') == r.get('scope_ref')), None)
        rows = []
        for name in sorted(slots):
            if name == 'pair_scope_ref':
                continue
            for t in (slots[name] if isinstance(slots[name], list) else [slots[name]]):
                tc = refs.get(t, {}).get('concept_id', '') if isinstance(t, str) else ''
                if tc.startswith('Y:'):
                    rows.append({'slot': name, 'target': ids.get(t, t), 'target_ref': t, 'target_kind': _kind(tc),
                                 'target_anchor': tc.split(':')[1]+'s.'+tc.split(':')[2]})
        if prof is None:
            missing.append(ids.get(ref, ref))
        else:
            for d in prof.get('slots', []):
                ys = [x for x in d.get('concept_ids', []) if x.startswith('Y:')]
                if d.get('required') and d.get('kind') == 'ref' and ys and d.get('name') not in slots:
                    rows.append({'slot': d['name'], 'absent': True, 'kinds': [_kind(x) for x in ys]})
        out.append({'id': ids.get(ref, ref), 'ref': ref, 'concept_id': c, 'dimension': DIM_OF[c.split(':')[2]], 'slots': rows})
    ignored = sum(1 for ref in refs if is_x(ref) and ref not in seen)
    return out, {'x_ignored': ignored, 'x_profiles_missing': sorted(missing)}


def _check_x(doc):
    xs, rep_ = doc['x_instances'], doc['x_report']
    need(isinstance(xs, list) and isinstance(rep_, dict) and set(rep_) == {'x_ignored', 'x_profiles_missing'}, 'VP09_SOURCE_INVALID',
         'x_instances must be an array and x_report carry x_ignored and x_profiles_missing (VP-09.3)')
    for x in xs:
        need(isinstance(x, dict) and set(x) == {'id', 'ref', 'concept_id', 'dimension', 'slots'} and x['dimension'] in DIM_OF.values()
             and isinstance(x['slots'], list), 'VP09_SOURCE_INVALID', 'x_instances entry shape (VP-09.3)')
        for sl in x['slots']:
            need(isinstance(sl, dict) and isinstance(sl.get('slot'), str) and
                 (set(sl) == {'slot', 'absent', 'kinds'} and sl['absent'] is True and sl['kinds'] or
                  set(sl) == {'slot', 'target', 'target_ref', 'target_kind', 'target_anchor'}), 'VP09_SOURCE_INVALID', 'x_instances slot shape (VP-09.3)')


def method_order(bindings):
    seen = []
    for b in bindings:
        if b['method_id'] not in seen:
            seen.append(b['method_id'])
    return [m for m in CATALOG_ORDER if m in seen]+[m for m in seen if m not in CATALOG_ORDER]



from_plan = tag_profile(from_plan, lambda *a, **k: k.get('profile'))
