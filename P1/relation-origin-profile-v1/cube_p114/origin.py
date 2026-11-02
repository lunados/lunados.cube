"""Shape checks and /9 projection for binding-context/10."""
from __future__ import annotations

import copy
import re

from cube_p113.control_flow import FORMAT9
from cube_p112.coverage import CoverageProfileError
from cube_p18.simulation import V2_TOP, V3_TOP
from cube_p19.comparison import V4_TOP
from cube_p110.migration import V5_TOP
from cube_p111.methods import V7_TOP
from cube_p112.coverage import V8_TOP
from cube_p113.control_flow import V9_TOP

FORMAT10 = 'aiaeao.cube.binding-context/10'
V10_TOP = ('origin_bases',)
SHA256 = re.compile(r'^[0-9a-f]{64}$')


def _need(ok, message):
    if not ok:
        raise CoverageProfileError(message)


def _str(value):
    return isinstance(value, str) and 0 < len(value) <= 512


def project_v9(ctx):
    """Discard P1.14 declarations only; all earlier declarations stay intact."""
    out = copy.deepcopy(ctx)
    out['format'] = FORMAT9
    out.pop('origin_bases', None)
    for pred in out.get('predicate_contracts', []):
        pred.pop('origin_binding', None)
    for plan in out.get('migration_plans', []):
        for dep in plan.get('dependencies', []):
            dep.pop('origin', None)
            dep.pop('basis', None)
    return out


def validate_context_v10(ctx, validate_v9):
    _need(isinstance(ctx, dict) and ctx.get('format') == FORMAT10, 'context/10: expected object and format')
    allowed = set(V2_TOP + V3_TOP + V4_TOP + V5_TOP + V7_TOP + V8_TOP + V9_TOP + V10_TOP)
    _need(not set(ctx) - allowed, f'context/10: unknown {sorted(set(ctx) - allowed)}')
    for i, pred in enumerate(ctx.get('predicate_contracts', [])):
        if 'origin_binding' in pred:
            _need(pred['origin_binding'] == 'required', f'/predicate_contracts/{i}/origin_binding: required only')
    bases = ctx.get('origin_bases', [])
    _need(isinstance(bases, list) and len(bases) <= 5000, '/origin_bases: array <= 5000')
    ids = set()
    for i, base in enumerate(bases):
        path = f'/origin_bases/{i}'
        _need(isinstance(base, dict), path + ': object')
        kind = base.get('kind')
        keys = ({'basis_id', 'kind', 'set_id', 'statement_ids', 'witness_ref'} if kind == 'statements'
                else {'basis_id', 'kind', 'record_sha256', 'statement_id', 'library_ref'} if kind == 'projection_record'
                else set())
        required = keys - ({'witness_ref'} if kind == 'statements' else set())
        _need(bool(keys) and required <= set(base) <= keys, path + ': invalid kind or fields')
        bid = base['basis_id']
        _need(_str(bid) and bid not in ids, path + '/basis_id: nonempty unique string')
        ids.add(bid)
        if kind == 'statements':
            statements = base['statement_ids']
            _need(_str(base['set_id']) and ('witness_ref' not in base or _str(base['witness_ref'])),
                  path + ': set_id required; witness_ref, if present, must be a string')
            _need(isinstance(statements, list) and 0 < len(statements) <= 5000 and
                  all(_str(s) for s in statements) and len(statements) == len(set(statements)),
                  path + '/statement_ids: nonempty unique strings')
        else:
            ref = base['library_ref']
            _need(isinstance(base['record_sha256'], str) and SHA256.fullmatch(base['record_sha256']) and
                  _str(base['statement_id']), path + ': record digest and statement_id required')
            _need(isinstance(ref, dict) and set(ref) == {'library_id', 'entry_id', 'revision', 'sha256'} and
                  ref['library_id'] == 'lunados.lib' and ref['entry_id'] == 'project.aggregate-relations' and
                  ref['revision'] == 'v1' and isinstance(ref['sha256'], str) and SHA256.fullmatch(ref['sha256']),
                  path + '/library_ref: project.aggregate-relations/v1 reference required')
    # Dependency origin/basis values are semantic findings (OR-2…OR-3), not
    # malformed context declarations. Their shape is checked after projection.
    validate_v9(project_v9(ctx))
    return ctx
