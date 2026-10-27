"""VP-07 migration source (MS-1…MS-3, D-10): the unbudgeted input of print-panels."""
from __future__ import annotations
import copy

from .common import (PROFILE, PROFILES, P071, P072, P073, V71UP, V72UP, V73UP, UNASSIGNED, KEY, HEX64, LENSES, VP07Error, need, keys, clean,
                     check_edge_styles, check_binding)
from .phases import PhasesPrinter, CELL_071

FORMAT = 'aiaeao.cube.vp07-migration-source/1'
LIMITS = {'rows': 200, 'objects': 200, 'cells': 5000, 'transitions': 1000}
REQUIRED = ('format', 'profile', 'reference_version', 'context_id', 'plan_id', 'source_context_sha256', 'title', 'steps', 'rows',
            'objects', 'cells', 'transitions', 'facet_bindings', 'declaration_status')
OPTIONAL = ('edge_styles',)


def validate_source(src):
    need(isinstance(src, dict) and src.get('format') == FORMAT, 'VP07_SOURCE_INVALID',
         'input is not an '+FORMAT+' document (a VP-04 request or VP-03 bundle cannot be partitioned, D-10)')
    v71 = src.get('profile') in V71UP
    v72 = src.get('profile') in V72UP
    v73 = src.get('profile') in V73UP
    keys(src, REQUIRED, OPTIONAL+(('target_step',) if v71 else ())+(('layer_order', 'layer_sequence') if v72 else ())
         + (('local_methods',) if v73 else ()), 'VP07_SOURCE_INVALID', 'migration source')
    need(src['profile'] in PROFILES and src['reference_version'] == 'v9.4', 'VP07_SOURCE_INVALID', 'wrong profile or reference_version')
    need(src['declaration_status'] == 'declared_unverified', 'VP07_SOURCE_INVALID', 'declaration_status must be declared_unverified')
    need(isinstance(src['source_context_sha256'], str) and HEX64.fullmatch(src['source_context_sha256']) is not None,
         'VP07_SOURCE_INVALID', 'source_context_sha256 must be 64 lowercase hex')
    for k in ('context_id', 'plan_id'):
        need(clean(src[k], 100), 'VP07_SOURCE_INVALID', k+' must be clean text')
    for k, lim in LIMITS.items():
        need(isinstance(src[k], list) and len(src[k]) <= lim, 'VP07_SOURCE_INVALID', f'{k} must be an array of <= {lim} (MS-2)')
    for o in src['objects']:
        need(isinstance(o, dict) and 'form_id' in o, 'VP07_SOURCE_INVALID', 'source objects need form_id (flow panels draw them as cards)')
    for c in src['cells']:
        need(isinstance(c, dict) and 'id' in c, 'VP07_SOURCE_INVALID', 'source cells need a stable id')
        need(v71 or not set(c) & set(CELL_071), 'VP07_SOURCE_INVALID', 'gap fields need profile '+P071+' (VP-07.1 §2)')
        need(v73 or 'method' not in c, 'VP07_SOURCE_INVALID', 'method fields need profile '+P073+' (VP-07.3 §2)')
    for t in src['transitions']:
        need(v71 or not (isinstance(t, dict) and 'code' in t), 'VP07_SOURCE_INVALID', 'transition codes need profile '+P071)
        need(v73 or not (isinstance(t, dict) and 'methods' in t), 'VP07_SOURCE_INVALID', 'method fields need profile '+P073+' (VP-07.3 §2)')
    if v73:
        _methods073(src)
    for it in src['rows']+src['objects']:
        need(isinstance(it, dict), 'VP07_SOURCE_INVALID', 'row and object must be objects')
        need(v72 or 'layer' not in it, 'VP07_SOURCE_INVALID', 'layer fields need profile '+P072+' (VP-07.2 §2)')
    layers = _layers072(src) if v72 else None
    tracks = Tracks()
    tracks.layers = layers['rows'] if layers else None
    tracks.methods = v73  # VP-07.4 PM-1: partition key `method` needs declared method fields (0.7.3+)
    for r in src['rows']:
        if 'track' in r:
            need(clean(r['track'], 40), 'VP07_SOURCE_INVALID', 'row track must be clean text <= 40')
            tracks[r['id']] = r['track']
    plan = as_plan(src, [r['id'] for r in src['rows']], src['cells'], src['steps'], 'detail', src['title'], full=True)
    d = PhasesPrinter().validate(plan)  # structural rules (VP07_PHASES_STEPS / VP07_PHASES_REFERENCE)
    used_rows = {c['row'] for c in d['cells']}
    used_objects = {c['object'] for c in d['cells']}
    need(used_rows == set(d['rows']), 'VP07_SOURCE_INVALID', 'every source row must be referenced by a cell (PE-3 coverage)')
    need(used_objects == set(d['objects']), 'VP07_SOURCE_INVALID', 'every source object must be referenced by a cell (PE-3 coverage)')
    targets = {'row': set(d['rows']), 'object': set(d['objects']), 'cell': {c['id'] for c in d['cells']}}
    need(isinstance(src['facet_bindings'], list), 'VP07_SOURCE_INVALID', 'facet_bindings must be an array')
    seen = set()
    for b in src['facet_bindings']:
        keys(b, ('lens', 'target_kind', 'target_id', 'declaration_ref', 'note', 'basis'), (), 'VP07_SOURCE_INVALID', 'facet binding')
        need(b['lens'] in LENSES, 'VP07_SOURCE_INVALID', 'unknown facet lens')
        need(b['target_kind'] in targets and b['target_id'] in targets[b['target_kind']], 'VP07_SOURCE_INVALID', 'facet target not in source')
        need(clean(b['declaration_ref'], 180) and b['declaration_ref'].startswith(('decl:', 'fixture:')), 'VP07_SOURCE_INVALID',
             'facet declaration_ref must be scoped decl: or fixture:')
        need(clean(b['note'], 80) and b['basis'] == 'declared_unverified', 'VP07_SOURCE_INVALID', 'facet note <= 80, basis declared_unverified')
        key = (b['lens'], b['target_kind'], b['target_id'])
        need(key not in seen, 'VP07_SOURCE_INVALID', 'duplicate facet target for one lens')
        seen.add(key)
    styles = check_edge_styles(src['edge_styles']) if 'edge_styles' in src else None
    ends = {}
    if v71:
        ends = {c['id']: (c.get('declared_end') or 'target') for c in d['cells']}
        for g in PhasesPrinter.gaps(d):
            ends[g['cell_id']] = 'unexplained'
        for c in d['cells']:
            if 'declared_end' not in c and ends[c['id']] != 'unexplained':
                ends[c['id']] = _explained(d, c)
    return {'derived': d, 'tracks': tracks, 'styles': styles, 'declared_ends': ends, 'layers': layers}


def _methods073(src):
    """VP-07.3 MT-1…MT-3: declared bindings on transitions (`methods`) and cells (`method`); catalog or local methods only."""
    local = src.get('local_methods', [])
    need(isinstance(local, list) and all(clean(m, 100) for m in local) and len(set(local)) == len(local), 'VP07_SOURCE_INVALID',
         'local_methods must be distinct method IDs')
    for t in src['transitions']:
        if isinstance(t, dict) and 'methods' in t:
            need(isinstance(t['methods'], list) and t['methods'], 'VP07_SOURCE_INVALID', 'transition methods must be a nonempty array')
            for b in t['methods']:
                check_binding(b, local, 'transition '+str(t.get('id')))
    for c in src['cells']:
        if 'method' in c:
            check_binding(c['method'], local, 'cell '+str(c.get('id')))


class Tracks(dict):
    """Declared track map (row → track); `.layers` carries the VP-07.2 row → layer map (None before 0.7.2);
    `.methods` is True for sources with VP-07.3 method fields."""
    layers = None
    methods = False


def _layers072(src):
    """VP-07.2 LS-2: layer_order, layer_sequence and per-item layer must agree; None without layers."""
    items = src['rows']+src['objects']
    has = 'layer_order' in src or 'layer_sequence' in src or any('layer' in it for it in items)
    if not has:
        return None
    lo, seq = src.get('layer_order'), src.get('layer_sequence')
    need(isinstance(lo, list) and 1 <= len(lo) <= 13 and all(clean(x, 24) for x in lo) and len(set(lo)) == len(lo), 'VP07_SOURCE_INVALID',
         'layer_order must be 1…13 distinct clean names <= 24 (LS-2)')
    need(UNASSIGNED not in lo[:-1], 'VP07_SOURCE_INVALID', 'reserved layer unassigned may only be last (D-4)')
    of = {}
    for it in items:
        need(it.get('layer') in lo, 'VP07_SOURCE_INVALID', 'item '+repr(it.get('id'))+' has no layer of layer_order (LS-2)')
        need(of.get(it['id'], it['layer']) == it['layer'], 'VP07_SOURCE_INVALID', 'item '+repr(it['id'])+' is in two layers')
        of[it['id']] = it['layer']
    need(isinstance(seq, list) and sorted(seq) == sorted(of) and len(set(seq)) == len(seq), 'VP07_SOURCE_INVALID',
         'layer_sequence must list every layered row and object once (LS-2)')
    idx = [lo.index(of[i]) for i in seq]
    need(idx == sorted(idx), 'VP07_SOURCE_INVALID', 'layer_sequence must follow layer_order (LS-2)')
    return {'order': lo, 'of': of, 'seq': {i: k for k, i in enumerate(seq)},
            'rows': {r['id']: r['layer'] for r in src['rows']}}


def layer_key(layers, item_id):
    """LO-1 sort key: (layer index, position in the declared sequence)."""
    return (layers['order'].index(layers['of'][item_id]), layers['seq'][item_id])


def _explained(d, c):
    """Which declaration explains the end of a non-gap cell on the full source (GM-3 transcription)."""
    k = d['index'][c['steps'][-1]]
    if k >= d['tindex']:
        return 'target'
    R = {}
    for t in d['transitions']:
        for r in t['retires']:
            R[r] = min(R.get(r, 99999), d['index'][t['at']])
    if c['object'] in R and R[c['object']] <= k+1:
        return 'object_retired'
    if c['row'] in R and R[c['row']] <= k+1:
        return 'subject_retired'
    if 'successor' in c:
        return 'successor'
    if c.get('dropped'):
        return 'dropped'
    if 'ends_reason' in c:
        return 'ends_reason'
    return 'object_retired'  # conflicted referent (DG-7): reported by the conflict rules, never as a gap


def as_plan(src, row_ids, cells, steps, granularity, title, subtitle=None, full=False, ends=None):
    """Build a cube.phases plan. full=True keeps every row/object/transition verbatim (validation);
    otherwise objects and transitions are restricted to the panel's cells and step window."""
    rows = {r['id']: r for r in src['rows'] if isinstance(r, dict) and 'id' in r}
    used = []
    for c in cells:
        if isinstance(c, dict) and c.get('object') not in used:
            used.append(c.get('object'))
    v71 = src.get('profile') in V71UP
    plan = {'printer_profile': src['profile'] if v71 else PROFILE, 'reference_version': 'v9.4', 'view': 'cube.phases', 'lens': 'neutral',
            'granularity': granularity, 'title': title, 'steps': copy.deepcopy(steps),
            'rows': [{k: v for k, v in rows[r].items() if k not in ('track', 'layer')} for r in row_ids if r in rows],
            'objects': [{k: v for k, v in o.items() if k != 'layer'} for o in copy.deepcopy(src['objects'])
                        if full or o.get('id') in used],
            'cells': copy.deepcopy(cells), 'transitions': [], 'declaration_status': 'declared_unverified'}
    if full:
        plan['transitions'] = copy.deepcopy(src['transitions'])
    else:
        step_ids = {s['id'] for s in steps}
        vis = set(used) | (set(row_ids) if v71 else set())
        for k, t in enumerate(src['transitions']):
            ret = [o for o in t['retires'] if o in vis]
            intro = [o for o in t['introduces'] if o in vis]
            if t['at'] in step_ids and (ret or intro):
                x = {**copy.deepcopy(t), 'retires': ret, 'introduces': intro}
                if v71:
                    x['code'] = t.get('code', 'T'+str(k+1))  # TM-1: source numbering kept in every panel
                plan['transitions'].append(x)
        if v71 and ends:
            for c in plan['cells']:
                c.setdefault('declared_end', ends[c['id']])  # GM-3: end explained on the full source
    if v71:
        plan['target_step'] = src.get('target_step', src['steps'][-1]['id'])
    if src.get('profile') in V73UP and src.get('local_methods'):
        plan['local_methods'] = list(src['local_methods'])
    if src.get('profile') in V72UP and 'layer_order' in src:
        plan['layer_order'] = list(src['layer_order'])
        plan['row_layers'] = {r: rows[r]['layer'] for r in row_ids if r in rows}
    if 'edge_styles' in src:
        plan['edge_styles'] = copy.deepcopy(src['edge_styles'])
    if subtitle:
        plan['subtitle'] = subtitle
    return plan
