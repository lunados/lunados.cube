"""VP-07 migration source (MS-1…MS-3, D-10): the unbudgeted input of print-panels."""
from __future__ import annotations
import copy

from .common import PROFILE, KEY, HEX64, LENSES, VP07Error, need, keys, clean, check_edge_styles
from .phases import PhasesPrinter

FORMAT = 'aiaeao.cube.vp07-migration-source/1'
LIMITS = {'rows': 200, 'objects': 200, 'cells': 5000, 'transitions': 1000}
REQUIRED = ('format', 'profile', 'reference_version', 'context_id', 'plan_id', 'source_context_sha256', 'title', 'steps', 'rows',
            'objects', 'cells', 'transitions', 'facet_bindings', 'declaration_status')
OPTIONAL = ('edge_styles',)


def validate_source(src):
    need(isinstance(src, dict) and src.get('format') == FORMAT, 'VP07_SOURCE_INVALID',
         'input is not an '+FORMAT+' document (a VP-04 request or VP-03 bundle cannot be partitioned, D-10)')
    keys(src, REQUIRED, OPTIONAL, 'VP07_SOURCE_INVALID', 'migration source')
    need(src['profile'] == PROFILE and src['reference_version'] == 'v9.4', 'VP07_SOURCE_INVALID', 'wrong profile or reference_version')
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
    return {'derived': d, 'tracks': tracks, 'styles': styles}


def as_plan(src, row_ids, cells, steps, granularity, title, subtitle=None, full=False):
    """Build a cube.phases plan. full=True keeps every row/object/transition verbatim (validation);
    otherwise objects and transitions are restricted to the panel's cells and step window."""
    rows = {r['id']: r for r in src['rows'] if isinstance(r, dict) and 'id' in r}
    used = []
    for c in cells:
        if isinstance(c, dict) and c.get('object') not in used:
            used.append(c.get('object'))
    plan = {'printer_profile': PROFILE, 'reference_version': 'v9.4', 'view': 'cube.phases', 'lens': 'neutral',
            'granularity': granularity, 'title': title, 'steps': copy.deepcopy(steps),
            'rows': [{k: v for k, v in rows[r].items() if k != 'track'} for r in row_ids if r in rows],
            'objects': copy.deepcopy(src['objects']) if full else [copy.deepcopy(o) for o in src['objects'] if o.get('id') in used],
            'cells': copy.deepcopy(cells), 'transitions': [], 'declaration_status': 'declared_unverified'}
    if full:
        plan['transitions'] = copy.deepcopy(src['transitions'])
    else:
        step_ids = {s['id'] for s in steps}
        for t in src['transitions']:
            ret = [o for o in t['retires'] if o in used]
            intro = [o for o in t['introduces'] if o in used]
            if t['at'] in step_ids and (ret or intro):
                plan['transitions'].append({**copy.deepcopy(t), 'retires': ret, 'introduces': intro})
    if 'edge_styles' in src:
        plan['edge_styles'] = copy.deepcopy(src['edge_styles'])
    if subtitle:
        plan['subtitle'] = subtitle
    return plan
