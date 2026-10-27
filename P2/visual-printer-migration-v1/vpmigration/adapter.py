"""VP-07 adapter `from-plan` (AD-1…AD-9): P1.10 binding-context/5 plan → VP-07 migration source.

Deterministic fixed mapping. No P1 validation, no inference: every field shown comes from
a declared context, track map, label map or witness prefix list.
"""
from __future__ import annotations

from .common import PROFILE, PROFILES, P071, P072, P073, V71UP, V72UP, METHOD_PROFILE_REF, check_binding, UNASSIGNED, LATEST, END_REASONS, KEY, VP07Error, need, keys, clean, sha_json, excerpt, check_edge_styles
from .source import FORMAT as SOURCE_FORMAT, validate_source

CONTEXT_FORMAT = 'aiaeao.cube.binding-context/5'
CONTEXT_FORMATS_071 = (CONTEXT_FORMAT, 'aiaeao.cube.binding-context/6')  # VP-07.1: /6 adds ends_reason
CONTEXT_FORMAT_7 = 'aiaeao.cube.binding-context/7'  # VP-07.3: P1.11 method bindings
TRACK_FORMAT = 'aiaeao.cube.vp07-track-map/1'
LAYER_FORMAT = 'aiaeao.cube.vp07-layer-map/1'
LABEL_FORMAT = 'aiaeao.cube.vp07-label-map/1'
PREFIX_FORMAT = 'aiaeao.cube.vp07-witness-prefixes/1'
MAPPING_FORMAT = 'aiaeao.cube.vp07-mapping/1'
# AD-2: concept_id → (anchor_id, form_id, concept_key)
MAPPING = {
    'Z:module-body:integration': ('module-bodies.integration', 'form.module-block', 'Integration'),
    'Z:module-body:provider': ('module-bodies.provider', 'form.module-block', 'Provider'),
    'Z:module-body:third-party-dependency': ('module-bodies.third-party-dependency', 'form.module-block', 'ThirdPartyDependency'),
    'Z:module-body:runtime': ('module-bodies.runtime', 'form.module-block', 'Runtime'),
    'Y:resource-object:resource': ('resource-objects.resource', 'form.resource-card', 'Resource'),
    'Y:identity-anchor:actor': ('identity-anchors.actor', 'form.identity-chip', 'Actor'),
}
MAX_DECL_REF = 140  # VP-02 edge declaration_ref limit


def _tracks(doc):
    if doc is None:
        return {}
    keys(doc, ('format', 'tracks'), (), 'VP07_ADAPTER_INPUT', 'track map')
    need(doc['format'] == TRACK_FORMAT, 'VP07_ADAPTER_INPUT', 'track map format must be '+TRACK_FORMAT)
    need(isinstance(doc['tracks'], dict) and doc['tracks'], 'VP07_ADAPTER_INPUT', 'tracks must map names to subject refs')
    owner = {}
    for name, refs in doc['tracks'].items():
        need(clean(name, 40), 'VP07_ADAPTER_INPUT', 'track name must be clean text <= 40')
        need(isinstance(refs, list) and refs and all(isinstance(r, str) for r in refs), 'VP07_ADAPTER_INPUT', 'track '+name+' needs subject refs')
        for r in refs:
            need(r not in owner, 'VP07_ADAPTER_INPUT', 'subject '+repr(r)+' assigned to two tracks ('+str(owner.get(r))+', '+name+')')
            owner[r] = name
    return owner


def _layer_map(doc, refs):
    """VP-07.2 LM-1…LM-3: declared layer order and ref → layer assignment (presentation input only)."""
    keys(doc, ('format', 'layer_order', 'layers'), (), 'VP07_ADAPTER_INPUT', 'layer map')
    need(doc['format'] == LAYER_FORMAT, 'VP07_ADAPTER_INPUT', 'layer map format must be '+LAYER_FORMAT)
    lo = doc['layer_order']
    need(isinstance(lo, list) and 1 <= len(lo) <= 12 and all(clean(x, 24) for x in lo) and len(set(lo)) == len(lo), 'VP07_ADAPTER_INPUT',
         'layer_order must be 1…12 distinct clean names <= 24 (LM-1)')
    need(UNASSIGNED not in lo, 'VP07_ADAPTER_INPUT', 'layer name unassigned is reserved (D-4)')
    need(isinstance(doc['layers'], dict), 'VP07_ADAPTER_INPUT', 'layers must map layer names to ref lists')
    owner = {}
    for name, rs in doc['layers'].items():
        need(name in lo, 'VP07_ADAPTER_INPUT', 'layer '+repr(name)+' is not in layer_order (LM-2)')
        need(isinstance(rs, list) and all(isinstance(r, str) for r in rs), 'VP07_ADAPTER_INPUT', 'layer '+name+' needs a ref list')
        for r in rs:
            need(r not in owner, 'VP07_ADAPTER_INPUT', 'ref '+repr(r)+' assigned to two layers ('+str(owner.get(r))+', '+name+')')
            need(r in refs, 'VP07_ADAPTER_INPUT', 'layer map names undeclared referent '+repr(r))
            owner[r] = name
    return lo, owner


def _labels(doc):
    if doc is None:
        return {}
    keys(doc, ('format', 'labels'), (), 'VP07_ADAPTER_INPUT', 'label map')
    need(doc['format'] == LABEL_FORMAT, 'VP07_ADAPTER_INPUT', 'label map format must be '+LABEL_FORMAT)
    need(isinstance(doc['labels'], dict), 'VP07_ADAPTER_INPUT', 'labels must map refs to {id,label}')
    ids = set()
    for ref, v in doc['labels'].items():
        keys(v, ('id', 'label'), (), 'VP07_ADAPTER_INPUT', 'label entry')
        need(isinstance(v['id'], str) and KEY.fullmatch(v['id']) is not None, 'VP07_ADAPTER_INPUT', 'label id must be a stable ID')
        need(clean(v['label'], 60), 'VP07_ADAPTER_INPUT', 'label must be clean text <= 60')
        need(v['id'] not in ids, 'VP07_ADAPTER_INPUT', 'label map assigns one id twice')
        ids.add(v['id'])
    return doc['labels']


def _prefixes(doc):
    if doc is None:
        return []
    keys(doc, ('format', 'prefixes'), (), 'VP07_ADAPTER_INPUT', 'witness prefix list')
    need(doc['format'] == PREFIX_FORMAT, 'VP07_ADAPTER_INPUT', 'witness prefix format must be '+PREFIX_FORMAT)
    need(isinstance(doc['prefixes'], list), 'VP07_ADAPTER_INPUT', 'prefixes must be an array')
    for p in doc['prefixes']:
        keys(p, ('prefix', 'note'), (), 'VP07_ADAPTER_INPUT', 'witness prefix')
        need(clean(p['prefix'], 40) and clean(p['note'], 60), 'VP07_ADAPTER_INPUT', 'prefix <= 40, note <= 60')
    return doc['prefixes']


def _declared_ends(plan, pids):
    """GM-3: per dependency, the declaration that explains its end on the FULL plan (transcription, not P1 validation).
    Order mirrors P1.10.1 DG-2…DG-7; dependencies with invalid phases or conflicted referents get no entry."""
    idx = {p: i for i, p in enumerate(pids)}
    roles = [p.get('role') for p in plan.get('phases', [])]
    target = max(i for i, r in enumerate(roles) if r == 'target') if 'target' in roles else len(pids)-1
    retire, intro = {}, {}
    for t in plan.get('transitions', []):
        k = idx.get(t.get('at_phase'))
        if k is None:
            continue
        for r in t.get('retires', []):
            retire.setdefault(r, []).append(k)
        for r in t.get('introduces', []):
            intro.setdefault(r, []).append(k)
    conflict = {r for r in set(retire) | set(intro) if len(retire.get(r, [])) > 1 or len(intro.get(r, [])) > 1
                or (r in retire and r in intro and min(retire[r]) <= min(intro[r]))}
    R = {r: min(v) for r, v in retire.items()}
    out = {}
    for d in plan.get('dependencies', []):
        ks = sorted(idx[p] for p in d['holds_in'] if p in idx)
        if not ks or len(ks) != len(d['holds_in']) or ks != list(range(ks[0], ks[-1]+1)):
            continue
        k, o, s = ks[-1], d['object'], d['subject']
        if k >= target:
            e = 'target'
        elif o in conflict or s in conflict:
            continue
        elif o in R and R[o] <= k+1:
            e = 'object_retired'
        elif s in R and R[s] <= k+1:
            e = 'subject_retired'
        elif d.get('dropped'):
            e = 'dropped'
        elif d.get('successor_ref') is not None:
            e = 'successor'
        elif d.get('ends_reason') in END_REASONS and d.get('witness_ref'):
            e = 'ends_reason'
        else:
            e = 'unexplained'
        out[d['dependency_id']] = e
    return out, pids[target]


def from_plan(context, plan_id, tracks=None, track=None, labels=None, steps=None, subjects=None, edge_styles=None,
              witness_prefixes=None, profile=None, layers=None):
    is7 = isinstance(context, dict) and context.get('format') == CONTEXT_FORMAT_7
    if profile is None:  # VP-07.2 LS-1: 0.7.2 only when a layer map is given; VP-07.3 D-1: a /7 context selects 0.7.3
        profile = P073 if is7 else P072 if layers is not None else P071
    need(profile in PROFILES, 'VP07_ADAPTER_INPUT', 'profile must be one of '+', '.join(PROFILES))
    need(layers is None or profile in V72UP, 'VP07_ADAPTER_INPUT', 'a layer map needs profile '+P072+' (LS-1)')  # 0.7.3 includes 0.7.2
    v71 = profile in V71UP
    v73 = profile == P073
    formats = CONTEXT_FORMATS_071+(CONTEXT_FORMAT_7,) if v73 else CONTEXT_FORMATS_071 if v71 else (CONTEXT_FORMAT,)
    need(isinstance(context, dict) and context.get('format') in formats, 'VP07_ADAPTER_INPUT',
         'context must be '+' or '.join(formats)+' (got '+repr(context.get('format') if isinstance(context, dict) else None)+')')
    ctx_id = context.get('context_id')
    need(clean(ctx_id, 80), 'VP07_ADAPTER_INPUT', 'context_id must be clean text')
    plans = context.get('migration_plans')
    need(isinstance(plans, list), 'VP07_ADAPTER_INPUT', 'context has no migration_plans')
    pi = next((i for i, p in enumerate(plans) if isinstance(p, dict) and p.get('plan_id') == plan_id), None)
    need(pi is not None, 'VP07_ADAPTER_INPUT', 'unknown plan_id '+repr(plan_id))
    plan = plans[pi]
    local = _methods_in(context, plan, pi, ctx_id) if is7 else []
    phases = plan.get('phases', [])
    pids = [p['phase_id'] for p in phases]
    owner = _tracks(tracks)
    labelmap = _labels(labels)
    prefixes = _prefixes(witness_prefixes)
    styles = check_edge_styles(edge_styles) if edge_styles is not None else None
    refs = {r['ref']: r for r in context.get('referents', []) if isinstance(r, dict) and 'ref' in r}
    lmap = _layer_map(layers, refs) if layers is not None else None
    for r in owner:
        need(r in refs, 'VP07_ADAPTER_INPUT', 'track map names unknown subject '+repr(r))
    # slice: steps
    if steps:
        need(isinstance(steps, str) and steps.count(':') == 1, 'VP07_ADAPTER_INPUT', 'steps must be first:last')
        a, b = steps.split(':')
        need(a in pids and b in pids and pids.index(a) <= pids.index(b), 'VP07_ADAPTER_INPUT', 'steps range not in plan order')
        window = pids[pids.index(a):pids.index(b)+1]
    else:
        window = list(pids)
    need(len(window) >= 1, 'VP07_ADAPTER_INPUT', 'plan has no phases')
    # slice: subjects
    if track is not None:
        need(owner, 'VP07_ADAPTER_INPUT', '--track needs a declared track map')
        need(track in set(owner.values()), 'VP07_ADAPTER_INPUT', 'unknown track '+repr(track))
    wanted = set(subjects) if subjects else None
    selected = []
    for j, d in enumerate(plan.get('dependencies', [])):
        if wanted is not None and d['subject'] not in wanted:
            continue
        if track is not None and owner.get(d['subject']) != track:
            continue
        for p in d['holds_in']:
            need(p in pids, 'VP07_ADAPTER_INPUT', 'dependency '+str(d.get('dependency_id'))+' holds in undeclared phase '+repr(p))
        st = [p for p in window if p in d['holds_in']]
        if st:
            selected.append((j, d, st))
    need(selected, 'VP07_ADAPTER_INPUT', 'slice selects no dependency')
    # referents → display items (AD-2, AD-7)
    items = {}

    def item(ref, role):
        need(ref in refs, 'VP07_ADAPTER_INPUT', 'dependency names undeclared referent '+repr(ref))
        r = refs[ref]
        m = MAPPING.get(r.get('concept_id'))
        need(m is not None, 'VP07_ADAPTER_MAPPING', 'no mapping row for concept '+repr(r.get('concept_id'))+' (referent '+repr(ref)+')')
        if ref in labelmap:
            ident, label = labelmap[ref]['id'], labelmap[ref]['label']
        else:
            need(KEY.fullmatch(ref) is not None and len(ref) <= 60, 'VP07_ADAPTER_MAPPING',
                 'ref '+repr(ref)+' is not a valid display ID (<= 60 chars) and has no label-map entry (D-11)')
            ident, label = ref, ref
        layer = (r.get('layers') or ['α'])[0]
        out = {'id': ident, 'anchor_id': m[0], 'form_id': m[1], 'label': label,
               'semantic_ref': f"{r.get('home', '')}:{layer}:{m[2]}[\"{ref}\"]"}
        prev = items.get(ident)
        need(prev is None or prev[0] == ref, 'VP07_ADAPTER_MAPPING', 'two refs map to display id '+repr(ident))
        items[ident] = (ref, out, r.get('concept_id'))
        return out
    ends, target_step = _declared_ends(plan, pids) if v71 else ({}, None)
    rows, objects, cells, facets, deps_out = [], [], [], [], []
    row_ids, obj_ids = [], []
    for j, d, st in selected:
        s = item(d['subject'], 'row')
        o = item(d['object'], 'object')
        if s['id'] not in row_ids:
            row = dict(s)
            if d['subject'] in owner:
                row['track'] = owner[d['subject']]
            rows.append(row); row_ids.append(s['id'])
        if o['id'] not in obj_ids:
            objects.append(dict(o)); obj_ids.append(o['id'])
        did = d['dependency_id']
        need(isinstance(did, str) and KEY.fullmatch(did) is not None, 'VP07_ADAPTER_MAPPING', 'dependency_id '+repr(did)+' is not a valid display ID')
        pointer = f'/migration_plans/{pi}/dependencies/{j}'
        ref = f'decl:{ctx_id}#{pointer}'
        need(len(ref) <= MAX_DECL_REF, 'VP07_ADAPTER_MAPPING', 'declaration_ref exceeds 140 chars; shorten context_id')
        cell = {'id': did, 'row': s['id'], 'object': o['id'], 'predicate_id': d['predicate_id'], 'steps': st, 'declaration_ref': ref}
        if v71:
            if d.get('dropped') is True:
                cell['dropped'] = True
            elif isinstance(d.get('successor_ref'), str) and KEY.fullmatch(d['successor_ref']) is not None:
                cell['successor'] = d['successor_ref']
            if isinstance(d.get('ends_reason'), str) and clean(d['ends_reason'], 40):
                cell['ends_reason'] = d['ends_reason']
            if did in ends:
                cell['declared_end'] = ends[did]
        cells.append(cell)
        deps_out.append({'dependency_id': did, 'pointer': pointer, 'steps': st})
        # AD-4 facets: declared fields only
        exe = []
        if d.get('kind'):
            exe.append('kind '+d['kind'])
        if d.get('schedule'):
            exe.append('schedule '+d['schedule'])
        if exe:
            facets.append({'lens': 'cube.lens.execution', 'target_kind': 'cell', 'target_id': did, 'declaration_ref': ref,
                           'note': excerpt(' · '.join(exe), 80), 'basis': 'declared_unverified'})
        w = d.get('witness_ref')
        if w:
            facets.append({'lens': 'cube.lens.provenance', 'target_kind': 'cell', 'target_id': did, 'declaration_ref': ref+'/witness_ref',
                           'note': excerpt('witness '+w, 80), 'basis': 'declared_unverified'})
            hit = next((p for p in prefixes if w.startswith(p['prefix'])), None)
            if hit:
                facets.append({'lens': 'cube.lens.epistemology', 'target_kind': 'cell', 'target_id': did, 'declaration_ref': ref+'/witness_ref',
                               'note': hit['note'], 'basis': 'declared_unverified'})
    # transitions restricted to the slice
    transitions, dropped = [], []
    for k, t in enumerate(plan.get('transitions', [])):
        ret = [items_id(items, r) for r in t.get('retires', [])]
        intro = [items_id(items, r) for r in t.get('introduces', [])]
        vis = set(obj_ids) | (set(row_ids) if v71 else set())  # VP-07.1 GM-2: transitions may retire subjects
        ret = [x for x in ret if x in vis]
        intro = [x for x in intro if x in vis]
        tid = t.get('transition_id')
        if t.get('at_phase') not in window or not (ret or intro):
            dropped.append({'transition_id': tid, 'reason': 'outside_slice'}); continue
        need(isinstance(tid, str) and KEY.fullmatch(tid) is not None, 'VP07_ADAPTER_MAPPING', 'transition_id '+repr(tid)+' is not a valid display ID')
        tr = {'id': tid, 'at': t['at_phase'], 'retires': ret, 'introduces': intro,
              'declaration_ref': f'decl:{ctx_id}#/migration_plans/{pi}/transitions/{k}'}
        if v71:
            tr['code'] = 'T'+str(k+1)  # PD-3: full-plan order, stable across slices
        transitions.append(tr)
    mwarn = _attach_methods(plan, pi, ctx_id, items, cells, transitions) if is7 else []
    lwarn, lorder, lseq = [], None, None
    if lmap is not None:  # VP-07.2 LS-2: transcribe declared layers, order rows/objects by them
        lorder, owner_of = list(lmap[0]), lmap[1]
        shown = list(dict.fromkeys(row_ids+obj_ids))
        layer_of = {i: owner_of.get(items[i][0], UNASSIGNED) for i in shown}
        lseq = [items_id(items, r) for name in lorder for r in layers['layers'].get(name, []) if items_id(items, r) in layer_of]
        lseq += [i for i in shown if layer_of[i] == UNASSIGNED]
        if any(v == UNASSIGNED for v in layer_of.values()):
            lorder.append(UNASSIGNED)
            lwarn = [{'code': 'VP07_LAYER_UNASSIGNED', 'item_id': i} for i in shown if layer_of[i] == UNASSIGNED]
        pos = {i: k for k, i in enumerate(lseq)}
        for coll in (rows, objects):
            for it in coll:
                it['layer'] = layer_of[it['id']]
            coll.sort(key=lambda it: pos[it['id']])
    role = {p['phase_id']: p.get('role', '') for p in phases}
    step_list = [{'id': p, 'label': excerpt(f'{p} · {role[p]}', 40)} for p in window]
    ctx_sha = sha_json(context)
    src = {'format': SOURCE_FORMAT, 'profile': profile, 'reference_version': 'v9.4', 'context_id': ctx_id, 'plan_id': plan_id,
           'source_context_sha256': ctx_sha, 'title': excerpt(f'{plan_id} · {window[0]} → {window[-1]}', 78), 'steps': step_list,
           'rows': rows, 'objects': objects, 'cells': cells, 'transitions': transitions, 'facet_bindings': facets,
           'declaration_status': 'declared_unverified'}
    if v71:
        src['target_step'] = target_step
    if v73:
        src['local_methods'] = local
    if lmap is not None:
        src['layer_order'] = lorder
        src['layer_sequence'] = lseq
    if styles is not None:
        src['edge_styles'] = edge_styles
    validate_source(src)
    used_steps = {p for c in cells for p in c['steps']}
    mapping = {'format': MAPPING_FORMAT, 'profile': profile, 'source_context_sha256': ctx_sha, 'context_id': ctx_id, 'plan_id': plan_id,
               'slice': {'steps': window, 'subjects': sorted(wanted) if wanted else None, 'track': track},
               'track_map_sha256': sha_json(tracks) if tracks is not None else None,
               'label_map_sha256': sha_json(labels) if labels is not None else None,
               'witness_prefixes_sha256': sha_json(witness_prefixes) if witness_prefixes is not None else None,
               'referents': [{'ref': ref, 'id': ident, 'label': out['label'], 'concept_id': cid, 'anchor_id': out['anchor_id'],
                              'form_id': out['form_id']} for ident, (ref, out, cid) in items.items()],
               'dependencies': deps_out, 'empty_steps': [p for p in window if p not in used_steps],
               'dropped_transitions': dropped, 'facets_generated': len(facets),
               'p1_validation_performed': False, 'declaration_status': 'declared_unverified'}
    if lmap is not None:
        mapping.update(layer_map_sha256=sha_json(layers), warnings=lwarn)
    if v73:
        mapping['warnings'] = lwarn+mwarn
    return src, mapping


def _methods_in(context, plan, pi, ctx_id):
    """VP-07.3 MT-1, D-6: a /7 context imports P1.11 only; every binding of the plan names a catalog or local method."""
    need(context.get('method_profile_refs') == [METHOD_PROFILE_REF], 'VP07_ADAPTER_INPUT',
         f'method_profile_refs must be [{METHOD_PROFILE_REF!r}] (VP-07.3 §2)')
    local = [m['method_id'] for m in context.get('method_contracts') or [] if isinstance(m, dict) and isinstance(m.get('method_id'), str)]
    for ptr, b in _bindings(plan, pi):
        need(isinstance(b, dict) and isinstance(b.get('arguments'), dict), 'VP07_ADAPTER_INPUT', f'binding at {ptr} is not a P1.11 binding')
        check_binding({'method_id': b.get('method_id'), 'arguments': {}, 'declaration_ref': f'decl:{ctx_id}#{ptr}'}, local, ptr, 'VP07_ADAPTER_INPUT')
    return local


def _bindings(plan, pi):
    for k, t in enumerate(plan.get('transitions', [])):
        for n, b in enumerate(t.get('methods', []) if isinstance(t, dict) else []):
            yield f'/migration_plans/{pi}/transitions/{k}/methods/{n}', b
    for j, d in enumerate(plan.get('dependencies', [])):
        if isinstance(d, dict) and 'method' in d:
            yield f'/migration_plans/{pi}/dependencies/{j}/method', d['method']


def _attach_methods(plan, pi, ctx_id, items, cells, transitions):
    """MT-2/MT-3: declared bindings onto the shown transitions and cells; refs → display IDs; refs outside the slice stay
    as declared ref text and are marked hidden (D-7)."""
    warn = []

    def conv(owner, b, ptr):
        args, hidden = {}, []
        for role, r in b['arguments'].items():
            ident = items_id(items, r)
            args[role] = ident if ident is not None else r
            if ident is None:
                hidden.append(role)
                warn.append({'code': 'VP07_METHOD_ARGUMENT_HIDDEN', 'owner': owner, 'method_id': b['method_id'], 'role': role, 'ref': r,
                             'declaration_ref': f'decl:{ctx_id}#{ptr}'})
        out = {'method_id': b['method_id'], 'arguments': args, 'declaration_ref': f'decl:{ctx_id}#{ptr}'}
        if isinstance(b.get('witness_ref'), str) and clean(b['witness_ref'], 120):
            out['witness_ref'] = b['witness_ref']
        if hidden:
            out['hidden_roles'] = hidden
        return out
    shown_t = {t['id']: t for t in transitions}
    shown_c = {c['id']: c for c in cells}
    for k, t in enumerate(plan.get('transitions', [])):
        tr = shown_t.get(t.get('transition_id'))
        if tr is not None and t.get('methods'):
            tr['methods'] = [conv(tr['id'], b, f'/migration_plans/{pi}/transitions/{k}/methods/{n}') for n, b in enumerate(t['methods'])]
    for j, d in enumerate(plan.get('dependencies', [])):
        c = shown_c.get(d.get('dependency_id'))
        if c is not None and 'method' in d:
            c['method'] = conv(c['id'], d['method'], f'/migration_plans/{pi}/dependencies/{j}/method')
    return warn


def items_id(items, ref):
    for ident, (r, _, _) in items.items():
        if r == ref:
            return ident
    return None
