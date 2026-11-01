"""P1.12 /8 context validation: /7 plus coverage declarations, population rules and typed instance membership.

Descriptive only. Nothing here counts statements, infers coverage, or inspects a live system (spec §0, CV-5, PR-2).
"""
from __future__ import annotations
import copy

from cube_p111.methods import FORMAT7, MethodProfileError, V7_TOP
from cube_p110.migration import V5_TOP
from cube_p18.simulation import V2_TOP, V3_TOP, _ne
from cube_p19.comparison import V4_TOP

FORMAT8 = 'aiaeao.cube.binding-context/8'
V8_TOP = ('coverage_declarations', 'population_rules')
INSTANCE_CONCEPT = 'Y:identified-object:bounded-execution'
DIRECTIONS = ('outgoing', 'incoming')
KINDS = ('absence', 'count', 'join_activation')


class CoverageProfileError(MethodProfileError):
    """Invalid caller /8 configuration (MCP config error), never a semantic FAIL."""


def _need(cond, msg):
    if not cond:
        raise CoverageProfileError(msg)


def _str(v):
    return _ne(v) and len(v) <= 512


def _opt_instance(o, path):
    if 'instance_ref' in o:
        _need(_str(o['instance_ref']), f'{path}/instance_ref: nonempty string')


def _declaration(d, path):
    """CV-1 shape."""
    _need(isinstance(d, dict), f'{path}: object')
    _need(_str(d.get('declaration_id')) and _str(d.get('predicate_id')) and _str(d.get('witness_ref')),
          f'{path}: declaration_id, predicate_id and witness_ref are required nonempty strings')
    if d.get('scope') == 'referent_relation_direction':
        _need(set(d) <= {'declaration_id', 'scope', 'referent', 'predicate_id', 'direction', 'instance_ref', 'witness_ref'},
              f'{path}: unknown field')
        _need(_str(d.get('referent')) and d.get('direction') in DIRECTIONS, f'{path}: referent and direction (outgoing|incoming) required')
    elif d.get('scope') == 'pair':
        _need(set(d) <= {'declaration_id', 'scope', 'subject', 'predicate_id', 'object', 'instance_ref', 'witness_ref'},
              f'{path}: unknown field')
        _need(_str(d.get('subject')) and _str(d.get('object')), f'{path}: subject and object required')
    else:
        raise CoverageProfileError(f'{path}/scope: referent_relation_direction or pair (D-2; no view-level coverage)')
    _opt_instance(d, path)


def _rule(r, path):
    """PR-1 shape."""
    _need(isinstance(r, dict), f'{path}: object')
    _need(_str(r.get('rule_id')) and _str(r.get('predicate_id')) and _str(r.get('witness_ref')),
          f'{path}: rule_id, predicate_id and witness_ref are required nonempty strings')
    k = r.get('kind')
    _need(k in KINDS, f'{path}/kind: absence, count or join_activation')
    if k == 'count':
        _need(set(r) <= {'rule_id', 'kind', 'referent', 'predicate_id', 'direction', 'min', 'max', 'instance_ref', 'witness_ref'},
              f'{path}: unknown field')
        _need(_str(r.get('referent')) and r.get('direction') in DIRECTIONS, f'{path}: referent and direction required')
        mn = r.get('min')
        _need(isinstance(mn, int) and not isinstance(mn, bool) and mn >= 0, f'{path}/min: integer >= 0')
        if 'max' in r:
            mx = r['max']
            _need(isinstance(mx, int) and not isinstance(mx, bool) and mx >= mn, f'{path}/max: integer >= min')
        _opt_instance(r, path)
    elif k == 'absence':
        _need(set(r) <= {'rule_id', 'kind', 'subject', 'predicate_id', 'object', 'instance_ref', 'witness_ref'}, f'{path}: unknown field')
        _need(_str(r.get('subject')) or _str(r.get('object')), f'{path}: subject or object required')
        for f in ('subject', 'object'):
            if f in r:
                _need(_str(r[f]), f'{path}/{f}: nonempty string')
        _opt_instance(r, path)
    else:
        _need(set(r) <= {'rule_id', 'kind', 'instance_ref', 'gateway', 'predicate_id', 'incoming_flows', 'witness_ref'},
              f'{path}: unknown field')
        _need(_str(r.get('instance_ref')) and _str(r.get('gateway')), f'{path}: instance_ref and gateway required')
        fl = r.get('incoming_flows')
        _need(isinstance(fl, list) and fl, f'{path}/incoming_flows: nonempty array')
        seen = set()
        for n, f in enumerate(fl):
            _need(isinstance(f, dict) and set(f) <= {'flow', 'min'} and _str(f.get('flow')), f'{path}/incoming_flows/{n}: flow required')
            _need(f['flow'] not in seen, f'{path}/incoming_flows/{n}: duplicate flow')
            seen.add(f['flow'])
            if 'min' in f:
                _need(isinstance(f['min'], int) and not isinstance(f['min'], bool) and f['min'] >= 1, f'{path}/incoming_flows/{n}/min: integer >= 1')


def _ids(items, key, path):
    seen = set()
    for i, x in enumerate(items):
        _need(x[key] not in seen, f'{path}/{i}/{key}: duplicate')
        seen.add(x[key])


def project_v7(ctx):
    """View for the unchanged P1.11 path: format /7, P1.12 fields removed."""
    out = copy.deepcopy(ctx)
    out['format'] = FORMAT7
    for k in V8_TOP:
        out.pop(k, None)
    for r in out.get('referents', []) if isinstance(out.get('referents'), list) else []:
        if isinstance(r, dict):
            r.pop('instance_ref', None)
    for p in out.get('predicate_contracts', []) if isinstance(out.get('predicate_contracts'), list) else []:
        if isinstance(p, dict):
            p.pop('requires_same_instance', None)
    return out


def validate_context_v8(ctx, validate_v7):
    """Shape checks for /8 (config errors), then the unchanged /7 validation on the projection."""
    _need(isinstance(ctx, dict), 'context/8: expected object')
    extra = set(ctx) - set(V2_TOP + V3_TOP + V4_TOP + V5_TOP + V7_TOP + V8_TOP)
    _need(not extra, f'context/8: unknown {sorted(extra)}')
    _need(ctx.get('format') == FORMAT8, 'Unsupported context format')
    for i, r in enumerate(ctx.get('referents', []) if isinstance(ctx.get('referents'), list) else []):
        if isinstance(r, dict) and 'instance_ref' in r:
            _need(_str(r['instance_ref']), f'/referents/{i}/instance_ref: nonempty string')
    for i, p in enumerate(ctx.get('predicate_contracts', []) if isinstance(ctx.get('predicate_contracts'), list) else []):
        if isinstance(p, dict) and 'requires_same_instance' in p:
            _need(isinstance(p['requires_same_instance'], bool), f'/predicate_contracts/{i}/requires_same_instance: boolean')
    decls = ctx.get('coverage_declarations', [])
    _need(isinstance(decls, list) and len(decls) <= 2048, 'coverage_declarations: array (<= 2048)')
    for i, d in enumerate(decls):
        _declaration(d, f'/coverage_declarations/{i}')
    _ids(decls, 'declaration_id', '/coverage_declarations')
    rules = ctx.get('population_rules', [])
    _need(isinstance(rules, list) and len(rules) <= 512, 'population_rules: array (<= 512)')
    for i, r in enumerate(rules):
        _rule(r, f'/population_rules/{i}')
    _ids(rules, 'rule_id', '/population_rules')
    validate_v7(project_v7(ctx))
    return ctx


# --- CV-3: coverage -----------------------------------------------------------
def _inst_ok(decl, inst):
    """CV-4: a declaration without instance_ref covers all instances; with one, only that instance."""
    return 'instance_ref' not in decl or decl['instance_ref'] == inst


def covering(rule, decls):
    """Return the declaration IDs that cover the rule, or [] if it is not covered (CV-3)."""
    p, inst = rule['predicate_id'], rule.get('instance_ref')
    rrd = [d for d in decls if d['scope'] == 'referent_relation_direction' and d['predicate_id'] == p and _inst_ok(d, inst)]
    if rule['kind'] == 'count':
        hit = [d for d in rrd if d['referent'] == rule['referent'] and d['direction'] == rule['direction']]
        return [d['declaration_id'] for d in hit[:1]]
    if rule['kind'] == 'absence':
        s, o = rule.get('subject'), rule.get('object')
        if s and o:
            pair = [d for d in decls if d['scope'] == 'pair' and d['predicate_id'] == p and d['subject'] == s and d['object'] == o
                    and _inst_ok(d, inst)]
            if pair:
                return [pair[0]['declaration_id']]
        hit = [d for d in rrd if (s and d['referent'] == s and d['direction'] == 'outgoing') or (o and d['referent'] == o and d['direction'] == 'incoming')]
        return [d['declaration_id'] for d in hit[:1]]
    ids = []
    for f in rule['incoming_flows']:
        hit = [d for d in rrd if d['referent'] == f['flow'] and d['direction'] == 'incoming']
        if not hit:
            return []
        ids.append(hit[0]['declaration_id'])
    return ids


def rule_refs(rule):
    if rule['kind'] == 'count':
        return [('referent', rule['referent'])] + ([('instance_ref', rule['instance_ref'])] if 'instance_ref' in rule else [])
    if rule['kind'] == 'absence':
        return [(f, rule[f]) for f in ('subject', 'object', 'instance_ref') if f in rule]
    return [('instance_ref', rule['instance_ref']), ('gateway', rule['gateway'])] + \
        [(f'incoming_flows/{n}/flow', f['flow']) for n, f in enumerate(rule['incoming_flows'])]


def decl_refs(d):
    keys = ('referent',) if d['scope'] == 'referent_relation_direction' else ('subject', 'object')
    return [(k, d[k]) for k in keys] + ([('instance_ref', d['instance_ref'])] if 'instance_ref' in d else [])
