"""P1.9 /4 context validation: comparison protocols, comparisons, replay fields.

Descriptive only. Nothing here computes a statistic, opens a unit list,
checks that parity held, re-runs an evaluator or recomputes a digest.
"""
from __future__ import annotations
import copy

from cube_p18.simulation import (SimulationError, ORIGINS, METHOD_ID, SHA_HEX, DIGEST,
                                 _ne, _shape, _idlist, FORMAT3, V2_TOP, V3_TOP,
                                 validate_context_v3 as _validate_v3)

FORMAT4 = 'aiaeao.cube.binding-context/4'
V4_TOP = ('comparison_protocols', 'comparisons')
RECORD_EXTRA = ('replay_of', 'output_digest')
DIRECTIONS = ('lower_better', 'higher_better', 'none')
NONCOMP = ('report_incomparable', 'report_undetermined')
ROLES = ('control', 'treatment', 'reference')
UNITS = ('world', 'seed', 'cell', 'world_seed')
PARITY_KINDS = ('result_equivalence', 'coverage', 'digest_equal', 'declared_other')
STAT_KINDS = ('delta_a_minus_b', 'ratio_a_over_b', 'interval_a_minus_b', 'declared_other')
OUTCOMES = ('a_preferred', 'b_preferred', 'equivalent_under_criteria',
            'incomparable_under_criteria', 'undetermined_with_available_evidence')


class ComparisonError(SimulationError):
    """Invalid caller /4 configuration (MCP config error), never a semantic FAIL."""


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and v == v and v not in (float('inf'), float('-inf'))


def _scalar(v):
    return v is None or isinstance(v, (str, int, float, bool))


def _strlist(v, path, allow_empty=True):
    if not isinstance(v, list) or (not allow_empty and not v) or not all(_ne(x) for x in v) or len(v) != len(set(v)):
        raise ComparisonError(path + ': expected unique string array')


def project_v3(ctx):
    """Lossless view for the unchanged P1.8 path: drop only /4 additions."""
    out = copy.deepcopy(ctx)
    out['format'] = FORMAT3
    for k in V4_TOP:
        out.pop(k, None)
    for r in out.get('evaluation_records', []):
        if isinstance(r, dict):
            for k in RECORD_EXTRA:
                r.pop(k, None)
    return out


def validate_context_v4(ctx, v2_validator, legacy_validator, concepts):
    if not isinstance(ctx, dict):
        raise ComparisonError('context/4: expected object')
    extra = set(ctx) - set(V2_TOP + V3_TOP + V4_TOP)
    if extra:
        raise ComparisonError(f'context/4: unknown {sorted(extra)}')
    if ctx.get('format') != FORMAT4:
        raise ComparisonError('Unsupported context format')
    # Record-level /4 fields are checked here, then removed for the frozen /3 path.
    rec_ids = []
    for i, r in enumerate(ctx.get('evaluation_records', [])):
        if not isinstance(r, dict):
            continue
        path = f'/evaluation_records/{i}'
        if 'replay_of' in r and (not _ne(r['replay_of']) or r['replay_of'] == r.get('record_id')):
            raise ComparisonError(path + ': replay_of must name another record')
        if 'output_digest' in r and (not isinstance(r['output_digest'], str) or DIGEST.fullmatch(r['output_digest']) is None):
            raise ComparisonError(path + ': output_digest must be sha256:<64 lowercase hex>')
        rec_ids.append(r.get('record_id'))
    _validate_v3(project_v3(ctx), v2_validator, legacy_validator, concepts)

    methods = {m['method_id']: m for m in ctx.get('method_contracts', [])}
    seen = set()
    for i, p in enumerate(ctx.get('comparison_protocols', [])):
        path = f'/comparison_protocols/{i}'
        _shape(p, ('protocol_id', 'revision', 'scope', 'origin', 'criteria', 'equivalence_margin',
                   'non_comparability', 'aggregation', 'required_parity', 'library_ref'),
               ('protocol_id', 'revision', 'scope', 'origin', 'criteria', 'non_comparability', 'aggregation'), path)
        if not all(_ne(p[k]) for k in ('protocol_id', 'revision', 'scope')) or p['origin'] not in ORIGINS:
            raise ComparisonError(path + ': invalid protocol metadata')
        if p['protocol_id'] in seen:
            raise ComparisonError(path + ': duplicate protocol_id')
        seen.add(p['protocol_id'])
        if not isinstance(p['criteria'], list) or not p['criteria']:
            raise ComparisonError(path + '/criteria: expected nonempty array (CP-1)')
        mids = set()
        for j, c in enumerate(p['criteria']):
            cp = f'{path}/criteria/{j}'
            _shape(c, ('metric_id', 'direction', 'unit'), ('metric_id', 'direction'), cp)
            if not _ne(c['metric_id']) or c['metric_id'] in mids or c['direction'] not in DIRECTIONS:
                raise ComparisonError(cp + ': invalid or duplicate metric (CP-1)')
            if 'unit' in c and not _ne(c['unit']):
                raise ComparisonError(cp + ': invalid unit')
            mids.add(c['metric_id'])
        marg = p.get('equivalence_margin', {})
        if not isinstance(marg, dict) or not all(k in mids and _num(v) and v >= 0 for k, v in marg.items()):
            raise ComparisonError(path + '/equivalence_margin: non-negative numbers for declared metrics only (CP-3)')
        if p['non_comparability'] not in NONCOMP:
            raise ComparisonError(path + ': invalid non_comparability (CP-4)')
        agg = p['aggregation']
        if agg != 'none':
            m = methods.get(agg) if isinstance(agg, str) else None
            if m is None or METHOD_ID.fullmatch(agg) is None or m.get('effect_class') != 'pure_declarative':
                raise ComparisonError(path + ': aggregation must be "none" or a declared pure_declarative method (CP-2)')
        if 'required_parity' in p:
            _strlist(p['required_parity'], path + '/required_parity')
            if not all(k in PARITY_KINDS for k in p['required_parity']):
                raise ComparisonError(path + ': unknown parity kind (CP-5)')
        if 'library_ref' in p:
            lib = p['library_ref']
            _shape(lib, ('library_id', 'entry_id', 'revision', 'sha256'), ('library_id', 'entry_id', 'revision', 'sha256'), path + '/library_ref')
            if not all(_ne(lib[k]) for k in ('library_id', 'entry_id', 'revision')) or \
               not isinstance(lib['sha256'], str) or SHA_HEX.fullmatch(lib['sha256']) is None:
                raise ComparisonError(path + ': malformed library_ref')

    seen = set()
    for i, c in enumerate(ctx.get('comparisons', [])):
        path = f'/comparisons/{i}'
        _shape(c, ('comparison_id', 'protocol_ref', 'scope', 'origin', 'arms', 'pairing', 'parity', 'splits', 'design', 'outcomes'),
               ('comparison_id', 'protocol_ref', 'scope', 'arms', 'pairing'), path)
        if not all(_ne(c[k]) for k in ('comparison_id', 'protocol_ref', 'scope')):
            raise ComparisonError(path + ': invalid comparison metadata')
        if 'origin' in c and c['origin'] not in ORIGINS:
            raise ComparisonError(path + ': invalid origin')
        if c['comparison_id'] in seen:
            raise ComparisonError(path + ': duplicate comparison_id')
        seen.add(c['comparison_id'])
        if not isinstance(c['arms'], list):
            raise ComparisonError(path + '/arms: expected array')
        aids = set()
        for j, a in enumerate(c['arms']):
            ap = f'{path}/arms/{j}'
            _shape(a, ('arm_id', 'scenario_ref', 'role'), ('arm_id', 'scenario_ref', 'role'), ap)
            if not _ne(a['arm_id']) or not _ne(a['scenario_ref']) or a['arm_id'] in aids or a['role'] not in ROLES:
                raise ComparisonError(ap + ': invalid or duplicate arm (AR-1)')
            aids.add(a['arm_id'])
        pr = c['pairing']
        _shape(pr, ('unit', 'units_ref', 'shared_parameters', 'varied_parameters'),
               ('unit', 'units_ref', 'shared_parameters', 'varied_parameters'), path + '/pairing')
        if pr['unit'] not in UNITS or not _ne(pr['units_ref']):
            raise ComparisonError(path + '/pairing: invalid unit or units_ref (AR-2)')
        _strlist(pr['shared_parameters'], path + '/pairing/shared_parameters')
        _strlist(pr['varied_parameters'], path + '/pairing/varied_parameters')
        if set(pr['shared_parameters']) & set(pr['varied_parameters']):
            raise ComparisonError(path + '/pairing: a parameter cannot be both shared and varied (AR-3)')
        for j, q in enumerate(c.get('parity', [])):
            qp = f'{path}/parity/{j}'
            _shape(q, ('parity_id', 'kind', 'witness_ref', 'arm_refs'), ('parity_id', 'kind'), qp)
            if not _ne(q['parity_id']) or q['kind'] not in PARITY_KINDS:
                raise ComparisonError(qp + ': invalid parity (AR-5)')
            if 'witness_ref' in q and not _ne(q['witness_ref']):
                raise ComparisonError(qp + ': invalid witness_ref')
            if 'arm_refs' in q:
                _strlist(q['arm_refs'], qp + '/arm_refs', allow_empty=False)
        if 'splits' in c:
            _strlist(c['splits'], path + '/splits', allow_empty=False)
        if 'design' in c:
            _shape(c['design'], ('factors',), ('factors',), path + '/design')
            f = c['design']['factors']
            if not isinstance(f, dict) or not f or not all(_ne(k) and isinstance(v, list) and v and all(_scalar(x) for x in v) for k, v in f.items()):
                raise ComparisonError(path + '/design/factors: factor -> nonempty list of JSON scalars')
        oids = set()
        for j, o in enumerate(c.get('outcomes', [])):
            op = f'{path}/outcomes/{j}'
            _shape(o, ('outcome_id', 'a', 'b', 'metric_id', 'metric_ids', 'outcome', 'scope', 'split', 'statistic',
                       'annotation_ref', 'witness_ref'), ('outcome_id', 'a', 'b', 'outcome', 'annotation_ref'), op)
            if not all(_ne(o[k]) for k in ('outcome_id', 'a', 'b', 'outcome', 'annotation_ref')) or o['outcome_id'] in oids:
                raise ComparisonError(op + ': invalid or duplicate outcome')
            oids.add(o['outcome_id'])
            if o['a'] == o['b']:
                raise ComparisonError(op + ': an outcome compares two different arms (OC-2)')
            if ('metric_id' in o) == ('metric_ids' in o):
                raise ComparisonError(op + ': exactly one of metric_id / metric_ids (OC-2)')
            if 'metric_id' in o and not _ne(o['metric_id']):
                raise ComparisonError(op + ': invalid metric_id')
            if 'metric_ids' in o:
                _strlist(o['metric_ids'], op + '/metric_ids', allow_empty=False)
            if 'scope' in o and (not isinstance(o['scope'], dict) or not o['scope'] or
                                 not all(_ne(k) and _scalar(v) for k, v in o['scope'].items())):
                raise ComparisonError(op + '/scope: factor -> JSON scalar')
            if 'split' in o and not _ne(o['split']):
                raise ComparisonError(op + ': invalid split')
            if 'witness_ref' in o and not _ne(o['witness_ref']):
                raise ComparisonError(op + ': invalid witness_ref')
            if 'statistic' in o:
                st = o['statistic']
                _shape(st, ('kind', 'declared_value'), ('kind', 'declared_value'), op + '/statistic')
                if st['kind'] not in STAT_KINDS:
                    raise ComparisonError(op + '/statistic: invalid kind (OC-4)')
                v = st['declared_value']
                if st['kind'] == 'interval_a_minus_b':
                    if not (isinstance(v, list) and len(v) == 2 and all(_num(x) for x in v) and v[0] <= v[1]):
                        raise ComparisonError(op + '/statistic: interval must be [lo, hi]')
                elif st['kind'] != 'declared_other' and not _num(v):
                    raise ComparisonError(op + '/statistic: declared_value must be a number')
                elif st['kind'] == 'ratio_a_over_b' and v <= 0:
                    raise ComparisonError(op + '/statistic: ratio must be positive')
    return ctx
