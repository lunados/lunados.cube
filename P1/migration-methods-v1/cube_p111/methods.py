"""P1.11 /7 context validation: /6 plus a pinned migration method catalog and method bindings.

Descriptive only. Nothing here runs, schedules, ranks or admits a method.
"""
from __future__ import annotations
import copy, hashlib, json
from pathlib import Path

from cube_p1101.migration import FORMAT6, RevisionError, validate_context_v6 as _validate_v6
from cube_p110.migration import V5_TOP
from cube_p18.simulation import V2_TOP, V3_TOP, _ne
from cube_p19.comparison import V4_TOP

FORMAT7 = 'aiaeao.cube.binding-context/7'
V7_TOP = ('method_profile_refs',)
PROFILE_ORIGIN = 'profile_declaration_unverified'
_PDIR = Path(__file__).resolve().parent / 'profiles'
# MC-1: pinned catalogs. The SHA-256 is fixed here and in SHA256SUMS.txt; a changed file is refused.
PINNED = {
    'P1.11/migration-methods-v1': ('migration-methods-v1.json',
                                   '5e317bce914609f42bbcbe8b22edd2989a63247686de840faae63f686f6b4c49'),
}
_CACHE: dict = {}


class MethodProfileError(RevisionError):
    """Invalid caller /7 configuration (MCP config error), never a semantic FAIL."""


def load_catalog(profile_id):
    if profile_id not in PINNED:
        raise MethodProfileError('method_profile_refs: unknown or unpinned catalog')
    if profile_id not in _CACHE:
        name, sha = PINNED[profile_id]
        raw = (_PDIR / name).read_bytes()
        if hashlib.sha256(raw).hexdigest() != sha:
            raise MethodProfileError('method catalog file does not match its pinned SHA-256')
        doc = json.loads(raw.decode('utf-8'))
        if doc.get('format') != 'aiaeao.cube.p1.11.method-profile/1' or doc.get('profile_id') != profile_id \
                or doc.get('reference_version') != 'v9.4':
            raise MethodProfileError('method catalog header mismatch')
        for m in doc['methods']:
            if m.get('origin') != PROFILE_ORIGIN or 'scope' in m or m.get('effect_class') != 'pure_declarative':
                raise MethodProfileError('catalog methods must be unscoped pure_declarative profile declarations (MC-2)')
            if not (m['argument_min'] == m['argument_max'] == len(m['roles'])):
                raise MethodProfileError('catalog roles must match argument_min/max (MC-2)')
        _CACHE[profile_id] = doc
    return _CACHE[profile_id]


def _ref_id(item):
    return item if isinstance(item, str) else item.get('profile_id') if isinstance(item, dict) else None


def catalog_methods(ctx):
    """{method_id: catalog entry} of every imported catalog (MI-1)."""
    out = {}
    for item in ctx.get('method_profile_refs', []):
        for m in load_catalog(_ref_id(item))['methods']:
            if m['method_id'] in out:
                raise MethodProfileError('two imported catalogs define ' + m['method_id'])
            out[m['method_id']] = m
    return out


def _projected(m, scope):
    """MI-2: P1.8 method contract shape for the unchanged P1.4/P1.8 path; profile-only fields dropped (D-4)."""
    return {'method_id': m['method_id'], 'revision': m['revision'], 'scope': scope, 'origin': 'external_declaration_unverified',
            'argument_min': m['argument_min'], 'argument_max': m['argument_max'], 'effect_class': m['effect_class']}


def project_v6(ctx):
    """View for the unchanged P1.10.1 path: format /6, bindings removed, imported methods added as scoped contracts."""
    imported = catalog_methods(ctx)
    out = copy.deepcopy(ctx)
    out['format'] = FORMAT6
    out.pop('method_profile_refs', None)
    for mp in out.get('migration_plans', []) if isinstance(out.get('migration_plans'), list) else []:
        if not isinstance(mp, dict):
            continue
        for t in mp.get('transitions', []) if isinstance(mp.get('transitions'), list) else []:
            if isinstance(t, dict):
                t.pop('methods', None)
        for d in mp.get('dependencies', []) if isinstance(mp.get('dependencies'), list) else []:
            if isinstance(d, dict):
                d.pop('method', None)
    if imported:
        out['method_contracts'] = list(out.get('method_contracts', [])) + [_projected(m, ctx.get('scope_ref')) for m in imported.values()]
    return out


def _binding(b, path):
    """MB-1…MB-3 / MV-6: binding shape; shape errors are configuration errors."""
    if not isinstance(b, dict) or set(b) - {'method_id', 'arguments', 'witness_ref'} or not {'method_id', 'arguments'} <= set(b):
        raise MethodProfileError(f'{path}: binding needs method_id and arguments (optional witness_ref)')
    if not _ne(b['method_id']) or len(b['method_id']) > 120:
        raise MethodProfileError(f'{path}/method_id: nonempty string <= 120')
    a = b['arguments']
    if not isinstance(a, dict) or not a or not all(_ne(k) and _ne(v) for k, v in a.items()):
        raise MethodProfileError(f'{path}/arguments: nonempty object of role -> referent ref')
    if 'witness_ref' in b and not _ne(b['witness_ref']):
        raise MethodProfileError(f'{path}/witness_ref: nonempty string')


def validate_context_v7(ctx, v2_validator, legacy_validator, concepts):
    if not isinstance(ctx, dict):
        raise MethodProfileError('context/7: expected object')
    extra = set(ctx) - set(V2_TOP + V3_TOP + V4_TOP + V5_TOP + V7_TOP)
    if extra:
        raise MethodProfileError(f'context/7: unknown {sorted(extra)}')
    if ctx.get('format') != FORMAT7:
        raise MethodProfileError('Unsupported context format')
    refs = ctx.get('method_profile_refs', [])
    if not isinstance(refs, list) or len({_ref_id(r) for r in refs}) != len(refs):
        raise MethodProfileError('method_profile_refs: expected array of distinct catalog ids')
    imported = catalog_methods(ctx)
    for m in ctx.get('method_contracts', []) if isinstance(ctx.get('method_contracts'), list) else []:
        if isinstance(m, dict) and m.get('method_id') in imported:
            raise MethodProfileError('method_contracts: local contract redefines imported ' + m['method_id'])
    for i, mp in enumerate(ctx.get('migration_plans', []) if isinstance(ctx.get('migration_plans'), list) else []):
        if not isinstance(mp, dict):
            continue
        for j, t in enumerate(mp.get('transitions', []) if isinstance(mp.get('transitions'), list) else []):
            if isinstance(t, dict) and 'methods' in t:
                if not isinstance(t['methods'], list) or not t['methods']:
                    raise MethodProfileError(f'/migration_plans/{i}/transitions/{j}/methods: nonempty array')
                for k, b in enumerate(t['methods']):
                    _binding(b, f'/migration_plans/{i}/transitions/{j}/methods/{k}')
        for j, d in enumerate(mp.get('dependencies', []) if isinstance(mp.get('dependencies'), list) else []):
            if isinstance(d, dict) and 'method' in d:
                _binding(d['method'], f'/migration_plans/{i}/dependencies/{j}/method')
    _validate_v6(project_v6(ctx), v2_validator, legacy_validator, concepts)
    return ctx
