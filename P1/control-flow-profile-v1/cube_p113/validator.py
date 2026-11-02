"""Additive P1.13 validator: /9 projects to /8, then CF and TB checks run.

The Cube validates declarations and individual statements. Trace evaluation belongs
to analyze.trace-conformance/v1 in lunados.lib.
"""
from __future__ import annotations

from cube_semantic.validator import SemanticValidator as FrozenValidator, join, nodes
from cube_parser.parser import parse_result
from cube_p112.validator import P112Validator, CODES as P112_CODES, _unwrap
from cube_p113.control_flow import FORMAT9, project_v8, validate_context_v9

PROFILE = 'P1.13/control-flow-profile-v1'
CODES = {
    'P1_CONTROL_FLOW_INVALID': ('scope_consistency', 'P1.13 CF-2…CF-4: invalid gateway control-flow declaration'),
    'P1_CONTROL_FLOW_UNSUPPORTED': ('scope_consistency', 'P1.13 CF-5: gateway type outside exclusive and parallel'),
    'P1_FLOW_UNDECLARED': ('scope_consistency', 'P1.13 TB-1…TB-2: statement names a flow or target outside the declaration'),
    'P1_TOKEN_POSITION_UNDECLARED': ('scope_consistency', 'P1.13 TB-1: routing token has no at_gateway position'),
    'P1_BINDING_CONTEXT_REQUIRED': P112_CODES['P1_BINDING_CONTEXT_REQUIRED'],
}
_LABEL = {'scope_consistency': 'scope', 'referent_binding': 'referent'}


def _d(code, status, path, message):
    stage, rule = CODES[code]
    return stage, status, {'code': code, 'stage': stage, 'severity': 'error' if status == 'FAIL' else 'unresolved',
                           'message': f'{path}: {message}', 'reference_rule': rule}


class P113Validator:
    def __init__(self):
        self.p112 = P112Validator()
        self.concepts = self.p112.concepts

    def validate_context(self, ctx):
        if isinstance(ctx, dict) and ctx.get('format') == FORMAT9:
            return validate_context_v9(ctx, self.p112.validate_context)
        return self.p112.validate_context(ctx)

    def _context_checks(self, ctx, out):
        refs = {r['ref']: r for r in ctx.get('referents', [])}
        gateways = ctx.get('control_flow', {}).get('gateways', [])
        by_gateway = {g['gateway']: g for g in gateways}
        declared_flows = set()
        outgoing_owner, incoming_owner = {}, {}
        seen_gateways = set()
        for i, g in enumerate(gateways):
            base = f'/control_flow/gateways/{i}'
            if g['gateway'] in seen_gateways:
                out.append(_d('P1_CONTROL_FLOW_INVALID', 'FAIL', base + '/gateway', 'Duplicate gateway.'))
            seen_gateways.add(g['gateway'])
            if g['gateway'] not in refs:
                out.append(_d('P1_BINDING_CONTEXT_REQUIRED', 'UNRESOLVED', base + '/gateway',
                              f'Undeclared gateway referent {g["gateway"]!r} (CF-1).'))
            for j, flow in enumerate(g['incoming']):
                path = f'{base}/incoming/{j}'
                declared_flows.add(flow)
                if flow not in refs:
                    out.append(_d('P1_BINDING_CONTEXT_REQUIRED', 'UNRESOLVED', path,
                                  f'Undeclared incoming flow referent {flow!r} (CF-1).'))
                if flow in incoming_owner:
                    out.append(_d('P1_CONTROL_FLOW_INVALID', 'FAIL', path,
                                  f'Incoming flow {flow!r} already belongs to {incoming_owner[flow]!r} (CF-4).'))
                incoming_owner[flow] = g['gateway']
            defaults = 0
            orders = set()
            for j, f in enumerate(g['outgoing']):
                path = f'{base}/outgoing/{j}'
                flow = f['flow']
                declared_flows.add(flow)
                for field in ('flow', 'target'):
                    if f[field] not in refs:
                        out.append(_d('P1_BINDING_CONTEXT_REQUIRED', 'UNRESOLVED', path + '/' + field,
                                      f'Undeclared {field} referent {f[field]!r} (CF-1).'))
                if flow in outgoing_owner:
                    out.append(_d('P1_CONTROL_FLOW_INVALID', 'FAIL', path + '/flow',
                                  f'Outgoing flow {flow!r} already belongs to {outgoing_owner[flow]!r} (CF-4).'))
                outgoing_owner[flow] = g['gateway']
                if g['type'] == 'parallel':
                    if any(k in f for k in ('default', 'order', 'condition_ref')):
                        out.append(_d('P1_CONTROL_FLOW_INVALID', 'FAIL', path,
                                      'Parallel gateway cannot declare default, order or condition_ref (CF-3).'))
                elif g['type'] == 'exclusive':
                    if f.get('default') is True:
                        defaults += 1
                        if 'order' in f or 'condition_ref' in f:
                            out.append(_d('P1_CONTROL_FLOW_INVALID', 'FAIL', path,
                                          'Default flow cannot carry order or condition_ref (CF-2).'))
                    elif 'order' not in f and (len(g['outgoing']) > 1 or 'condition_ref' in f):
                        out.append(_d('P1_CONTROL_FLOW_INVALID', 'FAIL', path + '/order',
                                      'Non-default branch needs an order (CF-2).'))
                    if 'order' in f:
                        if f['order'] in orders:
                            out.append(_d('P1_CONTROL_FLOW_INVALID', 'FAIL', path + '/order',
                                          f'Duplicate condition order {f["order"]} (CF-2).'))
                        orders.add(f['order'])
            if g['type'] == 'exclusive' and defaults > 1:
                out.append(_d('P1_CONTROL_FLOW_INVALID', 'FAIL', base,
                              'Exclusive gateway has more than one default (CF-2).'))
            if g['type'] not in ('exclusive', 'parallel'):
                out.append(_d('P1_CONTROL_FLOW_UNSUPPORTED', 'UNRESOLVED', base + '/type',
                              f'Gateway type {g["type"]!r} is outside P1.13 (CF-5).'))
        for i, r in enumerate(ctx.get('referents', [])):
            if 'at_gateway' in r and r['at_gateway'] not in by_gateway:
                out.append(_d('P1_BINDING_CONTEXT_REQUIRED', 'UNRESOLVED', f'/referents/{i}/at_gateway',
                              f'{r["at_gateway"]!r} is not a declared gateway (TB-1).'))
        return refs, by_gateway, declared_flows

    def _statement_checks(self, raw, input_format, ctx, refs, gateways, flows, out):
        parsed = parse_result(raw, input_format=input_format)
        if parsed['structure_status'] != 'PASS':
            return
        scope = ctx.get('scope_ref')
        roles = {p['predicate_id']: p['control_flow_role'] for p in ctx.get('predicate_contracts', [])
                 if p.get('scope') == scope and 'control_flow_role' in p}
        for path, node, _ in nodes(parsed['ast']):
            if node['kind'] != 'relation' or node['predicate_id'] not in roles:
                continue
            subject, obj = _unwrap(node['subject']), _unwrap(node['object'])
            if subject['kind'] != 'reference' or obj['kind'] != 'reference':
                continue
            token, target = subject['referent_ref'], obj['referent_ref']
            if roles[node['predicate_id']] == 'on_flow':
                if target in refs and target not in flows:
                    out.append(_d('P1_FLOW_UNDECLARED', 'FAIL', path or '/',
                                  f'{target!r} is not a declared flow (TB-2).'))
                continue
            if token not in refs or target not in refs:
                continue
            at = refs[token].get('at_gateway')
            if at is None:
                out.append(_d('P1_TOKEN_POSITION_UNDECLARED', 'UNRESOLVED', path or '/',
                              f'Routing token {token!r} has no at_gateway (TB-1).'))
                continue
            g = gateways.get(at)
            if g is None or g['type'] not in ('exclusive', 'parallel'):
                continue  # Already unresolved by context check.
            if g['type'] != 'exclusive' or target not in {f['target'] for f in g['outgoing']}:
                out.append(_d('P1_FLOW_UNDECLARED', 'FAIL', path or '/',
                              f'{target!r} is not an outgoing target of exclusive gateway {at!r} (TB-1).'))

    def validate_bytes(self, raw, *, input_format='acg_text', context=None, qualification_profiles=None):
        if context is None or context.get('format') != FORMAT9:
            return self.p112.validate_bytes(raw, input_format=input_format, context=context,
                                            qualification_profiles=qualification_profiles)
        self.validate_context(context)
        report = self.p112.validate_bytes(raw, input_format=input_format, context=project_v8(context),
                                          qualification_profiles=qualification_profiles)
        add = []
        refs, gateways, flows = self._context_checks(context, add)
        self._statement_checks(raw, input_format, context, refs, gateways, flows, add)
        if not add:
            return report
        checks = report['checks']
        by_stage = {}
        for stage, status, diagnostic in add:
            by_stage.setdefault(stage, []).append(status)
            report['diagnostics'].append(diagnostic)
        for stage, statuses in by_stage.items():
            before = [checks[stage]['status']] if checks[stage]['status'] != 'NOT_EVALUATED' else []
            checks[stage] = FrozenValidator._stage(before + statuses, _LABEL[stage])
        report['overall_status'] = join([check['status'] for check in checks.values()])
        if report['overall_status'] == 'NOT_EVALUATED':
            report['overall_status'] = 'UNRESOLVED'
        return report


def validate_context(ctx):
    return P113Validator().validate_context(ctx)
