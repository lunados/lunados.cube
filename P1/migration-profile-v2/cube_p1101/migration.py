"""P1.10.1 /6 context validation: /5 plus optional dependency `ends_reason` (DG-6).

Descriptive only. Nothing here probes a live system or decides why a dependency ends.
"""
from __future__ import annotations
import copy

from cube_p110.migration import FORMAT5, MigrationError, V5_TOP, validate_context_v5 as _validate_v5
from cube_p18.simulation import V2_TOP, V3_TOP, _ne
from cube_p19.comparison import V4_TOP

FORMAT6 = 'aiaeao.cube.binding-context/6'
END_REASONS = ('scope_end', 'replaced_outside_plan', 'other')


class RevisionError(MigrationError):
    """Invalid caller /6 configuration (MCP config error), never a semantic FAIL."""


def project_v5(ctx):
    """Lossless view for the unchanged P1.10 path: format /5, `ends_reason` removed."""
    out = copy.deepcopy(ctx)
    out['format'] = FORMAT5
    for mp in out.get('migration_plans', []) if isinstance(out.get('migration_plans'), list) else []:
        if isinstance(mp, dict):
            for d in mp.get('dependencies', []) if isinstance(mp.get('dependencies'), list) else []:
                if isinstance(d, dict):
                    d.pop('ends_reason', None)
    return out


def validate_context_v6(ctx, v2_validator, legacy_validator, concepts):
    if not isinstance(ctx, dict):
        raise RevisionError('context/6: expected object')
    extra = set(ctx) - set(V2_TOP + V3_TOP + V4_TOP + V5_TOP)
    if extra:
        raise RevisionError(f'context/6: unknown {sorted(extra)}')
    if ctx.get('format') != FORMAT6:
        raise RevisionError('Unsupported context format')
    for i, mp in enumerate(ctx.get('migration_plans', []) if isinstance(ctx.get('migration_plans'), list) else []):
        for j, d in enumerate(mp.get('dependencies', []) if isinstance(mp, dict) and isinstance(mp.get('dependencies'), list) else []):
            if isinstance(d, dict) and 'ends_reason' in d:
                r = d['ends_reason']
                if not _ne(r) or len(r) > 40:
                    raise RevisionError(f'/migration_plans/{i}/dependencies/{j}/ends_reason: nonempty string <= 40 (DG-6)')
    _validate_v5(project_v5(ctx), v2_validator, legacy_validator, concepts)
    return ctx
