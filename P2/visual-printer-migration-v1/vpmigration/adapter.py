"""VP-07 adapter `from-plan` (AD-1…AD-9): P1.10 binding-context/5 plan → VP-07 migration source.

Deterministic fixed mapping. No P1 validation, no inference: every field shown comes from
a declared context, track map, label map or witness prefix list.
"""
from __future__ import annotations

from .common import PROFILE, KEY, VP07Error, need, keys, clean, sha_json, excerpt, check_edge_styles
from .source import FORMAT as SOURCE_FORMAT, validate_source

CONTEXT_FORMAT = 'aiaeao.cube.binding-context/5'
TRACK_FORMAT = 'aiaeao.cube.vp07-track-map/1'
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


def from_plan(context, plan_id, tracks=None, track=None, labels=None, steps=None, subjects=None, edge_styles=None,
              witness_prefixes=None):
    need(isinstance(context, dict) and context.get('format') == CONTEXT_FORMAT, 'VP07_ADAPTER_INPUT',
         'context must be '+CONTEXT_FORMAT+' (got '+repr(context.get('format') if isinstance(context, dict) else None)+')')
    ctx_id = context.get('context_id')
    need(clean(ctx_id, 80), 'VP07_ADAPTER_INPUT', 'context_id must be clean text')
    plans = context.get('migration_plans')
    need(isinstance(plans, list), 'VP07_ADAPTER_INPUT', 'context has no migration_plans')
    pi = next((i for i, p in enumerate(plans) if isinstance(p, dict) and p.get('plan_id') == plan_id), None)
    need(pi is not None, 'VP07_ADAPTER_INPUT', 'unknown plan_id '+repr(plan_id))
    plan = plans[pi]
    phases = plan.get('phases', [])
    pids = [p['phase_id'] for p in phases]
    owner = _tracks(tracks)
    labelmap = _labels(labels)
    prefixes = _prefixes(witness_prefixes)
    styles = check_edge_styles(edge_styles) if edge_styles is not None else None
    refs = {r['ref']: r for r in context.get('referents', []) if isinstance(r, dict) and 'ref' in r}
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
        cells.append({'id': did, 'row': s['id'], 'object': o['id'], 'predicate_id': d['predicate_id'], 'steps': st, 'declaration_ref': ref})
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
        ret = [x for x in ret if x in obj_ids]
        intro = [x for x in intro if x in obj_ids]
        tid = t.get('transition_id')
        if t.get('at_phase') not in window or not (ret or intro):
            dropped.append({'transition_id': tid, 'reason': 'outside_slice'}); continue
        need(isinstance(tid, str) and KEY.fullmatch(tid) is not None, 'VP07_ADAPTER_MAPPING', 'transition_id '+repr(tid)+' is not a valid display ID')
        transitions.append({'id': tid, 'at': t['at_phase'], 'retires': ret, 'introduces': intro,
                            'declaration_ref': f'decl:{ctx_id}#/migration_plans/{pi}/transitions/{k}'})
    role = {p['phase_id']: p.get('role', '') for p in phases}
    step_list = [{'id': p, 'label': excerpt(f'{p} · {role[p]}', 40)} for p in window]
    ctx_sha = sha_json(context)
    src = {'format': SOURCE_FORMAT, 'profile': PROFILE, 'reference_version': 'v9.4', 'context_id': ctx_id, 'plan_id': plan_id,
           'source_context_sha256': ctx_sha, 'title': excerpt(f'{plan_id} · {window[0]} → {window[-1]}', 78), 'steps': step_list,
           'rows': rows, 'objects': objects, 'cells': cells, 'transitions': transitions, 'facet_bindings': facets,
           'declaration_status': 'declared_unverified'}
    if styles is not None:
        src['edge_styles'] = edge_styles
    validate_source(src)
    used_steps = {p for c in cells for p in c['steps']}
    mapping = {'format': MAPPING_FORMAT, 'profile': PROFILE, 'source_context_sha256': ctx_sha, 'context_id': ctx_id, 'plan_id': plan_id,
               'slice': {'steps': window, 'subjects': sorted(wanted) if wanted else None, 'track': track},
               'track_map_sha256': sha_json(tracks) if tracks is not None else None,
               'label_map_sha256': sha_json(labels) if labels is not None else None,
               'witness_prefixes_sha256': sha_json(witness_prefixes) if witness_prefixes is not None else None,
               'referents': [{'ref': ref, 'id': ident, 'label': out['label'], 'concept_id': cid, 'anchor_id': out['anchor_id'],
                              'form_id': out['form_id']} for ident, (ref, out, cid) in items.items()],
               'dependencies': deps_out, 'empty_steps': [p for p in window if p not in used_steps],
               'dropped_transitions': dropped, 'facets_generated': len(facets),
               'p1_validation_performed': False, 'declaration_status': 'declared_unverified'}
    return src, mapping


def items_id(items, ref):
    for ident, (r, _, _) in items.items():
        if r == ref:
            return ident
    return None
