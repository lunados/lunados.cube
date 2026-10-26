"""P1.10 /5 context validation: predicate profile import, migration plan shapes, /4 projection.

Descriptive only. Nothing here probes a live system, discovers a dependency,
interprets a date or decides a migration order.
"""
from __future__ import annotations
import copy, hashlib, json
from pathlib import Path

from cube_p18.simulation import ORIGINS, SHA_HEX, _ne, _shape, V2_TOP, V3_TOP
from cube_p19.comparison import ComparisonError, V4_TOP, FORMAT4, validate_context_v4 as _validate_v4

FORMAT5 = 'aiaeao.cube.binding-context/5'
V5_TOP = ('predicate_profile_refs', 'migration_plans')
PROFILE_ORIGIN = 'profile_declaration_unverified'
PHASE_ROLES = ('current', 'intermediate', 'target')
KINDS = ('job', 'sync', 'dns', 'auth', 'account', 'api', 'data', 'docs', 'other')
_PDIR = Path(__file__).resolve().parent / 'profiles'
# PP-1: pinned profiles. The SHA-256 is fixed here and in SHA256SUMS.txt; a changed file is refused.
PINNED = {
    'P1.10/migration-predicates-v1': ('migration-predicates-v1.json',
                                      '93241f8345bcc2a96db28896e87783675555c68cd3e2f9cbe6cf7dc9790e6a29'),
}
_CACHE: dict = {}


class MigrationError(ComparisonError):
    """Invalid caller /5 configuration (MCP config error), never a semantic FAIL."""


def load_profile(profile_id):
    if profile_id not in PINNED:
        raise MigrationError('predicate_profile_refs: unknown or unpinned profile')
    if profile_id not in _CACHE:
        name, sha = PINNED[profile_id]
        raw = (_PDIR / name).read_bytes()
        if hashlib.sha256(raw).hexdigest() != sha:
            raise MigrationError('predicate profile file does not match its pinned SHA-256')
        doc = json.loads(raw.decode('utf-8'))
        if doc.get('format') != 'aiaeao.cube.p1.10.predicate-profile/1' or doc.get('profile_id') != profile_id \
                or doc.get('reference_version') != 'v9.4':
            raise MigrationError('predicate profile header mismatch')
        for c in doc['contracts']:
            if c.get('origin') != PROFILE_ORIGIN or 'scope' in c:
                raise MigrationError('profile contracts must be unscoped profile declarations')
        _CACHE[profile_id] = (doc, sha)
    return _CACHE[profile_id]


def _ref_id(item):
    return item if isinstance(item, str) else item.get('profile_id') if isinstance(item, dict) else None


def imported_contracts(ctx):
    """PP-5 / D-8: imported contracts bound to the importing context scope_ref."""
    out = []
    for item in ctx.get('predicate_profile_refs', []):
        doc, _ = load_profile(_ref_id(item))
        for c in doc['contracts']:
            e = copy.deepcopy(c)
            e['scope'] = ctx['scope_ref']
            out.append(e)
    return out


def project_v4(ctx):
    """View for the unchanged P1.9 path: drop /5 additions, add imported contracts.

    The frozen /1 origin enum does not know profile_declaration_unverified; on the
    projection, imported entries carry external_declaration_unverified. The report
    exposes no contract origin, so the frozen report is unaffected.
    """
    out = copy.deepcopy(ctx)
    out['format'] = FORMAT4
    imported = imported_contracts(ctx)
    for k in V5_TOP:
        out.pop(k, None)
    for e in imported:
        e['origin'] = 'external_declaration_unverified'
    out['predicate_contracts'] = list(out.get('predicate_contracts', [])) + imported
    return out


def _strset(v, path, allow_empty=True):
    if not isinstance(v, list) or (not allow_empty and not v) or not all(_ne(x) for x in v) or len(v) != len(set(v)):
        raise MigrationError(path + ': expected unique string array')


def validate_context_v5(ctx, v2_validator, legacy_validator, concepts):
    if not isinstance(ctx, dict):
        raise MigrationError('context/5: expected object')
    extra = set(ctx) - set(V2_TOP + V3_TOP + V4_TOP + V5_TOP)
    if extra:
        raise MigrationError(f'context/5: unknown {sorted(extra)}')
    if ctx.get('format') != FORMAT5:
        raise MigrationError('Unsupported context format')
    # Profile import (PP-1, D-3, D-8)
    refs = ctx.get('predicate_profile_refs', [])
    if not isinstance(refs, list) or len(refs) > 8:
        raise MigrationError('predicate_profile_refs: expected array')
    ids = []
    for i, item in enumerate(refs):
        path = f'/predicate_profile_refs/{i}'
        if isinstance(item, dict):
            _shape(item, ('profile_id', 'library_ref'), ('profile_id',), path)
            if 'library_ref' in item:
                lib = item['library_ref']
                _shape(lib, ('library_id', 'entry_id', 'revision', 'sha256'), ('library_id', 'entry_id', 'revision', 'sha256'), path + '/library_ref')
                if not all(_ne(lib[k]) for k in ('library_id', 'entry_id', 'revision')) or \
                   not isinstance(lib['sha256'], str) or SHA_HEX.fullmatch(lib['sha256']) is None:
                    raise MigrationError(path + ': malformed library_ref')
        elif not _ne(item):
            raise MigrationError(path + ': expected profile id')
        pid = _ref_id(item)
        _, sha = load_profile(pid)
        if isinstance(item, dict) and 'library_ref' in item and item['library_ref']['sha256'] != sha:
            raise MigrationError(path + ': library_ref SHA-256 differs from the pinned profile (D-3)')
        ids.append(pid)
    if len(ids) != len(set(ids)):
        raise MigrationError('predicate_profile_refs: duplicate profile')
    if refs and not _ne(ctx.get('scope_ref')):
        raise MigrationError('predicate_profile_refs require a context scope_ref (D-8)')
    imported = {c['predicate_id'] for c in imported_contracts(ctx)} if refs else set()
    for i, p in enumerate(ctx.get('predicate_contracts', []) if isinstance(ctx.get('predicate_contracts'), list) else []):
        if isinstance(p, dict) and p.get('predicate_id') in imported:
            raise MigrationError(f'/predicate_contracts/{i}: redefines an imported predicate (D-2)')

    # Plan shapes. Semantic findings (phases, references, ordering) are NOT raised here.
    plans = ctx.get('migration_plans', [])
    if not isinstance(plans, list) or len(plans) > 64:
        raise MigrationError('migration_plans: expected array')
    seen_plans = set()
    for i, mp in enumerate(plans):
        path = f'/migration_plans/{i}'
        _shape(mp, ('plan_id', 'revision', 'scope', 'origin', 'phases', 'transitions', 'dependencies'),
               ('plan_id', 'revision', 'scope', 'origin', 'phases', 'transitions', 'dependencies'), path)
        if not all(_ne(mp[k]) for k in ('plan_id', 'revision', 'scope')) or mp['origin'] not in ORIGINS:
            raise MigrationError(path + ': invalid plan metadata')
        if mp['plan_id'] in seen_plans:
            raise MigrationError(path + ': duplicate plan_id')
        seen_plans.add(mp['plan_id'])
        if not isinstance(mp['phases'], list) or not mp['phases']:
            raise MigrationError(path + '/phases: expected nonempty array')
        for j, ph in enumerate(mp['phases']):
            _shape(ph, ('phase_id', 'role'), ('phase_id', 'role'), f'{path}/phases/{j}')
            if not _ne(ph['phase_id']) or ph['role'] not in PHASE_ROLES:
                raise MigrationError(f'{path}/phases/{j}: invalid phase')
        if not isinstance(mp['transitions'], list) or len(mp['transitions']) > 1000:
            raise MigrationError(path + '/transitions: expected array')
        tids = set()
        for j, t in enumerate(mp['transitions']):
            tp = f'{path}/transitions/{j}'
            _shape(t, ('transition_id', 'at_phase', 'retires', 'introduces', 'T', 'witness_ref'),
                   ('transition_id', 'at_phase', 'retires', 'introduces'), tp)
            if not _ne(t['transition_id']) or t['transition_id'] in tids or not _ne(t['at_phase']):
                raise MigrationError(tp + ': invalid or duplicate transition')
            tids.add(t['transition_id'])
            _strset(t['retires'], tp + '/retires'); _strset(t['introduces'], tp + '/introduces')
            if 'T' in t:
                _shape(t['T'], ('role', 'value'), ('role',), tp + '/T')
                if not _ne(t['T']['role']) or ('value' in t['T'] and not isinstance(t['T']['value'], str)):
                    raise MigrationError(tp + '/T: role must be a string, value a string')
            if 'witness_ref' in t and not _ne(t['witness_ref']):
                raise MigrationError(tp + ': invalid witness_ref')
        if not isinstance(mp['dependencies'], list) or len(mp['dependencies']) > 5000:
            raise MigrationError(path + '/dependencies: expected array')
        dids = set()
        for j, d in enumerate(mp['dependencies']):
            dp = f'{path}/dependencies/{j}'
            _shape(d, ('dependency_id', 'subject', 'predicate_id', 'object', 'kind', 'holds_in',
                       'successor_ref', 'dropped', 'schedule', 'witness_ref'),
                   ('dependency_id', 'subject', 'predicate_id', 'object', 'kind', 'holds_in'), dp)
            if not all(_ne(d[k]) for k in ('dependency_id', 'subject', 'predicate_id', 'object')) or d['dependency_id'] in dids:
                raise MigrationError(dp + ': invalid or duplicate dependency')
            dids.add(d['dependency_id'])
            if d['kind'] not in KINDS:
                raise MigrationError(dp + ': kind outside the descriptive enum (DP-5)')
            _strset(d['holds_in'], dp + '/holds_in', allow_empty=False)
            for k in ('successor_ref', 'schedule', 'witness_ref'):
                if k in d and not _ne(d[k]):
                    raise MigrationError(f'{dp}/{k}: expected nonempty string')
            if 'dropped' in d and not isinstance(d['dropped'], bool):
                raise MigrationError(dp + '/dropped: expected boolean')
            if d.get('dropped') and 'successor_ref' in d:
                raise MigrationError(dp + ': successor_ref and dropped are exclusive (DP-4)')
            if d.get('successor_ref') == d['dependency_id']:
                raise MigrationError(dp + ': a dependency cannot succeed itself')
    _validate_v4(project_v4(ctx), v2_validator, legacy_validator, concepts)
    return ctx
