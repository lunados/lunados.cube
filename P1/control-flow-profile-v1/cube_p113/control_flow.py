"""Shape validation and /8 projection for the additive P1.13 context."""
from __future__ import annotations
import copy

from cube_p112.coverage import FORMAT8, CoverageProfileError, V8_TOP
from cube_p111.methods import V7_TOP
from cube_p110.migration import V5_TOP
from cube_p18.simulation import V2_TOP, V3_TOP, _ne
from cube_p19.comparison import V4_TOP

FORMAT9 = 'aiaeao.cube.binding-context/9'
V9_TOP = ('control_flow',)


def _need(ok, message):
    if not ok:
        raise CoverageProfileError(message)


def _str(value):
    return _ne(value) and len(value) <= 512


def project_v8(ctx):
    """Remove only P1.13 fields; let P1.12 perform its unchanged /8→/7 projection."""
    out = copy.deepcopy(ctx)
    out['format'] = FORMAT8
    out.pop('control_flow', None)
    for ref in out.get('referents', []) if isinstance(out.get('referents'), list) else []:
        if isinstance(ref, dict):
            ref.pop('at_gateway', None)
    for pred in out.get('predicate_contracts', []) if isinstance(out.get('predicate_contracts'), list) else []:
        if isinstance(pred, dict):
            pred.pop('control_flow_role', None)
    return out


def validate_context_v9(ctx, validate_v8):
    """Malformed /9 fields are caller configuration errors, never semantic FAILs."""
    _need(isinstance(ctx, dict), 'context/9: expected object')
    allowed = set(V2_TOP + V3_TOP + V4_TOP + V5_TOP + V7_TOP + V8_TOP + V9_TOP)
    _need(not set(ctx) - allowed, f'context/9: unknown {sorted(set(ctx) - allowed)}')
    _need(ctx.get('format') == FORMAT9, 'Unsupported context format')
    for i, ref in enumerate(ctx.get('referents', []) if isinstance(ctx.get('referents'), list) else []):
        if isinstance(ref, dict) and 'at_gateway' in ref:
            _need(_str(ref['at_gateway']), f'/referents/{i}/at_gateway: nonempty string')
    for i, pred in enumerate(ctx.get('predicate_contracts', []) if isinstance(ctx.get('predicate_contracts'), list) else []):
        if isinstance(pred, dict) and 'control_flow_role' in pred:
            _need(pred['control_flow_role'] in ('routing', 'on_flow'),
                  f'/predicate_contracts/{i}/control_flow_role: routing or on_flow')
    if 'control_flow' in ctx:
        cf = ctx['control_flow']
        _need(isinstance(cf, dict) and set(cf) == {'gateways'}, '/control_flow: gateways array only')
        gateways = cf['gateways']
        _need(isinstance(gateways, list) and len(gateways) <= 512, '/control_flow/gateways: array (<= 512)')
        for i, gateway in enumerate(gateways):
            path = f'/control_flow/gateways/{i}'
            _need(isinstance(gateway, dict) and set(gateway) == {'gateway', 'type', 'incoming', 'outgoing'},
                  f'{path}: gateway, type, incoming and outgoing only')
            _need(_str(gateway['gateway']) and _str(gateway['type']), f'{path}: nonempty gateway and type')
            incoming, outgoing = gateway['incoming'], gateway['outgoing']
            _need(isinstance(incoming, list) and incoming and all(_str(f) for f in incoming),
                  f'{path}/incoming: nonempty array of flow refs')
            _need(isinstance(outgoing, list) and outgoing, f'{path}/outgoing: nonempty array')
            for j, flow in enumerate(outgoing):
                fp = f'{path}/outgoing/{j}'
                _need(isinstance(flow, dict) and {'flow', 'target'} <= set(flow) and
                      set(flow) <= {'flow', 'target', 'order', 'condition_ref', 'default'},
                      f'{fp}: flow and target required; unknown field')
                _need(_str(flow['flow']) and _str(flow['target']), f'{fp}: nonempty flow and target refs')
                if 'order' in flow:
                    _need(type(flow['order']) is int and flow['order'] >= 1, f'{fp}/order: integer >= 1')
                if 'condition_ref' in flow:
                    _need(_str(flow['condition_ref']), f'{fp}/condition_ref: nonempty string')
                if 'default' in flow:
                    _need(type(flow['default']) is bool, f'{fp}/default: boolean')
    validate_v8(project_v8(ctx))
    return ctx
