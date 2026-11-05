"""Shape checks, reference v2 and /10 projection for binding-context/11 (P1.15)."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from cube_p112.coverage import CoverageProfileError
from cube_p16.instantiation import reference as reference_v1
from cube_p18.simulation import V2_TOP, V3_TOP
from cube_p19.comparison import V4_TOP
from cube_p110.migration import V5_TOP
from cube_p111.methods import V7_TOP
from cube_p112.coverage import V8_TOP
from cube_p113.control_flow import V9_TOP
from cube_p114.origin import FORMAT10, V10_TOP

FORMAT11 = 'aiaeao.cube.binding-context/11'
V11_TOP = ('scope_nesting',)
VOCAB_V2 = Path(__file__).resolve().parents[1] / 'instantiation_reference_v2.json'
VOCAB_V2_SHA256 = 'de8f042c9433ca2047957e53c557c8d82038b52f83787243991b22cd5cdb1754'


def _need(ok, message):
    if not ok:
        raise CoverageProfileError(message)


def _str(value):
    return isinstance(value, str) and 0 < len(value) <= 512


def reference_v2():
    raw = VOCAB_V2.read_bytes()
    _need(hashlib.sha256(raw).hexdigest() == VOCAB_V2_SHA256, 'P1.15 reference v2 sha256 mismatch; fail closed')
    doc = json.loads(raw)
    _need(len(doc.get('endpoints', [])) == 10 and doc.get('reference_version') == 'v9.4', 'Invalid P1.15 reference v2')
    return {e['concept_id']: e for e in doc['endpoints']}, doc


def project_v10(ctx):
    """Drop P1.15 declarations and narrow instantiation profiles to reference v1 for the unchanged lower layers.
    X-endpoint results of the lower layers are superseded by P1.15 (SN-4, SN-6)."""
    out = copy.deepcopy(ctx)
    out['format'] = FORMAT10
    out.pop('scope_nesting', None)
    v1 = reference_v1()
    for prof in out.get('instantiation_profiles', []):
        base = {s['name']: s for s in v1.get(prof.get('concept_id'), {}).get('slots', [])}
        for slot in prof.get('slots', []):
            b = base.get(slot.get('name'))
            if b and slot.get('kind') == 'ref' and isinstance(slot.get('concept_ids'), list):
                narrowed = [c for c in slot['concept_ids'] if c in b['concept_ids']]
                slot['concept_ids'] = narrowed or list(b['concept_ids'])
    return out


def _check_profiles_v2(ctx):
    eps, _ = reference_v2()
    for i, p in enumerate(ctx.get('instantiation_profiles', [])):
        path = f'/instantiation_profiles/{i}'
        if not isinstance(p, dict) or p.get('concept_id') not in eps or not isinstance(p.get('slots'), list):
            continue  # shape errors are reported by the lower layers on the projection
        base = {s['name']: s for s in eps[p['concept_id']]['slots']}
        for j, s in enumerate(p['slots']):
            b = base.get(s.get('name')) if isinstance(s, dict) else None
            if b and s.get('kind') == 'ref' and isinstance(s.get('concept_ids'), list):
                _need(set(s['concept_ids']) <= set(b['concept_ids']), f'{path}/slots/{j}: widens reference v2')


def validate_context_v11(ctx, validate_v10):
    _need(isinstance(ctx, dict) and ctx.get('format') == FORMAT11, 'context/11: expected object and format')
    allowed = set(V2_TOP + V3_TOP + V4_TOP + V5_TOP + V7_TOP + V8_TOP + V9_TOP + V10_TOP + V11_TOP)
    _need(not set(ctx) - allowed, f'context/11: unknown {sorted(set(ctx) - allowed)}')
    nest = ctx.get('scope_nesting', [])
    _need(isinstance(nest, list) and len(nest) <= 512, '/scope_nesting: array <= 512 (SN-1)')
    inners = set()
    for i, n in enumerate(nest):
        path = f'/scope_nesting/{i}'
        _need(isinstance(n, dict) and set(n) == {'inner', 'outer'}, path + ': exactly inner and outer (SN-1)')
        _need(_str(n['inner']) and _str(n['outer']) and n['inner'] != n['outer'], path + ': nonempty, distinct strings (SN-1)')
        _need(n['inner'] not in inners, path + '/inner: one parent per scope (SN-1)')
        inners.add(n['inner'])
    _check_profiles_v2(ctx)
    validate_v10(project_v10(ctx))
    return ctx
