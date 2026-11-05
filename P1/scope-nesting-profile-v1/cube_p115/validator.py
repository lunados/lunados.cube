"""P1.15: scope chains, reference v2 and Admission outcomes layered on the unchanged P1.14 validator."""
from __future__ import annotations

from cube_parser.parser import parse_result
from cube_semantic.validator import SemanticValidator as FrozenValidator, join, nodes
from cube_p16.instantiation import CODES as P16_CODES, InstantiationCheck
from cube_p114.validator import P114Validator
from cube_p115.nesting import FORMAT11, project_v10, reference_v2, validate_context_v11

PROFILE = 'P1.15/scope-nesting-profile-v1'
CODES = {
    'P1_SCOPE_NESTING_INVALID': ('scope_consistency', 'P1.15 SN-2, SN-3: declared scope chain must end in the context scope'),
    'P1_ADMISSION_OUTCOME_CONFLICT': ('referent_binding', 'P1.15 AO-1: outcomes of one request share request_ref, at most one admitted'),
    'P1_SCOPE_CONFLICT': ('referent_binding', 'P1.15 SN-4: X endpoint scope neither the validation scope nor nested in it'),
    'P1_BINDING_CONTEXT_REQUIRED': ('referent_binding', 'P1.3 declared context referent required'),
    'P1_REFERENT_MISMATCH': ('referent_binding', 'P1.3 exact identity consistency'),
}
LABEL = {'referent_binding': 'referent', 'scope_consistency': 'scope'}
SUPERSEDED = set(P16_CODES) | {'P1_SCOPE_CONFLICT', 'P1_REFERENT_MISMATCH'}


def _diag(code, path, message, *, status='FAIL'):
    stage, rule = CODES[code]
    return {'code': code, 'stage': stage, 'severity': 'error' if status == 'FAIL' else 'unresolved',
            'message': f'{path}: {message}', 'reference_rule': rule}


class _CheckV2(InstantiationCheck):
    """P1.6 instance check with reference v2 and the unnarrowed /11 profiles."""

    def __init__(self, context):
        self.ctx = context
        self.vocab, _ = reference_v2()
        self.refs = {r['ref']: (i, r) for i, r in enumerate(context['referents'])}
        self.profiles = context.get('instantiation_profiles', [])


def chains(ctx):
    """SN-2, SN-3: map every valid inner scope to True; return diagnostics for invalid declarations."""
    scope = ctx.get('scope_ref')
    refs = {r['ref']: r for r in ctx['referents']}
    parent = {n['inner']: n['outer'] for n in ctx.get('scope_nesting', [])}
    diags, valid = [], {}

    def is_x_scope(ref):
        r = refs.get(ref)
        return bool(r) and r['concept_id'].startswith('X:scope:') and r.get('scope_ref') == ref

    for i, n in enumerate(ctx.get('scope_nesting', [])):
        path = f'/scope_nesting/{i}'
        if not is_x_scope(n['inner']):
            diags.append(_diag('P1_SCOPE_NESTING_INVALID', path + '/inner', 'Inner must be a declared X scope referent whose scope_ref is itself.'))
            continue
        if n['outer'] != scope and not is_x_scope(n['outer']):
            diags.append(_diag('P1_SCOPE_NESTING_INVALID', path + '/outer', 'Outer must be the context scope or a declared X scope referent.'))
            continue
        seen, cur = [n['inner']], n['outer']
        while cur != scope and cur in parent and cur not in seen and is_x_scope(cur):
            seen.append(cur)
            cur = parent[cur]
        if cur == scope:
            valid[n['inner']] = True
        elif cur in seen:
            diags.append(_diag('P1_SCOPE_NESTING_INVALID', path, 'Scope chain contains a cycle.'))
        else:
            diags.append(_diag('P1_SCOPE_NESTING_INVALID', path, 'Scope chain does not end in the context scope.'))
    return valid, diags


class P115Validator:
    def __init__(self):
        self.p114 = P114Validator()
        self.concepts = self.p114.concepts
        self.exact = FrozenValidator().resolver.exact

    def validate_context(self, ctx):
        if isinstance(ctx, dict) and ctx.get('format') == FORMAT11:
            return validate_context_v11(ctx, self.p114.validate_context)
        return self.p114.validate_context(ctx)

    def _endpoint(self, ctx, check, valid, refid, path, layer, add, *, concept=None):
        refs = {r['ref']: r for r in ctx['referents']}
        r = refs.get(refid)
        if r is None:
            add.append(_diag('P1_BINDING_CONTEXT_REQUIRED', path, 'X endpoint referent is not declared.', status='UNRESOLVED'))
            return
        if concept and (r['concept_id'] != concept or layer not in r['layers']):
            add.append(_diag('P1_REFERENT_MISMATCH', path, 'X endpoint concept/home/layer contradicts request.'))
            return
        if r.get('scope_ref') != ctx.get('scope_ref') and not valid.get(r.get('scope_ref')):
            add.append(_diag('P1_SCOPE_CONFLICT', path, 'X endpoint scope is neither the validation scope nor nested in it by a declared chain.'))
            return
        _, ds = check.run(refid, layer)
        for d in ds:
            add.append({k: v for k, v in d.items() if k != 'ast_path'} | {'message': d['ast_path'] + ': ' + d['message']})

    def validate_bytes(self, raw, *, input_format='acg_text', context=None, qualification_profiles=None):
        if context is None or context.get('format') != FORMAT11:
            return self.p114.validate_bytes(raw, input_format=input_format, context=context,
                                            qualification_profiles=qualification_profiles)
        ctx = context
        self.validate_context(ctx)
        report = self.p114.validate_bytes(raw, input_format=input_format, context=project_v10(ctx),
                                          qualification_profiles=qualification_profiles)
        parsed = parse_result(raw, input_format=input_format)
        refs = {r['ref']: r for r in ctx['referents']}
        valid, add = chains(ctx)
        check = _CheckV2(ctx)
        x_paths, nested_paths = [], []
        if parsed['structure_status'] == 'PASS':
            for path, node, _ in nodes(parsed['ast']):
                if node['kind'] != 'reference':
                    continue
                addr = node['address']
                e = self.exact.get((addr['home'], addr['concept_key']))
                if not e or not e['concept_id'].startswith('X:endpoint:'):
                    continue
                x_paths.append(path)
                r = refs.get(node['referent_ref'])
                if r and r.get('scope_ref') != ctx.get('scope_ref') and valid.get(r.get('scope_ref')):
                    nested_paths.append(path)
                self._endpoint(ctx, check, valid, node['referent_ref'], path, addr['layer'], add, concept=e['concept_id'])
        # AO-1, AO-2: outcomes of one Admission request at an exclusive gateway
        for i, g in enumerate((ctx.get('control_flow') or {}).get('gateways', [])):
            if g.get('type') != 'exclusive':
                continue
            outs = [o['target'] for o in g['outgoing'] if refs.get(o['target'], {}).get('concept_id') == 'X:endpoint:admission']
            if len(outs) < 2:
                continue
            gp = f'/control_flow/gateways/{i}'
            slots = [refs[t].get('slots') or {} for t in outs]
            if len({s.get('request_ref') for s in slots}) != 1 or None in {s.get('request_ref') for s in slots}:
                add.append(_diag('P1_ADMISSION_OUTCOME_CONFLICT', gp, 'Outcomes of one request must share request_ref.'))
            if sum(1 for s in slots if s.get('decision') == 'admitted') > 1:
                add.append(_diag('P1_ADMISSION_OUTCOME_CONFLICT', gp, 'At most one outcome may be admitted.'))
            for t in outs:
                self._endpoint(ctx, check, valid, t, f'{gp}/outgoing[{t}]', 'α', add)
        # Supersede lower X-endpoint results: P1.6 diagnostics, and the scope conflict of nested endpoints.
        def lower_x(d):
            msg = d['message']
            if d['code'] in P16_CODES and msg.startswith('/referents/'):
                return True
            for p in x_paths:
                if msg.startswith(p + ': ') and d['code'] in SUPERSEDED and d['stage'] == 'referent_binding':
                    return True
            for p in nested_paths:
                if msg.startswith(p + ': ') and d['code'] == 'P1_SCOPE_CONFLICT':
                    return True
            return False
        report['diagnostics'] = [d for d in report['diagnostics'] if not lower_x(d)]
        seen = {(d['code'], d['message']) for d in report['diagnostics']}
        for d in add:
            if (d['code'], d['message']) not in seen:
                seen.add((d['code'], d['message']))
                report['diagnostics'].append(d)
        for stage in ('referent_binding', 'scope_consistency'):
            statuses = [('FAIL' if d['severity'] == 'error' else 'UNRESOLVED') for d in report['diagnostics'] if d['stage'] == stage]
            if statuses or report['checks'][stage]['status'] != 'NOT_EVALUATED':
                report['checks'][stage] = FrozenValidator._stage(statuses or ['PASS'], LABEL[stage])
        report['diagnostics'].sort(key=lambda d: (d.get('byte_start', 10**12), d['code'], d['stage'], d['message']))
        report['overall_status'] = join([c['status'] for c in report['checks'].values()])
        if report['overall_status'] == 'NOT_EVALUATED':
            report['overall_status'] = 'UNRESOLVED'
        return report


def validate_context(ctx):
    return P115Validator().validate_context(ctx)
