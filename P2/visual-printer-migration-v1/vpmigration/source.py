"""VP-07 migration source (MS-1…MS-3, D-10): the unbudgeted input of print-panels."""
from __future__ import annotations
import copy

from .common import PROFILE, PROFILES, P071, KEY, HEX64, LENSES, VP07Error, need, keys, clean, check_edge_styles
from .phases import PhasesPrinter, CELL_071

FORMAT = 'aiaeao.cube.vp07-migration-source/1'
LIMITS = {'rows': 200, 'objects': 200, 'cells': 5000, 'transitions': 1000}
REQUIRED = ('format', 'profile', 'reference_version', 'context_id', 'plan_id', 'source_context_sha256', 'title', 'steps', 'rows',
            'objects', 'cells', 'transitions', 'facet_bindings', 'declaration_status')
OPTIONAL = ('edge_styles',)


def validate_source(src):
    need(isinstance(src, dict) and src.get('format') == FORMAT, 'VP07_SOURCE_INVALID',
         'input is not an '+FORMAT+' document (a VP-04 request or VP-03 bundle cannot be partitioned, D-10)')
    v71 = src.get('profile') == P071
    keys(src, REQUIRED, OPTIONAL+(('target_step',) if v71 else ()), 'VP07_SOURCE_INVALID', 'migration source')
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
    for t in src['transitions']:
        need(v71 or not (isinstance(t, dict) and 'code' in t), 'VP07_SOURCE_INVALID', 'transition codes need profile '+P071)
    tracks = {}
    for r in src['rows']:
        need(isinstance(r, dict), 'VP07_SOURCE_INVALID', 'row must be an object')
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
    return {'derived': d, 'tracks': tracks, 'styles': styles, 'declared_ends': ends}


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
    v71 = src.get('profile') == P071
    plan = {'printer_profile': P071 if v71 else PROFILE, 'reference_version': 'v9.4', 'view': 'cube.phases', 'lens': 'neutral',
            'granularity': granularity, 'title': title, 'steps': copy.deepcopy(steps),
            'rows': [{k: v for k, v in rows[r].items() if k != 'track'} for r in row_ids if r in rows],
            'objects': copy.deepcopy(src['objects']) if full else [copy.deepcopy(o) for o in src['objects'] if o.get('id') in used],
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
    if 'edge_styles' in src:
        plan['edge_styles'] = copy.deepcopy(src['edge_styles'])
    if subtitle:
        plan['subtitle'] = subtitle
    return plan
